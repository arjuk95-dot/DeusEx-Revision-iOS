#pragma once

class UObject;

// EngineI's optional platform-service entry point. DXEngine has no provider.
class NGamePlatform
{
public:
    static void RegisterFunctions();
    static void Instance(UObject*& ReturnValue);
};
