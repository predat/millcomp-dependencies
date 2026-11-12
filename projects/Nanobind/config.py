{
    'version': '3.1.0',
    'url': 'https://github.com/wjakob/nanobind',
    'downloads': ['https://github.com/wjakob/nanobind/archive/refs/tags/v3.1.0.tar.gz'],
    'license': ['LICENSE'],
    'dependencies': ['Python', 'Robin-map'],
    'cmake': [
        '-DNB_TEST=OFF',
        '-DNB_USE_SUBMODULE_DEPS=OFF',
        '-DNB_CREATE_INSTALL_RULES=ON',
        # Its sources, compiled into each module, are data: share/nanobind (not nanobind/ at the archive's top). CMake finds
        # share/nanobind/cmake/nanobind-config.cmake. STRING: a PATH cache variable given a relative path is made absolute
        # against the working directory, not the prefix.
        '-DNB_INSTALL_DATADIR:STRING=share/nanobind',
    ],
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
