{
    'version': '1.4.368',
    'url': 'https://github.com/KhronosGroup/Vulkan-Loader',
    'downloads': ['https://github.com/KhronosGroup/Vulkan-Loader/archive/refs/tags/v1.4.368.tar.gz'],
    'license': ['LICENSE.txt'],
    'dependencies': ['Vulkan-Headers'],
    'cmake': ['-DBUILD_TESTS=OFF', '-DUPDATE_DEPS=OFF'],
    'cmake:linux': ['-DBUILD_WSI_XCB_SUPPORT=OFF', '-DBUILD_WSI_XLIB_SUPPORT=OFF', '-DBUILD_WSI_WAYLAND_SUPPORT=OFF'],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/KhronosGroup/Vulkan-Loader',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '1',
        }
    ],
}
