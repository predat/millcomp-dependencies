#!/usr/bin/env python3
"""Looks for new upstream versions of the projects, within the series each project's `updates` allows, and applies
them: the project's config.py (its version, everywhere it appears) and lock.json. A version whose sources do not
download yet for every platform (a release without all its assets) waits for a later run. Standard library only.

`updates`, in a project's config.py, is a list of:
  {'kind': 'git-tags', 'repo': <git URL>, 'tag': <regex; its groups are the version's numbers>, 'series': '3.2'}
  {'kind': 'python-build-standalone', 'series': '3.13'}  the latest release, when it has a newer CPython
  {'kind': 'qt', 'series': '6.12'}                         Qt's online repository, on every platform
  {'kind': 'pypi', 'package': 'numpy', 'series': '2'}      a pin, package==version, in the project's commands; only in
                                                           the Python project (its version is the Python it must install in)
`series`: the versions allowed, that one and what is below it ('3.2': 3.2.x; absent: any).
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import urllib.request

import build

QT_REPOSITORY = "https://download.qt.io/online/qtsdkrepository"
QT_PLATFORMS = ["linux_x64", "windows_x86", "mac_x64"]


def parse(version):
    return tuple(int(part) for part in version.split("."))


def newest(versions, current, series):
    """The highest of `versions` above `current` in `series`, or None."""
    allowed = [
        v
        for v in versions
        if (series is None or v == series or v.startswith(series + ".")) and parse(v) > parse(current)
    ]
    return max(allowed, key=parse) if allowed else None


def get(url):
    headers = {"User-Agent": "millcomp-dependencies-updates"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as response:
        return response.read()


def gitTags(project, spec, text):
    output = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", spec["repo"]], capture_output=True, text=True, check=True
    ).stdout
    tags = {}
    for line in output.splitlines():
        tag = line.split("refs/tags/", 1)[1]
        match = re.fullmatch(spec["tag"], tag)
        if match:
            tags[".".join(str(int(group)) for group in match.groups() if group is not None)] = tag
    current = project["version"]
    if current not in tags:
        raise RuntimeError(f"no tag for the current version {current}")
    found = newest(tags, current, spec.get("series"))
    if not found:
        return None
    return current, found, [("plain", tags[current], tags[found]), ("version", current, found)]


def pythonBuildStandalone(project, spec, text):
    release = json.loads(get("https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"))
    date = release["tag_name"]
    oldDate = re.search(r"/download/(\d{8})/", text).group(1)
    triples = set(re.findall(r"cpython-[\d.]+%2B\d{8}-([\w-]+)-install_only\.tar\.gz", text))
    versions = None
    for triple in triples:  # a version every platform has
        pattern = rf"cpython-(\d+\.\d+\.\d+)\+{date}-{re.escape(triple)}-install_only\.tar\.gz"
        found = {match.group(1) for asset in release["assets"] if (match := re.fullmatch(pattern, asset["name"]))}
        versions = found if versions is None else versions & found
    current = project["version"]
    found = newest(versions or [], current, spec.get("series"))
    if not found:  # a new build of the same CPython is not worth rebuilding everything that links it
        return None
    return (
        current,
        found,
        [
            ("plain", f"/download/{oldDate}/", f"/download/{date}/"),
            ("plain", f"%2B{oldDate}-", f"%2B{date}-"),
            ("version", current, found),
        ],
    )


def qt(project, spec, text):
    series = spec["series"]
    prefix = "qt6_" + series.replace(".", "")
    versions = None
    for platform in QT_PLATFORMS:  # a version every platform has
        listing = get(f"{QT_REPOSITORY}/{platform}/desktop/").decode()
        found = {f"{series}.{int(patch)}" for patch in re.findall(rf'href="{prefix}(\d+)/"', listing)}
        versions = found if versions is None else versions & found
    current = project["version"]
    found = newest(versions, current, series)
    return (current, found, [("version", current, found)]) if found else None


def allows(requires, python):
    """Whether a Requires-Python specifier (">=3.9,<3.13", "!=3.0.*") accepts the Python version `python`."""
    for clause in filter(None, (part.strip() for part in (requires or "").split(","))):
        operator, version = re.fullmatch(r"(~=|===|==|!=|<=|>=|<|>)\s*(.+)", clause).groups()
        if version.endswith(".*"):  # a prefix
            prefix = parse(version[:-2])
            if (python[: len(prefix)] == prefix) != (operator == "=="):
                return False
            continue
        bound = parse(version)
        padded = python[: len(bound)] + (0,) * (len(bound) - len(python))
        if operator == "~=":
            if not (padded >= bound and python[: len(bound) - 1] == bound[:-1]):
                return False
        elif not {
            "==": padded == bound,
            "===": padded == bound,
            "!=": padded != bound,
            "<=": padded <= bound,
            ">=": padded >= bound,
            "<": padded < bound,
            ">": padded > bound,
        }[operator]:
            return False
    return True


def pypi(project, spec, text):
    """A package installed in the archive's Python: only its releases that Python can install."""
    package = spec["package"]
    python = parse(project["version"])
    current = re.search(rf"'{re.escape(package)}==([\d.]+)'", text).group(1)
    releases = json.loads(get(f"https://pypi.org/pypi/{package}/json"))["releases"]
    final = [
        v
        for v, files in releases.items()
        if re.fullmatch(r"\d+(\.\d+)*", v)
        and any(not f.get("yanked") and allows(f.get("requires_python"), python) for f in files)
    ]
    found = newest(final, current, spec.get("series"))
    return (current, found, [("plain", f"'{package}=={current}'", f"'{package}=={found}'")]) if found else None


