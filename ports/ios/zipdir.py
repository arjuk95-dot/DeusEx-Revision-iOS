#!/usr/bin/env python3
"""Host-side resource packer (never execute an iOS zipdir while cross-building)."""
import pathlib
import sys
import zipfile


def pack(output, source):
    source = pathlib.Path(source).resolve(strict=True)
    output = pathlib.Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Resource symlink is not permitted: {path}")
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(source).as_posix(), (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: zipdir.py OUTPUT SOURCE")
    pack(sys.argv[1], sys.argv[2])
