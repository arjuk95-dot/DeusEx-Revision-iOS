#!/usr/bin/env python3
"""Prepare private Revision INIs for an imported iOS Documents/DeusEx tree.

No game data is downloaded, published, executed, or silently replaced. Paths
remain relative to DeusEx/System so iOS container UUID changes are harmless.
"""
import argparse
import ntpath
import os
import pathlib
import re


def decode_game_text(raw):
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16').split('\0', 1)[0]
    # The game's byte-oriented INIs, as DXEngine IniFile::ReadGameText.
    return raw.decode('latin-1').split('\0', 1)[0]


def rewrite(text, game_root, original_system):
    game_root = pathlib.Path(game_root).resolve(strict=True)
    original_system = pathlib.Path(original_system).resolve(strict=True)
    original_system.relative_to(game_root)  # Reject an unrelated installation.
    engine_system = game_root / 'System'
    section = ''
    result = []
    paths = 0
    save_seen = cache_seen = False
    for line in text.splitlines():
        match = re.match(r'^\s*\[([^]]+)\]', line)
        if match:
            if section == 'core.system':
                if not save_seen: result.append('SavePath=../../DXEngine/Revision/Save')
                if not cache_seen: result.append('CachePath=../../DXEngine/Revision/Cache')
            section = match[1].casefold()
        key, separator, value = line.partition('=')
        if section == 'core.system' and separator:
            if key.strip().casefold() in ('paths', 'oggpath'):
                value = value.strip().replace('\\', '/')
                if not value or ntpath.isabs(value) or ntpath.splitdrive(value)[0]:
                    raise ValueError('Absolute/empty package path requires explicit review: ' + value)
                target = (original_system / value).resolve(strict=False)
                target.relative_to(game_root)  # Do not escape imported game tree.
                value = pathlib.Path(os.path.relpath(target, engine_system)).as_posix()
                line = key + '=' + value
                if key.strip().casefold() == 'paths': paths += 1
            elif key.strip().casefold() == 'savepath':
                line = key + '=../../DXEngine/Revision/Save'
                save_seen = True
            elif key.strip().casefold() == 'cachepath':
                line = key + '=../../DXEngine/Revision/Cache'
                cache_seen = True
        result.append(line)
    if section == 'core.system':
        if not save_seen: result.append('SavePath=../../DXEngine/Revision/Save')
        if not cache_seen: result.append('CachePath=../../DXEngine/Revision/Cache')
    if not paths:
        raise ValueError('Revision INI has no Core.System Paths; refusing vanilla fallback')
    return '\n'.join(result) + '\n'


def original_music_profile(text):
    """Alter only the private copy. Real Revision fallback, not missing files."""
    section = 'revision.revjcdentonmale'
    keys = ('bUseRevisionSoundtrack', 'bUsePS2Soundtrack', 'bUseRevisionVer2Soundtrack')
    output = []
    active = found = False
    for line in text.splitlines():
        match = re.match(r'^\s*\[([^]]+)\]', line)
        if match:
            active = match[1].casefold() == section
            output.append(line)
            if active:
                found = True
                output.extend(key + '=False' for key in keys)
            continue
        key, separator, _ = line.partition('=')
        if active and separator and key.strip().casefold() in {k.casefold() for k in keys}:
            continue
        output.append(line)
    if not found:
        output.extend(['[Revision.RevJCDentonMale]'] + [key + '=False' for key in keys])
    return '\n'.join(output) + '\n'


def choose_file(folder, candidates):
    for name in candidates:
        path = folder / name
        if path.is_file(): return path
    raise FileNotFoundError('Missing Revision configuration: ' + ', '.join(candidates))


def prepare(game_root, original_system=None, ini=None, userini=None, original_music=False):
    root = pathlib.Path(game_root).resolve(strict=True)
    original_system = pathlib.Path(original_system) if original_system else root / 'Revision/System'
    ini = pathlib.Path(ini) if ini else choose_file(original_system, ('Revision.ini', 'RevisionDefault.ini'))
    userini = pathlib.Path(userini) if userini else choose_file(original_system, ('RevisionUser.ini', 'RevisionDefUser.ini'))
    if not (root / 'System/DeusEx.exe').is_file():
        raise ValueError('Owned base Deus Ex System/DeusEx.exe is required for version detection')
    if not (root / 'Revision/System/Revision.u').is_file():
        raise ValueError('Revision/System/Revision.u is required')
    system_text = rewrite(decode_game_text(pathlib.Path(ini).read_bytes()), root, original_system)
    user_text = decode_game_text(pathlib.Path(userini).read_bytes())
    if not re.search(r'^\s*Class\s*=\s*Revision\.', user_text, re.M | re.I):
        raise ValueError('User INI does not select a Revision player class; review the actual installed profile')
    if original_music:
        user_text = original_music_profile(user_text)
    output = root.parent / 'DXEngine/Revision'
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ('Revision.ini', 'User.ini')):
        raise FileExistsError('Prepared profile already exists; do not overwrite user settings')
    # Preserve byte-oriented source encoding; non-Latin text originated as UTF-16.
    (output / 'Revision.ini').write_bytes(system_text.encode('utf-16'))
    (output / 'User.ini').write_bytes(user_text.encode('utf-16'))
    for name in ('Save', 'Cache'):
        (output / name).mkdir(exist_ok=True)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-root', required=True)
    parser.add_argument('--original-system')
    parser.add_argument('--ini')
    parser.add_argument('--userini')
    parser.add_argument('--original-music', action='store_true',
                        help='Use original tracker music; custom Ogg is not supported by the iOS bring-up')
    args = parser.parse_args()
    print(prepare(args.game_root, args.original_system, args.ini, args.userini, args.original_music))
