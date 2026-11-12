// iOS bootstrap added for the Arjuk port; not part of upstream DXEngine.
#import <Foundation/Foundation.h>
#include <SDL3/SDL.h>
#include "Precomp.h"
#include "GameApp.h"
#include "LauncherSettings.h"
#include "Utils/File.h"
#include "SandboxPaths.h"
#include "RevisionLaunch.h"
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
            const auto revision = RevisionLaunch::FromSandbox(paths);
            SDL_SetHint(SDL_HINT_RENDER_DRIVER, "metal");
            SDL_SetHint(SDL_HINT_ORIENTATIONS, "LandscapeLeft LandscapeRight");
            setenv("DXE_DISPLAY_BACKEND", "SDL3", 1);
            // First milestone: CPU rasterizer + SDL's Metal presentation.
            // Do not request desktop GL / ES 3.2 or Vulkan without MoltenVK.
            auto& settings = LauncherSettings::Get();
            settings.RenderDevice.Type = RenderDeviceType::Software;
            settings.RenderDevice.TypeNamed = true;
            settings.Performance.RenderScale = 0.5f;
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
