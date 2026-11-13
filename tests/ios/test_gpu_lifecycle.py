"""Source regression guards; actual UIKit suspend/resume needs a device test."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
class GPULifecycle(unittest.TestCase):
    def test_watch_drains_before_background_callback_returns(self):
        s=(ROOT/'DXEngine/RenderDevice/Vulkan/VulkanRenderDevice.cpp').read_text()
        watch=s.split('static bool IOSVulkanLifecycleWatch',1)[1].split('void VulkanRenderDevice::EnsureForeground',1)[0]
        self.assertIn('SDL_EVENT_WILL_ENTER_BACKGROUND',watch)
        self.assertLess(watch.index('IOSLifecycle::Suspend()'),watch.index('vkDeviceWaitIdle'))
        self.assertNotIn('throw ',watch)
        self.assertNotIn('ProcessEvents',watch)
        self.assertIn('SDL_EVENT_DID_ENTER_FOREGROUND',watch)
        self.assertIn('SDL_AddEventWatch(IOSVulkanLifecycleWatch, this)',s)
        self.assertIn('SDL_RemoveEventWatch(IOSVulkanLifecycleWatch, this)',s)
    def test_all_queue_submit_entrypoints_wait_for_foreground(self):
        s=(ROOT/'DXEngine/RenderDevice/Vulkan/CommandBufferManager.cpp').read_text()
        for method in ['WaitForTransfer()', 'SubmitCommands(bool present, int presentWidth, int presentHeight, bool wait)']:
            body=s.split('void CommandBufferManager::'+method,1)[1]
            self.assertLess(body.index('renderer->EnsureForeground()'),body.index('WaitForFrame()'))
        s=(ROOT/'DXEngine/RenderDevice/Vulkan/VulkanRenderDevice.cpp').read_text()
        body=s.split('void VulkanRenderDevice::Lock(',1)[1]
        self.assertLess(body.index('EnsureForeground()'),body.index('WaitForFrame()'))
    def test_parked_pump_does_not_render(self):
        s=(ROOT/'DXWidgets/src/window/sdl3/sdl3_display_window.cpp').read_text()
        body=s.split('void SDL3DisplayWindow::ProcessEvents()',1)[1].split('void SDL3DisplayWindow::RunLoop()',1)[0]
        self.assertIn('while (IOSLifecycle::IsSuspended())',body)
        self.assertIn('SDL_WaitEventTimeout(&event, 100)',body)
        dispatch=s.split('void SDL3DisplayWindow::DispatchEvent',1)[1]
        self.assertLess(dispatch.index('IOSLifecycle::IsSuspended()'),dispatch.index('return OnTimerEvent'))
        self.assertIn('entry.second->Touch.Reset()',dispatch)
    def test_real_drain_failure_is_not_hidden(self):
        s=(ROOT/'DXEngine/RenderDevice/Vulkan/VulkanRenderDevice.cpp').read_text()
        self.assertIn('BackgroundDrainResult != VK_SUCCESS',s)
        self.assertIn('Vulkan background drain failed:',s)
