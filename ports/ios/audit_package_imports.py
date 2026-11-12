#!/usr/bin/env python3
"""Read UE1 package import tables; never execute game files.

Reports declared dependencies only, not proof every import executes at runtime.
The input tree must be a private owned installation, never a public asset repo.
"""
import argparse
import json
import pathlib
import struct

class Reader:
    def __init__(self, data): self.data, self.pos = data, 0
    def read(self, count):
        if count < 0 or self.pos + count > len(self.data): raise ValueError('Truncated package')
        data = self.data[self.pos:self.pos + count]
        self.pos += count
        return data
    def index(self):
        b = self.read(1)[0]
        value, negative, more = b & 63, b & 128, b & 64
        shift = 6
        while more:
            if shift >= 32: raise ValueError('Invalid compact index')
            b = self.read(1)[0]
            value |= (b & 127) << shift
            more, shift = b & 128, shift + 7
        return -value if negative else value
    def name(self, version):
        if version >= 64:
            count = self.index()
            if abs(count) > 1024 * 1024: raise ValueError('Oversized package name')
            return self.read(abs(count) * (2 if count < 0 else 1)).decode('utf-16le' if count < 0 else 'latin-1').split('\0')[0]
        out = bytearray()
        while True:
            b = self.read(1)[0]
            if not b: return out.decode('latin-1')
            if len(out) >= 1024 * 1024: raise ValueError('Oversized package name')
            out.append(b)


def imports(data):
    r = Reader(data)
    magic, version, licensee, flags, count, offset, exports, export_offset, icount, ioffset = struct.unpack('<IHHIIIIIII', r.read(36))
    if magic != 0x9E2A83C1 or not 60 <= version < 100: raise ValueError('Not supported UE1 package')
    if count > len(data) // 5 or icount > len(data) // 7: raise ValueError('Invalid table counts')
    r.pos = offset
    names = []
    for _ in range(count):
        names.append(r.name(version)); r.read(4)
    def name(index):
        if not 0 <= index < len(names): raise ValueError('Invalid name index')
        return names[index]
    r.pos = ioffset
    result = set()
    for _ in range(icount):
        class_package, class_name = name(r.index()), name(r.index())
        outer = struct.unpack('<i', r.read(4))[0]
        object_name = name(r.index())
        if outer == 0 and class_name.casefold() == 'package': result.add(object_name)
    return sorted(result, key=str.casefold)


def audit(root):
    root = pathlib.Path(root).resolve(strict=True)
    suffixes = {'.u', '.utx', '.uax', '.umx', '.dx'}
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix.casefold() in suffixes]
    available = {p.stem.casefold() for p in files}
    reports = []
    # Audit current Revision System scripts and menu/first map, not optional modes.
    for path in files:
        rel = path.relative_to(root).as_posix()
        if '/System/' not in '/' + rel and path.name.casefold() not in {'dx.dx', 'index.dx', '01_nyc_unatcoisland.dx'}: continue
        try:
            deps = imports(path.read_bytes())
            reports.append({'file': rel, 'imports': deps, 'not_found_anywhere': [n for n in deps if n.casefold() not in available]})
        except (ValueError, struct.error, UnicodeError) as e:
            reports.append({'file': rel, 'error': str(e)})
    return {'root': str(root), 'package_file_count': len(files), 'reports': reports,
            'caution': 'Presence anywhere may include optional modes outside active INI paths; declared missing imports are not runtime proof.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2))
