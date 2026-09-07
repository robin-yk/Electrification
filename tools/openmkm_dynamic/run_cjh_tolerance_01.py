"""Explicit CVODES tolerance diagnostic; production solver stays unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from run_aramco_cjh_baseline import ROOT, save, worker
from run_cjh_refine_02 import STRICT, compare

BATCH = "cjh-tolerance-01"
CASES = [
    (1750, .001, "docs/research/cjh-refine-04-2026-09-07/data/T1750-tau0.001-metrics.json"),
    (1750, .00006, "docs/research/cjh-refine-05-2026-09-07/data/T1750-tau6e-05-metrics.json")]


def instrument_factory(original, mode, evidence):
    assert mode in ("default", "tight")
    def make(ct, mech, p):
        result = original(ct, mech, p)
        net = result[-1]
        evidence.update(default_rtol=net.rtol, default_atol=net.atol)
        if mode == "tight":
            assert 1e-11 < net.rtol and 1e-19 < net.atol
            net.rtol, net.atol = 1e-11, 1e-19
        evidence.update(effective_rtol=net.rtol, effective_atol=net.atol)
        return result
    return make


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=4)
    a = ap.parse_args()
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if a.worker:
        import run_cstr_case as solver
        T, tau, mode, name = a.worker
        evidence = dict(mode=mode, initial_composition="unchanged feed")
        original = solver.make_reactor
        solver.make_reactor = instrument_factory(original, mode, evidence)
        try:
            worker(out, float(T), float(tau), "aramco", 80, name, STRICT)
        finally:
            solver.make_reactor = original
            save(out, name+"-integrator", evidence)
        return
    start = time.monotonic()
    ledger = json.loads((ROOT/"docs/research/c2co-campaign-2026-09-07/budget.json").read_text())
    reserved = [b for b in ledger["batches"] if b["status"] == "reserved"]
    assert len(reserved) == 1 and reserved[0]["id"] == BATCH and reserved[0]["reserved_s"] >= 540
    assert ledger["spent_s"]+ledger["reserved_s"] <= ledger["total_budget_s"] and ledger["batch_limit_s"] >= 540
    old = json.loads((ROOT/"docs/research/aramco-cjh-2026-09-07/data/manifest.json").read_text())
    hashes = {}
    for key, file in (("solver_sha256", "tools/openmkm_dynamic/run_cstr_case.py"),
                      ("mechanism_sha256", "tools/cantera/mechanisms/aramco20.yaml")):
        hashes[key] = hashlib.sha256((ROOT/file).read_bytes()).hexdigest()
        assert hashes[key] == old[key], "production model changed"
    jobs = [(T, tau, mode, f"T{T}-tau{tau}-{mode}", ref)
            for T, tau, ref in CASES for mode in ("default", "tight")]
    save(out, "manifest", dict(commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, hashes=hashes, budget_s=540, worker_limit_s=120,
        adapter="instrument_factory wraps production make_reactor only to inspect/set net.rtol and net.atol",
        tight=dict(rtol=1e-11, atol=1e-19), observation=STRICT,
        limitation="Same initial feed composition; no initial-state, physical or mechanism validation."))
    done, gates = [], []
    active = None
    try:
        for T, tau, mode, name, ref in jobs:
            active = name
            remaining = 540-(time.monotonic()-start)
            if remaining < 10:
                raise TimeoutError("batch budget exhausted")
            save(out, "status", dict(status="running", active=name, completed=done))
            with (out/(name+".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", __file__, "--output-dir", str(out),
                    "--worker", str(T), str(tau), mode, name], check=True, timeout=min(120, remaining),
                    stdout=log, stderr=subprocess.STDOUT)
            actual = json.loads((out/(name+"-metrics.json")).read_text())
            reference = ROOT/ref if mode == "default" else out/f"T{T}-tau{tau}-default-metrics.json"
            delta = compare(json.loads(reference.read_text()), actual)
            gates.append(dict(name=name, reference=str(reference.relative_to(ROOT)), **delta))
            save(out, "gates", gates)
            done.append(name)
        save(out, "status", dict(status="completed", completed=done, gates_passed=len(gates), new_map_points=0,
                                 wall_s=time.monotonic()-start))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=done, reason=str(exc),
                                 wall_s=time.monotonic()-start))
        raise


if __name__ == "__main__":
    main()
