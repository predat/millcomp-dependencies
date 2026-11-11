#!/usr/bin/env python3
"""Fetches the Qt modules millComp uses from Qt's official repository, checks them and unpacks them into --out.

aqtinstall 3.3.0 does not find Qt 6.12's Windows packages (their directory is qt6_6120/qt6_6120_msvc2022_64, not
qt6_6120/qt6_6120), and installs QtQuick and the rest that millComp has no use of. Needs py7zr on the PYTHONPATH.
"""

import argparse
import hashlib
import pathlib
import shutil
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ElementTree

REPOSITORY = "https://download.qt.io/online/qtsdkrepository"
# millComp: Widgets, GuiPrivate, Test (qtbase), Svg, ShaderTools. ICU: what qtbase links on Linux.
WANTED = ("qtbase-", "qtsvg-", "qtshadertools-", "icu-")


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "millcomp-dependencies-build"})
    with urllib.request.urlopen(request, timeout=600) as response:
        return response.read()


def archivesOf(platform, version):
    """(url, archive name) of the wanted archives."""
    compact = version.replace(".", "")
    if platform == "windows":
        arch, base = "win64_msvc2022_64", f"{REPOSITORY}/windows_x86/desktop/qt6_{compact}/qt6_{compact}_msvc2022_64"
    else:
        arch, base = "linux_gcc_64", f"{REPOSITORY}/linux_x64/desktop/qt6_{compact}/qt6_{compact}"
    packages = {f"qt.qt6.{compact}.{arch}", f"qt.qt6.{compact}.addons.qtshadertools.{arch}"}
    found = []
    for package in ElementTree.fromstring(get(f"{base}/Updates.xml")).findall("PackageUpdate"):
        name = package.findtext("Name")
        if name not in packages:
            continue
        packages.remove(name)
        for archive in (package.findtext("DownloadableArchives") or "").split(","):
            archive = archive.strip()
            if archive.startswith(WANTED):
                found.append((f"{base}/{name}/{package.findtext('Version')}{archive}", archive))
    if packages:
        sys.exit(f"not in Qt's repository: {sorted(packages)}")
    for module in WANTED[:3]:
        if not any(archive.startswith(module) for _, archive in found):
            sys.exit(f"no {module} archive")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["linux", "windows"], required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()

    import py7zr

    out = pathlib.Path(arguments.out)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as temporary:
        for url, archive in archivesOf(arguments.platform, arguments.version):
            print(f"  {archive}", flush=True)
            file = pathlib.Path(temporary) / archive
            file.write_bytes(get(url))
            wanted = get(url + ".sha256").split()[0].decode()
            if hashlib.sha256(file.read_bytes()).hexdigest() != wanted:
                sys.exit(f"{url}: does not match its .sha256")
            # Qt's archives hold bin/, lib/, include/...; ICU's holds its libraries alone, which go next to Qt's.
            with py7zr.SevenZipFile(file) as data:
                data.extractall(out / "lib" if archive.startswith("icu-") else out)
            file.unlink()


if __name__ == "__main__":
    main()
