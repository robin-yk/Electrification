import unittest
import numpy as np
from propose_rph_explore import choose
class SelectionTest(unittest.TestCase):
    def test_no_duplicate_and_two_distinct_points(self):
        x=np.array([[0.,0.,0.]])
        c=np.array([[0.,0.,0.],[.01,0.,0.],[1.,1.,1.],[0.,1.,0.]])
        ids,d,s=choose(x,c,np.array([100.,50.,3.,1.]))
        self.assertEqual(ids,[2,3]);self.assertGreaterEqual(d[ids[0]],.1)
    def test_insufficient_coverage_rejected(self):
        with self.assertRaises(AssertionError):choose(np.zeros((1,3)),np.zeros((2,3)),np.ones(2))
if __name__=='__main__':unittest.main()
