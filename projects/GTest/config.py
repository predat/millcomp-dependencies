{
    'version': '1.18.0',
    'url': 'https://github.com/google/googletest',
    'downloads': ['https://github.com/google/googletest/archive/refs/tags/v1.18.0.tar.gz'],
    'license': ['LICENSE'],
    'cmake': ['-DINSTALL_GTEST=ON', '-Dgtest_force_shared_crt=ON'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/google/googletest',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '1',
        }
    ],
}
