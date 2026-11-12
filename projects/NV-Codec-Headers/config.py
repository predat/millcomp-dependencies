{
    'version': '12.2.72.0',
    'url': 'https://github.com/FFmpeg/nv-codec-headers',
    'downloads': ['https://github.com/FFmpeg/nv-codec-headers/archive/refs/tags/n12.2.72.0.tar.gz'],
    # MIT, in the headers.
    'license': ['include/ffnvcodec/nvEncodeAPI.h'],
    # FFmpeg's NVENC encoders and NVDEC decoders: headers only, FFmpeg loads NVIDIA's driver when it runs. 12.2 needs a
    # driver 550 or newer (13.0: 570).
    'platforms': ['linux', 'windows'],
    'dependencies': ['Python'],
    'commands': [['{python}', '{projectDir}/install.py', '--source', '{source}', '--prefix', '{buildDir}']],
    # New versions, within the series (updates.py)
    'updates': [
        {
            'kind': 'git-tags',
            'repo': 'https://github.com/FFmpeg/nv-codec-headers',
            'tag': r'n(\d+)\.(\d+)\.(\d+)\.(\d+)',
            'series': '12.2',
        }
    ],
}
