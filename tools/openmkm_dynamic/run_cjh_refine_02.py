"""Bounded CJH sampling/horizon gates followed by a local map expansion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
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
    # carbon_audit stores only positive entries. Roundoff-sized entries may
    # disappear between runs; a material missing entry must still fail.
    missing = x.keys() ^ y.keys()
    assert all(abs(x.get(s, y.get(s, 0.))) <= 1e-12 for s in missing), "material species omission"
    errors = {s: abs(x.get(s, 0.)-y.get(s, 0.)) for s in x.keys() | y.keys()}
    worst = max(errors, key=errors.get)
    result = dict(worst_species=worst, max_abs_mol_per_feed_C=errors[worst],
                  conversion_abs=abs(reference["CH4_conversion"]-actual["CH4_conversion"]),
                  negligible_omissions=sorted(missing))
    assert errors[worst] < 1e-5 and result["conversion_abs"] < 1e-5, result
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--batch-id", default=BATCH)
    ap.add_argument("--resume-dir", type=Path)
    ap.add_argument("--plan", type=Path)
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
    plan = json.loads(a.plan.read_text()) if a.plan else None
    selected = [tuple(row) for row in plan["new_points"]] if plan else NEW
    references = [tuple(row) for row in plan["references"]] if plan else REFERENCES
    assert 0 < len(selected) <= 19 and 0 < len(references) <= 3
    assert len(selected) + len(references) <= 20
    if plan:
        assert plan["batch_id"] == a.batch_id
    ledger = json.loads((ROOT / "docs/research/c2co-campaign-2026-09-07/budget.json").read_text())
    reservations = [b for b in ledger["batches"] if b["status"] == "reserved"]
    assert len(reservations) == 1 and reservations[0]["id"] == a.batch_id
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
    paths = [ROOT / s for s in plan["prior_summaries"]] if plan else [baseline / "summary.json", ROOT / "docs/research/cjh-refine-01-2026-09-07/data/summary.json"]
    for path in paths:
        existing += json.loads(path.read_text())
    assert len(set(selected)) == len(selected) and not set(selected) & {(r["T_C"], r["tau_s"]) for r in existing}
    for T, tau, ref in references:
        reference = json.loads((ROOT/ref).read_text())
        assert (reference["T_C"], reference["tau_s"], reference["mechanism"]) == (T, tau, "aramco")
    jobs = [(T, tau, "gate", f"gate-T{T}-tau{tau}", ref) for T, tau, ref in references]
    jobs += [(T, tau, "map", f"T{T}-tau{tau}", None) for T, tau in selected]
    cache = []
    if a.resume_dir:
        source = a.resume_dir.resolve()
        parent = json.loads((source/"manifest.json").read_text())
        assert parent["hashes"] == hashes and parent["jobs"] == [list(j) for j in jobs]
        archive = json.loads((source.parent/"checksums.json").read_text())
        # The archive has already been checked by archive_checksums.py in the
        # workflow. Each reused raw file is also hashed in this manifest.
        for _, _, kind, name, _ in jobs:
            raw = source/(name+".json")
            if kind == "gate" and raw.exists():
                assert not (out/raw.name).exists(), "refuse existing output"
                assert hashlib.sha256(raw.read_bytes()).hexdigest() == archive["data/"+raw.name]
                cache.append(dict(file=str(raw.relative_to(ROOT)),
                                  sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
                shutil.copy2(raw, out/raw.name)
    # The first refinement supplies an observed error for the original grid's
    # linear prediction, not an independent test of a fitted surrogate.
    lookup = {(r["T_C"], r["tau_s"]): r for r in existing}
    prediction = (lookup[(1400, .01)]["C2H2_carbon_yield"] + lookup[(1800, .01)]["C2H2_carbon_yield"])/2
    observed = lookup[(1600, .01)]["C2H2_carbon_yield"]
    save(out, "manifest", dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, budget_s=LIMIT, per_worker_s=120, hashes=hashes, reused_raw=cache, plan=plan,
        closure=oldmanifest["closure"], feed="CH4:0.5, CO2:0.5", pressure_Pa=101325.,
        strict_overrides=STRICT, gate_points=80, map_points=20,
        expansion_evidence=dict(coarse_linear_C2H2_yield=prediction, observed_C2H2_yield=observed,
                                abs_error=abs(prediction-observed), prior_points=len(existing),
                                prior_maxima={k: {"T_C": (r := max(existing, key=lambda r: r[k]))["T_C"],
                                    "tau_s": r["tau_s"], "yield": r[k]} for k in ("C2H2_carbon_yield", "C2H4_carbon_yield")}),
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
