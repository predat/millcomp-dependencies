#!/usr/bin/env python3
"""Installs Slang's release: its directories (bin, include, lib, share) into the prefix, its licences and third-party
notices into licenses/Slang. Not extracted into the prefix itself: its LICENSES would be the prefix's licenses/ on
macOS's and Windows' case-insensitive file systems."""

import argparse
import pathlib
import shutil

LICENCES = ("LICENSE", "LICENSES", "third-party-notices")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    source, prefix = pathlib.Path(arguments.source), pathlib.Path(arguments.prefix)
    for entry in sorted(source.iterdir()):
        if entry.name in LICENCES:
            target = prefix / "licenses/Slang" / entry.name
        elif entry.is_dir():
            target = prefix / entry.name
        else:
            continue  # README.md
        if entry.is_dir():
            shutil.copytree(entry, target, symlinks=True, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry, target)


if __name__ == "__main__":
    main()
