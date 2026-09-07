import unittest
from unittest.mock import patch
from pathlib import Path
import run_rph_fixed_pulse as pulse
from run_rph_screen_450 import PEAKS, HOLDS, waveform

class ScreenTest(unittest.TestCase):
    def test_all_waveforms(self):
        self.assertEqual(len(PEAKS)*len(HOLDS),28)
        for p in PEAKS:
            for h in HOLDS:
                s=waveform(p,h)
                self.assertAlmostEqual(sum(x[0] for x in s),1.)
                self.assertTrue(all(x[0]>0 for x in s))
                self.assertEqual(s[0][1],723.15)
                self.assertEqual(s[1],(h,p+273.15,p+273.15))
                for a,b in zip(s,s[1:]+s[:1]):self.assertEqual(a[2],b[1])
    def test_worker_initializes_at_custom_floor(self):
        class Probe:
            @property
            def TPX(self): return None
            @TPX.setter
            def TPX(self,value):
                assert value[0]==723.15, value
                raise RuntimeError('probe reached custom floor')
        with patch.object(pulse.ct,'Solution',return_value=Probe()):
            with self.assertRaisesRegex(RuntimeError,'probe reached custom floor'):
                pulse.worker(Path('/private/tmp'),'unused',400,waveform=waveform(1800,.025))

if __name__=='__main__':unittest.main()
