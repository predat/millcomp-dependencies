{'version': '1.4.2',
 'url': 'https://github.com/KhronosGroup/MoltenVK',
 # Vulkan over Metal: the driver the Vulkan loader finds on macOS. Universal (x86_64 and arm64), macOS 12 and later.
 'platforms': ['macos'],
 'dependencies': ['Python'],  # install.py runs with the archive's Python
 'downloads': ['https://github.com/KhronosGroup/MoltenVK/releases/download/v1.4.2/MoltenVK-macos.tar'],
 'license': ['LICENSE'],
 'commands': [['{python}', '{projectDir}/install.py', '--source', '{source}', '--prefix', '{buildDir}']]}
