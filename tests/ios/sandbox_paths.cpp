#include "ports/ios/SandboxPaths.h"
#include <cassert>
#include "ports/ios/RevisionLaunch.h"
#include <fstream>
#include <chrono>
int main()
{
    const auto p = IOSPaths::FromDocuments("/private/App Container/Documents");
    assert(p.game == "/private/App Container/Documents/DeusEx");
    assert(p.state == "/private/App Container/Documents/DXEngine");
    assert(p.game != p.state);
    const auto temp = std::filesystem::temp_directory_path() / ("dx-revision-test-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    const auto revisionPaths = IOSPaths::FromDocuments(temp);
    bool missingRejected = false;
    try { RevisionLaunch::FromSandbox(revisionPaths); }
    catch (const std::runtime_error&) { missingRejected = true; }
    assert(missingRejected);
    std::filesystem::create_directories(revisionPaths.state / "Revision");
    std::filesystem::create_directories(revisionPaths.game / "Revision/System");
    std::ofstream(revisionPaths.state / "Revision/Revision.ini") << "fixture";
    std::ofstream(revisionPaths.state / "Revision/User.ini") << "fixture";
    missingRejected = false;
    try { RevisionLaunch::FromSandbox(revisionPaths); }
    catch (const std::runtime_error&) { missingRejected = true; }
    assert(missingRejected); // Config files alone must not boot vanilla.
    std::ofstream(revisionPaths.game / "Revision/System/Revision.u") << "fixture";
    const auto profile = RevisionLaunch::FromSandbox(revisionPaths);
    const auto args = profile.Arguments(revisionPaths);
    assert(args.size() == 5);
    assert(args[2] == "--ini=" + profile.systemIni.string());
    assert(args[3] == "--userini=" + profile.userIni.string());
    std::filesystem::remove_all(temp);
    for (const char* bad : {"", "Documents"})
    {
        bool rejected = false;
        try { IOSPaths::FromDocuments(bad); }
        catch (const std::invalid_argument&) { rejected = true; }
        assert(rejected);
    }
}
