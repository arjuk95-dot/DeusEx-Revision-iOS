# Revision 25916968: observed input and compatibility gates

Observed 2026-11-12 on the user's Steam installation. App 397550 had downloaded
3,543,697,856 bytes and staged 6,989,229,728 bytes, but was **not committed**:
StateFlags 1026, buildid 0, no InstalledDepots. Do not call this installed.
Steam startup remained blocked by Millennium/Steam.cfg. No configuration was
changed. Base GOTY manifest 6910 and System/DeusEx.exe were absent.

## Verified launch configuration

Staged executable: `Revision/System/Revision.exe`; source defaults are
`RevisionDefault.ini` and `RevisionDefUser.ini`. Existing user config is
`RevisionUser.ini`. Both user sources select `Revision.RevJCDentonMale`.

The source engine INI selects:

- Console: Revision.RevConsole
- GameEngine: Revision.RevGameEngine
- DefaultGame: Revision.RevGameInfo
- Root: Revision.RevRootWindow
- Map/LocalMap: Index.dx / DX.dx
- Desktop subsystems: D3D9Drv.D3D9RenderDevice, RGalaxy.GalaxyAudioSubsystem,
  WinDrvLite.WindowsClientLite, RenderExt.RenderExt, Extension.InputExt,
  SteamDrv.SteamGamePlatform

`Core.System` places Revision sounds/textures/maps/scripts first, followed by
NewVision and HDTP, then base music/sounds/textures/maps/scripts. The twelve
observed paths are covered in `test_revision.py`; their order is not changed.
OggPath points to Revision/Music. Relocation preserves that path, but does not
implement DXOgg/RGalaxy's native music behavior.

## What DXEngine actually does

Source inspection at upstream 8294980 plus port changes:

- `Engine.cpp` constructs its own audio, renderer, client, viewport and base
  GameEngine objects, not the Windows DLL subsystems. The port explicitly selects
  its software renderer. The INI's GameEngine class is used to read UseSound;
  its native RevGameEngine implementation is not instantiated by this code.
- Console and Root settings are loaded as script classes; Revision overrides
  remain intact. Native objects use the nearest registered class ancestor.
- `Frame::CallNative` must find an implemented native handler. Windows DLLs
  cannot supply one on iOS. Missing handlers remain errors, not success stubs.
  Diagnostics now include the package/class/function and numeric native index.
- No explicit DXOgg, SteamDrv, RGalaxy or RenderExt implementation was found in
  the inspected DXEngine source. Absence of a named implementation alone does
  not establish which calls are required to reach the menu or play a level.
- Upstream NATIVES.md's remark about a Revision script audit concerns its
  single-player stub inventory. It is not proof of compatibility with this
  installed Revision build or its native extensions.

Staged native DLLs include Revision.dll, RF.dll, DXOgg.dll, SteamDrv.dll,
EngineI.dll, RenderExt.dll, WinDrvLite.dll, RGalaxy.dll, steam_api.dll and
stock engine DLLs. Native-required functions must be identified from actual
package declarations/calls and startup logs before implementing equivalents.
Do not load these Windows binaries, remove Revision classes to mask errors,
report stubbed achievements as real, or substitute vanilla as a passing result.

## Next evidence required

1. Finish Steam installation through an approved startup fix; install owned
   base GOTY with any required EULA approval. Verify base 1112fm SHA1 against
   `UE1GameDatabase.h`.
2. On private copies, inventory Revision/RF/DXOgg native declarations and
   imports; identify the earliest reachable unsupported call. No game data in
   public repository, release, CI artifacts, or test fixtures.
3. Run the prepared Revision profile against the host engine before spending
   a macOS runner, if private assets can be materialized in the cloud safely.
   Log exact package/function failures and distinguish optional platform calls
   from gameplay requirements.
4. Compile the iOS target with an Apple SDK. First success means Revision's
   actual menu and first map on-device, not merely an app icon or vanilla menu.

## Update: installation committed and base-dependency audit

Steam subsequently committed Revision build 25916968: StateFlags 4,
6,616,112,546 bytes, content log Fully Installed / No Error at 15:11:01.
System contains 68 .u and 33 .dll files. User removed base Deus Ex afterward;
base System/Maps/Textures/Sounds/Music directories are absent. Revision remains
the target, not vanilla. No reinstall or EULA action was taken by this work.

Read-only import-table parser (mirrors Package.cpp/PackageStream.cpp) parsed
68 Revision System packages and four selected map variants with zero errors.
These actual package imports are absent everywhere in the remaining game tree:

| Input | Missing declared imports |
|---|---|
| Revision/Maps/DX.dx | Core |
| Revision/Maps/01_NYC_UNATCOIsland.dx | Ambient, Core, MoverSFX |
| Revision/System/Revision.u | Ambient, Core, InfoPortraits, MPCharacters, MoverSFX |
| Revision/Maps/00_Training.dx | Ambient, Core, MoverSFX, Training_Music |
| Revision/System/RevisionMission.u | Includes missing Fire |

Across all audited packages the absent union is Ambient, Core, Fire,
InfoPortraits, IpServer, MPCharacters, MoverSFX, Training_Music, UBrowser,
UWindow. This is declared-dependency evidence, not proof every import executes;
multiplayer-only/editor/optional references may not block the first milestone.

**Proven DXEngine startup requirement:** PropertyOffsets.cpp's
InitPropertyOffsets_Object calls GetPackage("Core") during PackageManager
construction. GetPackage throws when Core is absent from scanned files; the
active Paths scans .u, not native DLLs. RegisterNativeClasses stores C++ class
factories, not a substitute Core package. Core.dll's presence therefore does
not satisfy this engine's Core-package load. The DeusEx.exe SHA identity check
is separately an implementation gate, not the evidence for missing content.

Restore needed owned base assets while continuing to launch Revision's profile.
Do not claim all of vanilla needs to be played, or silently replace Revision
classes. The import audit tool never executes assets or redistributes them.
