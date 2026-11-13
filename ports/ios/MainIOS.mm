// iOS bootstrap added for the Arjuk port; not part of upstream DXEngine.
#import <Foundation/Foundation.h>
#include <SDL3/SDL.h>
#include "Precomp.h"
#include "GameApp.h"
#include "LauncherSettings.h"
#include "Utils/File.h"
#include "SandboxPaths.h"
#include "RevisionLaunch.h"
#include "Utils/MobilePresentation.h"
#include "Package/IniFile.h"
#include <cstdio>
#include <exception>

static int RunIOSGame()
{
    @autoreleasepool
    {
        try
        {
            NSURL* documents = [[[NSFileManager defaultManager]
                URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask] firstObject];
            if (!documents) throw std::runtime_error("Documents folder unavailable");
            const auto paths = IOSPaths::FromDocuments(documents.path.UTF8String);
            fs::create_directories(paths.game);
            fs::create_directories(paths.state);
            Directory::setEngineUserDir((paths.state / "Revision").string());
            fs::create_directories(paths.state / "Revision");
            // Logs are available in Files even when no debugger is connected.
            if (!std::freopen((paths.state / "startup.log").c_str(), "a", stderr))
                throw std::runtime_error("Cannot open startup log");
            auto revision = RevisionLaunch::FromSandbox(paths);
            const auto controllerProfile=paths.state / "Revision" / "User.controller-candidate.ini";
            if(!fs::is_regular_file(controllerProfile))
                throw std::runtime_error("Prepare User.controller-candidate.ini with controller_profile.py; this touch test requires verified native gamepad bindings. Original User.ini is preserved.");
            revision.userIni=controllerProfile;
            IniFile userProfile(revision.userIni.string());
            for (const char* key : {"bUseRevisionSoundtrack", "bUsePS2Soundtrack", "bUseRevisionVer2Soundtrack"})
            {
                const auto value = userProfile.GetValue("Revision.RevJCDentonMale", key);
                if (value != "False" && value != "false" && value != "FALSE" && value != "0")
                    throw std::runtime_error("This build uses original tracker music. Prepare the private profile with --original-music before launch.");
            }
            SDL_SetHint(SDL_HINT_TOUCH_MOUSE_EVENTS,"0");
            SDL_SetHint(SDL_HINT_MOUSE_TOUCH_EVENTS,"0");
            SDL_SetHint(SDL_HINT_RENDER_DRIVER, "metal");
            SDL_SetHint(SDL_HINT_ORIENTATIONS, "LandscapeLeft LandscapeRight");
            setenv("DXE_DISPLAY_BACKEND", "SDL3", 1);
            setenv("DXE_REVISION_ORIGINAL_MUSIC", "1", 1);
            std::fprintf(stderr, "Revision: original tracker soundtrack only; custom Ogg unavailable\n");
            // Vulkan rasterizes the scene on the Apple GPU through bundled MoltenVK.
            // Explicit Software preference is retained for recovery, never silently used.
            auto& settings = LauncherSettings::Get();
            settings.Gamepad.Enabled = true;
            const bool software = userProfile.GetValue("DXEngine.iOS", "Renderer") == "Software";
            settings.RenderDevice.Type = software ? RenderDeviceType::Software : RenderDeviceType::Vulkan;
            settings.RenderDevice.CPUDriver = false;
            if (!software)
            {
                NSString* library = [[[NSBundle mainBundle] privateFrameworksPath]
                    stringByAppendingPathComponent:@"MoltenVK.framework/MoltenVK"];
                if (![[NSFileManager defaultManager] fileExistsAtPath:library])
                    throw std::runtime_error("Bundled MoltenVK framework missing; GPU build is incomplete");
                // SDL and volk must load exactly the same Vulkan implementation.
                SDL_SetHint(SDL_HINT_VULKAN_LIBRARY, library.UTF8String);
                setenv("DXE_IOS_VULKAN_LIBRARY", library.UTF8String, 1);
                setenv("DXE_IOS_REQUIRE_GPU", "1", 1);
                std::fprintf(stderr, "iOS renderer: Vulkan via bundled MoltenVK; CPU fallback disabled\n");
            }
            else
            {
                unsetenv("DXE_IOS_REQUIRE_GPU");
                std::fprintf(stderr, "iOS renderer: explicitly selected Software recovery mode\n");
            }
            settings.RenderDevice.TypeNamed = true;
            // Read optional mobile preferences; never rewrite the user's profile.
            const auto scale=userProfile.GetValue("DXEngine.iOS", "RenderScale");
            settings.Performance.RenderScale = MobilePresentation::Number(scale.c_str(), 1.f/3.f, 0.25f, 1.f);
            const auto look=userProfile.GetValue("DXEngine.iOS", "TouchLookGain");
            const float lookGain=MobilePresentation::Number(look.c_str(), 3.f, 0.25f, 8.f);
            setenv("DXE_IOS_TOUCH_LOOK_GAIN", std::to_string(lookGain).c_str(), 1);
            const auto cpu=userProfile.GetValue("DXEngine.iOS", "CPUUpscale");
            setenv("DXE_IOS_CPU_UPSCALE", cpu == "True" || cpu == "1" ? "1" : "0", 1);
            const auto ui=userProfile.GetValue("DXEngine.iOS", "UIMode");
            setenv("DXE_IOS_UI_MODE", ui == "legacy" ? "legacy" : "fit", 1);
            std::fprintf(stderr,"iOS render scale %.3f; touch gain %.2f; UI %s\n",settings.Performance.RenderScale,lookGain,ui == "legacy" ? "legacy" : "fit");
            Array<std::string> args;
            for (const auto& arg : revision.Arguments(paths)) args.push_back(arg);
            GameApp app;
            return app.main(std::move(args));
        }
        catch (const std::exception& e)
        {
            std::fprintf(stderr, "iOS startup: %s\n", e.what());
            SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "DXEngine startup", e.what(), nullptr);
            return 1;
        }
    }
}

// SDL_main.h defines the token `main` as SDL_main on iOS. Keep it below
// all engine declarations and calls so GameApp::main is not renamed too.
#include <SDL3/SDL_main.h>
int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    return RunIOSGame();
}
