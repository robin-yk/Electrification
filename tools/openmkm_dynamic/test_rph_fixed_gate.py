import unittest
from run_rph_fixed_gate import PrescribedTemperatureReactor

class TemperatureDerivativeTest(unittest.TestCase):
    def test_controller_resolves_archived_inert_expansion(self):
        from run_rph_fixed_pulse import PRESSURE_K
        m,T,slope=3.376694805307223e-9,933.15,48000.
        estimated_old=m*slope/T/1e-8
        self.assertAlmostEqual(estimated_old,17.37522808842,delta=.02)
        self.assertLess(m*slope/T/PRESSURE_K/101325,1e-4)
    def test_periodic_segments_close_without_temperature_jumps(self):
        from run_rph_fixed_pulse import segments
        for period in [.5,1.,2.]:
            parts=segments(period)
            self.assertAlmostEqual(sum(p[0] for p in parts),period)
            self.assertEqual(parts[-1][2],parts[0][1])
            for left,right in zip(parts,parts[1:]):
                self.assertEqual(left[2],right[1])
            self.assertAlmostEqual(sum(b-a for _,a,b in parts),0)
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
