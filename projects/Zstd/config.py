{'version': '1.5.7',
 'url': 'https://facebook.github.io/zstd',
 # On macOS only, for Slang's libslang-llvm.dylib (see Slang/macos.py). OpenEXR uses its own copy.
 'platforms': ['macos'],
 'downloads': ['https://github.com/facebook/zstd/releases/download/v1.5.7/zstd-1.5.7.tar.gz'],
 'license': ['LICENSE'],
 'cmakeSource': 'build/cmake',
 'cmake': ['-DZSTD_BUILD_PROGRAMS=OFF',
           '-DZSTD_BUILD_STATIC=OFF',
           '-DZSTD_BUILD_SHARED=ON',
           '-DZSTD_BUILD_TESTS=OFF',
           '-DZSTD_LEGACY_SUPPORT=OFF']}
