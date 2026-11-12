#!/usr/bin/env python3
"""What nv-codec-headers' `make install` does, without make (Windows): the headers, and ffnvcodec.pc, which FFmpeg's
configure looks for."""

import argparse
import pathlib
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    source, prefix = pathlib.Path(arguments.source), pathlib.Path(arguments.prefix)
    shutil.copytree(source / "include/ffnvcodec", prefix / "include/ffnvcodec", dirs_exist_ok=True)
    pc = (source / "ffnvcodec.pc.in").read_text().replace("@@PREFIX@@", prefix.as_posix())
    (prefix / "lib/pkgconfig").mkdir(parents=True, exist_ok=True)
    (prefix / "lib/pkgconfig/ffnvcodec.pc").write_text(pc)


if __name__ == "__main__":
    main()
