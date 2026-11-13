# GPU touch/lifecycle corrective batch

Observed on device after GPU build 684f70a:
- Logs identify Apple A18 Pro GPU, Vulkan bindless path, render scale 0.333.
- Touch input state existed, but glyphs were drawn only by SDL's software bitmap presenter. Vulkan bypassed it.
- Startup log records Metal background GPU submission denial and VK_ERROR_DEVICE_LOST.
- Desktop 4x MSAA default applied to phone GPU; it had no software-renderer equivalent.

Corrections:
- VisitTouchLines exposes pure existing glyph/hit-region geometry. The game draws it via its active Vulkan device after game UI and before present. Software presentation is unchanged.
- MSAA is off by default on iOS; explicit DXEngine.iOS MSAA=2 or 4 retains optional antialiasing.
- Frame receipt reports active viewport, render scale and bounded 120-frame wall cadence. This includes simulation/input/presentation and is not GPU-only timing.
- Lifecycle correction is integrated separately in this batch.

Validation: existing native glyph fixture now also checks finite/bounded overlay geometry in both menu and gameplay modes. Source guards ensure overlay precedes present and does not depend on SDL RendererHandle. Actual glyph visibility, menu response, gameplay and background/foreground resume still require phone testing.
