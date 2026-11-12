import importlib.util
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('revision', pathlib.Path(__file__).resolve().parents[2] / 'ports/ios/prepare_revision.py')
revision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(revision)

class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / 'DeusEx'
        self.system = self.root / 'Revision/System'
        self.system.mkdir(parents=True)
        (self.root / 'System').mkdir()

    def test_paths_and_classes_preserved(self):
        source = '[Core.System]\nPaths=..\\System\\*.u\nPaths=..\\..\\System\\*.u\nSavePath=../Save\n[Engine.Engine]\nGameEngine=Revision.RevGameEngine\n'
        result = revision.rewrite(source, self.root, self.system)
        self.assertLess(result.index('Paths=../Revision/System/*.u'), result.index('Paths=*.u'))
        self.assertIn('GameEngine=Revision.RevGameEngine', result)
        self.assertIn('SavePath=../../DXEngine/Revision/Save', result)
        self.assertIn('CachePath=../../DXEngine/Revision/Cache', result)

    def test_observed_revision_default_path_order(self):
        paths = [r'..\Sounds\*.uax', r'..\Textures\*.utx', r'..\Maps\*.dx', r'..\System\*.u',
                 r'..\NewVision\Textures\*.utx', r'..\HDTP\Textures\*.utx', r'..\HDTP\System\*.u',
                 r'..\..\Music\*.umx', r'..\..\Sounds\*.uax', r'..\..\Textures\*.utx',
                 r'..\..\Maps\*.dx', r'..\..\System\*.u']
        text = '[Core.System]\nOggPath=..\\Music\n' + '\n'.join('Paths=' + p for p in paths)
        result = revision.rewrite(text, self.root, self.system)
        actual = [line[6:] for line in result.splitlines() if line.startswith('Paths=')]
        self.assertEqual(actual, ['../Revision/Sounds/*.uax', '../Revision/Textures/*.utx',
            '../Revision/Maps/*.dx', '../Revision/System/*.u', '../Revision/NewVision/Textures/*.utx',
            '../Revision/HDTP/Textures/*.utx', '../Revision/HDTP/System/*.u', '../Music/*.umx',
            '../Sounds/*.uax', '../Textures/*.utx', '../Maps/*.dx', '*.u'])
        self.assertIn('OggPath=../Revision/Music', result)

    def test_observed_default_filenames(self):
        ini = self.system / 'RevisionDefault.ini'
        user = self.system / 'RevisionDefUser.ini'
        ini.write_bytes(b'[Core.System]\nPaths=../System/*.u\n')
        user.write_bytes(b'[DefaultPlayer]\nClass=Revision.RevJCDentonMale\n')
        (self.root / 'System/DeusEx.exe').write_bytes(b'fixture')
        (self.system / 'Revision.u').write_bytes(b'fixture')
        output = revision.prepare(self.root)
        self.assertTrue((output / 'Revision.ini').is_file())
        self.assertTrue((output / 'User.ini').is_file())

    def test_escape_and_absolute_paths_rejected(self):
        for path in ('../../../outside/*.u', 'C:\\game\\*.u', '/game/*.u'):
            with self.assertRaises(ValueError):
                revision.rewrite('[Core.System]\nPaths=' + path, self.root, self.system)

    def test_missing_paths_rejected(self):
        with self.assertRaises(ValueError): revision.rewrite('[Engine.Engine]\n', self.root, self.system)

    def test_profile_preserves_user_and_refuses_overwrite(self):
        (self.root / 'System/DeusEx.exe').write_bytes(b'fixture')
        (self.system / 'Revision.u').write_bytes(b'fixture')
        ini = self.system / 'Revision.ini'
        ini.write_bytes(b'[Core.System]\nPaths=../System/*.u\n')
        user = self.system / 'RevisionUser.ini'
        user.write_bytes(b'[DefaultPlayer]\nClass=Revision.RevJCDentonMale\n')
        output = revision.prepare(self.root, self.system, ini, user)
        self.assertIn('Revision.RevJCDentonMale', revision.decode_game_text((output / 'User.ini').read_bytes()))
        with self.assertRaises(FileExistsError): revision.prepare(self.root, self.system, ini, user)

    def test_original_music_is_explicit_and_scoped(self):
        source = ('[Other]\nbUseRevisionSoundtrack=True\n[Revision.RevJCDentonMale]\n'
                  'bUseRevisionSoundtrack=True\nbUsePS2Soundtrack=True\n'
                  'bUseRevisionVer2Soundtrack=True\nUnrelated=Keep\n')
        result = revision.original_music_profile(source)
        self.assertIn('[Other]\nbUseRevisionSoundtrack=True', result)
        self.assertIn('Unrelated=Keep', result)
        self.assertEqual(result.count('bUseRevisionSoundtrack=False'), 1)
        self.assertIn('bUsePS2Soundtrack=False', result)
        self.assertIn('bUseRevisionVer2Soundtrack=False', result)
        self.assertEqual(revision.original_music_profile(result), result)

    def test_original_music_missing_section_added(self):
        result = revision.original_music_profile('[DefaultPlayer]\nClass=Revision.RevJCDentonMale\n')
        self.assertIn('[Revision.RevJCDentonMale]\nbUseRevisionSoundtrack=False', result)

if __name__ == '__main__': unittest.main()
