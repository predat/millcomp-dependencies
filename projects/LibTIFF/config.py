{
    'version': '4.7.2',
    'url': 'https://libtiff.gitlab.io/libtiff',
    'downloads': ['https://github.com/libsdl-org/libtiff/archive/refs/tags/v4.7.2.tar.gz'],
    'license': ['LICENSE.md'],
    'dependencies': ['ZLib', 'LibJPEG-Turbo'],
    'cmake': [
        '-Dtiff-tools=OFF',
        '-Dtiff-tests=OFF',
        '-Dtiff-contrib=OFF',
        '-Dtiff-docs=OFF',
        '-Dlzma=OFF',
        '-Dzstd=OFF',
        '-Dwebp=OFF',
        '-Djbig=OFF',
        '-Dlerc=OFF',
        '-Dlibdeflate=OFF',
        '-Dcxx=OFF',
    ],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/libsdl-org/libtiff',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '4',
        }
    ],
}
