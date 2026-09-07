import unittest
from run_c2co_pilot import product_metrics


class ProductMetricsTest(unittest.TestCase):
    def test_water_limited_stoichiometric_bound_and_carbon_basis(self):
        m = product_metrics(dict(carbon_in_kmol=10., species_out_kmol={
            "C2H2": 2., "C2H4": 1., "CO": 3., "H2O": .5, "H2": 1.}))
        self.assertAlmostEqual(m["C2H2_carbon_yield"], .4)
        self.assertAlmostEqual(m["CO_carbon_yield"], .3)
        self.assertAlmostEqual(m["AA_stoichiometric_carbon_upper_bound"], .15)
        self.assertAlmostEqual(m["H2O_mol_per_feed_C"], .05)

    def test_no_water_no_self_sufficient_bound(self):
        self.assertEqual(product_metrics(dict(carbon_in_kmol=10., species_out_kmol={
            "C2H2": 2., "CO": 3.}))["AA_stoichiometric_carbon_upper_bound"], 0.)
