{
    'version': '3.2.2.0',
    'url': 'https://openimageio.org',
    'downloads': ['https://github.com/AcademySoftwareFoundation/OpenImageIO/archive/refs/tags/v3.2.2.0.tar.gz'],
    'license': ['LICENSE.md'],
    'dependencies': [
        'OpenEXR',
        'OpenColorIO',
        'TBB',
        'Fmt',
        'Robin-map',
        'LibPNG',
        'LibTIFF',
        'LibJPEG-Turbo',
        'FreeType',
        'ZLib',
        'FFmpeg',
    ],
    # The ffmpeg plugin opens only the extensions it lists, even when asked for by name: MXF (DNxHD/DNxHR, ProRes) and
    # WebM (VP9, AV1) are movies too.
    'edits': [['src/ffmpeg.imageio/ffmpeginput.cpp', '"mpg", "mkv", nullptr', '"mpg", "mkv", "mxf", "webm", nullptr']],
    'cmake': [
        '-DOIIO_BUILD_TESTS=OFF',
        '-DOIIO_BUILD_TOOLS=ON',
        '-DUSE_PYTHON=OFF',
        '-DBUILD_DOCS=OFF',
        '-DINSTALL_DOCS=OFF',
        '-DOIIO_INTERNALIZE_FMT=OFF',
        '-DSTOP_ON_WARNING=OFF',
        '-DUSE_FFMPEG=ON',  # movies: ProRes, DNxHD/DNxHR, H.264, HEVC, VP9, AV1…
        '-DUSE_LIBRAW=OFF',
        '-DUSE_OPENCV=OFF',
        '-DUSE_OPENVDB=OFF',
        '-DUSE_PTEX=OFF',
        '-DUSE_WEBP=OFF',
        '-DUSE_LIBHEIF=OFF',
        '-DUSE_OPENJPEG=OFF',
        '-DUSE_DCMTK=OFF',
        '-DUSE_GIF=OFF',
        '-DUSE_JXL=OFF',
        '-DUSE_NUKE=OFF',
        '-DUSE_R3DSDK=OFF',
        '-DUSE_BZIP2=OFF',
        '-DUSE_QT=OFF',
        '-DUSE_LIBUHDR=OFF',
    ],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/AcademySoftwareFoundation/OpenImageIO',
            'tag': r'v(\d+)\.(\d+)\.(\d+)\.(\d+)',
            'series': '3',
        }
    ],
}
