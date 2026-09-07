"""Bounded CJH sampling/horizon gates followed by a local map expansion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from run_aramco_cjh_baseline import ROOT, save, worker

BATCH = "cjh-refine-02"
LIMIT = 540
STRICT = dict(min_cycles=20, max_cycles=100, cycle_tolerance=1e-10,
              cycle_output_tolerance=1e-10, stable_cycles_required=5)
REFERENCES = [
    (1600, .01, "docs/research/cjh-refine-01-2026-09-07/data/T1600-tau0.01-metrics.json"),
    (1400, .01, "docs/research/aramco-cjh-2026-09-07/data/T1400-tau0.01-metrics.json"),
    (1400, .3, "docs/research/cjh-refine-01-2026-09-07/data/T1400-tau0.3-metrics.json"),
]
NEW = [(T, tau) for T in (1500, 1700) for tau in (.003, .01, .03, .1)] + [
    (1600, .003), (1600, .03), (1300, .01), (1300, .03)]


def compare(reference, actual):
    x, y = reference["mol_per_feed_carbon"], actual["mol_per_feed_carbon"]
    assert x.keys() == y.keys(), "species mismatch"
    errors = {s: abs(x[s]-y[s]) for s in x}
    worst = max(errors, key=errors.get)
    result = dict(worst_species=worst, max_abs_mol_per_feed_C=errors[worst],
                  conversion_abs=abs(reference["CH4_conversion"]-actual["CH4_conversion"]))
    assert errors[worst] < 1e-5 and result["conversion_abs"] < 1e-5, result
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=4, metavar=("T", "TAU", "KIND", "NAME"))
    a = ap.parse_args()
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if a.worker:
        T, tau, kind, name = a.worker
        assert kind in ("gate", "map")
        worker(out, float(T), float(tau), "aramco", 80 if kind == "gate" else 20,
               name, STRICT if kind == "gate" else None)
        return
    start = time.monotonic()
    ledger = json.loads((ROOT / "docs/research/c2co-campaign-2026-09-07/budget.json").read_text())
    reservations = [b for b in ledger["batches"] if b["status"] == "reserved"]
    assert len(reservations) == 1 and reservations[0]["id"] == BATCH
    assert reservations[0]["reserved_s"] >= LIMIT
    assert ledger["spent_s"] + ledger["reserved_s"] <= ledger["total_budget_s"]
    assert LIMIT <= ledger["batch_limit_s"]
    baseline = ROOT / "docs/research/aramco-cjh-2026-09-07/data"
    oldmanifest = json.loads((baseline / "manifest.json").read_text())
    hashes = {}
    for key, path in (("solver_sha256", "tools/openmkm_dynamic/run_cstr_case.py"),
                      ("mechanism_sha256", "tools/cantera/mechanisms/aramco20.yaml")):
        hashes[key] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert hashes[key] == oldmanifest[key], "model changed"
    existing = []
    for path in (baseline / "summary.json", ROOT / "docs/research/cjh-refine-01-2026-09-07/data/summary.json"):
        existing += json.loads(path.read_text())
    assert len(set(NEW)) == len(NEW) and not set(NEW) & {(r["T_C"], r["tau_s"]) for r in existing}
    jobs = [(T, tau, "gate", f"gate-T{T}-tau{tau}", ref) for T, tau, ref in REFERENCES]
    jobs += [(T, tau, "map", f"T{T}-tau{tau}", None) for T, tau in NEW]
    # The first refinement supplies an observed error for the original grid's
    # linear prediction, not an independent test of a fitted surrogate.
    lookup = {(r["T_C"], r["tau_s"]): r for r in existing}
    prediction = (lookup[(1400, .01)]["C2H2_carbon_yield"] + lookup[(1800, .01)]["C2H2_carbon_yield"])/2
    observed = lookup[(1600, .01)]["C2H2_carbon_yield"]
    save(out, "manifest", dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, budget_s=LIMIT, per_worker_s=120, hashes=hashes,
        closure=oldmanifest["closure"], feed="CH4:0.5, CO2:0.5", pressure_Pa=101325.,
        strict_overrides=STRICT, gate_points=80, map_points=20,
        expansion_evidence=dict(coarse_linear_C2H2_yield=prediction, observed_C2H2_yield=observed,
                                abs_error=abs(prediction-observed)),
        limitations="No solver rtol/atol or alternate initial-state test; prescribed gas T, not an electrical device."))
    done, rows, gates = [], [], []
    active = None
    try:
        for T, tau, kind, name, ref in jobs:
            active = name
            remaining = LIMIT-(time.monotonic()-start)
            if remaining < 10:
                raise TimeoutError("batch budget exhausted")
            save(out, "status", dict(status="running", active=name, completed=done))
            with (out / (name+".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", __file__, "--output-dir", str(out), "--worker",
                    str(T), str(tau), kind, name], stdout=log, stderr=subprocess.STDOUT,
                    check=True, timeout=min(120, remaining))
            actual = json.loads((out/(name+"-metrics.json")).read_text())
            if kind == "gate":
                result = compare(json.loads((ROOT/ref).read_text()), actual)
                gates.append(dict(name=name, reference=ref, **result))
                save(out, "gates", gates)
            else:
                rows.append(actual)
                save(out, "summary", rows)
            done.append(name)
            print(json.dumps(dict(case=name, wall_s=actual["wall_s"])), flush=True)
        save(out, "status", dict(status="completed", completed=done, map_points=len(rows),
                                 gates_passed=len(gates), wall_s=time.monotonic()-start))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=done,
                                 reason=str(exc), wall_s=time.monotonic()-start))
        raise


if __name__ == "__main__":
    main()
