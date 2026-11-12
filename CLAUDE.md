# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This repository builds millComp's third-party dependencies (USD, OpenImageIO, OpenColorIO, Qt, Slang, Python, Vulkan,
MaterialX, FFmpeg, …) from source. It packs them into one relocatable archive per platform: Linux x86_64, Windows x64 (MSVC)
and macOS arm64. The approach is the same as GafferHQ/dependencies. The CI publishes the archives as GitHub releases.

## Commands

```sh
python build.py                                # build every project into build/install (incremental)
python build.py --projects OpenImageIO         # one project and what it depends on
python build.py --package                      # build, audit, strip, relocate, pack into build/package/
python build.py --update-lock                  # download sources missing from lock.json and record their sha256
python smoke/smoke.py build/package/millcompDependencies-<version>-<platform>.tar.xz   # the test
python updates.py --dry-run                    # which upstream versions are newer, within each project's series
ruff format .                                  # formatting (ruff.toml: 120 columns, quotes preserved)
```

On Windows, run from an MSVC developer environment and keep `--work-dir` short (the CI uses `D:/w`), because of
path-length limits. There are no unit tests. `smoke/smoke.py` is the test: it unpacks an archive into a temporary
directory, builds `smoke/` (CMake, C++ plus a nanobind module) against it, and runs it along with Python checks. This
proves the archive is complete and relocatable.

## Architecture

- **`build.py`** is the driver. It must use the **standard library only**, because it runs before anything is installed.
- **`projects/<Name>/config.py`** files are each a single dict literal. `build.py` evaluates them with `eval` and no
  builtins, so they can't contain imports or calls, only literals and comments. Keys are:
  - `version`, `downloads`, `extractTo`, `license`, `dependencies`, `platforms`
  - `edits` (`[file, old, new]` source changes, `old` found exactly once), `cmake`, `cmakeSource`, `commands`, `moves`,
    `environment`
  - `updates`

  Any key can take a platform suffix: `cmake:macos` or `downloads:windows`. `field()` returns the suffixed value when
  it exists, and the plain one otherwise. Strings are `str.format` templates with these variables: `{buildDir}`,
  `{work}`, `{source}`, `{python}` (the archive's own Python, so projects running it must depend on `Python`),
  `{projectDir}` and `{jobs}`. When a project has `cmake` keys, `build.py` adds common flags: Ninja, Release, shared
  libraries, rpaths, the Python location, and on macOS the deployment target 14.4 and Homebrew prefixes ignored.
  Helper scripts sit next to the config (`Qt/fetch.py`, `Slang/macos.py`, `MoltenVK/install.py`,
  `MaterialX/noX11.cmake`, `FFmpeg/ffmpeg.py`). FFmpeg is configured by `ffmpeg.py` (LGPL only, `--disable-autodetect`;
  on Windows through MSYS2's bash with MSVC); Dav1d uses Meson through `commands`.
- **`lock.json`** pins the sha256 of every download. A new or changed URL needs `--update-lock` (or `updates.py`).
- **Incremental builds.** Each project has a digest, written to `build/install/.stamps/<name>`. It combines the
  evaluated config (excluding `updates` and comments, so formatting and comments don't trigger a rebuild), the raw
  hash of the other files in its directory, its locked sources, its dependencies' digests and `DRIVER_REVISION`.
  Bump `DRIVER_REVISION` when a change in `build.py` affects every project. Each project's installed files are
  recorded in `.stamps/<name>.files` and removed before it is rebuilt, or when the project no longer exists.
- **`--package`** runs these steps in order:
  1. Write the manifest.
  2. Audit: `auditLinux` uses `readelf` and only allows `SYSTEM_LIBRARIES`. `auditMacos` uses `otool` and allows only
     `/usr/lib`, `/System/Library` and `@rpath`.
  3. `strip()` (Linux, macOS) removes the debug symbols from what the projects built, in place in `build/install`
     (`strip --strip-unneeded`; on macOS `strip -x` and an ad hoc signature again). `qt/` and `python/` are left as
     they are: they come stripped (Python is python-build-standalone's `install_only_stripped`).
  4. `relocate()` rewrites absolute prefixes in `.cmake` and `.pc` files to `${CMAKE_CURRENT_LIST_DIR}` and
     `${pcfiledir}`.
  5. Pack: `.tar.xz` (through the `xz` program when there is one, multithreaded), `.zip` on Windows.

  A library that leaks from the runner (Homebrew, system zstd or expat, …) fails the audit. Fix the project so it uses
  bundled or internal copies rather than loosening the audit.
- **`updates.py`** checks upstream for new versions: git tags, python-build-standalone releases, Qt's online
  repository, and PyPI. PyPI candidates are filtered by `Requires-Python` against the archive's Python. It updates
  `config.py` (the version wherever it appears) and `lock.json`. Each project's `updates` list sets its source and an
  allowed `series`. It finds PyPI pins in the text as `'numpy==X'`, which is why `ruff.toml` keeps quotes as they are.

## CI (`.github/workflows/`)

- **`main.yml`** runs on pushes to `main` and on `v*` tags. It is a matrix over Linux (a `rockylinux/rockylinux:9`
  container with gcc-toolset-14, on ubuntu-24.04), windows-2025 and macos-15. Each job restores `build/install` from the
  cache (key prefix `deps-<matrix.cache>-<platform>-`, bump the platform's `cache` to start
  fresh), builds with `--package`, runs the smoke test and uploads the archive. On a `v*` tag, a release job publishes
  the three archives. `VERSION` holds the release number, and the tag must match it.
- **`nightly.yml`** runs daily at 03:00 UTC. It runs `updates.py` and force-pushes the changes to `updates/nightly`. It
  then opens or refreshes the "Nightly dependency updates" pull request and dispatches `main.yml` on that branch. A
  push made with `GITHUB_TOKEN` doesn't trigger workflows, so the dispatch is required.

## Conventions

- Python code uses camelCase names. Comments explain why something is done, next to the setting they justify (see the
  `config.py` files).
- The `updates` series follow millComp's requirements: `python-3.13`, `numpy-2`, `usd-26.11`, `qt-6.12`, `oiio-3`,
  `ocio-2`, … Millcomp also builds at the studio in a rez context (Rocky 9, gcc 14), whose versions can differ from
  the archive's. Change a series only when millComp's requirements change.
