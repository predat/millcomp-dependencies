{
    'version': '4.3.0',
    'url': 'https://gitlab.com/AOMediaCodec/SVT-AV1',
    'downloads': ['https://gitlab.com/AOMediaCodec/SVT-AV1/-/archive/v4.3.0/SVT-AV1-v4.3.0.tar.gz'],
    'license': ['LICENSE.md', 'PATENTS.md'],
    # FFmpeg's AV1 encoder (libsvtav1): BSD, royalty free, where x264 and x265 are GPL. Its assembly needs nasm on x86_64.
    'cmake': ['-DBUILD_APPS=OFF', '-DBUILD_TESTING=OFF'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://gitlab.com/AOMediaCodec/SVT-AV1.git',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '4',
        }
    ],
}
