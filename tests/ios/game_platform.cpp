#include "Precomp.h"
#include "Native/NGamePlatform.h"
#include "VM/NativeFunc.h"
#include <cassert>

int main()
{
    NGamePlatform::RegisterFunctions();
    assert(NativeFunctions::NativeByIndex.size() > 1350);
    assert(NativeFunctions::NativeByIndex[1350]);
    auto result = ExpressionValue::ObjectValue(reinterpret_cast<UObject*>(1));
    NativeFunctions::NativeByIndex[1350](nullptr, &result);
    assert(result.ToType<UObject*>() == nullptr);
    // Repeated queries must remain unavailable, never manufacture a provider.
    NativeFunctions::NativeByIndex[1350](nullptr, &result);
    assert(result.ToType<UObject*>() == nullptr);
}
