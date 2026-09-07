import unittest
from summarize_cjh_progress import progress


class SamplingProgressTests(unittest.TestCase):
    def row(self, T, a, b):
        return dict(T_C=T, tau_s=.1, mechanism="aramco", C2H2_carbon_yield=a, C2H4_carbon_yield=b)

    def test_gains_are_percentage_points_and_best_is_retained(self):
        result = progress([("a", [self.row(1000, .1, .02)]), ("b", [self.row(1200, .09, .03)])])
        self.assertEqual(result[-1]["cumulative_points"], 2)
        self.assertEqual(result[-1]["maxima"]["C2H2_carbon_yield"]["gain_percentage_points"], 0)
        self.assertAlmostEqual(result[-1]["maxima"]["C2H4_carbon_yield"]["gain_percentage_points"], 1)

    def test_duplicate_rejected(self):
        row = self.row(1000, .1, .02)
        with self.assertRaises(ValueError):
            progress([("a", [row]), ("b", [row])])
