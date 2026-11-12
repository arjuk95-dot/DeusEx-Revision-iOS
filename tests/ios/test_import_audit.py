import importlib.util
import pathlib
import struct
import unittest
spec = importlib.util.spec_from_file_location('audit', pathlib.Path(__file__).resolve().parents[2] / 'ports/ios/audit_package_imports.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class ImportAuditTests(unittest.TestCase):
    def test_import_table(self):
        names = ['Core', 'Package', 'Engine']
        table = b''.join(bytes([len(n)+1]) + n.encode() + b'\0' + bytes(4) for n in names)
        entry = bytes([0, 1]) + struct.pack('<i', 0) + bytes([2])
        header = struct.pack('<IHHIIIIIII', 0x9E2A83C1, 69, 0, 0, 3, 36, 0, 0, 1, 36+len(table))
        self.assertEqual(audit.imports(header+table+entry), ['Engine'])
        with self.assertRaises(ValueError): audit.imports(header+table+entry[:-1])
    def test_invalid_magic(self):
        with self.assertRaises(ValueError): audit.imports(bytes(36))
    def test_signed_compact_index(self):
        self.assertEqual(audit.Reader(bytes([0x85])).index(), -5)
        self.assertEqual(audit.Reader(bytes([0x40, 1])).index(), 64)

if __name__ == '__main__': unittest.main()
