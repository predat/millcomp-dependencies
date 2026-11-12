#!/usr/bin/env python3
"""Configures, builds and installs FFmpeg, for reading video (OpenImageIO's ffmpeg plugin) and for writing it (millComp,
through FFmpeg's API).

LGPL: nothing GPL or nonfree, so no x264 or x265. What it decodes and encodes:
  - its own codecs: ProRes (prores_ks), DNxHD/DNxHR (dnxhd), H.264, HEVC and VP9 decoding, MJPEG, PNG, FFV1…;
  - AV1: dav1d decodes, SVT-AV1 encodes;
  - H.264 and HEVC encoding on the GPU: NVENC (Linux, Windows), VideoToolbox (macOS, ProRes too), Media Foundation
    (Windows). NVDEC, VideoToolbox and D3D11VA decode on the GPU.
Only what is asked is enabled (--disable-autodetect): nothing found on the build machine (xcb, libva, SDL…), which a user
of the archive does not have. On Windows, configure and make run in MSYS2's shell, with MSVC.
"""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys

PLATFORM = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
MSYS2 = pathlib.Path(os.environ.get("MSYS2_ROOT", "C:/msys64"))

OPTIONS = [
    "--enable-shared",
    "--disable-static",
    "--disable-autodetect",
    "--disable-doc",
    "--disable-debug",
    "--disable-avdevice",  # cameras, screens, sound cards: not millComp's
    "--disable-ffplay",  # needs SDL
    "--enable-libdav1d",
    "--enable-libsvtav1",
]
PLATFORM_OPTIONS = {
    "linux": [
        "--enable-pthreads",  # threads are autodetected too
        "--enable-zlib",
        "--enable-ffnvcodec",
        "--enable-nvenc",
        "--enable-nvdec",
        "--enable-cuvid",
        # Each library finds the others next to it, ffmpeg and ffprobe in ../lib. configure's tests run in a shell, which
        # would expand $ORIGIN: the placeholder becomes \$$$$ORIGIN in config.mak (expanded twice by make, once by sh).
        "--extra-ldflags=-Wl,-rpath,@ORIGIN@/../lib",
    ],
    "macos": [
        "--enable-pthreads",
        "--enable-zlib",
        "--enable-videotoolbox",
        "--enable-audiotoolbox",
        "--install-name-dir=@rpath",
        "--extra-ldflags=-Wl,-rpath,@loader_path/../lib",
    ],
    "windows": [
        "--toolchain=msvc",
        "--enable-w32threads",
        "--enable-zlib",
        "--enable-ffnvcodec",
        "--enable-nvenc",
        "--enable-nvdec",
        "--enable-cuvid",
        "--enable-mediafoundation",
        "--enable-d3d11va",
        "--enable-dxva2",
    ],
}


def msys(path):
    """D:/a/b as MSYS2's shell sees it: /d/a/b."""
    path = pathlib.Path(path).as_posix()
    return f"/{path[0].lower()}{path[2:]}" if len(path) > 1 and path[1] == ":" else path


def run(arguments, cwd, environment):
    print("  $ " + " ".join(arguments), flush=True)
    if PLATFORM == "windows":
        script = " ".join("'" + argument.replace("'", "'\\''") + "'" for argument in arguments)
        arguments = [str(MSYS2 / "usr/bin/bash.exe"), "-c", script]
    subprocess.run(arguments, cwd=cwd, env=environment, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--jobs", default=str(os.cpu_count()))
    arguments = parser.parse_args()

    prefix = pathlib.Path(arguments.prefix)
    build = pathlib.Path(arguments.build)
    build.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    configure = f"{pathlib.Path(arguments.source).as_posix()}/configure"
    options = [f"--prefix={prefix.as_posix()}", *OPTIONS, *PLATFORM_OPTIONS[PLATFORM]]
    # dav1d, SVT-AV1 and ffnvcodec are found with pkg-config: the archive's only.
    environment["PKG_CONFIG_LIBDIR"] = (prefix / "lib/pkgconfig").as_posix()
    if PLATFORM == "windows":
        # MSVC's link.exe before MSYS2's (coreutils' link), MSYS2's tools before Windows' (find, sort).
        cl = shutil.which("cl.exe", path=environment["PATH"])
        if not cl:
            sys.exit("cl.exe is not on PATH: run in an MSVC developer environment")
        environment["PATH"] = os.pathsep.join(
            [str(pathlib.Path(cl).parent), str(MSYS2 / "usr/bin"), environment["PATH"]]
        )
        environment["PKG_CONFIG_LIBDIR"] = msys(prefix / "lib/pkgconfig")
        configure = msys(configure)
        options += [
            f"--extra-cflags=-I{prefix.as_posix()}/include",
            f"--extra-ldflags=-LIBPATH:{prefix.as_posix()}/lib",
        ]
        # configure looks for zlib as -lz, z.lib; zlib names its import library libz.lib with MSVC (the DLL keeps its
        # name, libz.dll, whatever the import library's): a copy in the build directory.
        zlib = build / "zlib"
        zlib.mkdir(exist_ok=True)
        shutil.copy(prefix / "lib/libz.lib", zlib / "z.lib")
        options += [f"--extra-ldflags=-LIBPATH:{zlib.as_posix()}"]
    else:
        options += [f"--extra-cflags=-I{prefix.as_posix()}/include", f"--extra-ldflags=-L{prefix.as_posix()}/lib"]
        # configure runs cc, whatever CC says: the compiler the other projects use (gcc 14 on the CI's Linux).
        options += [f"--cc={environment['CC']}"] if environment.get("CC") else []
        options += [f"--cxx={environment['CXX']}"] if environment.get("CXX") else []

    run([configure, *options], build, environment)
    if PLATFORM == "linux":
        config = build / "ffbuild/config.mak"
        config.write_text(config.read_text().replace("@ORIGIN@", r"\$$$$ORIGIN"))
    run(["make", f"-j{arguments.jobs}"], build, environment)
    run(["make", "install"], build, environment)

    if PLATFORM == "linux":  # The rpath went through make and sh: check it did unharmed.
        output = subprocess.run(["readelf", "-d", str(prefix / "lib/libavcodec.so")], capture_output=True, text=True)
        if "[$ORIGIN/../lib]" not in output.stdout:
            sys.exit(f"libavcodec.so's rpath is not $ORIGIN/../lib:\n{output.stdout}")


if __name__ == "__main__":
    main()
