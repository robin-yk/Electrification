import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from robust_acquisition import search

class SearchTest(unittest.TestCase):
    def test_never_replaces_good_seed_with_bad_local_result(self):
        def f(x):return 1-(x[0]-.7)**2,np.array([-2*(x[0]-.7)])
        bad=SimpleNamespace(x=np.array([0.]),success=False,message='simulated bad local search')
        with patch('robust_acquisition.minimize',return_value=bad):
            p,v,_=search(f,[[0],[.7],[1]],restarts=2)
        self.assertAlmostEqual(p[0],.7);self.assertAlmostEqual(v,1.)
    def test_refines_between_seeds(self):
        def f(x):return 1-(x[0]-.731)**2,np.array([-2*(x[0]-.731)])
        p,v,_=search(f,[[0],[.5],[1]],restarts=3)
        self.assertAlmostEqual(p[0],.731,places=6);self.assertAlmostEqual(v,1.)
    def test_rejects_nonfinite_scores(self):
        with self.assertRaises(AssertionError):search(lambda x:(float('nan'),x),[[0],[1]])

if __name__=='__main__':unittest.main()
