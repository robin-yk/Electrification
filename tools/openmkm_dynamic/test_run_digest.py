import unittest
from run_digest import cache_key


class CacheTests(unittest.TestCase):
    def test_key_is_order_independent_and_sensitive_to_physics_and_tolerance(self):
        a = cache_key({"tau": 0.01, "closure": "const-pressure"}, "m", "s", {"rtol": 1e-8})
        self.assertEqual(a, cache_key({"closure": "const-pressure", "tau": 0.01}, "m", "s", {"rtol": 1e-8}))
        self.assertNotEqual(a, cache_key({"tau": 0.02, "closure": "const-pressure"}, "m", "s", {"rtol": 1e-8}))
        self.assertNotEqual(a, cache_key({"tau": 0.01, "closure": "const-pressure"}, "m", "s", {"rtol": 1e-7}))


if __name__ == "__main__":
    unittest.main()
