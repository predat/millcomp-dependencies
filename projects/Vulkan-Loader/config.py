{'version': '1.4.363',
 'url': 'https://github.com/KhronosGroup/Vulkan-Loader',
 'downloads': ['https://github.com/KhronosGroup/Vulkan-Loader/archive/refs/tags/v1.4.363.tar.gz'],
 'license': ['LICENSE.txt'],
 'dependencies': ['Vulkan-Headers'],
 'cmake': ['-DBUILD_TESTS=OFF', '-DUPDATE_DEPS=OFF'],
 'cmake:linux': ['-DBUILD_WSI_XCB_SUPPORT=OFF',
                 '-DBUILD_WSI_XLIB_SUPPORT=OFF',
                 '-DBUILD_WSI_WAYLAND_SUPPORT=OFF']}
