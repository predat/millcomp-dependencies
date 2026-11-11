# Built against an unpacked archive, wherever it is: what millComp asks of the dependencies (cmake/Dependencies.cmake),
# found the same way, and used once each by smoke.cpp and the Python module.
cmake_minimum_required(VERSION 4.0)
project(smoke LANGUAGES CXX C)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenImageIO 3 REQUIRED CONFIG)
find_package(OpenColorIO 2 REQUIRED CONFIG)
find_package(OpenEXR 3 REQUIRED CONFIG)
find_package(TBB REQUIRED CONFIG)
find_package(pxr REQUIRED CONFIG)
find_package(Python 3.11 REQUIRED COMPONENTS Interpreter Development.Module Development.Embed)
find_package(Vulkan REQUIRED)
find_package(slang CONFIG REQUIRED)
find_package(GTest REQUIRED CONFIG)
find_package(nanobind CONFIG REQUIRED)
find_package(Qt6 6.12 REQUIRED COMPONENTS Widgets GuiPrivate ShaderTools ShaderToolsPrivate Svg Test)

add_executable(smoke smoke.cpp)
target_link_libraries(
    smoke
    PRIVATE
        OpenImageIO::OpenImageIO
        OpenColorIO::OpenColorIO
        OpenEXR::OpenEXRCore
        TBB::tbb
        usd
        sdf
        tf
        Vulkan::Vulkan
        slang::slang
        Qt6::Widgets
        Qt6::Svg
        Qt6::ShaderTools
        # rhi/*.h, Qt's semi-public RHI API, are in the private include directories.
        Qt6::GuiPrivate
        Qt6::ShaderToolsPrivate
)
nanobind_add_module(_smoke NB_STATIC module.cpp)
