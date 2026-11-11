#!/usr/bin/env python3
"""Unpacks an archive somewhere else, builds smoke/ against it and runs it: the archive is complete and relocatable."""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=pathlib.Path)
    parser.add_argument("--jobs", type=int, default=os.cpu_count())
    arguments = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="mcdeps-") as temporary:
        temporary = pathlib.Path(temporary)
        if arguments.archive.name.endswith(".zip"):
            with zipfile.ZipFile(arguments.archive) as data:
                data.extractall(temporary)
        else:
            with tarfile.open(arguments.archive) as data:
                data.extractall(temporary, filter="tar")
        deps = next(path for path in temporary.iterdir() if path.is_dir())
        windows = sys.platform == "win32"
        python = deps / "python" / ("python.exe" if windows else "bin/python3")

        environment = dict(os.environ)
        environment.pop("CMAKE_PREFIX_PATH", None)
        environment.pop("PYTHONPATH", None)
        pathKeys = [deps / "bin", deps / "lib", deps / "qt/bin", deps / "python"]
        environment["PATH"] = os.pathsep.join([str(path) for path in pathKeys] + [environment["PATH"]])
        if not windows:
            environment["LD_LIBRARY_PATH"] = os.pathsep.join(str(path) for path in [deps / "lib", deps / "qt/lib", deps / "python/lib"])
        build = temporary / "build"
        subprocess.run(
            [
                "cmake", "-S", str(HERE), "-B", str(build), "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release", "-Wno-dev",
                f"-DCMAKE_PREFIX_PATH={deps.as_posix()};{(deps / 'qt').as_posix()}",
                f"-DPython_ROOT_DIR={(deps / 'python').as_posix()}", "-DPython_FIND_STRATEGY=LOCATION",
                "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF",
            ],
            check=True, env=environment,
        )  # fmt: skip
        subprocess.run(["cmake", "--build", str(build), "-j", str(arguments.jobs)], check=True, env=environment)
        subprocess.run([str(build / ("smoke.exe" if windows else "smoke")), str(temporary)], check=True, env=environment)

        environment["PYTHONPATH"] = os.pathsep.join([str(build), str(deps / "lib/python")])
        check = "import _smoke, numpy; from pxr import Usd, Sdf; assert _smoke.answer() == 42 and Usd.Stage.CreateInMemory(); print('Python:', numpy.__version__)"
        subprocess.run([str(python), "-c", check], check=True, env=environment)
        # Open files on Windows would fail the cleanup.
        shutil.rmtree(build, ignore_errors=True)


if __name__ == "__main__":
    main()
