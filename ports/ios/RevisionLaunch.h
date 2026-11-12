// Revision-first launch contract for the iOS port, not upstream DXEngine.
#pragma once
#include "SandboxPaths.h"
#include <string>
#include <vector>

struct RevisionLaunch
{
    std::filesystem::path systemIni;
    std::filesystem::path userIni;

    static RevisionLaunch FromSandbox(const IOSPaths& paths)
    {
        // The prepared profile contains Revision's actual class settings and
        // ordered package paths, rebased for the imported sandbox. Never silently
        // boot vanilla Deus Ex when Revision is missing or unprepared.
        RevisionLaunch profile{paths.state / "Revision" / "Revision.ini",
                               paths.state / "Revision" / "User.ini"};
        for (const auto& file : {profile.systemIni, profile.userIni})
            if (!std::filesystem::is_regular_file(file))
                throw std::runtime_error("Revision profile is not prepared: " + file.string());
        if (!std::filesystem::is_regular_file(paths.game / "Revision" / "System" / "Revision.u"))
            throw std::runtime_error("Revision game package is missing; import owned base game and Revision data");
        return profile;
    }

    std::vector<std::string> Arguments(const IOSPaths& paths) const
    {
        return {paths.game.string(), "--userdir=" + (paths.state / "Revision").string(),
                "--ini=" + systemIni.string(), "--userini=" + userIni.string(), "--verbose"};
    }
};
