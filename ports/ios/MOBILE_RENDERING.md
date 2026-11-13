# Mobile rendering correction

The game remains CPU-rasterized; Metal presents and scales the result. No GPU-renderer or measured FPS claim.

Optional read-only preferences in the private User.controller-candidate.ini, [DXEngine.iOS]:
- RenderScale: 0.25–1 (default 1/3; formerly fixed 1/2).
- TouchLookGain: 0.25–8 (default 3); normalized to reference screen width, unaffected by render resolution. Existing game mouse sensitivity still applies.
- UIMode: fit (default) or legacy. Fit preserves a 640x480 minimum logical UI, including below 480 render pixels. This is native port fit scaling, not a claim of implementing every Revision RF scaling mode.
- CPUUpscale: True/1 restores legacy CPU scaling for A/B. Default uses Metal bilinear upscale after gamma. Edges may differ slightly because legacy filtered before gamma; aspect, gamma curve and native touch overlay are preserved.

No game data, saves or INI files are rewritten by these preferences. startup.log records scene/upload/native dimensions. Verify on device: dock coronas are single glows; HUD/menu/subtitles legible; menus fit and click locations agree; swipe while firing; compare FPS/thermals and sharpness on the same save.
