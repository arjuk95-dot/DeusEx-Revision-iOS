import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class GPUTiming(unittest.TestCase):
 def test_split_cpu_timings_are_bounded(self):
  s=(ROOT/"DXEngine/RenderDevice/Vulkan/CommandBufferManager.cpp").read_text()
  for part in ("ProbeFenceMs","ProbeAcquireMs","ProbeSubmitMs","ProbePresentMs","ProbeFrames == 120","not GPU timestamps"):
   self.assertIn(part,s)
  self.assertIn("renderer->UseVSync ? 2 : 3",s) # diagnostic does not change presentation policy
 def test_optional_probe_keeps_lookup_and_empty_result(self):
  s=(ROOT/"DXEngine/Engine.cpp").read_text()
  s=s[s.index('else if (command == "get"'):s.index('else if (command == "set"')]
  self.assertIn("packages->FindClassAnyPackage(className)",s)
  self.assertIn('className == "LaunchSystem" && propertyName == "Paths"',s)
  self.assertIn("LogUnimplemented",s)
  self.assertIn("return {};",s)
 def test_scene_and_overlay_measured_separately(self):
  s=(ROOT/"DXEngine/Render/RenderSubsystem.cpp").read_text()
  self.assertIn("phaseScene+=ms(probeLocked,probeDrawn)",s)
  self.assertIn("phaseOverlay+=ms(probeDrawn,probeOverlay)",s)
