# Bring-up validation, 2026-11-12

Source baseline: `829498083a0cbf71391a5b2fde830d50d80b6da1`.
Host: Linux x86_64, GCC 14.2, CMake 4.4.4. No Apple SDK available.

Passed:
- Full native Linux `DXEngine` compile and link with desktop display backends
  disabled, including DXCommon, DXWidgets, DXGPU, OpenMPT and zipdir.
- `DXEngine --version` prints the upstream version and features.
- Missing-game smoke check with `--no-launcher --userdir=/tmp/dxe-host-smoke`
  exits 1 with `No UE1 game found in the given folder` (expected).
- C++20 sandbox-path regression test with `-Wall -Wextra -Werror`.
- Six Python tests: correct IPA payload layout; reject host executable,
  simulator bundle, missing resources, symlinks; deterministic resource pack.
- Actual engine Resources packed and archive-integrity checked.
- Build shell syntax and non-Mac fail-fast guard.
- `git diff --check`.

The first host missing-game check without --userdir correctly failed at the
sandbox's read-only home path; rerun with writable state succeeded as above.
The iOS bootstrap explicitly sets the writable Documents path before startup.

Not verified:
- Objective-C++/iOS SDK compilation, linking or Xcode-generated bundle.
- iPhone installation, original game loading, visual/audio/controller behavior.
- Game assets, version detection on actual Steam data, save/load.
- Performance, multitouch, app background/resume or memory pressure.

No Actions jobs started by this work. No IPA exists yet. Synthetic Mach-O
headers in tests validate packager behavior only, not executable validity.

## Revision-first adaptation

User selected Revision as first playable milestone. Added strict Revision
profile selection (no vanilla fallback) and private INI preparation. Ten
Python tests now pass, plus expanded C++ tests rejecting missing Revision
profile/package and checking explicit --ini/--userini arguments. Rebaser tests
cover package precedence, preserved class settings, isolated save/cache paths,
absolute/escaping-path rejection, and no user-profile overwrite. A first test
expected `../System/*.u` but normalization correctly emits equivalent `*.u`;
the expectation was corrected, preserving package search meaning.

Actual installation configuration has not yet been validated. Download staging
reported Revision.u and RevisionUser.ini's Revision.RevJCDentonMale class; these
observations do not prove complete assets or runtime compatibility.

## Verified staged configuration follow-up

Twelve Python tests pass, now including the observed twelve-entry Revision
package-path order, OggPath relocation, and RevisionDefault.ini/RevisionDefUser.ini
selection. Expanded C++ launch tests still pass. Incremental native Linux engine
rebuild/link and --version pass after adding package-qualified missing-native
errors. No actual game startup or iOS SDK validation is implied. See
REVISION-COMPATIBILITY.md for the staged data and native-runtime audit findings.

## Actual dependency audit

Fifteen portable Python tests pass including UE1 import-table fixtures, invalid
headers/truncated tables and compact-index decoding. Matching read-only parser
ran against private installed Revision: 68 direct System .u + four map variants,
zero parser errors. Found absent imported base packages; see compatibility report
for exact lists and source-code proof that Core is required at engine startup.

## Owned base restored / host window harness

Asset worker verified Steam app6910 StateFlags4/build251801,
754,793,921 bytes. DeusEx.exe SHA1 matches supported Steam1112fm:
af951ddd35b38e8d9cc8501b8a50a02a3ab6cae7. All ten previously absent packages
are now present. Exact-precedence Revision startup closure is 84 files,
1,394,014,690 bytes with zero missing imports/parser errors; its private
transfer was requested, not yet verified locally.

SDL3 release-3.2.30 built locally with dummy video for bounded host diagnostics.
DXEngine rebuilt with its SDL3 backend. SDL-backed startup reaches the expected
missing-game check without a display initialization error. This verifies the
host harness only, not Revision gameplay, Metal or iOS.

## Windows Revision startup and first runtime fix

Private Library transfer was blocked before upload by helper capability discovery;
no game files were uploaded. Used existing MSVC/CMake/Ninja/Windows SDK on Legion
instead. Upstream 8294980 built unchanged (696 steps), then private copied INIs
launched Revision with software rendering and an eight-second test timeline.

Run 1 reached Revision game/player/mission/UI-root initialization, then stopped
at GamePlatform.Instance from RevJCDentonMale.UpdateRichPresence. Actual EngineI
script documents native 1350 returning a provider or None; Revision's normal
callers guard None. Added only that native returning None, no service identity,
achievement success, or other fake capabilities. Run 2 passed that error and
stopped at DXOgg.GetNextOggFileIntro in custom soundtrack setup. No menu screenshot
or iOS success is claimed. Original data/configs were untouched.

