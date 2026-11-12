{
    'version': '2023.2.0',
    'url': 'https://github.com/uxlfoundation/oneTBB',
    'downloads': ['https://github.com/uxlfoundation/oneTBB/archive/refs/tags/v2023.2.0.tar.gz'],
    'license': ['LICENSE.txt'],
    'cmake': ['-DTBB_TEST=OFF', '-DTBB_STRICT=OFF'],
    # New versions, within the series (updates.py). what OpenImageIO and USD build with
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/uxlfoundation/oneTBB',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '2023',
        }
    ],
}
