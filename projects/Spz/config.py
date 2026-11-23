{
    # Niantic's .spz codec of 3D Gaussian splats: millComp's .spz import and export (src/scene/splat). v2.1.0 rather
    # than v3: v3 reads and writes .spz version 4 through zstd, which the archive does not carry; v2.1.0 reads versions
    # 1 to 3 with zlib only. Pinned by the commit the v2.1.0 tag points to (a tag name could move). Its CMake project
    # says 1.1.0 (spzConfigVersion.cmake): millComp asks for spz 1.1.
    'version': '2.1.0',
    'url': 'https://github.com/nianticlabs/spz',
    'downloads': ['https://github.com/nianticlabs/spz/archive/2cf0be04d86b5f9632d9073ccbbe3b1e6a609f31.tar.gz'],
    'license': ['LICENSE'],
    'dependencies': ['ZLib'],
    'cmake': [
        # Static: its sources have no export macros (an MSVC DLL would export nothing), and three small sources are not
        # worth a run path. Position-independent anyway (its CMakeLists.txt sets it): it goes into libmillcomp.
        '-DBUILD_SHARED_LIBS=OFF',
        '-DBUILD_PYTHON_BINDINGS=OFF',
    ],
}
