"""Regression checks for the opt-in integration diagnostic."""
import ast
import inspect
import unittest
from pathlib import Path
import run_rph_fixed_pulse as pulse

class ToleranceTest(unittest.TestCase):
    def test_default_and_rejection(self):
        self.assertEqual(inspect.signature(pulse.worker).parameters['rtol'].default,1e-9)
        for value in [0,-1,float('nan'),float('inf'),1e-8]:
            with self.assertRaises(AssertionError):
                pulse.worker(Path('/tmp'), 'must-not-run',400,rtol=value)

    def test_requested_tolerance_reaches_net(self):
        tree=ast.parse(inspect.getsource(pulse.worker))
        assignment=next(x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='rtol' for t in x.targets))
        self.assertIsInstance(assignment.value,ast.Name)
        self.assertEqual(assignment.value.id,'rtol')

if __name__=='__main__':unittest.main()
