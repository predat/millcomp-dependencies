// Each dependency, used once. Prints one line per dependency, stops at the first that fails.
// Arguments: a directory to write in, the unpacked archive.
#include <MaterialXCore/Document.h>
#include <MaterialXFormat/Util.h>
#include <MaterialXGenShader/GenContext.h>
#include <MaterialXGenShader/Shader.h>
#include <MaterialXGenSlang/SlangShaderGenerator.h>
#include <OpenColorIO/OpenColorIO.h>
#include <OpenImageIO/imagebuf.h>
#include <OpenImageIO/imagebufalgo.h>
#include <QGuiApplication>
#include <rhi/qshaderbaker.h>
#include <pxr/base/plug/plugin.h>
#include <pxr/base/plug/registry.h>
#include <pxr/usd/sdf/fileFormat.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <slang-com-ptr.h>
#include <slang.h>
#include <tbb/parallel_for.h>
#include <vulkan/vulkan.h>
extern "C" {
#include <libavcodec/avcodec.h>
}

#include <atomic>
#include <initializer_list>
#include <memory>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <vector>

PXR_NAMESPACE_USING_DIRECTIVE

static void check(bool ok, const char* name)
{
    std::printf("%s: %s\n", name, ok ? "ok" : "FAILED");
    if (!ok)
        std::exit(1);
}

// A movie smoke.py wrote with the archive's ffmpeg, read by OpenImageIO's ffmpeg plugin: its frames are subimages.
static void checkMovie(const std::string& path, int channels, OIIO::TypeDesc format, const char* name)
{
    auto input = OIIO::ImageInput::open(path);
    if (!input)
        std::printf("%s\n", OIIO::geterror().c_str());
    check(input != nullptr, name);
    OIIO::ImageSpec spec;
    int frames = 0;
    while (input->seek_subimage(frames, 0))
        ++frames;
    spec = input->spec(5, 0);
    std::vector<unsigned char> pixels(spec.image_bytes());
    const bool read = input->read_image(5, 0, 0, spec.nchannels, spec.format, pixels.data());
    std::printf("%s: %d frames, %dx%d, %d channels, %s\n", name, frames, spec.width, spec.height, spec.nchannels,
                spec.format.c_str());
    check(read && frames >= 10 && spec.nchannels == channels && spec.format == format, name);
}

