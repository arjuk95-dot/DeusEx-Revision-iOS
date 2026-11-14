import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class VSyncOffBuild(unittest.TestCase):
    def test_ios_override_preserves_desktop_setting(self):
        source = (ROOT / "DXEngine/RenderDevice/RenderDevice.cpp").read_text()
        self.assertRegex(source, r"#ifdef DXE_IOS\s+//[^\n]*\n\s*UseVSync = false;\s*#else\s+UseVSync = settings.RenderDevice.UseVSync;\s*#endif")

    def test_swapchain_uses_requested_policy(self):
        source = (ROOT / "DXEngine/RenderDevice/Vulkan/CommandBufferManager.cpp").read_text()
        self.assertIn("renderer->UseVSync ? 2 : 3, renderer->UseVSync", source)

if __name__ == "__main__":
    unittest.main()
