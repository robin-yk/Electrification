"""Bounded, sequential GRI/Aramco comparison using the existing CSTR solver."""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import cantera as ct
import run_cstr_case as solver

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out/three-pairs"
SOURCES = [(6300012, "design-wide-frontier-w3.jsonl"),
           (6000015, "design-wide-frontier2-w2.jsonl"),
           (8300048, "design-wide-aimed-lowduty-w3.jsonl")]


def save(name, value):
    (OUT / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")


def parameters(record, points):
    i = record["inputs"]
    parser = argparse.ArgumentParser()
    solver.add_common_args(parser)
    parser.add_argument("--period-s", type=float)
    args = parser.parse_args([])
    args.waveform = "physical"
    args.t_min_c = 25.0
    args.voltage = i["voltage_V"]
    args.period_s = i["period_s"]
    args.duty = i["duty"]
    args.residence_time_s = i["tau_s"]
    args.feed = i["feed"]
    args.points_per_cycle = points
    args.min_cycles = 20
    args.max_cycles = 100
    args.record_cycles = 1
    args.cycle_tolerance = 1e-8
    return solver.build_params(args)


def metrics(r):
    a = r["carbon_audit"]
    c = a["carbon_in_kmol"]
    species = a["species_out_kmol"]
    y = {s: n * species.get(s, 0.0) / c
         for s, n in [("C2H2", 2), ("C2H4", 2), ("C2H6", 2),
                      ("C6H6", 6), ("CO", 1)]}
    y["C2_total"] = a["groups"]["C2"]["carbon_kmol"] / c
    y["C6_total"] = a["groups"]["C6"]["carbon_kmol"] / c
    return {"carbon_yields_per_feed_carbon": y,
            "CH4_conversion": r["cycle_summary"]["mean_ch4_conversion"],
            "cycles": r["cycle_summary"]["cycles_to_convergence"],
            "boundary_residual": r["cycle_summary"]["cycle_boundary_residual"],
            "element_residuals": {e: v["residual_fraction_of_in"]
                                  for e, v in a["elements"].items()}}


def execute(name, mech, p):
    cached = OUT / (name + ".json")
    if cached.exists():
        r = json.loads(cached.read_text())
        assert r["mechanism"] == mech, name + ": cached mechanism mismatch"
        for key, value in r["inputs"].items():
            assert p[key] == value, name + ": cached input mismatch " + key
        mech_path = Path(mech)
        if not mech_path.exists():
            mech_path = Path(ct.__file__).resolve().parent / "data" / mech
        digest = hashlib.sha256(mech_path.read_bytes()).hexdigest()
        assert r["mechanism_provenance"]["mechanism_sha256"] == digest, name + ": cached mechanism hash mismatch"
        m = metrics(r)
        assert r["cycle_summary"]["converged"] and m["boundary_residual"] < p["cycle_tolerance"]
        assert r["carbon_audit"]["group_partition_ok"]
        assert abs(r["outflow_mass_partition_residual"]) < 1e-6
        assert max(abs(x) for x in m["element_residuals"].values()) < 0.005
        m["wall_s"] = r["wall_s"]
        m["reused"] = True
        print("REUSE", name, json.dumps(m), flush=True)
        return m
    print("START", name, "substeps", len(solver.phase_grid(p)), flush=True)
    started = time.perf_counter()
    r = solver.run_case(mech, p)
    r["wall_s"] = time.perf_counter() - started
    # Sum of all outlet species masses, independently of the eleven-species recorder.
    gas = ct.Solution(mech)
    gas.TPX = p["t_min_K"], p["pressure_Pa"], p["feed"]
    c_per_kg = sum(gas.Y[k] / gas.molecular_weights[k] * gas.n_atoms(k, "C")
                   for k in range(gas.n_species))
    mass_in = r["carbon_audit"]["carbon_in_kmol"] / c_per_kg
    mass_out = sum(n * gas.molecular_weights[gas.species_index(s)]
                   for s, n in r["carbon_audit"]["species_out_kmol"].items())
    r["outflow_mass_partition_residual"] = mass_out / mass_in - 1
    save(name, r)
    m = metrics(r)
    m["wall_s"] = r["wall_s"]
    print("RESULT", name, json.dumps(m), flush=True)
    assert r["cycle_summary"]["converged"], name + ": periodic convergence failed"
    assert r["carbon_audit"]["group_partition_ok"], name + ": carbon grouping failed"
    assert abs(r["outflow_mass_partition_residual"]) < 1e-6, name + ": mass partition failed"
    assert max(abs(x) for x in m["element_residuals"].values()) < 0.005, name + ": elemental balance failed"
    return m


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior_path = OUT / "manifest.json"
    prior = json.loads(prior_path.read_text()) if prior_path.exists() else None
    if prior:
        assert prior["commit"] == "e841b5d49a0530cc82b6f35a036af7a1c6f5ef7d", "unrecognized cache origin"
        assert prior["cantera"] == ct.__version__, "cached Cantera version mismatch"
        for path in ("tools/openmkm_dynamic/run_cstr_case.py", "tools/openmkm_dynamic/element_drive.py"):
            old = subprocess.check_output(["git", "show", prior["commit"] + ":" + path], cwd=ROOT)
            assert old == (ROOT / path).read_bytes(), "cached solver changed: " + path
        save("parent-manifest", prior)
    manifest = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "cantera": ct.__version__, "python": platform.python_version(),
                "platform": platform.platform(), "cases": SOURCES,
                "parent_commit": prior["commit"] if prior else None,
                "limits": {"element_fraction": 0.005, "periodic_Y": 1e-8,
                           "yield_refinement_absolute": 0.002, "yield_refinement_relative": 0.02}}
    save("manifest", manifest)
    records = []
    for idx, filename in SOURCES:
        path = ROOT / "tools/openmkm_dynamic/data/wide" / filename
        record = next(r for line in path.read_text().splitlines()
                      if (r := json.loads(line))["design_index"] == idx)
        records.append(record)
        save(str(idx) + "-source", {"file": str(path.relative_to(ROOT)),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "record": record})
    cold = parameters(records[0], 40)
    cold.update(waveform="square", t_min_K=300., t_peak_K=300., min_cycles=3, max_cycles=5)
    cold.pop("_profile")
    baseline = execute("cold-nonreacting-limit", "gri30.yaml", cold)
    assert abs(baseline["CH4_conversion"]) < 1e-8, "cold analytic zero-conversion limit failed"
    summary = {}
    for record in records:
        idx = str(record["design_index"])
        summary[idx] = {}
        for level, points in [("base", 200), ("refined", 400)]:
            p = parameters(record, points)
            grid = solver.phase_grid(p)
            save(idx + "-" + level + "-waveform", {
                "phase_width_temperature_K": [[ph, dp, solver.waveform_temperature(ph, p)] for ph, dp in grid]})
            for label, mech, jac in [("gri", "gri30.yaml", "dense"),
                                     ("aramco", str(ROOT / "tools/cantera/mechanisms/aramco20.yaml"), "sparse")]:
                p["jacobian"] = jac
                key = label + "-" + level
                summary[idx][key] = execute(idx + "-" + key, mech, p)
                save("summary", summary)
        for label in ("gri", "aramco"):
            a, b = (summary[idx][label + "-" + level] for level in ("base", "refined"))
            differences = {k: abs(v - b["carbon_yields_per_feed_carbon"][k])
                           for k, v in a["carbon_yields_per_feed_carbon"].items()}
            summary[idx][label + "-refinement_differences"] = differences
            save("summary", summary)
            for k, d in differences.items():
                v = abs(b["carbon_yields_per_feed_carbon"][k])
                assert d <= max(0.002, 0.02 * v), idx + " " + label + " " + k + ": refinement failed"
            assert abs(a["CH4_conversion"] - b["CH4_conversion"]) <= 0.002, idx + ": conversion refinement failed"
        print("PAIR PASSED", idx, flush=True)
    save("status", {"status": "completed", "validated_pairs": list(summary)})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        OUT.mkdir(parents=True, exist_ok=True)
        save("status", {"status": "stopped", "reason": str(exc)})
        raise
