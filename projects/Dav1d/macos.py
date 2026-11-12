#!/usr/bin/env python3
"""Meson installs libdav1d.dylib with its install prefix as install name (/Users/runner/.../lib/libdav1d.7.dylib), which
what links it (FFmpeg) records: makes it @rpath/libdav1d.7.dylib, as build.py's CMake projects have, and signs it again
(arm64 runs signed code only)."""

import argparse
import pathlib
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    for file in sorted((pathlib.Path(arguments.prefix) / "lib").glob("libdav1d*.dylib")):
        if file.is_symlink():
            continue
        name = subprocess.run(["otool", "-D", str(file)], capture_output=True, text=True, check=True).stdout.split()[-1]
        identity = f"@rpath/{pathlib.PurePosixPath(name).name}"
        print(f"  {file.name}: {name} -> {identity}")
        subprocess.run(["install_name_tool", "-id", identity, str(file)], check=True)
        subprocess.run(["codesign", "--force", "--sign", "-", str(file)], check=True)


if __name__ == "__main__":
    main()
