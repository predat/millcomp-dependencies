{
    'version': '12.2.1',
    'url': 'https://fmt.dev',
    'downloads': ['https://github.com/fmtlib/fmt/archive/refs/tags/12.2.1.tar.gz'],
    'license': ['LICENSE'],
    'cmake': ['-DFMT_TEST=OFF', '-DFMT_DOC=OFF'],
    # New versions, within the series (updates.py)
    'updates': [
        {'kind': 'git-tags', 'repo': 'https://github.com/fmtlib/fmt', 'tag': r'(\d+)\.(\d+)\.(\d+)', 'series': '12'}
    ],
}
