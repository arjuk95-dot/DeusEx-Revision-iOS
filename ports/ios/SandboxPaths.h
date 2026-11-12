// iOS port addition. Kept independent of UIKit for portable regression tests.
#pragma once
#include <filesystem>
#include <stdexcept>
struct IOSPaths
{
    std::filesystem::path game;
    std::filesystem::path state;
    static IOSPaths FromDocuments(const std::filesystem::path& documents)
    {
        if (documents.empty() || !documents.is_absolute())
            throw std::invalid_argument("Documents must be an absolute sandbox path");
        return {documents / "DeusEx", documents / "DXEngine"};
    }
};
