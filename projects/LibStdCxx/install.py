#!/usr/bin/env python3
"""Installs libstdc++.so.6 from a conda package (a zip holding pkg-*.tar.zst, which Python 3.12's tarfile cannot read:
tar --zstd unpacks it) in lib/, and its licences in licenses/LibStdCxx: the package's runtime library exception, and
GPL 3 with it from the build machine's GCC (Rocky's libgcc). Not libstdc++.so: a link against the archive must keep
taking the compiler's own libstdc++, never this one."""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    source = pathlib.Path(arguments.source)
    prefix = pathlib.Path(arguments.prefix)
    packages = list(source.glob("pkg-*.tar.zst"))
    if len(packages) != 1:
        sys.exit(f"{source}: {len(packages)} pkg-*.tar.zst, not one")
    unpacked = source / "pkg"
    unpacked.mkdir()
    subprocess.run(["tar", "--zstd", "-xf", str(packages[0]), "-C", str(unpacked)], check=True)

    libraries = [path for path in (unpacked / "lib").glob("libstdc++.so.6.*") if not path.is_symlink()]
    if len(libraries) != 1:
        sys.exit(f"{unpacked / 'lib'}: {len(libraries)} libstdc++.so.6.*, not one")
    library = libraries[0]
    (prefix / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copy2(library, prefix / "lib" / library.name)
    link = prefix / "lib/libstdc++.so.6"
    if link.is_symlink() or link.exists():
        link.unlink()
    os.symlink(library.name, link)

    licenses = prefix / "licenses/LibStdCxx"
    licenses.mkdir(parents=True, exist_ok=True)
    shutil.copy2(unpacked / "share/licenses/libstdc++/RUNTIME.LIBRARY.EXCEPTION", licenses)
    for name in ("COPYING3", "COPYING.RUNTIME"):
        gcc = pathlib.Path("/usr/share/licenses/libgcc") / name
        if not gcc.exists():
            sys.exit(f"{gcc}: missing (Rocky's libgcc ships it)")
        shutil.copy2(gcc, licenses)


if __name__ == "__main__":
    main()
