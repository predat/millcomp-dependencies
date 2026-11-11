#!/usr/bin/env python3
"""Slang's macOS release links libraries of Homebrew's (libslang-llvm.dylib: /opt/homebrew/opt/zstd/lib/libzstd.1.dylib),
which a user of the archive does not have. Points them at the archive's (@rpath, which Slang's libraries set to
@loader_path/../lib), and signs again what it changed: arm64 runs signed code only."""

import argparse
import pathlib
import subprocess
import sys

HOMEBREW = ("/opt/homebrew/", "/usr/local/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    lib = pathlib.Path(arguments.prefix) / "lib"
    for file in sorted(lib.glob("libslang*.dylib")) + sorted(lib.glob("libgfx*.dylib")):
        if file.is_symlink():
            continue
        output = subprocess.run(["otool", "-L", str(file)], capture_output=True, text=True, check=True).stdout
        needed = [line.strip().split(" (compatibility")[0] for line in output.splitlines()[1:]]
        changes = [name for name in needed if name.startswith(HOMEBREW)]
        for name in changes:
            library = pathlib.PurePosixPath(name).name
            if not (lib / library).exists():
                sys.exit(f"{file.name} needs {name}, and lib/{library} is not there")
            print(f"  {file.name}: {name} -> @rpath/{library}")
            subprocess.run(["install_name_tool", "-change", name, f"@rpath/{library}", str(file)], check=True)
        if changes:
            subprocess.run(["codesign", "--force", "--sign", "-", str(file)], check=True)


if __name__ == "__main__":
    main()
