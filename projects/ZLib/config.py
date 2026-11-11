{'version': '1.3.1',
 'url': 'https://zlib.net',
 'downloads': ['https://github.com/madler/zlib/archive/refs/tags/v1.3.1.tar.gz'],
 'license': ['LICENSE'],
 'cmake': ['-DZLIB_BUILD_EXAMPLES=OFF'],
 # New versions, within the series (updates.py)
 'updates': [{'kind': 'git-tags', 'repo': 'https://github.com/madler/zlib', 'tag': r'v(\d+)\.(\d+)(?:\.(\d+))?', 'series': '1'}]}
