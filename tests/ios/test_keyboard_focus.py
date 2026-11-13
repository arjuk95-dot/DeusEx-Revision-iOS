import pathlib,unittest,plistlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
class KeyboardFocusRegression(unittest.TestCase):
 def test_menu_button_does_not_use_throwing_edit_cast(self):
  s=(ROOT/'DXEngine/Engine.cpp').read_text();s=s[s.index('void Engine::TickWindow'):]
  self.assertIn('UObject::TryCast<UEditWindow>(dxRootWindow->FocusWindow())',s)
  self.assertNotIn('UObject::Cast<UEditWindow>',s)
  self.assertIn('edit && edit->IsEditingEnabled()',s)
 def test_indirect_input_enabled(self):
  self.assertTrue(plistlib.loads((ROOT/'ports/ios/Info.plist.in').read_bytes())['UIApplicationSupportsIndirectInputEvents'])
 def test_overlay_not_on_unrelated_dialog(self):
  s=(ROOT/'DXWidgets/src/window/sdl3/sdl3_display_window.cpp').read_text()
  draw=s[s.index('void SDL3DisplayWindow::TouchDraw()'):]
  self.assertIn('if(!TouchEnabled)return;',draw)
  self.assertNotIn('SDL_RenderDebugText',draw)
