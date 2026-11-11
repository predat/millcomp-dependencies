# MaterialXConfig.cmake asks for X11's Xt on Linux whatever was built. Only MaterialXRenderHw links X11, a render
# platform module, which MATERIALX_BUILD_RENDER_PLATFORMS=OFF leaves out: without this, every project finding MaterialX
# would need libXt's development files. Run as: cmake -DCONFIG=<MaterialXConfig.cmake> -P noX11.cmake
file(READ "${CONFIG}" text)
string(REPLACE "    find_dependency(X11 REQUIRED COMPONENTS Xt)\n" "" result "${text}")
if(result STREQUAL text)
    message(FATAL_ERROR "${CONFIG}: no find_dependency(X11 REQUIRED COMPONENTS Xt) to remove; check MaterialX's config")
endif()
file(WRITE "${CONFIG}" "${result}")
message(STATUS "${CONFIG}: X11 no longer required")
