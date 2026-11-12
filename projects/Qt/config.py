{
    'version': '6.12.0',
    'url': 'https://www.qt.io',
    'dependencies': ['Python'],
    'environment': {'PYTHONPATH': '{work}/py7zr'},
    'commands': [['{python}', '-m', 'pip', 'install', '--no-cache-dir', '--target', '{work}/py7zr', 'py7zr==1.0.0']],
    'commands:linux': [
        ['{python}', '{projectDir}/fetch.py', '--platform', 'linux', '--version', '6.12.0', '--out', '{buildDir}/qt']
    ],
    'commands:windows': [
        ['{python}', '{projectDir}/fetch.py', '--platform', 'windows', '--version', '6.12.0', '--out', '{buildDir}/qt']
    ],
    'commands:macos': [
        ['{python}', '{projectDir}/fetch.py', '--platform', 'macos', '--version', '6.12.0', '--out', '{buildDir}/qt']
    ],
    # New versions, within the series (updates.py). millComp: qt-6.12
    'updates': [{'kind': 'qt', 'series': '6.12'}],
}
