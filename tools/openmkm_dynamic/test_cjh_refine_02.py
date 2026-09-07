import unittest
import json
from pathlib import Path
from run_cjh_refine_02 import compare, NEW, REFERENCES, STRICT


class ValidationGateTests(unittest.TestCase):
    def test_identical(self):
        row = dict(mol_per_feed_carbon={"CH4": .5, "CO": .4}, CH4_conversion=.5)
        self.assertEqual(compare(row, row)["max_abs_mol_per_feed_C"], 0)

    def test_changed_species_blocks(self):
        row = dict(mol_per_feed_carbon={"CH4": .5}, CH4_conversion=.5)
        other = dict(mol_per_feed_carbon={"CH4": .501}, CH4_conversion=.5)
        with self.assertRaises(AssertionError):
            compare(row, other)

    def test_changed_conversion_blocks(self):
        row = dict(mol_per_feed_carbon={"CH4": .5}, CH4_conversion=.5)
        with self.assertRaises(AssertionError):
            compare(row, dict(row, CH4_conversion=.51))

    def test_positive_only_sparse_output_accepts_negligible_omission(self):
        row = dict(mol_per_feed_carbon={"CH4": .5, "trace": 1e-31}, CH4_conversion=.5)
        other = dict(mol_per_feed_carbon={"CH4": .5}, CH4_conversion=.5)
        self.assertLess(compare(row, other)["max_abs_mol_per_feed_C"], 1e-12)

    def test_material_omission_blocks(self):
        row = dict(mol_per_feed_carbon={"CH4": .5, "CO": .01}, CH4_conversion=.5)
        with self.assertRaises(AssertionError):
            compare(row, dict(mol_per_feed_carbon={"CH4": .5}, CH4_conversion=.5))

    def test_plan_is_bounded(self):
        self.assertEqual(len(set(NEW)), 12)
        self.assertEqual(len(REFERENCES), 3)
        self.assertEqual(STRICT["min_cycles"], 20)

    def test_short_residence_plan_has_no_repeated_prior_points(self):
        root = Path(__file__).resolve().parents[2]
        for batch, count in (("03", 33), ("04", 45), ("05", 57)):
            with self.subTest(batch=batch):
                plan = json.loads((Path(__file__).parent/f"cjh-refine-{batch}.json").read_text())
                new = {tuple(row) for row in plan["new_points"]}
                self.assertEqual(len(new), 12)
                self.assertEqual(len(plan["references"]), 2)
                prior = [r for p in plan["prior_summaries"] for r in json.loads((root/p).read_text())]
                self.assertEqual(len(prior), count)
                self.assertFalse(new & {(r["T_C"], r["tau_s"]) for r in prior})
