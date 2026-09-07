import unittest
from run_rph_fixed_gate import PrescribedTemperatureReactor

class TemperatureDerivativeTest(unittest.TestCase):
    def test_replaces_only_temperature_equation(self):
        class Dummy:
            temperature_slope=123.0
            def component_index(self,name):
                assert name=="temperature"
                return 2
        lhs=[2.,3.,4.,5.];rhs=[6.,7.,8.,9.]
        PrescribedTemperatureReactor.after_eval(Dummy(),0,lhs,rhs)
        self.assertEqual(lhs,[2.,3.,1.,5.])
        self.assertEqual(rhs,[6.,7.,123.,9.])
if __name__=="__main__": unittest.main()
