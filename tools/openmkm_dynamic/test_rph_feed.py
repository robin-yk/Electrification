import inspect
import unittest
from pathlib import Path
import run_rph_fixed_pulse as p
class FeedTest(unittest.TestCase):
    def test_default_and_domain(self):
        self.assertEqual(inspect.signature(p.worker).parameters['feed_ch4'].default,.5)
        for x in [0,1,-.1,1.1,float('nan')]:
            with self.assertRaises(AssertionError):p.worker(Path('/tmp'),'must-not-run',400,feed_ch4=x)
if __name__=='__main__':unittest.main()
