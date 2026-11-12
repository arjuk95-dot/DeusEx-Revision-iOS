#include "Precomp.h"
#include "NGamePlatform.h"
#include "VM/NativeFunc.h"
#include "Utils/Logger.h"

void NGamePlatform::RegisterFunctions()
{
    RegisterVMNativeFunc_1("GamePlatform", "Instance", &NGamePlatform::Instance, 1350);
}

void NGamePlatform::Instance(UObject*& ReturnValue)
{
    // EngineI documents Instance as returning a provider or None. Revision's
    // normal startup/menu paths explicitly handle None. We have no Steam (or
    // other platform) provider: do not fabricate identities, achievement
    // success, or stat persistence. Unsupported unguarded calls stay errors.
    ReturnValue = nullptr;
    static bool logged = false;
    if (!logged)
    {
        LogMessage("GamePlatform: no platform provider; Instance returns None");
        logged = true;
    }
}
