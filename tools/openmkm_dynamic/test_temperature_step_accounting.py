"""Algebraic state-update checks only: no chemistry or ReactorNet integration."""
import unittest
import numpy as np
import cantera as ct
from temperature_step_accounting import open_temperature_step

class StepAccountingTest(unittest.TestCase):
    def setup_case(self,cls):
        g=ct.Solution("gri30.yaml")
        g.TPX=773.15,101325,"CH4:.02,C2H2:.01,AR:.97"
        r=cls(g,energy="off",clone=False)
        f=ct.Solution("gri30.yaml");f.TPX=773.15,101325,"CH4:.05,AR:.95"
        return g,r,f.Y.copy()

    def test_old_reset_has_unaccounted_species_mass(self):
        for cls in (ct.IdealGasConstPressureReactor,ct.IdealGasConstPressureMoleReactor):
            g,r,feed=self.setup_case(cls)
            before=r.mass*g.Y.copy()
            g.TP=2073.15,101325;r.syncState()
            self.assertGreater(np.max(abs(r.mass*g.Y-before))/sum(before),.1)

    def test_corrected_steps_close_species_for_both_state_formulations(self):
        for cls in (ct.IdealGasConstPressureReactor,ct.IdealGasConstPressureMoleReactor):
            g,r,feed=self.setup_case(cls)
            vol=r.volume;initial=r.mass*g.Y.copy()
            out,extra=open_temperature_step(r,g,2073.15,101325,feed)
            hot=r.mass*g.Y.copy()
            np.testing.assert_allclose(initial,hot+out,rtol=0,atol=1e-12*sum(initial))
            self.assertEqual(extra,0)
            out2,extra2=open_temperature_step(r,g,773.15,101325,feed)
            cold=r.mass*g.Y.copy()
            np.testing.assert_allclose(cold,hot+extra2*feed,rtol=0,atol=1e-12*sum(initial))
            self.assertGreater(extra2,0)
            self.assertEqual(float(sum(out2)),0)
            self.assertAlmostEqual(r.volume/vol,1)
            self.assertAlmostEqual(g.P/101325,1)
            # Restoring T and P restores total moles, not the species inventory.
            self.assertAlmostEqual(sum(cold/g.molecular_weights)/sum(initial/g.molecular_weights),1)

    def test_identity_step_has_no_extra_flow(self):
        g,r,feed=self.setup_case(ct.IdealGasConstPressureMoleReactor)
        before=r.mass*g.Y.copy()
        out,extra=open_temperature_step(r,g,g.T,g.P,feed)
        self.assertLess(float(sum(out))+extra,1e-12*sum(before))
        np.testing.assert_allclose(r.mass*g.Y,before,rtol=1e-12,atol=1e-30)

if __name__=="__main__":unittest.main()
