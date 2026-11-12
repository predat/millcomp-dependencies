{
    'version': '1.4.1',
    'url': 'https://github.com/Tessil/robin-map',
    'downloads': ['https://github.com/Tessil/robin-map/archive/refs/tags/v1.4.1.tar.gz'],
    'license': ['LICENSE'],
    'cmake': [],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/Tessil/robin-map',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '1',
        }
    ],
}