Linux full rebuild passes; direct registered-handler test invokes index1350
and verifies None on repeated calls. Other platform natives were not
fabricated. DXOgg requires its own implementation/explicit capability handling;
engine -nosound does not skip Revision's music-setup script.

## Bounded diagnostic rendered Revision UI

A separate Windows-only diagnostic run registered explicitly env-gated DXOgg
handlers that disable custom-track playback and report custom tracks unavailable.
Its disposable profile selected Revision's original soundtrack mode. This is
not a production DXOgg implementation: normal startup without the diagnostic
flag still stops at unsupported Ogg natives.

The eight-second timeline exited 0 without timeout. A captured screenshot showed
the EIDOS splash with Revision's `Update complete, new settings enabled.` notice
and OK button. Log reached the Revision mission state machine and `Playing vanilla
ambient!`. This verifies rendered Revision UI, not menu interaction, gameplay,
custom Ogg audio, or iOS. Original game files were not modified. Further menu and
first-scene testing is pending.

A subsequent 110-second diagnostic run also exited 0, with screenshots at 30 and
75 seconds. The latter showed Revision's logo and cinematic background, without
the prior settings modal. This establishes sustained startup rendering only.
Computer Use app approval timed out before screenshot/input access; no menu or
gameplay input was sent. The diagnostic source remained opt-in and original data
untouched. Interactive testing requires the supported app-access approval.

## Approved interactive menu test

App access succeeded on retry. Supported desktop input opened Revision's actual
menu with Escape, navigated New Game and difficulty to character/skills setup,
and activated Start Game using Alt+S. Logs verified travel to 00_Intro with
Revision.RevJCDentonMale and RevisionMission.RevisionMissionIntro. LOADING was
rendered; the 110-second test exited 0 without a runtime error. First playable
scene was not yet verified. Custom Ogg remained explicitly disabled in this
Windows diagnostic, not fixed or silently claimed supported.

## First Revision playable scene reached on Windows diagnostic

Approved interaction followed normal New Game, difficulty and character setup,
then the full Revision intro (animated characters, dialogue/subtitles and Paris
scene). It transitioned normally to Liberty Island, New York. Supported UI
inspection verified dock/Statue world rendering, HUD/inventory, and pressing 1
equipped a visible pistol with six-round ammo HUD. Movement displacement was not
sufficiently observed to claim movement validation. The 290-second timeline exited
0 without watchdog termination. Engine screenshot Shot0007.bmp and run6-stderr.log
remain privately on Legion. A repeated nonfatal LaunchSystem lookup warning remains.

This is actual Revision flow, not a vanilla-map substitute, but still Windows
software rendering with diagnostic custom-Ogg-disabled/original tracker music.
It does not validate iOS, full gameplay, custom soundtrack, or all native APIs.

Remote iOS build remains blocked on separate repository creation: connected
GitHub actions expose no repository-create/fork operation; arjuk95-dot has only
BCD/FNV repositories, deliberately not reused. Latest Legion browser inventory
shows Edge/Chrome extension, not the user-preferred in-app browser. No Apple
execution environment is connected. No GitHub runner time has been spent.

## First Apple build result

Run 43220750723 on standard macos-15-intel/Xcode 16.4 built and installed
SDL3 for arm64 iPhoneOS successfully. Engine configure then failed to locate
SDL3Config.cmake even though the installation log showed it present. iOS package
rooting excluded the external target dependency prefix. Fixed iOS lookup to require
an explicit SDL3_DIR and search that path without SDK rerooting or host fallback.
A synthetic CMake package test with root-only lookup verifies the search pattern;
actual Apple engine compile remains pending. Cache save is now independent of
engine success, retaining successfully installed SDL after later build failures.

Run 43222788285 passed the SDL discovery fix and reached Apple engine compilation.
It stopped at Exception.cpp's explicit unsupported-target guard. Extended the
existing execinfo/backtrace implementation to Apple; Apple-format symbol lines
are retained verbatim for symbolication rather than assuming glibc formatting.
The successful target SDL dependency was cached despite engine failure. No IPA
exists from this run; the next Apple compile must validate remaining sources.

Run 43252050540 compiled all sources and reached final arm64 Apple link. It
failed only because SDL_main.h's main macro renamed GameApp::main in MainIOS.mm.
Moved SDL's entrypoint include below the engine bootstrap helper and left a small
main wrapper afterward. A regression test checks declaration/call ordering so
SDL's macro cannot affect the engine's main method again. Actual Apple relink
is pending; no IPA produced by this run. SDL dependency cache was restored.
