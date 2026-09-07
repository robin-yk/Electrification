"""Verify opt-in stopping against archived long runs, without a new sweep."""
import argparse
import json
import time
import subprocess
from pathlib import Path
import run_three_pairs as pairs
import run_cstr_case as solver


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=pairs.ROOT, text=True).strip(),
        "reference_directory": str(args.reference_dir), "min_cycles": 3,
        "stable_cycles_required": 3, "state_tolerance": 1e-8, "outflow_tolerance": 1e-8,
        "reference_yield_agreement": 1e-6}, indent=2) + "\n")
    rows = []
    tests = [(6300012, "gri"), (6300012, "aramco"), (6000015, "aramco")]
    for idx, label in tests:
        ref = json.loads((args.reference_dir / f"{idx}-{label}-base.json").read_text())
        record = json.loads((args.reference_dir / f"{idx}-source.json").read_text())["record"]
        p = pairs.parameters(record, 200)
        p.update(min_cycles=3, cycle_output_tolerance=1e-8, stable_cycles_required=3)
        p["jacobian"] = "dense" if label == "gri" else "sparse"
        mech = "gri30.yaml" if label == "gri" else str(pairs.ROOT / "tools/cantera/mechanisms/aramco20.yaml")
        start = time.perf_counter()
        result = solver.run_case(mech, p)
        wall = time.perf_counter() - start
        (args.output_dir / f"{idx}-{label}-adaptive.json").write_text(json.dumps(result) + "\n")
        assert result["mechanism_provenance"]["mechanism_sha256"] == ref["mechanism_provenance"]["mechanism_sha256"]
        a, b = pairs.metrics(result), pairs.metrics(ref)
        errors = {k: abs(v - b["carbon_yields_per_feed_carbon"][k]) for k, v in a["carbon_yields_per_feed_carbon"].items()}
        passed = (result["cycle_summary"]["converged"] and max(errors.values()) < 1e-6
                  and abs(a["CH4_conversion"] - b["CH4_conversion"]) < 1e-6
                  and max(abs(v) for v in a["element_residuals"].values()) < 0.005
                  and result["carbon_audit"]["group_partition_ok"])
        rows.append(dict(case=idx, mechanism=label, passed=passed, cycles=a["cycles"],
                         reference_cycles=b["cycles"], wall_s=wall, reference_wall_s=ref["wall_s"],
                         carbon_yield_errors=errors))
        (args.output_dir / "validation.json").write_text(json.dumps(rows, indent=2) + "\n")
        print(json.dumps(rows[-1]), flush=True)
        assert passed, "early stopping did not reproduce the reference; do not activate"


if __name__ == "__main__":
    main()
