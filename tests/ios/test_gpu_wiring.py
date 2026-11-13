"""Focused source guards for the iOS GPU loader contract, not runtime GPU proof."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
class GPUWiring(unittest.TestCase):
    def test_same_explicit_loader(self):
        boot = (ROOT/'ports/ios/MainIOS.mm').read_text()
        volk = (ROOT/'DXGPU/src/volk/volk.c').read_text()
        self.assertIn('SDL_SetHint(SDL_HINT_VULKAN_LIBRARY, library.UTF8String)', boot)
        self.assertIn('setenv("DXE_IOS_VULKAN_LIBRARY", library.UTF8String', boot)
        self.assertIn('getenv("DXE_IOS_VULKAN_LIBRARY")', volk)
    def test_no_silent_cpu_fallback(self):
        engine = (ROOT/'DXEngine/Engine.cpp').read_text()
        self.assertIn('if (std::getenv("DXE_IOS_REQUIRE_GPU"))\n                throw;', engine)
    def test_rebuilds_vulkan_sdl_and_embeds_framework(self):
        build = (ROOT/'ports/ios/build.sh').read_text()
        self.assertIn('-DSDL_VULKAN=ON', build)
        self.assertIn('install-vulkan-v1', build)
        self.assertIn('b5d947b1660e6e9fed40b9cd2387e160aaab9e80b775c0cef7e14059405178c1', build)
        self.assertIn('"$app/Frameworks/"', build)

    def test_gpu_overlay_is_before_present(self):
        render=(ROOT/'DXEngine/Render/RenderSubsystem.cpp').read_text()
        start=render.index('PostRender();')
        self.assertLess(render.index('VisitTouchLines',start),render.index('Device->Unlock(true)',start))
        backend=(ROOT/'DXWidgets/src/window/sdl3/sdl3_display_backend.cpp').read_text().split('void SDL3DisplayBackend::VisitTouchLines')[1]
        self.assertIn('IOSTouch::OverlayLines',backend)
        self.assertNotIn('RendererHandle',backend)
    def test_mobile_msaa_is_opt_in(self):
        boot=(ROOT/'ports/ios/MainIOS.mm').read_text()
        self.assertIn('GetValue("DXEngine.iOS", "MSAA")',boot)
        self.assertIn('AntialiasMode::MSAA2x : AntialiasMode::Off',boot)
