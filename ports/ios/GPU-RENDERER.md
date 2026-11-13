# iOS hardware renderer integration

This branch uses the existing Vulkan scene renderer through the official MoltenVK
1.4.2 iOS dynamic framework, rather than rasterizing the world on the CPU. SDL3
creates a Vulkan/Metal surface; volk and SDL load the same bundled framework.
No desktop OpenGL, Zink, or new renderer implementation is involved.

The downloaded official iOS package is SHA-256 pinned in build.sh. Its arm64
framework is embedded in the IPA, and must be signed by the sideload installer.
The previous SDL build excluded Vulkan, so this uses a separate install/cache.

All cba16fa UI, corona, swipe gain, render-scale and software recovery fixes are
retained. The private controller profile may set `[DXEngine.iOS] Renderer=Software`
for explicit recovery. GPU initialization errors otherwise remain visible rather
than silently falling back to CPU rendering. The default render scale remains
1/3 until on-device performance/thermal checks justify increasing it.

Existing Vulkan code supplies world/lightmap/detail/macro surfaces, meshes,
masked/translucent tiles and HUD, mirrors, fog and postprocessing. It already has
non-bindless descriptors, missing-BC1/RGB8 decode fallback, shader-clip fallback,
and Apple portability-extension support. This is source coverage, not device
validation.

## Acceptance

1. Device IPA includes arm64 MoltenVK framework and required engine resources.
2. Startup log identifies an Apple GPU, not CPU driver; actual map draws through
   Vulkan, with usable HUD/dialogue and existing controller/swipe controls.
3. Compare same save/view/settings against previous build for textures/lightmaps,
   transparency, yellow coronas, mirrors and gamma. Verify suspend/resume.
4. Only then compare sustained frame time and heat at matched render scale.

A successful compile is not proof of rendering correctness or a measured speedup.
