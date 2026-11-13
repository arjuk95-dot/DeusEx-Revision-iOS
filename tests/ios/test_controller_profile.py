import importlib.util
import pathlib
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('controller',pathlib.Path(__file__).resolve().parents[2]/'ports/ios/controller_profile.py')
controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
class ControllerTests(unittest.TestCase):
    def fixture(self):
        return '[Other]\nJoy1=Untouched\n[Engine.Input]\n'+'\n'.join(k+'=Actual'+k for k in set(controller.SOURCES.values()))+'\nJoy1=Old\nJoyX=Axis astrafe speed=2\n'
    def test_scoped_preserved_idempotent(self):
        result=controller.controller_profile(self.fixture())
        for expected in ('[Other]\nJoy1=Untouched','Joy12=ActualLeftMouse','Joy3=ActualRightMouse','JoyX=Axis astrafe speed=2','Semicolon=ActualSemicolon'): self.assertIn(expected,result)
        self.assertEqual(result,controller.controller_profile(result))
    def test_missing_binding_fails(self):
        with self.assertRaises(ValueError): controller.controller_profile('[Engine.Input]\nLeftMouse=Fire\n')
    def test_copy_preserves_source_and_refuses_existing(self):
        with tempfile.TemporaryDirectory() as folder:
            source=pathlib.Path(folder)/'User.ini';target=pathlib.Path(folder)/'Candidate.ini';original=self.fixture().encode('utf-16');source.write_bytes(original)
            controller.prepare_controller_copy(source,target);self.assertEqual(source.read_bytes(),original)
            self.assertIn('Joy12=ActualLeftMouse',target.read_bytes().decode('utf-16'));candidate=target.read_bytes()
            with self.assertRaises(FileExistsError): controller.prepare_controller_copy(source,target)
            self.assertEqual(target.read_bytes(),candidate)
if __name__=='__main__': unittest.main()
