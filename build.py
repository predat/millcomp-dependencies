#!/usr/bin/env python3
"""Builds millComp's dependencies and packs them into one archive per platform, as GafferHQ/dependencies does.

Each project is projects/<Name>/config.py, a dictionary (the format is in README.md). Sources are checked against
lock.json. A project is rebuilt only when its digest changed (its config, its sources, its dependencies'), so a
build that stopped goes on where it was. Standard library only: it has to run before anything is installed.
"""

import argparse
import fnmatch
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
VERSION = (ROOT / "VERSION").read_text().strip()
LOCK = ROOT / "lock.json"
PLATFORM = "windows" if sys.platform == "win32" else "linux" if sys.platform.startswith("linux") else None
# Bump to rebuild everything: what build.py passes to every project changed.
DRIVER_REVISION = 1

# Left out of the archive: not needed to build against the dependencies or to run them.
EXCLUDED = [".stamps", ".stamps/*", "share/doc/*", "share/man/*", "doc/*", "man/*", "*/__pycache__/*", "*.pdb", "python/lib/python3.*/test/*", "python/Lib/test/*", "qt/sbom/*", "qt/doc/*"]

# What a Linux library of the archive may need from the system: the C and C++ runtimes. Qt's own libraries are not
# checked (they need X11, xcb, GL, as any Qt application does).
SYSTEM_LIBRARIES = ["ld-linux*", "libc.so*", "libm.so*", "libdl.so*", "libpthread.so*", "librt.so*", "libutil.so*", "libstdc++.so*", "libgcc_s.so*"]


def loadProjects():
    projects = {}
    for config in sorted((ROOT / "projects").glob("*/config.py")):
        project = eval(compile(config.read_text(), str(config), "eval"), {"__builtins__": {}})
        projects[config.parent.name] = project
    for name, project in projects.items():
        for dependency in project.get("dependencies", []):
            if dependency not in projects:
                sys.exit(f"{name}: unknown dependency {dependency}")
    return projects


def ordered(projects, wanted):
    """`wanted` and what it needs, dependencies first."""
    result, visiting = [], set()

    def visit(name):
        if name in result:
            return
        if name in visiting:
            sys.exit(f"cycle through {name}")
        visiting.add(name)
        for dependency in projects[name].get("dependencies", []):
            visit(dependency)
        result.append(name)

    for name in wanted:
        if name not in projects:
            sys.exit(f"unknown project {name}")
        visit(name)
    return result


def field(project, key, platform=PLATFORM):
    """A list field and its platform's additions (`key:windows`)."""
    return list(project.get(key, [])) + list(project.get(f"{key}:{platform}", []))


def lockEntry(lock, url):
    if url not in lock:
        sys.exit(f"{url} is not in lock.json: run build.py --update-lock")
    return lock[url]


def fetch(url, archives):
    file = archives / url.split("/")[-1].replace("%2B", "+")
    # The same file name for two projects' tags (v3.2.1.tar.gz): the URL's hash keeps them apart.
    file = archives / f"{hashlib.sha256(url.encode()).hexdigest()[:12]}-{file.name}"
    if not file.exists():
        archives.mkdir(parents=True, exist_ok=True)
        print(f"  downloading {url}", flush=True)
        partial = file.with_name(file.name + ".part")
        request = urllib.request.Request(url, headers={"User-Agent": "millcomp-dependencies-build"})
        with urllib.request.urlopen(request, timeout=300) as response, open(partial, "wb") as out:
            shutil.copyfileobj(response, out)
        partial.rename(file)
    return file


