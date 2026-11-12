import importlib.util
import pathlib
import plistlib
import struct
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'ports/ios' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

pack = load('package_ipa').package
resources = load('zipdir').pack

class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.app = self.root / 'DXEngine.app'
        self.app.mkdir()
        self.info = {'CFBundleExecutable': 'DXEngine', 'CFBundleSupportedPlatforms': ['iPhoneOS']}
        self.write_info()
        # Synthetic fixture only, not a runnable app or user deliverable.
        (self.app / 'DXEngine').write_bytes(struct.pack('<IIII', 0xFEEDFACF, 0x0100000C, 0, 2))
        (self.app / 'DXEngine.pk3').write_bytes(b'fixture')
        self.output = self.root / 'test.ipa'

    def write_info(self):
        (self.app / 'Info.plist').write_bytes(plistlib.dumps(self.info))

    def test_payload(self):
        pack(self.app, self.output)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.testzip(), None)
            self.assertIn('Payload/DXEngine.app/DXEngine.pk3', z.namelist())

    def test_host_binary_rejected(self):
        (self.app / 'DXEngine').write_bytes(b'\x7fELF' + bytes(12))
        with self.assertRaises(ValueError): pack(self.app, self.output)

    def test_simulator_rejected(self):
        self.info['CFBundleSupportedPlatforms'] = ['iPhoneSimulator']
        self.write_info()
        with self.assertRaises(ValueError): pack(self.app, self.output)

    def test_missing_resources_rejected(self):
        (self.app / 'DXEngine.pk3').unlink()
        with self.assertRaises(ValueError): pack(self.app, self.output)

    def test_symlink_rejected(self):
        (self.app / 'link').symlink_to('/tmp')
        with self.assertRaises(ValueError): pack(self.app, self.output)

    def test_resource_archive(self):
        src = self.root / 'resources'
        (src / 'fonts').mkdir(parents=True)
        (src / 'fonts/name.ttf').write_bytes(b'font fixture')
        resources(self.output, src)
        first = self.output.read_bytes()
        resources(self.output, src)
        self.assertEqual(first, self.output.read_bytes())
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.read('fonts/name.ttf'), b'font fixture')

if __name__ == '__main__': unittest.main()
