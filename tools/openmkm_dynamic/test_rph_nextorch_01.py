import unittest
import numpy as np
from propose_rph_nextorch_01 import encode,decode,training
from run_rph_nextorch_01 import waveform

class ProposalTest(unittest.TestCase):
    def test_yield_training_uses_carbon_fraction_not_mass_productivity(self):
        from propose_rph_yield_01 import training as yield_training
        rows,_=yield_training()
        self.assertEqual(len(rows),39)
        best=max(rows,key=lambda r:r['y'][0])
        self.assertEqual((best['peak_C'],best['hold_s'],best['flow_sccm']),(1800,.5,50))
        self.assertAlmostEqual(best['y'][0],11.173434652866495,places=8)
    def test_round_trip_and_bounds(self):
        for x in [(1200,.025,50),(1800,.5,1600),(1500,.2,800)]:
            self.assertTrue(np.allclose(decode(encode(*x)),x))
        self.assertTrue(np.allclose(encode(1200,.025,50),[0,0,0]))
        self.assertTrue(np.allclose(encode(1800,.5,1600),[1,1,1]))
    def test_training_is_38_distinct_450C_points(self):
        rows,_=training();self.assertEqual(len(rows),38)
        self.assertEqual(len({tuple(r['x']) for r in rows}),38)
    def test_continuous_waveform(self):
        s=waveform(1532.21,.1234)
        self.assertAlmostEqual(sum(v[0] for v in s),1.)
        self.assertEqual(s[0][1],723.15)
        for a,b in zip(s,s[1:]+s[:1]):self.assertEqual(a[2],b[1])

if __name__=='__main__':unittest.main()
