{'version': '1.6.59',
 'url': 'http://www.libpng.org',
 'downloads': ['https://github.com/pnggroup/libpng/archive/refs/tags/v1.6.59.tar.gz'],
 'license': ['LICENSE'],
 'dependencies': ['ZLib'],
 'cmake': ['-DPNG_TESTS=OFF', '-DPNG_STATIC=OFF', '-DPNG_TOOLS=OFF',
           # On by default on macOS since 1.6.5x: a png.framework next to the dylib. No effect elsewhere.
           '-DPNG_FRAMEWORK=OFF']}
