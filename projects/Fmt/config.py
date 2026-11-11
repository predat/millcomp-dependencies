{'version': '12.1.0',
 'url': 'https://fmt.dev',
 'downloads': ['https://github.com/fmtlib/fmt/archive/refs/tags/12.1.0.tar.gz'],
 'license': ['LICENSE'],
 'cmake': ['-DFMT_TEST=OFF', '-DFMT_DOC=OFF'],
 # New versions, within the series (updates.py)
 'updates': [{'kind': 'git-tags', 'repo': 'https://github.com/fmtlib/fmt', 'tag': r'(\d+)\.(\d+)\.(\d+)', 'series': '12'}]}
