{
    'version': '14.4.0',
    'url': 'https://gcc.gnu.org/onlinedocs/libstdc++/',
    # GCC 14's libstdc++.so.6 in lib/compat/, for the prebuilt binaries that need more than Rocky 9's (GCC 11, GLIBCXX_3.4.29):
    # Slang's libslang-llvm.so needs GLIBCXX_3.4.30 (GCC 12), so without it a user Slang node has no CPU path on the
    # studio's platform. What build.py builds needs nothing of it (gcc-toolset-14 links what GCC 11's lacks statically).
    # Not in lib/: a process holds one libstdc++, which must be the newest it needs, and a build with a compiler newer
    # than GCC 14 (GCC 16's GLIBCXX_3.4.35) needs its own; in lib/ the archive's $ORIGIN run paths and the consumer's
    # would always load this one (1.0.6 broke such builds). The consumer adds lib/compat/ to its run paths when its
    # compiler's libstdc++ is older (millComp: cmake/MillcompDependencies.cmake). conda-forge's build, against glibc
    # 2.17; Rocky 9's libgcc_s is enough for it.
    'platforms': ['linux'],
    'dependencies': ['Python'],  # install.py runs with the archive's Python
    'downloads': ['https://conda.anaconda.org/conda-forge/linux-64/libstdcxx-14.4.0-h934c35e_7.conda'],
    'commands': [['{python}', '{projectDir}/install.py', '--source', '{source}', '--prefix', '{buildDir}']],
}
