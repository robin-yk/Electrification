import unittest
from summarize_cjh_map import nondominated


class ParetoTest(unittest.TestCase):
    def test_tradeoff_and_dominated(self):
        r = [dict(C2H2_carbon_yield=x, CO_carbon_yield=y) for x,y in ((.2,.3),(.1,.4),(.1,.2))]
        self.assertEqual(nondominated(r), r[:2])
