import unittest
from types import SimpleNamespace
from run_cjh_tolerance_01 import instrument_factory


class ToleranceAdapterTests(unittest.TestCase):
    def test_default_unchanged(self):
        net = SimpleNamespace(rtol=1e-9, atol=1e-15)
        result, evidence = (object(), net), {}
        self.assertIs(instrument_factory(lambda *a: result, "default", evidence)(None, None, {}), result)
        self.assertEqual((net.rtol, net.atol), (1e-9, 1e-15))
        self.assertEqual(evidence["effective_rtol"], 1e-9)

    def test_tight_changes_only_integrator(self):
        net = SimpleNamespace(rtol=1e-9, atol=1e-15)
        phase, evidence = object(), {}
        result = instrument_factory(lambda *a: (phase, net), "tight", evidence)(None, None, {})
        self.assertIs(result[0], phase)
        self.assertEqual((net.rtol, net.atol), (1e-11, 1e-19))
        self.assertEqual(evidence["default_atol"], 1e-15)

    def test_not_actually_tighter_blocks(self):
        net = SimpleNamespace(rtol=1e-12, atol=1e-20)
        with self.assertRaises(AssertionError):
            instrument_factory(lambda *a: (net,), "tight", {})(None, None, {})
