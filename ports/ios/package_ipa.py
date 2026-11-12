#!/usr/bin/env python3
"""Package an actual arm64 iPhone app for user-controlled sideload signing."""
import argparse
import pathlib
import plistlib
import struct
import zipfile


def package(app, output):
    app = pathlib.Path(app).resolve(strict=True)
    if not app.is_dir() or app.suffix != ".app":
        raise ValueError("Expected a built .app directory")
    with (app / "Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    executable = info["CFBundleExecutable"]
    if not executable or pathlib.Path(executable).name != executable:
        raise ValueError("Invalid bundle executable name")
    binary = app / executable
    with binary.open("rb") as stream:
        header = stream.read(16)
    if len(header) != 16:
        raise ValueError("Missing Mach-O header")
    magic, cpu, subtype, filetype = struct.unpack("<IIII", header)
    if magic != 0xFEEDFACF or cpu != 0x0100000C or filetype != 2:
        raise ValueError("Expected thin arm64 Mach-O executable, not host binary")
    if info.get("CFBundleSupportedPlatforms") != ["iPhoneOS"]:
        raise ValueError("Expected iPhoneOS device app, not simulator")
    if not (app / "DXEngine.pk3").is_file():
        raise ValueError("Missing DXEngine.pk3")
    files = sorted(app.rglob("*"))
    if any(p.is_symlink() for p in files):
        raise ValueError("Unexpected symlink in static bring-up bundle")
    output = pathlib.Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            if path.is_file():
                archive.write(path, (pathlib.Path("Payload") / app.name / path.relative_to(app)).as_posix())
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app")
    parser.add_argument("output")
    args = parser.parse_args()
    print(package(args.app, args.output))
