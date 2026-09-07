"""Bounded chemical-only pilot, not heater or acrylic-acid reactor validation."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "P1": dict(feed="CH4:0.5, CO2:0.5", peak_c=1800., tau_s=0.1),
    "P2": dict(feed="CH4:0.05, CO2:0.05, HE:0.90", peak_c=1800., tau_s=0.1),
    "P3": dict(feed="CH4:0.5, CO2:0.5", peak_c=1400., tau_s=0.1),
    "P4": dict(feed="CH4:0.5, CO2:0.5", peak_c=1800., tau_s=0.01),
}


def product_metrics(audit):
    c = audit["carbon_in_kmol"]
    assert c > 0
    n = audit["species_out_kmol"]
    return {
        "C2H2_carbon_yield": 2 * n.get("C2H2", 0.) / c,
        "C2H4_carbon_yield": 2 * n.get("C2H4", 0.) / c,
        "CO_carbon_yield": n.get("CO", 0.) / c,
        "H2O_mol_per_feed_C": n.get("H2O", 0.) / c,
        "H2_mol_per_feed_C": n.get("H2", 0.) / c,
        "AA_stoichiometric_carbon_upper_bound": 3 * min(
            n.get("C2H2", 0.), n.get("CO", 0.), n.get("H2O", 0.)) / c,
    }


def save(out, name, data):
    (out / (name + ".json")).write_text(json.dumps(data, indent=2) + "\n")


def worker(out, case, mechanism, points):
    import run_cstr_case as solver
    import run_three_pairs as pairs
    cfg = CASES["P1" if case == "cold" else case]
    parser = argparse.ArgumentParser()
    solver.add_common_args(parser)
    args = parser.parse_args([])
    args.period_s = 1.0
    args.waveform = "trapezoid"
    args.t_min_c = 600.
    args.t_peak_c = cfg["peak_c"]
    args.duty = .05
    args.ramp_up_fraction = .025
    args.ramp_down_fraction = .1
    args.feed = cfg["feed"]
    args.residence_time_s = cfg["tau_s"]
    args.points_per_cycle = points
    args.min_cycles, args.max_cycles, args.record_cycles = 3, 100, 1
    args.cycle_tolerance = 1e-8
    args.jacobian = "sparse" if mechanism == "aramco" else "dense"
    if case == "cold":
        args.t_min_c = args.t_peak_c = 26.85
    p = solver.build_params(args)
    p.update(cycle_output_tolerance=1e-8, stable_cycles_required=3)
    pairs.OUT = out
    mech = "gri30.yaml" if mechanism == "gri" else str(ROOT / "tools/cantera/mechanisms/aramco20.yaml")
    key = f"{case}-{mechanism}-{points}"
    save(out, key + "-parameters", p)
    metrics = pairs.execute(key, mech, p)
    raw = json.loads((out / (key + ".json")).read_text())
    metrics.update(product_metrics(raw["carbon_audit"]))
    save(out, key + "-metrics", metrics)
    if case == "cold":
        assert abs(metrics["CH4_conversion"]) < 1e-8, "cold conversion gate"


def refinement(out, mechanism):
    a, b = [json.loads((out / f"P1-{mechanism}-{p}-metrics.json").read_text()) for p in (200, 400)]
    changes = {}
    for k, v in a.items():
        if k.endswith("yield") or k.endswith("feed_C") or k == "AA_stoichiometric_carbon_upper_bound":
            changes[k] = abs(v - b[k])
            assert changes[k] <= max(.002, .02 * abs(b[k])), f"{mechanism}: {k} refinement"
    for k, v in a["carbon_yields_per_feed_carbon"].items():
        assert abs(v - b["carbon_yields_per_feed_carbon"][k]) <= max(.002, .02 * abs(b["carbon_yields_per_feed_carbon"][k])), k
    assert abs(a["CH4_conversion"] - b["CH4_conversion"]) <= .002
    save(out, mechanism + "-refinement", changes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=3, metavar=("CASE", "MECHANISM", "POINTS"))
    args = ap.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.worker:
        worker(out, args.worker[0], args.worker[1], int(args.worker[2]))
        return
    started = time.monotonic()
    completed = []
    save(out, "manifest", {
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "cases": CASES, "period_s": 1., "t_min_c": 600., "duty": .05,
        "ramp_up_fraction": .025, "ramp_down_fraction": .1,
        "pressure_Pa": 101325., "closure": "constant pressure, prescribed gas T, inlet=outlet=mass/tau",
        "budget_wall_s": 540, "per_case_wall_s": 120,
        "claim": "chemical pilot only; no experimental, energy, soot or downstream-reactor validation",
        "hashes": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
            "tools/openmkm_dynamic/run_cstr_case.py", "tools/openmkm_dynamic/run_c2co_pilot.py",
            "tools/cantera/mechanisms/aramco20.yaml")},
    })
    jobs = [("cold", "gri", 200), ("P1", "gri", 200), ("P1", "gri", 400),
            ("P1", "aramco", 200), ("P1", "aramco", 400)]
    jobs += [(case, "aramco", 200) for case in ("P2", "P3", "P4")]
    active = None
    try:
        for case, mech, points in jobs:
            active = f"{case}-{mech}-{points}"
            remaining = 540 - (time.monotonic() - started)
            if remaining < 10:
                raise TimeoutError("total budget exhausted")
            save(out, "status", dict(status="running", active=active, completed=completed))
            print("DISPATCH", active, flush=True)
            with (out / (active + ".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()),
                    "--output-dir", str(out), "--worker", case, mech, str(points)],
                    stdout=log, stderr=subprocess.STDOUT, check=True, timeout=min(120, remaining))
            completed.append(active)
            if case == "P1" and points == 400:
                refinement(out, mech)
        save(out, "status", dict(status="completed", completed=completed,
             note="P1 paired/refined; P2-P4 provisional base-grid only", wall_s=time.monotonic()-started))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=completed,
             reason=str(exc), wall_s=time.monotonic()-started))
        raise


if __name__ == "__main__":
    main()
