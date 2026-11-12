#include "Precomp.h"
#include "NRevisionOgg.h"
#include "VM/NativeFunc.h"
#include "Utils/Logger.h"
#include <cstdlib>

namespace
{
void EmptyTrack(UObject*, std::string& value) { value.clear(); }
void Position(UObject*, float& value) { value = 0.0f; }
void Stop(UObject*) {} // No custom stream exists; do not stop tracker music.
void Available(const std::string&, const std::string&, BitfieldBool& value)
{
    // Capability check, deliberately NOT an assertion about file existence.
    value = false;
}
void Unsupported(UObject*, const std::string&, const std::string&, int, uint8_t)
{
    throw std::runtime_error("Custom Ogg playback is unavailable in original-music mode; select Revision's original soundtrack");
}
void UnsupportedVolume(UObject* self, const std::string& intro, const std::string& loop,
                       int position, uint8_t transition, float)
{
    Unsupported(self, intro, loop, position, transition);
}
}

void NRevisionOgg::RegisterFunctions()
{
    const char* mode = std::getenv("DXE_REVISION_ORIGINAL_MUSIC");
    if (!mode || std::string(mode) != "1") return;
    LogMessage("Revision: ORIGINAL TRACKER MUSIC ONLY; custom Ogg unavailable (not a missing-file check)");
    RegisterVMNativeFunc_1("DXOgg", "GetNextOggFileIntro", &EmptyTrack, 0);
    RegisterVMNativeFunc_1("DXOgg", "GetNextOggFileLoop", &EmptyTrack, 0);
    RegisterVMNativeFunc_1("DXOgg", "GetCurrentSongPosition", &Position, 0);
    RegisterVMNativeFunc_0("DXOgg", "StopPlayback", &Stop, 0);
    RegisterVMNativeFunc_3("DXOgg", "CheckFiles", &Available, 0);
    // Unexpected custom playback must fail clearly, not silently succeed.
    RegisterVMNativeFunc_4("DXOgg", "SetCurrentOgg", &Unsupported, 0);
    RegisterVMNativeFunc_5("DXOgg", "SetCurrentOggWithVolume", &UnsupportedVolume, 0);
}
