# millComp dependencies

This repository builds the third-party libraries millComp depends on and packs them into one archive per platform.
The approach is the same as [GafferHQ/dependencies](https://github.com/GafferHQ/dependencies):

| Platform | Archive | Built on |
|---|---|---|
| Linux x86_64 | `millcompDependencies-<version>-linux.tar.gz` | Ubuntu 24.04, gcc 14 |
| Windows x64 | `millcompDependencies-<version>-windows.zip` | Windows Server 2025, MSVC |
| macOS arm64 | `millcompDependencies-<version>-macos.tar.gz` | macOS 15, deployment target 14.4 |

The archives are published as [releases](https://github.com/predat/millcomp-dependencies/releases), each with its
`.sha256`.

## Contents

The archive contains the following libraries:

- **USD**, with usdMtlx and Python bindings
- **MaterialX**
- **OpenImageIO**, **OpenColorIO**, **OpenEXR** and **Imath**
- **oneTBB**
- **Qt 6**, including its private modules (rhi, shader tools)
- **Slang**
- **Vulkan**: headers and loader, plus **MoltenVK** on macOS
- **Python**, from python-build-standalone, with numpy
- **nanobind** and **robin-map**
- **fmt** and **GoogleTest**
- **zlib**, **libpng**, **libjpeg-turbo**, **libtiff** and **FreeType**

Each archive's `manifest.json` gives the exact version of every project, its URL and the sha256 of its sources. The
licences are in `licenses/<project>/`. Each project's recipe is in `projects/<Name>/config.py`.

Most projects are compiled from source. A few are taken prebuilt from their official releases:
- Qt, from Qt's online repository
- Slang
- MoltenVK
- Python, from python-build-standalone

## Using an archive

Unpack the archive anywhere: it is relocatable, and the CMake and pkg-config files use relative paths. Then build and
run millComp against it:

```sh
DEPS=/path/to/millcompDependencies-<version>-<platform>

cmake -S . -B build -G Ninja \
  -DCMAKE_PREFIX_PATH="$DEPS;$DEPS/qt" \
  -DPython_ROOT_DIR="$DEPS/python" -DPython_FIND_STRATEGY=LOCATION

# Running, Linux:
export LD_LIBRARY_PATH="$DEPS/lib:$DEPS/qt/lib:$DEPS/python/lib"
export PYTHONPATH="$DEPS/lib/python"          # pxr
# Windows: put %DEPS%\bin, %DEPS%\lib, %DEPS%\qt\bin and %DEPS%\python on PATH.
```

A few points need care in millComp itself:

- **MaterialX** searches for its data libraries next to the executable. Pass it the archive's path:
  `MaterialX::loadLibraries({"libraries"}, MaterialX::FileSearchPath(deps), …)`.
- **Vulkan on macOS**: the loader only looks for drivers in system locations. Point it at the archive's MoltenVK with
  `VK_DRIVER_FILES=$DEPS/share/vulkan/icd.d/MoltenVK_icd.json`, and enable portability enumeration on the instance.
- **TBB with Qt**: compile with `QT_NO_EMIT`, because TBB uses `emit` as an identifier.
- **On Linux**, the archive only expects the C and C++ runtimes from the system, plus X11 and the graphics libraries
  that any Qt application needs.

`smoke/` shows all of this in practice: it is the test the CI runs on every archive.

## Building

The requirements are Python 3.10 or later, CMake, Ninja and a C++ compiler:
- **Linux**: gcc 14, plus the headers `libgl-dev`, `libegl-dev`, `libx11-dev` and `libxkbcommon-dev`, and `nasm`.
- **Windows**: Visual Studio with the C++ tools, run from a developer command prompt.
- **macOS**: Xcode.

The CI's exact setup is in `.github/workflows/main.yml`.

```sh
python build.py --package          # everything, then build/package/millcompDependencies-*
python build.py --projects USD     # USD and what it depends on, into build/install
python smoke/smoke.py build/package/millcompDependencies-<version>-<platform>.tar.gz
```

`build.py` only uses the standard library. Builds are incremental: a project is rebuilt only when its recipe, its
sources or one of its dependencies changes, so an interrupted build resumes where it stopped. On Windows, keep the
work directory short to avoid the path-length limit, for example `--work-dir D:/w`.

With `--package`, the archive is audited before it is packed. On Linux and macOS, a library that depends on something
outside the archive and the system (Homebrew, the runner's packages) makes the build fail.

## Recipes: `projects/<Name>/config.py`

Each recipe is a single Python dictionary. It is evaluated without builtins, so it can contain literals and comments,
nothing else:

```python
{
    'version': '3.2.3',
    'url': 'https://github.com/AcademySoftwareFoundation/Imath',
    'downloads': ['https://github.com/AcademySoftwareFoundation/Imath/archive/refs/tags/v3.2.3.tar.gz'],
    'license': ['LICENSE.md'],
    'cmake': ['-DBUILD_TESTING=OFF', '-DPYTHON=OFF'],
    'updates': [{'kind': 'git-tags', 'repo': 'https://github.com/AcademySoftwareFoundation/Imath',
                 'tag': r'v(\d+)\.(\d+)\.(\d+)', 'series': '3'}],
}
```

| Key | Meaning |
|---|---|
| `version` | the version, written to the manifest |
| `url` | the project's home page |
| `downloads` | the source archives, checked against `lock.json` |
| `extractTo` | where to extract them (default: `{source}`) |
| `license` | patterns of licence files, relative to the extracted sources |
| `dependencies` | projects to build first |
| `platforms` | the platforms the project is built on (default: all) |
| `cmake` | CMake options. With this key the project is configured, built and installed with CMake (Ninja, Release, shared libraries, rpaths and the archive's Python are added) |
| `cmakeSource` | the subdirectory holding `CMakeLists.txt` |
| `commands` | commands run after CMake, or instead of it |
| `moves` | `[from, to]` pairs, moved after the commands |
| `environment` | extra environment variables |
| `updates` | where `updates.py` looks for new versions, and which series are allowed |

Any key can take a platform suffix that overrides it on that platform: `cmake:macos`, `downloads:windows`,
`commands:linux`… Strings can use these variables:
- `{buildDir}`: the install prefix
- `{source}`: the extracted sources
- `{work}`: the work directory
- `{projectDir}`: the recipe's directory, for helper scripts
- `{python}`: the archive's Python. Projects that use it must depend on `Python`.
- `{jobs}`: the number of parallel jobs

After adding or changing a download, record its hash:

```sh
python build.py --update-lock
```

## Updates and releases

Every night at 03:00 UTC, the `nightly` workflow runs `updates.py`. The script checks each project's upstream for new
versions within the series its `updates` allows. The sources are git tags, python-build-standalone, Qt's repository
and PyPI. For PyPI, it only considers versions the archive's Python can install. When it finds updates, it:

1. Updates the recipes and `lock.json` on the `updates/nightly` branch.
2. Opens or refreshes the **Nightly dependency updates** pull request.
3. Builds and tests the branch on all three platforms.

To try it locally: `python updates.py --dry-run`.

To publish a release:

1. Merge the pull request once it is green.
2. Bump `VERSION`.
3. Push the matching tag:

   ```sh
   git tag -a v1.0.3 -m "millComp dependencies 1.0.3" && git push origin v1.0.3
   ```

   The tag's build publishes the three archives as a release.

The Python code is formatted with `ruff format .` (see `ruff.toml`).
