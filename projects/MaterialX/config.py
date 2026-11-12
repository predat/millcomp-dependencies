{
    'version': '1.39.5',
    'url': 'https://materialx.org',
    'downloads': ['https://github.com/AcademySoftwareFoundation/MaterialX/archive/refs/tags/v1.39.5.tar.gz'],
    'license': ['LICENSE'],
    # The core, the format and the shader generators (GLSL, MSL, OSL, MDL, Slang), shared, its data libraries in
    # libraries/. No render platform modules (they need OpenGL, Metal), no Python, viewer or graph editor.
    'cmake': [
        '-DMATERIALX_BUILD_SHARED_LIBS=ON',
        '-DMATERIALX_BUILD_PYTHON=OFF',
        '-DMATERIALX_BUILD_VIEWER=OFF',
        '-DMATERIALX_BUILD_GRAPH_EDITOR=OFF',
        '-DMATERIALX_BUILD_DOCS=OFF',
        '-DMATERIALX_BUILD_TESTS=OFF',
        '-DMATERIALX_BUILD_RENDER_PLATFORMS=OFF',
        '-DMATERIALX_INSTALL_RESOURCES=OFF',
        '-DMATERIALX_BUILD_USE_CCACHE=OFF',
    ],
    'commands:linux': [
        ['cmake', '-DCONFIG={buildDir}/lib/cmake/MaterialX/MaterialXConfig.cmake', '-P', '{projectDir}/noX11.cmake']
    ],
    # New versions, within the series (updates.py). what USD 26.11 is tested with
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/AcademySoftwareFoundation/MaterialX',
            'tag': r'v(\d+)\.(\d+)\.(\d+)',
            'series': '1.39',
        }
    ],
}
