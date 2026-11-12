#!/usr/bin/env bash
# iOS bring-up only. Run on a Mac with Xcode; never starts CI implicitly.
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
[[ "$(uname -s)" == Darwin ]] || { echo "Requires macOS + Xcode's iOS SDK" >&2; exit 1; }
xcrun --sdk iphoneos --show-sdk-path >/dev/null
command -v cmake >/dev/null
command -v python3 >/dev/null
sdl_sha=f5e5f6588921eed3d7d048ce43d9eb1ff0da0ffc # SDL release-3.2.30
prefix="$root/.ios-deps"
if [[ ! -d "$prefix/SDL/.git" ]]; then
    mkdir -p "$prefix"
    git clone --branch release-3.2.30 --depth 1 https://github.com/libsdl-org/SDL.git "$prefix/SDL"
fi
[[ "$(git -C "$prefix/SDL" rev-parse HEAD)" == "$sdl_sha" ]] || { echo 'SDL pin mismatch' >&2; exit 1; }
common=(-G Xcode -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_SYSROOT=iphoneos
    -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED=NO)
if [[ ! -f "$prefix/install/lib/cmake/SDL3/SDL3Config.cmake" ]]; then
cmake -S "$prefix/SDL" -B "$root/build-ios-sdl" "${common[@]}" \
    -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TESTS=OFF -DSDL_TEST_LIBRARY=OFF -DSDL_VULKAN=OFF \
    -DCMAKE_INSTALL_PREFIX="$prefix/install"
cmake --build "$root/build-ios-sdl" --config Release --target install --parallel "${JOBS:-4}"
fi
cmake -S "$root" -B "$root/build-ios" "${common[@]}" \
    -DCMAKE_PREFIX_PATH="$prefix/install" -DSDL3_DIR="$prefix/install/lib/cmake/SDL3" \
    -DZIPDIR_EXECUTABLE="$root/ports/ios/zipdir.py"
cmake --build "$root/build-ios" --config Release --target DXEngine --parallel "${JOBS:-4}"
app="$root/build-ios/Release-iphoneos/DXEngine.app"
mkdir -p "$app/Licenses"
cp "$root/LICENSE.md" "$app/Licenses/DXEngine-and-third-parties.md"
cp "$root/Thirdparty/openal-soft/COPYING" "$app/Licenses/OpenAL-Soft.txt"
cp "$prefix/SDL/LICENSE.txt" "$app/Licenses/SDL3.txt"
python3 "$root/ports/ios/package_ipa.py" "$app" \
    "$root/dist/DXEngine-iOS-bringup-unsigned.ipa"
