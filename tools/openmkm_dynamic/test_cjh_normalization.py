import unittest
from run_aramco_cjh_baseline import reference_rates


class NormalizationTest(unittest.TestCase):
    def test_carbon_and_mass_basis(self):
        r = reference_rates({"C2H2": .5, "CO": .25})
        self.assertAlmostEqual(r["C2H2"], .5 * (50e-3 * 60 / 22.414) * 26.038 / .0288)
        self.assertEqual(r["C2_stable_sum"], r["C2H2"])
        self.assertAlmostEqual(reference_rates({"CO": .25}, mass_mg=57.6)["CO"], r["CO"] / 2)