def sha256(file):
    digest = hashlib.sha256()
    with open(file, "rb") as data:
        for block in iter(lambda: data.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def extract(archive, destination):
    """Unpacks `archive` into `destination`, without its single top-level directory when it has one."""
    temporary = destination.with_name(destination.name + ".extract")
    shutil.rmtree(temporary, ignore_errors=True)
    temporary.mkdir(parents=True)
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as data:
            data.extractall(temporary)
    else:
        with tarfile.open(archive) as data:
            data.extractall(temporary, filter="tar")
    entries = list(temporary.iterdir())
    source = entries[0] if len(entries) == 1 and entries[0].is_dir() else temporary
    destination.mkdir(parents=True, exist_ok=True)
    for entry in source.iterdir():
        target = destination / entry.name
        if target.is_dir() and entry.is_dir():
            shutil.copytree(entry, target, dirs_exist_ok=True, symlinks=True)
        else:
            if target.exists() or target.is_symlink():
                target.unlink()
            shutil.move(str(entry), str(target))
    shutil.rmtree(temporary)


def projectFiles(name):
    """The hashes of what a project's directory holds: config.py, and the scripts it runs."""
    directory = ROOT / "projects" / name
    return {path.relative_to(directory).as_posix(): sha256(path) for path in sorted(directory.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def digests(projects, names, lock):
    result = {}
    for name in names:
        project = projects[name]
        content = {
            "driver": DRIVER_REVISION,
            "files": projectFiles(name),
            "sources": {url: lockEntry(lock, url) for url in field(project, "downloads")},
            "dependencies": {dependency: result[dependency] for dependency in project.get("dependencies", [])},
        }
        result[name] = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    return result


def substitute(text, variables):
    return text.format(**variables)


def run(command, cwd, environment):
    print("  $ " + " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], cwd=cwd, env=environment, check=True)


def buildProject(name, project, buildDir, workDir, archives, lock, jobs):
    work = workDir / name
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    source = work / "source"
    python = buildDir / "python" / ("python.exe" if PLATFORM == "windows" else "bin/python3")
    variables = {
        "buildDir": buildDir.as_posix(),
        "work": work.as_posix(),
        "source": source.as_posix(),
        "python": python.as_posix(),
        "projectDir": (ROOT / "projects" / name).as_posix(),
        "jobs": jobs,
    }

    for url in field(project, "downloads"):
        file = fetch(url, archives)
        if sha256(file) != lockEntry(lock, url):
            file.unlink()
            sys.exit(f"{url}: the file does not match lock.json")
        destination = project.get("extractTo")
        extract(file, pathlib.Path(substitute(destination, variables)) if destination else source)

    environment = dict(os.environ)
    environment["CMAKE_PREFIX_PATH"] = buildDir.as_posix()
    if PLATFORM == "windows":
        environment["PATH"] = os.pathsep.join([str(buildDir / "bin"), str(buildDir / "lib"), str(buildDir / "python"), environment["PATH"]])
    else:
        environment["PATH"] = os.pathsep.join([str(buildDir / "bin"), str(buildDir / "python/bin"), environment["PATH"]])
        environment["LD_LIBRARY_PATH"] = os.pathsep.join([str(buildDir / "lib"), environment.get("LD_LIBRARY_PATH", "")])
    for key, value in project.get("environment", {}).items():
        environment[key] = substitute(value, variables)

    if "cmake" in project or "cmake:windows" in project or "cmake:linux" in project:
        cmakeSource = source / project.get("cmakeSource", ".")
        arguments = [
            "cmake",
            "-S", cmakeSource,
            "-B", work / "build",
            "-G", "Ninja",
            "-Wno-dev",
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_INSTALL_PREFIX={variables['buildDir']}",
            f"-DCMAKE_PREFIX_PATH={variables['buildDir']}",
            "-DCMAKE_INSTALL_LIBDIR=lib",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
            "-DBUILD_SHARED_LIBS=ON",
            f"-DPython_ROOT_DIR={(buildDir / 'python').as_posix()}",
            f"-DPython3_ROOT_DIR={(buildDir / 'python').as_posix()}",
            "-DPython_FIND_STRATEGY=LOCATION",
            "-DPython3_FIND_STRATEGY=LOCATION",
        ]
        if PLATFORM == "linux":
            arguments += ["-DCMAKE_INSTALL_RPATH=$ORIGIN/../lib", "-DCMAKE_C_FLAGS=-fPIC", "-DCMAKE_CXX_FLAGS=-fPIC"]
        arguments += [substitute(argument, variables) for argument in field(project, "cmake")]
        run(arguments, work, environment)
        run(["cmake", "--build", work / "build", "-j", jobs], work, environment)
        run(["cmake", "--install", work / "build"], work, environment)

    for command in field(project, "commands"):
        run([substitute(part, variables) for part in command], work, environment)
    for source_, destination in field(project, "moves"):
        target = pathlib.Path(substitute(destination, variables))
        shutil.rmtree(target, ignore_errors=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(substitute(source_, variables), str(target))

    licenses = buildDir / "licenses" / name
    licenses.mkdir(parents=True, exist_ok=True)
    for pattern in field(project, "license"):
        root = pathlib.Path(substitute(project.get("extractTo", "{source}"), variables))
        found = list(root.glob(pattern))
        if not found:
            sys.exit(f"{name}: no license file {pattern} in {root}")
        for file in found:
            shutil.copy(file, licenses / file.name)
    shutil.rmtree(work, ignore_errors=True)


def writeManifest(projects, names, lock, buildDir):
    manifest = {
        "version": VERSION,
        "platform": PLATFORM,
        "projects": {
            name: {
                "version": projects[name].get("version", ""),
                "url": projects[name].get("url", ""),
                "sources": {url: lock[url] for url in field(projects[name], "downloads")},
            }
            for name in names
        },
    }
    (buildDir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def auditLinux(buildDir):
    """Fails on a library that needs something neither in the archive nor in SYSTEM_LIBRARIES: a dependency that a
    project found on the build machine, and that a user of the archive does not have."""
    shipped, failures = set(), []
    files = []
    for path in list(buildDir.rglob("*.so*")) + list((buildDir / "bin").glob("*")):
        if path.is_file() and not path.is_symlink() or path.is_symlink() and path.exists():
            shipped.add(path.name)
            if path.is_file() and "/qt/" not in path.as_posix() and "/python/" not in path.as_posix():
                files.append(path)
    for file in files:
        result = subprocess.run(["readelf", "-d", str(file)], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "(NEEDED)" not in line:
                continue
            needed = line.split("[")[1].split("]")[0]
            if needed not in shipped and not any(fnmatch.fnmatch(needed, pattern) for pattern in SYSTEM_LIBRARIES):
                failures.append(f"{file.relative_to(buildDir)} needs {needed}")
    if failures:
        sys.exit("libraries found on the build machine:\n  " + "\n  ".join(sorted(set(failures))))
    print(f"audit: {len(files)} files, nothing from the build machine")


def package(buildDir, output):
    excluded = lambda relative: any(fnmatch.fnmatch(relative, pattern) for pattern in EXCLUDED)
    top = f"millcompDependencies-{VERSION}-{PLATFORM}"
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for directory, subdirectories, names in os.walk(buildDir):
        for name in names + [d for d in subdirectories if (pathlib.Path(directory) / d).is_symlink()]:
            path = pathlib.Path(directory) / name
            relative = path.relative_to(buildDir).as_posix()
            if not excluded(relative):
                files.append((path, f"{top}/{relative}"))
    if PLATFORM == "windows":
        archive = output / f"{top}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as data:
            for path, name in files:
                data.write(path, name)
    else:
        archive = output / f"{top}.tar.gz"
        with tarfile.open(archive, "w:gz", compresslevel=6) as data:
            for path, name in files:
                data.add(path, name, recursive=False)
    (output / f"{archive.name}.sha256").write_text(f"{sha256(archive)}  {archive.name}\n")
    print(f"{archive}: {archive.stat().st_size >> 20} MB, {len(files)} files")
    return archive


def updateLock(projects, archives):
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    wanted = set()
    for project in projects.values():
        for platform in ("linux", "windows"):
            wanted.update(field(project, "downloads", platform))
    for url in sorted(wanted):
        if url not in lock:
            lock[url] = sha256(fetch(url, archives))
    lock = {url: lock[url] for url in sorted(wanted)}
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    print(f"lock.json: {len(lock)} sources")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", nargs="*", help="only these projects and what they need; default: all")
    parser.add_argument("--build-dir", default="build/install", help="the install prefix, what gets packed")
    parser.add_argument("--work-dir", default="build/work", help="sources and objects; keep it short on Windows")
    parser.add_argument("--archives", default="build/archives", help="the downloaded sources")
    parser.add_argument("--output", default="build/package", help="where the archive goes")
    parser.add_argument("--jobs", type=int, default=os.cpu_count(), help="parallel compile jobs of a project")
    parser.add_argument("--package", action="store_true", help="pack the archive once built")
    parser.add_argument("--update-lock", action="store_true", help="download what lock.json misses, record its hash, and stop")
    arguments = parser.parse_args()

    if not PLATFORM:
        sys.exit(f"{sys.platform}: only linux and windows are supported")
    projects = loadProjects()
    archives = pathlib.Path(arguments.archives).resolve()
    if arguments.update_lock:
        updateLock(projects, archives)
        return
    lock = json.loads(LOCK.read_text())
    buildDir = pathlib.Path(arguments.build_dir).resolve()
    workDir = pathlib.Path(arguments.work_dir).resolve()
    stamps = buildDir / ".stamps"
    stamps.mkdir(parents=True, exist_ok=True)

    names = ordered(projects, arguments.projects or sorted(projects))
    # On this platform only: a `platforms` list leaves a project out, and those that need it must say so too.
    names = [name for name in names if PLATFORM in projects[name].get("platforms", [PLATFORM])]
    current = digests(projects, names, lock)
    for index, name in enumerate(names):
        stamp = stamps / name
        if stamp.exists() and stamp.read_text() == current[name]:
            print(f"[{index + 1}/{len(names)}] {name}: up to date", flush=True)
            continue
        print(f"[{index + 1}/{len(names)}] {name} {projects[name].get('version', '')}", flush=True)
        stamp.unlink(missing_ok=True)
        buildProject(name, projects[name], buildDir, workDir, archives, lock, arguments.jobs)
        stamp.write_text(current[name])

    if arguments.package:
        writeManifest(projects, names, lock, buildDir)
        if PLATFORM == "linux":
            auditLinux(buildDir)
        package(buildDir, pathlib.Path(arguments.output).resolve())


if __name__ == "__main__":
    main()
