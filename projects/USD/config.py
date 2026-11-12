{'version': '26.11.1',
 'url': 'https://openusd.org',
 'downloads': ['https://github.com/PixarAnimationStudios/OpenUSD/archive/refs/tags/v26.11.1.tar.gz'],
 'license': ['LICENSE.txt'],
 'dependencies': ['Python', 'TBB', 'MaterialX'],
 'cmake': ['-DPXR_BUILD_IMAGING=OFF',
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
           '-DPXR_INSTALL_LOCATION=../plugin/usd'],
 # python-build-standalone's macOS python3 links Python statically, though its sysconfig names libpython3.X.dylib, so
 # USD does not find out by itself: its modules linking libpython would load a second Python in the process, which
 # crashes. They resolve Python's symbols in the process instead; executables still link libpython.
 'cmake:macos': ['-DPXR_PY_UNDEFINED_DYNAMIC_LOOKUP=ON'],
 # New versions, within the series (updates.py). millComp: usd-26.11
 'updates': [{'kind': 'git-tags', 'repo': 'https://github.com/PixarAnimationStudios/OpenUSD', 'tag': r'v(\d+)\.(\d+)(?:\.(\d+))?', 'series': '26.11'}]}
