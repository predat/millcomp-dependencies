// Each dependency, used once. Prints one line per dependency, stops at the first that fails.
#include <OpenColorIO/OpenColorIO.h>
#include <OpenImageIO/imagebuf.h>
#include <OpenImageIO/imagebufalgo.h>
#include <QGuiApplication>
#include <rhi/qshaderbaker.h>
#include <pxr/usd/sdf/fileFormat.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <slang-com-ptr.h>
#include <slang.h>
#include <tbb/parallel_for.h>
#include <vulkan/vulkan.h>

#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>

PXR_NAMESPACE_USING_DIRECTIVE

static void check(bool ok, const char* name)
{
    std::printf("%s: %s\n", name, ok ? "ok" : "FAILED");
    if (!ok)
        std::exit(1);
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

    const auto config = OCIO_NAMESPACE::Config::CreateFromFile("ocio://default");
    check(config && config->getColorSpace("ACEScg"), "OpenColorIO");

    const auto stage = UsdStage::CreateInMemory("smoke.usda");
    const UsdPrim prim = stage->DefinePrim(SdfPath("/comp"));
    check(prim.IsValid() && SdfFileFormat::FindByExtension("usda"), "USD (its plugins found)");

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
