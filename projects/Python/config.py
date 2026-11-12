{
    'version': '3.13.18',
    'url': 'https://www.python.org',
    'downloads:linux': [
        'https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.13.18%2B20261110-x86_64-unknown-linux-gnu-install_only.tar.gz'
    ],
    'downloads:windows': [
        'https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.13.18%2B20261110-x86_64-pc-windows-msvc-install_only.tar.gz'
    ],
    'downloads:macos': [
        'https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.13.18%2B20261110-aarch64-apple-darwin-install_only.tar.gz'
    ],
    'extractTo': '{buildDir}/python',
    'license:linux': ['lib/python3.13/LICENSE.txt'],
    'license:windows': ['LICENSE.txt'],
    'license:macos': ['lib/python3.13/LICENSE.txt'],
    'commands': [['{python}', '-m', 'pip', 'install', '--no-cache-dir', 'numpy==2.5.4']],
    # New versions, within the series (updates.py). millComp: python-3.13, numpy-2
    'updates': [
        {'kind': 'python-build-standalone', 'series': '3.13'},
        {'kind': 'pypi', 'package': 'numpy', 'series': '2'},
    ],
}
