"""Compile the owner-approved game icon with Apple's iOS asset compiler."""
import json
from pathlib import Path
import plistlib
import shutil
import struct
import subprocess

SOURCE = None

def compile_icon(work, app, source, minimum_os="16.0"):
    global SOURCE
    SOURCE = Path(source)
    work,app=Path(work),Path(app)
    if (app / "Assets.car").exists():
        raise ValueError("Existing asset catalog: integrate icon into that catalog, do not overwrite")
    data=SOURCE.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack_from('>II',data,16)
    assert width==height and 1024<=width<=8192 and data[25]==2,'Expected an opaque RGB square icon'
    catalog=work/'Assets.xcassets'
    icons=catalog/'AppIcon.appiconset'
    icons.mkdir(parents=True)
    (catalog/'Contents.json').write_text(json.dumps({'info':{'author':'xcode','version':1}}))
    (icons/'Contents.json').write_text(json.dumps({'images':[{'filename':'AppIcon1024.png','idiom':'universal','platform':'ios','size':'1024x1024'}],'info':{'author':'xcode','version':1}}))
    subprocess.run(['sips','--resampleHeightWidth','1024','1024',str(SOURCE),'--out',str(icons/'AppIcon1024.png')],check=True)
    partial=work/'app-icon-info.plist'
    subprocess.run(['xcrun','actool',str(catalog),'--compile',str(app),'--platform','iphoneos',
                    '--minimum-deployment-target',str(minimum_os),'--app-icon','AppIcon','--target-device','iphone',
                    '--target-device','ipad','--output-partial-info-plist',str(partial),
                    '--warnings','--notices','--output-format','human-readable-text'],check=True)
    info=plistlib.loads(partial.read_bytes())
    assert info['CFBundleIcons']['CFBundlePrimaryIcon']['CFBundleIconName']=='AppIcon'
    assert (app/'Assets.car').is_file() and (app/'Assets.car').stat().st_size>0
    # Modern actool keeps some sizes in Assets.car. Supply loose high-density
    # renditions too, for guest-container icon readers that inspect PNG files.
    for pixels,name in [(120,'AppIcon60x60@2x.png'),(180,'AppIcon60x60@3x.png'),(152,'AppIcon76x76@2x~ipad.png'),(167,'AppIcon83.5x83.5@2x~ipad.png')]:
        if not (app/name).exists():
            subprocess.run(['sips','--resampleHeightWidth',str(pixels),str(pixels),str(icons/'AppIcon1024.png'),'--out',str(app/name)],check=True)
    ipad=info['CFBundleIcons~ipad']['CFBundlePrimaryIcon']['CFBundleIconFiles']
    if 'AppIcon83.5x83.5' not in ipad:ipad.append('AppIcon83.5x83.5')
    shutil.copyfile(icons/'AppIcon1024.png',app/'AppIcon.png')
    info['CFBundleIconFile']='AppIcon.png'
    return {key:value for key,value in info.items() if key in ['CFBundleIcons','CFBundleIcons~ipad','CFBundleIconFile']}


if __name__ == '__main__':
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description='Add icon BEFORE app signing and IPA packaging; never use on a signed release')
    parser.add_argument('source')
    parser.add_argument('app')
    parser.add_argument('--minimum-os', default='16.0')
    args = parser.parse_args()
    app = Path(args.app)
    if (app / '_CodeSignature').exists():
        raise SystemExit('Refusing a signed app: integrate before signing')
    info_path = app / 'Info.plist'
    info = plistlib.loads(info_path.read_bytes())
    if info.get('CFBundleIcons') or info.get('CFBundleIconFile'):
        raise SystemExit('App already has icon metadata; do not replace without review')
    with tempfile.TemporaryDirectory(prefix='native-icon-') as work:
        info.update(compile_icon(work, app, args.source, args.minimum_os))
    info_path.write_bytes(plistlib.dumps(info))
    print('Icon catalog and LiveContainer loose icon renditions installed:', app)
