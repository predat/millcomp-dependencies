{
    'version': '26.11.1',
    'url': 'https://openusd.org',
    'downloads': ['https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v26.11.1.tar.gz'],
    'license': ['LICENSE.txt'],
    'dependencies': ['Python', 'TBB', 'MaterialX'],
    # Installed where CMake finds packages and USD finds plugins, instead of USD's own places at the archive's top:
    # pxrConfig.cmake and its targets in lib/cmake/pxr (not ./ and cmake/), its plugins in lib/usd with its libraries'
    # (not plugin/usd, a difference USD's own comment wonders about). CMake computes the targets' prefix from where they
    # are installed; pxrConfig.cmake finds the rest from its own directory.
    'edits': [
        ['pxr/CMakeLists.txt', 'DESTINATION "${CMAKE_INSTALL_PREFIX}"', 'DESTINATION "lib/cmake/pxr"'],
        [
            'pxr/CMakeLists.txt',
            'install(EXPORT pxrTargets DESTINATION "cmake")',
            'install(EXPORT pxrTargets DESTINATION "lib/cmake/pxr")',
        ],
        ['pxr/pxrConfig.cmake.in', '"${PXR_CMAKE_DIR}/cmake/pxrTargets.cmake"', '"${PXR_CMAKE_DIR}/pxrTargets.cmake"'],
        ['pxr/pxrConfig.cmake.in', '"${PXR_CMAKE_DIR}/include"', '"${PXR_CMAKE_DIR}/../../../include"'],
        [
            'cmake/macros/Private.cmake',
            '_get_install_dir("plugin/usd" pluginInstallPrefix)',
            '_get_install_dir("lib/usd" pluginInstallPrefix)',
        ],
        ['cmake/macros/Public.cmake', 'DESTINATION plugin/usd', 'DESTINATION lib/usd'],
    ],
    'cmake': [
        '-DPXR_BUILD_IMAGING=OFF',
        '-DPXR_BUILD_USD_IMAGING=OFF',
        '-DPXR_BUILD_USDVIEW=OFF',
        '-DPXR_BUILD_TESTS=OFF',
        '-DPXR_BUILD_EXAMPLES=OFF',
        '-DPXR_BUILD_TUTORIALS=OFF',
        '-DPXR_BUILD_HTML_DOCUMENTATION=OFF',
        '-DPXR_ENABLE_MATERIALX_SUPPORT=ON',  # usdMtlx: USD reads .mtlx files
        '-DPXR_ENABLE_OPENVDB_SUPPORT=OFF',
        '-DPXR_ENABLE_PTEX_SUPPORT=OFF',
        '-DPXR_ENABLE_OSL_SUPPORT=OFF',
        '-DPXR_ENABLE_HDF5_SUPPORT=OFF',
        '-DPXR_ENABLE_METAL_SUPPORT=OFF',
        '-DPXR_ENABLE_PYTHON_SUPPORT=ON',
        '-DPXR_USE_DEBUG_PYTHON=OFF',
        '-DPXR_BUILD_MONOLITHIC=OFF',
        # The same on every platform, where millComp looks: lib/python/pxr. USD's default is Python's
        # site-packages, which differs between platforms.
        '-DPXR_PYTHON_INSTALL_DIR=lib/python',
    ],
    # python-build-standalone's python3 links Python statically, on Linux as on macOS, though its sysconfig names
    # libpython3.X.so / .dylib, so USD does not find out by itself: its libraries and modules linking libpython would
    # load a second Python in the process (two interpreters' state; on macOS, a crash), and find it only through a
    # RUNPATH to the build machine's python/lib. They resolve Python's symbols in the process instead: the interpreter's,
    # or an executable's, since executables still link libpython (pxrTargets gives it to executables only). Windows'
    # python.exe loads python3X.dll, which the modules then share: nothing to do there.
    'cmake:linux': ['-DPXR_PY_UNDEFINED_DYNAMIC_LOOKUP=ON'],
    'cmake:macos': ['-DPXR_PY_UNDEFINED_DYNAMIC_LOOKUP=ON'],
    # New versions, within the series (updates.py). millComp: usd-26.11
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/PixarAnimationStudios/OpenUSD',
            'tag': r'v(\d+)\.(\d+)(?:\.(\d+))?',
            'series': '26.11',
        }
    ],
}
