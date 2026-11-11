#!/usr/bin/env python3
"""Installs MoltenVK's dylib in lib/ and its ICD manifest in share/vulkan/icd.d/, pointing at the dylib relative to
itself, so that the archive works wherever it is unpacked. The loader does not look there on its own: point
VK_DRIVER_FILES at the manifest."""

import argparse
import json
import pathlib
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--prefix", required=True)
    arguments = parser.parse_args()

    built = pathlib.Path(arguments.source) / "MoltenVK/dynamic/dylib/macOS"
    prefix = pathlib.Path(arguments.prefix)
    (prefix / "lib").mkdir(parents=True, exist_ok=True)
    shutil.copy2(built / "libMoltenVK.dylib", prefix / "lib/libMoltenVK.dylib")

    manifest = json.loads((built / "MoltenVK_icd.json").read_text())
    manifest["ICD"]["library_path"] = "../../../lib/libMoltenVK.dylib"  # relative to the manifest
    icd = prefix / "share/vulkan/icd.d"
    icd.mkdir(parents=True, exist_ok=True)
    (icd / "MoltenVK_icd.json").write_text(json.dumps(manifest, indent=4) + "\n")


if __name__ == "__main__":
    main()
