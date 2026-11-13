"""Prepare an opt-in native SDL gamepad profile copy. Never synthesize keys."""
import re
from pathlib import Path
SOURCES={'Joy1':'LeftMouse','Joy2':'Space','Joy3':'RightMouse','Joy4':'X','Joy5':'MouseWheelUp','Joy6':'MouseWheelDown','Joy7':'I','Joy8':'Escape','Joy9':'Shift','Joy10':'Semicolon','Joy11':'RightMouse','Joy12':'LeftMouse'}
def controller_profile(text):
    lines=text.splitlines();section='';bindings={}
    for line in lines:
        match=re.match(r'^\s*\[([^]]+)\]',line)
        if match: section=match[1].casefold()
        key,sep,value=line.partition('=')
        if section=='engine.input' and sep: bindings[key.strip().casefold()]=value.strip()
    missing=[key for key in SOURCES.values() if not bindings.get(key.casefold())]
    if missing: raise ValueError('Controller action requires verified binding: '+', '.join(sorted(set(missing))))
    mapping={joy:bindings[key.casefold()] for joy,key in SOURCES.items()}
    result=[];active=False
    for line in lines:
        match=re.match(r'^\s*\[([^]]+)\]',line)
        if match:
            active=match[1].casefold()=='engine.input';result.append(line)
            if active: result.extend(k+'='+v for k,v in mapping.items())
            continue
        key,sep,_=line.partition('=')
        if active and sep and key.strip().casefold() in {k.casefold() for k in mapping}: continue
        result.append(line)
    return '\n'.join(result)+'\n'
def prepare_controller_copy(source,destination):
    raw=Path(source).read_bytes()
    encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
    result=controller_profile(raw.decode(encoding))
    with Path(destination).open('xb') as output: output.write(result.encode(encoding))
    return Path(destination)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();print(prepare_controller_copy(a.source,a.destination))
