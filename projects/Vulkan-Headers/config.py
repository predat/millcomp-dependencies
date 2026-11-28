{
    'version': '1.4.369',
    'url': 'https://github.com/KhronosGroup/Vulkan-Headers',
    'downloads': ['https://github.com/KhronosGroup/Vulkan-Headers/archive/refs/tags/v1.4.369.tar.gz'],
    'license': ['LICENSE.md'],
    'cmake': ['-DVULKAN_HEADERS_ENABLE_TESTS=OFF', '-DVULKAN_HEADERS_ENABLE_INSTALL=ON'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/KhronosGroup/Vulkan-Headers',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '1',
        }
    ],
}
