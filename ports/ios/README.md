# DXEngine iOS bring-up (altered source, not an upstream release)

Based on JuggyMcNutty/DXEngine commit
`829498083a0cbf71391a5b2fde830d50d80b6da1`. DXEngine is a C++20 reimplementation
of the Deus Ex/Unreal Engine 1 runtime, derived from Surreal Engine. It is not
the unrelated Unity OpenEX project and does not recompile the original x86 EXE.
The existing script VM interprets the original game scripts; the port should
not need JIT entitlements. Keep upstream `LICENSE.md` and attribution intact.

**Status: Apple arm64 bring-up IPA built, not an iPhone-validated game.**
Manual run 43265850857 at b2aec11 compiled, linked and packaged successfully.
The unsigned IPA contains engine code/resources only. Device installation,
Revision startup, touch input and audio remain unverified on iOS.

## Current target: Revision first

The user selected **Deus Ex: Revision** as the first running-game milestone.
Vanilla Deus Ex is only the owned base-data/version dependency, not a substitute
launch target. No ragdoll or other gameplay enhancements are being added.

Steam apps 397550 (Revision) and 6910 (owned base) are installed privately. Observed layout is
`Deus Ex/Revision/System`, with `Revision.u`, and `RevisionUser.ini` selects
`Revision.RevJCDentonMale`. Upstream NATIVES.md mentions a Revision script audit;
that is not proof of this installed build running on iOS. Its extra gameplay
mode directories and native dependencies require verification on actual files.

The app requires a prepared `Documents/DXEngine/Revision/Revision.ini` and
`User.ini`, plus `Documents/DeusEx/Revision/System/Revision.u`. Missing Revision
is an explicit error, never an automatic vanilla launch. The preparer below
rebases the actual installed INI Paths from its original System directory to
DXEngine's base `DeusEx/System` while preserving package order and class names.
It isolates saves/cache and refuses to overwrite an existing user profile.
Run only after the complete private game tree is staged; do not invent INIs.

```sh
python3 ports/ios/prepare_revision.py \
  --game-root /private/staging/Documents/DeusEx --original-music
```

Observed source defaults are `RevisionDefault.ini` and `RevisionDefUser.ini`.
The preparer prefers existing `Revision.ini` / `RevisionUser.ini`, otherwise
those defaults. Optional explicit arguments can override selection. The complete
ordered twelve-path list and OggPath rebasing have regression tests. Base data
and Revision imports were checked on Legion. A Windows diagnostic reached
Liberty Island through normal Revision new-game flow, with HUD and pistol input.
That diagnostic explicitly disabled custom Ogg playback and used original tracker
music. The next build provides explicit original-tracker-only capability:
prepare with `--original-music`, which alters the copied User.ini only. iOS
rejects a profile still selecting custom soundtracks. Custom-track availability
returns false; unexpected custom playback requests fail clearly rather than
claiming success. Full Ogg playback remains unsupported. This is not iOS validation.
See `VALIDATION.md` for evidence and `REVISION-COMPATIBILITY.md` for native risks.

## First milestone and deliberate limits

* SDL3/UIKit application entry, iPhone/iPad landscape app bundle.
* Existing CPU software renderer, displayed by SDL's Metal renderer. The
  existing GLES path asks for ES 3.2; iOS only supports ES 3.0. MoltenVK remains
  a later acceleration path, not a dependency of this first milestone.
* Render scale 0.5 for bring-up. No performance or sustained thermals claim.
* Gamepad bindings use the existing SDL gamepad path. Touch controls are **not
  implemented** yet; do not describe this as touch-playable.
* `Documents/DeusEx/` for privately imported original game files, and separate
  `Documents/DXEngine/` for engine settings/logs/screenshots. Exposed through
  Files/Finder file sharing, without embedding game data in the application.
* dyld executable-path lookup replaces Linux `/proc/self/exe` on Apple hosts.
* No in-process RELAUNCH/session reset yet: the bring-up logs the unsupported
  command; quit/reopen instead. Pause/resume, audio interruptions, rotation,
  low-memory handling, and save persistence need actual device testing.

