import unittest
from run_cstr_case import periodic_gate


class PeriodicGateTests(unittest.TestCase):
    def test_default_preserves_boundary_only_policy(self):
        p = {"min_cycles": 20, "cycle_tolerance": 1e-8}
        self.assertFalse(periodic_gate(19, 1e-10, float("inf"), 0, p)[1])
        self.assertTrue(periodic_gate(20, 1e-10, float("inf"), 0, p)[1])

    def test_output_drift_blocks_false_boundary_plateau(self):
        p = {"min_cycles": 3, "cycle_tolerance": 1e-8,
             "cycle_output_tolerance": 1e-8, "stable_cycles_required": 3}
        self.assertEqual(periodic_gate(5, 1e-10, 1e-3, 2, p), (0, False))
        streak, done = periodic_gate(5, 1e-10, 1e-10, 0, p)
        self.assertEqual((streak, done), (1, False))
        streak, done = periodic_gate(6, 1e-10, 1e-10, streak, p)
        self.assertEqual((streak, done), (2, False))
        self.assertEqual(periodic_gate(7, 1e-10, 1e-10, streak, p), (3, True))

    def test_nonfinite_residual_never_passes(self):
        p = {"min_cycles": 3, "cycle_tolerance": 1e-8,
             "cycle_output_tolerance": 1e-8, "stable_cycles_required": 3}
        self.assertEqual(periodic_gate(5, float("nan"), 0, 2, p), (0, False))


if __name__ == "__main__":
    unittest.main()
