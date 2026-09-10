"""Runtime gate regression tests; no mechanism or chemistry."""
import os
import sys
import unittest
from unittest.mock import patch
from cantera_runtime import prepare_runtime, REQUIRED

class RuntimeTests(unittest.TestCase):
    def test_wrong_version_stops_before_import(self):
        with patch("importlib.metadata.version", return_value="3.1.0"):
            with self.assertRaisesRegex(SystemExit, "No calculation started"):
                prepare_runtime()
        self.assertNotIn("cantera", sys.modules)

    def test_settings_are_forced(self):
        with patch.dict(os.environ, {k: "wrong" for k in REQUIRED}):
            with patch("importlib.metadata.version", return_value="3.2.0"):
                result = prepare_runtime()
            self.assertEqual({k: os.environ[k] for k in REQUIRED}, REQUIRED)
            self.assertEqual(result["cantera"], "3.2.0")
        self.assertNotIn("cantera", sys.modules)

if __name__ == "__main__":
    unittest.main()
