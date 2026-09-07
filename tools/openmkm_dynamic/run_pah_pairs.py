"""Paired mechanism comparison against the archived Aramco constant-temperature map.

AramcoMech 2.0 stops at C8 and carries benzene as its largest ring, so every
archived map here reports the carbon that reaches C2H2, C4H2 and C6H6 and then
stops. That leaves one question the archives cannot answer: how much of that
carbon would keep going, to naphthalene and past it.

This batch answers it by running four conditions taken from the archived maps
under a second mechanism, named with --mechanism. CRECK 2003 high temperature
carries PAH and soot-precursor lumps and answers the question. GRI-Mech 3.0
stops at C3, so it answers nothing about rings and instead shows what a
mechanism ceiling does to the same four conditions. The Aramco side is read
from the archives and is not recomputed, so nothing archived can move here.

A changed mechanism is a new model. The two mechanisms are reported side by
side and nothing is transferred between them: no optimum, no ranking, and no
validation status. The comparison is of two calculations, not of a calculation
against a measurement.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from run_aramco_cjh_baseline import MECHANISMS, ROOT, save, worker

LIMIT = 1200
PER_WORKER = 300
FEEDS = {"co2": "CH4:0.5, CO2:0.5", "h2o": "CH4:0.5, H2O:0.5"}
# Where each feed's archived Aramco map lives. Read, never rewritten.
ARCHIVES = {
    "co2": ("docs/research/aramco-cjh-2026-09-07",
            "docs/research/cjh-refine-01-2026-09-07",
            "docs/research/cjh-refine-02-resume-2026-09-07",
            "docs/research/cjh-refine-03-2026-09-07",
            "docs/research/cjh-refine-04-2026-09-07",
            "docs/research/cjh-refine-05-2026-09-07"),
    "h2o": ("docs/research/h2o-cjh-2026-09-07",
            "docs/research/h2o-cjh-extend-2026-09-07"),
}
# Two conditions per feed: the acetylene maximum that feed's map found, and the
# benzene-rich moderate-severity corner. Both are archived points.
CONDITIONS = (("co2", 1750., .001), ("co2", 1200., 1.),
              ("h2o", 1800., .001), ("h2o", 1200., 1.))
# One condition per feed also runs at 40 phase points, to show that the answer
# is not a property of the sampling grid.
SAMPLING_GATES = (("co2", 1750., .001), ("h2o", 1200., 1.))
# Named rings tracked out of the C7+ bucket. Everything else in that bucket is
# reported as a remainder, so the partition still closes.
RINGS = ("C10H8", "C12H8", "C14H10", "C16H10")
MECHANISM_LABELS = {
    "creck": "CRECK 2003 high temperature with soot and NOx",
    "gri": "GRI-Mech 3.0",
}
MECHANISM_CAVEATS = {
    "creck": ("The CRECK BIN species are lumped soot precursors, not a measured soot yield."),
    "gri": ("GRI-Mech 3.0 has no species above C3 and no aromatic chemistry, and it is a "
            "natural-gas combustion mechanism that is not validated for oxygen-free pyrolysis "
            "above about 1200 C. Its result here bounds what the mechanism can represent, not "
            "what the chemistry does."),
}


def archived_aramco(feed, T, tau):
    """The archived Aramco metrics row for one condition, or an assertion."""
    for directory in ARCHIVES[feed]:
        for row in json.loads((ROOT / directory / "data/summary.json").read_text()):
            if row["T_C"] == T and row["tau_s"] == tau:
                return directory, row
    raise AssertionError(f"{feed} {T} C {tau} s is not in the archived map")


def case_name(mech, feed, T, tau):
    return f"{mech}-{feed}-T{T:g}-tau{tau:g}"


def pah_partition(case_json):
    """Outlet carbon by ring size, as fractions of carbon out.

    C7+ is the mechanism's whole heavy pool. The named rings are pulled out of
    it and the rest is reported as `BIN_and_other`, which for CRECK is mostly
    the lumped soot-precursor particles.
    """
    audit = case_json["carbon_audit"]
    total = audit["carbon_out_kmol"]
    assert total > 0 and audit["group_partition_ok"]
    species = audit["species_out_kmol"]
    heavy = audit["groups"]["C7+"]["fraction_of_carbon_out"]
    named = {r: species.get(r, 0.) * _carbon_atoms(r) / total for r in RINGS}
    bins = sum(v * _carbon_atoms(k) for k, v in species.items()
               if k.startswith("BIN")) / total
    return dict(C7plus_fraction=heavy, named_rings=named, BIN_fraction=bins,
                other_C7plus_fraction=heavy - sum(named.values()) - bins)


def _carbon_atoms(name):
    """Carbon atoms in a species, from the mechanism, not from the name."""
    return _CARBON[name]


_CARBON = {}


def load_carbon_counts(mechanism):
    import cantera as ct
    gas = ct.Solution(mechanism)
    return {s: gas.n_atoms(s, "C") for s in gas.species_names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=4, metavar=("FEED", "T", "TAU", "POINTS"))
    ap.add_argument("--name", default=None)
    # The mechanism under test. Aramco is the archived side and is never rerun.
    ap.add_argument("--mechanism", default="creck",
                    choices=[k for k in MECHANISMS if k != "aramco"])
    a = ap.parse_args()
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    if a.worker:
        feed, T, tau, points = a.worker
        name = a.name
        worker(out, float(T), float(tau), a.mechanism, int(points), name, feed=FEEDS[feed])
        if name == "cold":
            m = json.loads((out / "cold-metrics.json").read_text())
            assert abs(m["CH4_conversion"]) < 1e-8, "cold limit is not zero conversion"
        return

    start = time.monotonic()
    solver_sha = hashlib.sha256((ROOT / "tools/openmkm_dynamic/run_cstr_case.py").read_bytes()).hexdigest()
    aramco_sha = hashlib.sha256((ROOT / "tools/cantera/mechanisms/aramco20.yaml").read_bytes()).hexdigest()
    test_path = Path(MECHANISMS[a.mechanism])
    if not test_path.exists():          # a mechanism Cantera ships, named not pathed
        import cantera as ct
        test_path = Path(ct.__file__).resolve().parent / "data" / MECHANISMS[a.mechanism]
    test_sha = hashlib.sha256(test_path.read_bytes()).hexdigest()
    for feed in ARCHIVES:
        for directory in ARCHIVES[feed]:
            old = json.loads((ROOT / directory / "data/manifest.json").read_text())
            # Two manifest shapes exist in the archives: the hashes at the top
            # level, and the same two keys nested under "hashes".
            old = old.get("hashes", old)
            assert old["solver_sha256"] == solver_sha, directory + ": solver changed"
            assert old["mechanism_sha256"] == aramco_sha, directory + ": Aramco changed"
    reference = {f"{feed}-{T:g}-{tau:g}": dict(archive=archived_aramco(feed, T, tau)[0],
                                               metrics=archived_aramco(feed, T, tau)[1])
                 for feed, T, tau in CONDITIONS}

    jobs = [("co2", 26.85, .1, 20, "cold")]
    jobs += [(f, T, tau, 20, case_name(a.mechanism, f, T, tau)) for f, T, tau in CONDITIONS]
    jobs += [(f, T, tau, 40, "gate-sampling-" + case_name(a.mechanism, f, T, tau))
             for f, T, tau in SAMPLING_GATES]

    save(out, "manifest", dict(
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, budget_s=LIMIT, per_worker_s=PER_WORKER,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        solver_sha256=solver_sha, mechanism_sha256=test_sha,
        aramco_sha256=aramco_sha, mechanism_key=a.mechanism,
        mechanism_file=MECHANISMS[a.mechanism],
        mechanism=MECHANISM_LABELS[a.mechanism],
        feeds=FEEDS, pressure_Pa=101325.,
        closure="constant pressure prescribed constant T, equal inlet/outlet mass/tau; variable volume",
        reference_archives={k: v["archive"] for k, v in reference.items()},
        note=("Paired PAH comparison. The Aramco side is read from the archives listed above "
              "and is not recomputed. The two mechanisms are two models: no optimum, ranking "
              "or validation status transfers between them."),
        limitations=("Prescribed gas temperature, no heater energy balance, no particle "
                     "dynamics and no experimental validation of either mechanism at these "
                     "conditions. " + MECHANISM_CAVEATS[a.mechanism])))

    _CARBON.update(load_carbon_counts(MECHANISMS[a.mechanism]))
    done, rows, gates, active = [], [], [], None
    try:
        for feed, T, tau, points, name in jobs:
            active = name
            remaining = LIMIT - (time.monotonic() - start)
            if remaining < 10:
                raise TimeoutError("total budget exhausted")
            save(out, "status", dict(status="running", active=name, completed=done))
            with (out / (name + ".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", __file__, "--output-dir", str(out),
                                "--worker", feed, str(T), str(tau), str(points),
                                "--name", name],
                               stdout=log, stderr=subprocess.STDOUT, check=True,
                               timeout=min(PER_WORKER, remaining))
            case = json.loads((out / (name + ".json")).read_text())
            metrics = json.loads((out / (name + "-metrics.json")).read_text())
            partition = pah_partition(case)
            if name.startswith("gate-sampling-"):
                base = json.loads((out / (name[len("gate-sampling-"):] + ".json")).read_text())
                basep = pah_partition(base)
                worst = max(abs(partition["named_rings"][r] - basep["named_rings"][r]) for r in RINGS)
                worst = max(worst, abs(partition["C7plus_fraction"] - basep["C7plus_fraction"]),
                            abs(partition["BIN_fraction"] - basep["BIN_fraction"]))
                gate = dict(name=name, max_abs_carbon_fraction=worst)
                assert worst < 1e-5, gate
                gates.append(gate)
                save(out, "gates", gates)
            elif name != "cold":
                key = f"{feed}-{T:g}-{tau:g}"
                rows.append({"feed": feed, "T_C": T, "tau_s": tau,
                             "mechanism": a.mechanism,
                             a.mechanism: dict(metrics=metrics, pah=partition),
                             "aramco": reference[key]})
                save(out, "summary", rows)
            done.append(name)
            print(json.dumps(dict(case=name, wall_s=metrics["wall_s"])), flush=True)
        save(out, "status", dict(status="completed", completed=done, conditions=len(rows),
                                 gates_passed=len(gates), wall_s=time.monotonic() - start))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=done,
                                 reason=str(exc), wall_s=time.monotonic() - start))
        raise


if __name__ == "__main__":
    main()
