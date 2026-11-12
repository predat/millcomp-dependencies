{
    'version': '1.5.4',
    'url': 'https://code.videolan.org/videolan/dav1d',
    'downloads': ['https://code.videolan.org/videolan/dav1d/-/archive/1.5.4/dav1d-1.5.4.tar.gz'],
    'license': ['COPYING'],
    # FFmpeg's AV1 decoder: its own decodes with a GPU only.
    'commands': [
        [
            'meson',
            'setup',
            '{work}/build',
            '{source}',
            '--prefix={buildDir}',
            '--libdir=lib',
            '--buildtype=release',
            '--default-library=shared',
            '-Denable_tools=false',
            '-Denable_tests=false',
            '-Denable_examples=false',
            '-Denable_docs=false',
        ],
        ['meson', 'compile', '-C', '{work}/build', '-j', '{jobs}'],
        ['meson', 'install', '-C', '{work}/build'],
    ],
    'commands:macos': [['{python}', '{projectDir}/macos.py', '--prefix', '{buildDir}']],
    'dependencies:macos': ['Python'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://code.videolan.org/videolan/dav1d.git',
            'tag': r'(\d+)\.(\d+)\.(\d+)',
            'series': '1',
        }
    ],
}