int main(int argc, char** argv)
{
    std::atomic<int> sum = 0;
    tbb::parallel_for(0, 1000, [&](int i) { sum += i; });
    check(sum == 499500, "TBB");

    const std::string path = std::string(argc > 1 ? argv[1] : ".") + "/smoke.exr";
    OIIO::ImageBuf image(OIIO::ImageSpec(16, 16, 4, OIIO::TypeDesc::HALF));
    const float color[] = {0.25f, 0.5f, 0.75f, 1.0f};
    OIIO::ImageBufAlgo::fill(image, color);
    check(image.write(path), "OpenImageIO write (OpenEXR)");
    OIIO::ImageBuf back(path);
    float pixel[4];
    back.getpixel(3, 3, pixel);
    check(back.read() && pixel[2] == 0.75f, "OpenImageIO read");

    // FFmpeg: the encoders millComp writes with, the decoders, and OpenImageIO reading movies.
    for (const char* encoder : {"prores_ks", "dnxhd", "libsvtav1", "ffv1", "mjpeg", "png",
#ifdef __APPLE__
                                "h264_videotoolbox", "hevc_videotoolbox", "prores_videotoolbox",
#else
                                "h264_nvenc", "hevc_nvenc", "av1_nvenc",
#endif
#ifdef _WIN32
                                "h264_mf", "hevc_mf",
#endif
         })
        check(avcodec_find_encoder_by_name(encoder) != nullptr, (std::string("FFmpeg encoder ") + encoder).c_str());
    for (const char* decoder : {"prores", "dnxhd", "h264", "hevc", "vp9", "libdav1d"})
        check(avcodec_find_decoder_by_name(decoder) != nullptr, (std::string("FFmpeg decoder ") + decoder).c_str());
    const std::string movies = argc > 1 ? argv[1] : ".";
    checkMovie(movies + "/prores.mov", 4, OIIO::TypeDesc::UINT16, "OpenImageIO movie: ProRes 4444, alpha");
    checkMovie(movies + "/dnxhr.mxf", 3, OIIO::TypeDesc::UINT16, "OpenImageIO movie: DNxHR HQX, MXF");
    checkMovie(movies + "/av1.mp4", 3, OIIO::TypeDesc::UINT8, "OpenImageIO movie: AV1 (dav1d)");

    const auto config = OCIO_NAMESPACE::Config::CreateFromFile("ocio://default");
    check(config && config->getColorSpace("ACEScg"), "OpenColorIO");

    const auto stage = UsdStage::CreateInMemory("smoke.usda");
    const UsdPrim prim = stage->DefinePrim(SdfPath("/comp"));
    check(prim.IsValid() && SdfFileFormat::FindByExtension("usda"), "USD (its plugins found)");
    check(SdfFileFormat::FindByExtension("mtlx") != nullptr, "USD MaterialX plugin (usdMtlx)");
    const PlugPluginPtr shaders = PlugRegistry::GetInstance().GetPluginWithName("usdShaders");
    check(shaders && shaders->Load(), "USD plugin library (usdShaders, in lib/usd)");

    // MaterialX finds its data libraries next to the executable: millComp, as this test, says where they are, the
    // directory holding libraries/ (share/materialx in the archive).
    const MaterialX::FilePath deps = MaterialX::FilePath(argc > 2 ? argv[2] : ".") / "share" / "materialx";
    MaterialX::DocumentPtr stdlib = MaterialX::createDocument();
    MaterialX::loadLibraries({"libraries"}, MaterialX::FileSearchPath(deps), stdlib);
    check(!stdlib->getNodeDefs().empty(), "MaterialX (its libraries found)");
    MaterialX::DocumentPtr materials = MaterialX::createDocument();
    materials->importLibrary(stdlib);
    MaterialX::NodePtr surface = materials->addNode("standard_surface", "surface", MaterialX::SURFACE_SHADER_TYPE_STRING);
    MaterialX::GenContext context(MaterialX::SlangShaderGenerator::create());
    context.registerSourceCodeSearchPath(deps);
    MaterialX::ShaderPtr shader = context.getShaderGenerator().generate("surface", surface, context);
    check(shader && !shader->getSourceCode(MaterialX::Stage::PIXEL).empty(), "MaterialX (Slang shader generated)");

    Slang::ComPtr<slang::IGlobalSession> session;
    check(SLANG_SUCCEEDED(slang::createGlobalSession(session.writeRef())), "Slang");

    uint32_t version = 0;
    check(vkEnumerateInstanceVersion(&version) == VK_SUCCESS && version != 0, "Vulkan loader");
#ifdef __APPLE__
    // Without a driver, vkCreateInstance fails (VK_ERROR_INCOMPATIBLE_DRIVER): it succeeds once the loader has loaded
    // MoltenVK through VK_DRIVER_FILES. MoltenVK is a portability driver, which the loader lists only when asked to. The
    // runner may have no GPU Metal sees: the count is printed, not checked.
    const char* extensions[] = {VK_KHR_PORTABILITY_ENUMERATION_EXTENSION_NAME};
    VkInstanceCreateInfo instanceInfo{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    instanceInfo.flags = VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR;
    instanceInfo.enabledExtensionCount = 1;
    instanceInfo.ppEnabledExtensionNames = extensions;
    VkInstance instance = VK_NULL_HANDLE;
    check(vkCreateInstance(&instanceInfo, nullptr, &instance) == VK_SUCCESS, "MoltenVK (loaded by the Vulkan loader)");
    uint32_t devices = 0;
    vkEnumeratePhysicalDevices(instance, &devices, nullptr);
    std::printf("MoltenVK: %u GPU(s)\n", devices);
    vkDestroyInstance(instance, nullptr);
#endif

    qputenv("QT_QPA_PLATFORM", "offscreen");
    QGuiApplication application(argc, argv);
    QShaderBaker baker;
    baker.setGeneratedShaders({{QShader::SpirvShader, QShaderVersion(100)}});
    baker.setGeneratedShaderVariants({QShader::StandardShader}); // None by default: bake() would make nothing.
    baker.setSourceString("#version 440\nlayout(location = 0) out vec4 c;\nvoid main() { c = vec4(1.0); }\n", QShader::FragmentStage);
    const bool baked = baker.bake().isValid();
    if (!baked)
        std::printf("%s\n", qPrintable(baker.errorMessage()));
    check(baked, "Qt (offscreen, ShaderTools)");
    return 0;
}
