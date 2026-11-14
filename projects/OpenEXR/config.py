{
    'version': '3.5.4',
    'url': 'https://openexr.com',
    'downloads': ['https://github.com/AcademySoftwareFoundation/openexr/archive/refs/tags/v3.5.4.tar.gz'],
    'license': ['LICENSE.md'],
    'dependencies': ['Imath', 'ZLib'],
    'cmake': [
        '-DBUILD_TESTING=OFF',
        '-DOPENEXR_BUILD_TOOLS=OFF',
        '-DOPENEXR_BUILD_EXAMPLES=OFF',
        '-DOPENEXR_INSTALL_TOOLS=OFF',
        '-DOPENEXR_INSTALL_EXAMPLES=OFF',
        '-DOPENEXR_BUILD_PYTHON=OFF',
        # Their vendored copies, not the build machine's.
        '-DOPENEXR_FORCE_INTERNAL_ZSTD=ON',
        '-DOPENEXR_FORCE_INTERNAL_DEFLATE=ON',
    ],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/AcademySoftwareFoundation/openexr',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '3',
        }
    ],
}