## Required data

Use an owned **Deus Ex 1112fm** installation. Copy its installation contents
into `Documents/DeusEx`, preserving `System`, `Maps`, `Textures`, `Sounds`, and
`Music`. Engine package/version detection remains upstream's responsibility.
No game binaries, textures, maps, or music are included in this repository or
resource pack. A Steam download is a private input, not permission to publish
the downloaded assets. Missing/incorrect game data is an expected startup
error, not a reason to generate fake content.

## Build on macOS with Xcode

Prerequisites: Xcode's iPhoneOS SDK, CMake, git, Python 3. No downloaded Apple
SDK or non-Apple macOS VM is required or used. This Linux development workspace
cannot validate the Apple compilation/link step.

```sh
ports/ios/build.sh
```

The script pins SDL 3.2.30 (`f5e5f6588921eed3d7d048ce43d9eb1ff0da0ffc`), builds
static SDL and OpenAL Soft, and creates an unsigned arm64 device app for iOS
15+. The host Python resource packer avoids running a cross-compiled zipdir.
The IPA packager rejects host/simulator builds and missing engine resources.
Expected result after a successful Apple build:
`dist/DXEngine-iOS-bringup-unsigned.ipa`. Signing/installing is separate; use an
authorized sideload signer. An unsigned IPA is not immediately installable.
The script completed on standard macos-15-intel with Xcode 16.4.
A successful Apple build is not a device gameplay or performance test.

Do not automatically launch/retry hosted CI. Run portable checks first, then
use one intentional macOS compilation job, saving its log and dependencies
for incremental fixes. The ios-bringup workflow is manual-dispatch only. Upstream multi-port CI is
restricted to its upstream repository; this fork does not run it on pull
requests. The manual job uploads internal test artifacts, not public releases.

## Licensing before distribution

DXEngine and Surreal Engine use zlib licenses; retain all notices in
`LICENSE.md`. SDL uses zlib. OpenAL Soft is LGPL and statically linked for this
bring-up: distributing a binary requires corresponding source, notices, and
relinkable application objects or another compliant relinking arrangement.
**Do not publish the IPA until these materials are prepared.** Upstream
third-party notices also apply. Original Deus Ex assets must stay outside
public source, releases, and CI artifacts.

## Portable checks (no macOS runner)

```sh
g++ -std=c++20 -Wall -Wextra -Werror -I. tests/ios/sandbox_paths.cpp -o /tmp/dxe-path-test
/tmp/dxe-path-test
python3 -m unittest discover -s tests/ios -p 'test_*.py' -v
bash -n ports/ios/build.sh
ports/ios/zipdir.py /tmp/DXEngine.pk3 Resources
```

Tests use synthetic fixture headers only, never fake game/app deliverables.
Native Linux configure/compile catches shared-source regressions but is not
proof that Objective-C++, UIKit, Apple audio, or an iOS app works.

## Next verification gates

1. Compile/link on an actual iOS SDK, including SDL, OpenAL, SIMD and C++20.
2. Verify correct arm64 device Mach-O, required libraries/resources, bundle
   metadata, and license/relink materials. Produce direct `.ipa`, not a ZIP
   wrapper around it.
3. Install through the user's signer and launch first without assets, then
   with their Steam data; inspect `Documents/DXEngine/startup.log`.
4. Reach Revision's menu/first level using a gamepad, save/load, and resume from
   background. Only then add touch controls and pursue renderer performance.

## Optional private app icon

Set `DXE_APP_ICON=/private/path/AppIcon.png` on the Apple build machine to compile
an owner-cleared icon before packaging. The helper uses actool and supplies
LiveContainer-readable loose renditions. It rejects signed apps or existing icon
metadata/catalogs rather than overwriting them. The generated Revision branding
master is deliberately not in this public source repository pending redistribution
review; a build without the optional input remains iconless. Device icon display
and actool integration require Apple validation. No extra CI run is needed solely
for icons.