CHECKS = {"git-tags": gitTags, "python-build-standalone": pythonBuildStandalone, "qt": qt, "pypi": pypi}


def replace(text, kind, old, new):
    if kind == "plain":
        return text.replace(old, new)
    # A version, not part of a longer one: 1.4.0 in v1.4.0.tar.gz, not in 1.4.01 or 11.4.0.
    return re.sub(rf"(?<![\d.]){re.escape(old)}(?!\d|\.\d)", new, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archives", default="build/archives", help="where build.py keeps the downloaded sources")
    parser.add_argument("--summary", help="write the changes there, as a Markdown table")
    parser.add_argument("--dry-run", action="store_true", help="print what would change, change nothing")
    arguments = parser.parse_args()

    projects = build.loadProjects()
    lock = json.loads(build.LOCK.read_text())
    archives = pathlib.Path(arguments.archives).resolve()
    changes, problems = [], []
    for name, project in sorted(projects.items()):
        path = build.ROOT / "projects" / name / "config.py"
        text = path.read_text()
        applied = []
        for spec in project.get("updates", []):
            try:
                found = CHECKS[spec["kind"]](project, spec, text)
            except Exception as error:  # one project's source failing leaves the others
                problems.append(f"{name}: {spec['kind']}: {error}")
                continue
            if found:
                old, new, replacements = found
                for kind, before, after in replacements:
                    text = replace(text, kind, before, after)
                applied.append((spec.get("package", name), old, new))
        if not applied:
            continue
        print(f"{name}: " + ", ".join(f"{label} {old} -> {new}" for label, old, new in applied), flush=True)
        if arguments.dry_run:
            changes.append(applied)
            continue
        updated = eval(compile(text, str(path), "eval"), {"__builtins__": {}})
        try:
            for platform in build.PLATFORMS:
                for url in build.field(updated, "downloads", platform):
                    if url not in lock:
                        build.fetch(url, archives)
        except Exception as error:
            problems.append(f"{name}: not every source downloads yet ({error}); left for a later run")
            continue
        path.write_text(text)
        projects[name] = updated
        changes.append(applied)

    if changes and not arguments.dry_run:
        build.updateLock(projects, archives)
    for problem in problems:
        print(f"warning: {problem}", flush=True)
    rows = [row for applied in changes for row in applied]
    if arguments.summary:
        lines = ["| Dependency | From | To |", "|---|---|---|"] + [
            f"| {label} | {old} | {new} |" for label, old, new in rows
        ]
        if problems:
            lines += ["", "Not updated:", ""] + [f"- {problem}" for problem in problems]
        pathlib.Path(arguments.summary).write_text("\n".join(lines) + "\n")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"changed={'true' if rows and not arguments.dry_run else 'false'}\n")
    print(f"{len(rows)} updates" if rows else "up to date")


if __name__ == "__main__":
    main()
