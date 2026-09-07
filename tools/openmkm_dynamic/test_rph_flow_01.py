import unittest
from unittest.mock import patch
from pathlib import Path
import run_rph_fixed_pulse as pulse

class FlowInputTest(unittest.TestCase):
    def test_rejects_nonpositive_or_nonfinite_flow(self):
        for q in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(AssertionError):pulse.worker(Path('/private/tmp'),'unused',400,flow_sccm=q)
    def test_flow_parameter_sets_mass_flow(self):
        # Stop before integration, after the inlet controller receives its rate.
        def stop(*args,**kwargs):
            self.assertAlmostEqual(kwargs['mdot'],self.expected,places=18)
            raise RuntimeError('flow verified')
        for q in [50,100,200,400]:
            self.expected=q/22414/60*28.014/1000
            with patch.object(pulse.ct,'MassFlowController',side_effect=stop):
                with self.assertRaisesRegex(RuntimeError,'flow verified'):
                    pulse.worker(Path('/private/tmp'),'unused',400,inert=True,flow_sccm=q)

if __name__=='__main__':unittest.main()
