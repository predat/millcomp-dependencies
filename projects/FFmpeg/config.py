{
    'version': '9.0.2',
    'url': 'https://ffmpeg.org',
    'downloads': ['https://github.com/FFmpeg/FFmpeg/archive/refs/tags/n9.0.2.tar.gz'],
    # LGPL 2.1 or later: no GPL or nonfree part is enabled (ffmpeg.py).
    'license': ['LICENSE.md', 'COPYING.LGPLv2.1'],
    'dependencies': ['Python', 'ZLib', 'Dav1d', 'SVT-AV1'],
    'dependencies:linux': ['NV-Codec-Headers'],
    'dependencies:windows': ['NV-Codec-Headers'],
    'commands': [
        [
            '{python}',
            '{projectDir}/ffmpeg.py',
            '--source',
            '{source}',
            '--prefix',
            '{buildDir}',
            '--build',
            '{work}/build',
            '--jobs',
            '{jobs}',
        ]
    ],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/FFmpeg/FFmpeg',
            'tag': r'n(\d+)\.(\d+)(?:\.(\d+))?',
            'series': '9',
        }
    ],
}
