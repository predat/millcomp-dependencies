{
    'version': '2026.22',
    'url': 'https://shader-slang.org',
    'downloads:linux': [
        'https://github.com/shader-slang/slang/releases/download/v2026.22/slang-2026.22-linux-x86_64.tar.gz'
    ],
    'downloads:windows': [
        'https://github.com/shader-slang/slang/releases/download/v2026.22/slang-2026.22-windows-x86_64.zip'
    ],
    'downloads:macos': [
        'https://github.com/shader-slang/slang/releases/download/v2026.22/slang-2026.22-macos-aarch64.tar.gz'
    ],
    'extractTo': '{buildDir}',
    'license': ['LICENSE'],
    # 2026.18's macOS release linked Homebrew's zstd; macos.py stops the build if a release links Homebrew again.
    'dependencies:macos': ['Python'],  # macos.py runs with the archive's Python
    'commands:macos': [['{python}', '{projectDir}/macos.py', '--prefix', '{buildDir}']],
    # New versions, within the series (updates.py)
    'updates': [
        {'kind': 'git-tags', 'repo': 'https://github.com/shader-slang/slang', 'tag': r'v(\d+)\.(\d+)(?:\.(\d+))?'}
    ],
}
