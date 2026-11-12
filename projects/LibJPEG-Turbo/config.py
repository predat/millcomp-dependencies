{'version': '3.2.1',
 'url': 'https://libjpeg-turbo.org',
 'downloads': ['https://github.com/libjpeg-turbo/libjpeg-turbo/archive/refs/tags/3.2.1.tar.gz'],
 'license': ['LICENSE.md'],
 'cmake': ['-DENABLE_STATIC=OFF', '-DWITH_TURBOJPEG=OFF'],
 # New versions, within the series (updates.py)
 'updates': [{'kind': 'git-tags', 'repo': 'https://github.com/libjpeg-turbo/libjpeg-turbo', 'tag': r'(\d+)\.(\d+)\.(\d+)', 'series': '3'}]}
