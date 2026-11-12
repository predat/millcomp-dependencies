{
    'version': '2.15.0',
    'url': 'https://freetype.org',
    'downloads': ['https://github.com/freetype/freetype/archive/refs/tags/VER-2-15-0.tar.gz'],
    'license': ['LICENSE.TXT'],
    'dependencies': ['ZLib', 'LibPNG'],
    'cmake': [
        '-DFT_DISABLE_BZIP2=ON',
        '-DFT_DISABLE_HARFBUZZ=ON',
        '-DFT_DISABLE_BROTLI=ON',
        '-DFT_REQUIRE_ZLIB=ON',
        '-DFT_REQUIRE_PNG=ON',
    ],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/freetype/freetype',
            'tag': r'VER-(\d+)-(\d+)-(\d+)',
            'series': '2',
        }
    ],
}
