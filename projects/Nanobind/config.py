{
    'version': '3.1.0',
    'url': 'https://github.com/wjakob/nanobind',
    'downloads': ['https://github.com/wjakob/nanobind/archive/refs/tags/v3.1.0.tar.gz'],
    'license': ['LICENSE'],
    'dependencies': ['Python', 'Robin-map'],
    'cmake': ['-DNB_TEST=OFF', '-DNB_USE_SUBMODULE_DEPS=OFF', '-DNB_CREATE_INSTALL_RULES=ON'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/wjakob/nanobind',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '3',
        }
    ],
}
