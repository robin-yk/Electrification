"""Aramco CH4/H2O constant-temperature CJH map on the archived CH4/CO2 grid.

Same reactor closure, mechanism, convergence settings and (T, tau) grid as the
33-condition CH4/CO2 map, with the oxidant changed from CO2 to H2O. The point is
the paired comparison of one changed variable, so nothing else may move.

Carbon-basis yields from the two feeds do NOT share a denominator: with CO2 half
the inlet carbon arrives as CO2, with H2O all of it arrives as CH4. The reports
carry both the yield and the CH4 conversion so the reader can renormalize.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from run_aramco_cjh_baseline import ROOT, save, worker

FEED = "CH4:0.5, H2O:0.5"
REFERENCE_FEED = "CH4:0.5, CO2:0.5"
LIMIT = 1800
PER_WORKER = 180
# The archived CH4/CO2 grid, reproduced exactly.
GRID = [(T, tau) for T, taus in (
    (1000, (.01, .1, 1.)),
    (1200, (.01, .03, .1, .3, 1.)),
    (1300, (.01, .03)),
    (1400, (.01, .03, .1, .3, 1.)),
    (1500, (.003, .01, .03, .1)),
    (1600, (.003, .01, .03, .1, 1.)),
    (1700, (.003, .01, .03, .1)),
    (1800, (.01, .03, .1, .3, 1.)),
) for tau in taus]
# Horizon gate: many more cycles and far tighter tolerances than the map points.
STRICT = dict(min_cycles=20, max_cycles=100, cycle_tolerance=1e-10,
              cycle_output_tolerance=1e-10, stable_cycles_required=5)
# One low-conversion condition and one high-conversion condition.
GATES = [(1400, .1), (1700, .01)]


def compare(reference, actual, what):
    """Largest disagreement in any species, on a per-inlet-carbon basis."""
    x, y = reference["mol_per_feed_carbon"], actual["mol_per_feed_carbon"]
    missing = x.keys() ^ y.keys()
    assert all(abs(x.get(s, y.get(s, 0.))) <= 1e-12 for s in missing), what + ": material species omission"
    errors = {s: abs(x.get(s, 0.) - y.get(s, 0.)) for s in x.keys() | y.keys()}
    worst = max(errors, key=errors.get)
    result = dict(gate=what, worst_species=worst, max_abs_mol_per_feed_C=errors[worst],
                  conversion_abs=abs(reference["CH4_conversion"] - actual["CH4_conversion"]),
                  negligible_omissions=sorted(missing))
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
        points = {"map": 20, "sampling": 40, "horizon": 20, "cold": 20}[kind]
        worker(out, float(T), float(tau), "aramco", points, name,
               STRICT if kind == "horizon" else None, feed=FEED)
        if kind == "cold":
            m = json.loads((out / (name + "-metrics.json")).read_text())
            assert abs(m["CH4_conversion"]) < 1e-8, "cold limit is not zero conversion"
        return

    start = time.monotonic()
    hashes = {key: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
              for key, path in (("solver_sha256", "tools/openmkm_dynamic/run_cstr_case.py"),
                                ("mechanism_sha256", "tools/cantera/mechanisms/aramco20.yaml"))}
    reference = ROOT / "docs/research/aramco-cjh-2026-09-07/data/manifest.json"
    old = json.loads(reference.read_text())
    for key in hashes:
        assert hashes[key] == old[key], "solver or mechanism changed since the CH4/CO2 map"
    archived = []
    for path in ("docs/research/aramco-cjh-2026-09-07/data/summary.json",
                 "docs/research/cjh-refine-01-2026-09-07/data/summary.json",
                 "docs/research/cjh-refine-02-resume-2026-09-07/data/summary.json"):
        archived += json.loads((ROOT / path).read_text())
    assert {(r["T_C"], r["tau_s"]) for r in archived} == set(GRID), "grid differs from the archive"

    # The gated conditions are computed first so their gates close before the
    # rest of the map is spent. A failed gate then stops the remaining points.
    jobs = [(26.85, .1, "cold", "cold")]
    jobs += [(T, tau, "map", f"T{T}-tau{tau}") for T, tau in GATES]
    jobs += [(T, tau, "sampling", f"gate-sampling-T{T}-tau{tau}") for T, tau in GATES]
    jobs += [(T, tau, "horizon", f"gate-horizon-T{T}-tau{tau}") for T, tau in GATES]
    jobs += [(T, tau, "map", f"T{T}-tau{tau}") for T, tau in GRID if (T, tau) not in GATES]

    save(out, "manifest", dict(
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, budget_s=LIMIT, per_worker_s=PER_WORKER, hashes=hashes,
        feed=FEED, reference_feed=REFERENCE_FEED, pressure_Pa=101325.,
        closure=old["closure"], note=old["note"], strict_overrides=STRICT,
        gate_points=40, map_points=20,
        limitations=("Prescribed gas temperature, no heater energy balance, no soot model, "
                     "no experimental validation. Carbon yields are per total inlet carbon, "
                     "which is all CH4 here and half CO2 in the reference feed.")))

    done, rows, gates = [], [], []
    active = None
    try:
        for T, tau, kind, name in jobs:
            active = name
            remaining = LIMIT - (time.monotonic() - start)
            if remaining < 10:
                raise TimeoutError("total budget exhausted")
            save(out, "status", dict(status="running", active=name, completed=done))
            with (out / (name + ".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", __file__, "--output-dir", str(out),
                                "--worker", str(T), str(tau), kind, name],
                               stdout=log, stderr=subprocess.STDOUT, check=True,
                               timeout=min(PER_WORKER, remaining))
            actual = json.loads((out / (name + "-metrics.json")).read_text())
            if kind in ("sampling", "horizon"):
                base = json.loads((out / f"T{T}-tau{tau}-metrics.json").read_text())
                gates.append(dict(name=name, **compare(base, actual, kind)))
                save(out, "gates", gates)
            elif kind == "map":
                rows.append(actual)
                save(out, "summary", rows)
            done.append(name)
            print(json.dumps(dict(case=name, wall_s=actual["wall_s"])), flush=True)

        save(out, "status", dict(status="completed", completed=done, map_points=len(rows),
                                 gates_passed=len(gates), wall_s=time.monotonic() - start))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=done,
                                 reason=str(exc), wall_s=time.monotonic() - start))
        raise


if __name__ == "__main__":
    main()
