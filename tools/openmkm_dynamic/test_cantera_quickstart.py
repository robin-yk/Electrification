"""Fast execution-management tests; no chemistry is launched."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from cantera_quickstart import digest, supervise

class QuickstartTests(unittest.TestCase):
    def test_timeout_interrupts_child(self):
        with tempfile.TemporaryFile(mode='w+') as log:
            result=supervise([sys.executable,'-c','import time; time.sleep(30)'],os.environ.copy(),log,.1)
        self.assertEqual(result['outcome'],'timeout')
        self.assertLess(result['wall_s'],3)

    def test_success(self):
        with tempfile.TemporaryFile(mode='w+') as log:
            result=supervise([sys.executable,'-c','print("ok")'],os.environ.copy(),log,3)
        self.assertEqual(result['outcome'],'completed')

    def test_digest_detects_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'result.json'
            path.write_text('1'); original=digest(path)
            path.write_text('2')
            self.assertNotEqual(original,digest(path))

if __name__=='__main__':
    unittest.main()
