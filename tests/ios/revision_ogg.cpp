#include "Precomp.h"
#include "Native/NRevisionOgg.h"
#include "VM/NativeFunc.h"
#include <cassert>
#include <cstdlib>

int main()
{
    unsetenv("DXE_REVISION_ORIGINAL_MUSIC");
    NRevisionOgg::RegisterFunctions();
    auto key = std::make_pair(NameString("CheckFiles"), NameString("DXOgg"));
    assert(!NativeFunctions::NativeByName.count(key));
    setenv("DXE_REVISION_ORIGINAL_MUSIC", "1", 1);
    NRevisionOgg::RegisterFunctions();
    assert(NativeFunctions::NativeByName.count(key));
    ExpressionValue check[] = {ExpressionValue::StringValue("existing-intro.ogg"),
        ExpressionValue::StringValue("existing-loop.ogg"), ExpressionValue::BoolValue(true)};
    NativeFunctions::NativeByName.at(key)(nullptr, check);
    assert(!check[2].ToType<bool>());
    for (const char* name : {"GetNextOggFileIntro", "GetNextOggFileLoop"})
    {
        auto value = ExpressionValue::StringValue("stale");
        NativeFunctions::NativeByName.at({name, "DXOgg"})(nullptr, &value);
        assert(value.ToString().empty());
    }
    auto pos = ExpressionValue::FloatValue(99.0f);
    NativeFunctions::NativeByName.at({"GetCurrentSongPosition", "DXOgg"})(nullptr, &pos);
    assert(pos.ToType<float>() == 0.0f);
    NativeFunctions::NativeByName.at({"StopPlayback", "DXOgg"})(nullptr, nullptr);
    ExpressionValue play[] = {ExpressionValue::StringValue("intro.ogg"),
        ExpressionValue::StringValue("loop.ogg"), ExpressionValue::IntValue(0),
        ExpressionValue::ByteValue(0), ExpressionValue::FloatValue(1.0f)};
    for (const char* name : {"SetCurrentOgg", "SetCurrentOggWithVolume"})
    {
        bool rejected = false;
        try { NativeFunctions::NativeByName.at({name, "DXOgg"})(nullptr, play); }
        catch (const std::runtime_error&) { rejected = true; }
        assert(rejected);
    }
}
