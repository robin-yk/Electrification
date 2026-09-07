"""Small isothermal CSTR baseline using the audited transient solver at delta T=0."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPERATURES_C = (1000, 1400, 1800)
TAUS_S = (.01, .1, 1.)


def reference_rates(species_mol_per_feed_C, flow_sccm=50., mass_mg=28.8):
    # Feed is CH4/CO2 50/50, so one carbon per inlet molecule. Standard 0 C, 1 atm.
    mol_C_h = flow_sccm * 1e-3 * 60 / 22.414
    mw = {"C2H2": 26.038, "C2H4": 28.054, "C2H6": 30.07,
          "CO": 28.01, "H2": 2.016, "H2O": 18.015}
    rates = {s: species_mol_per_feed_C.get(s, 0.) * mol_C_h * m * 1000 / mass_mg
             for s, m in mw.items()}
    rates["C2_stable_sum"] = sum(rates[s] for s in ("C2H2", "C2H4", "C2H6"))
    return rates


def save(out, name, value):
    (out / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")


def worker(out, T, tau, mech, points, name, convergence_overrides=None):
    import run_cstr_case as solver
    import run_three_pairs as pairs
    from run_c2co_pilot import product_metrics
    ap = argparse.ArgumentParser()
    solver.add_common_args(ap)
    a = ap.parse_args([])
    a.t_min_c = a.t_peak_c = T
    a.period_s = 5 * tau  # convergence observation blocks, NOT physical pulses
    a.duty = a.ramp_up_fraction = a.ramp_down_fraction = 0.
    a.waveform = "square"
    a.feed = "CH4:0.5, CO2:0.5"
    a.residence_time_s = tau
    a.points_per_cycle, a.hot_min_points = points, 0
    a.min_cycles, a.max_cycles, a.record_cycles = 3, 100, 1
    a.cycle_tolerance = 1e-8
    a.jacobian = "sparse" if mech == "aramco" else "dense"
    p = solver.build_params(a)
    p.update(cycle_output_tolerance=1e-8, stable_cycles_required=3)
    if convergence_overrides:
        allowed = {"min_cycles", "max_cycles", "cycle_tolerance", "cycle_output_tolerance", "stable_cycles_required"}
        assert set(convergence_overrides) <= allowed
        p.update(convergence_overrides)
    save(out, name + "-parameters", p)
    pairs.OUT = out
    mechanism = "gri30.yaml" if mech == "gri" else str(ROOT / "tools/cantera/mechanisms/aramco20.yaml")
    m = pairs.execute(name, mechanism, p)
    r = json.loads((out / (name + ".json")).read_text())
    audit = r["carbon_audit"]
    ratios = {s: n / audit["carbon_in_kmol"] for s, n in audit["species_out_kmol"].items()}
    m.update(product_metrics(audit))
    m.update(T_C=T, tau_s=tau, mechanism=mech,
        mol_per_feed_carbon=ratios,
        conditional_mg_product_per_mg_CFP_h=reference_rates(ratios),
        normalization=dict(flow_sccm=50., standard_T_K=273.15, standard_P_Pa=101325.,
                           CFP_mass_mg=28.8, implemented_device=False))
    save(out, name + "-metrics", m)
    if name == "cold":
        assert abs(m["CH4_conversion"]) < 1e-8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=5)
    ap.add_argument("--cases-file", type=Path)
    ap.add_argument("--reference-dir", type=Path)
    a = ap.parse_args()
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if a.worker:
        T, tau, mech, pts, name = a.worker
        worker(out, float(T), float(tau), mech, int(pts), name)
        return
    start = time.monotonic()
    jobs = [(26.85, .1, "gri", 20, "cold")]
    for mech in ("gri", "aramco"):
        jobs += [(1400, .1, mech, pts, f"gate-{mech}-{pts}") for pts in (20, 40)]
    jobs += [(T, tau, "aramco", 20, f"T{T}-tau{tau}") for T in TEMPERATURES_C for tau in TAUS_S
             if (T, tau) != (1400, .1)]
    if a.cases_file:
        budget = json.loads((ROOT / "docs/research/c2co-campaign-2026-09-07/budget.json").read_text())
        assert budget["spent_s"] + budget["reserved_s"] <= budget["total_budget_s"]
        assert budget["batch_limit_s"] >= 540
        reservation = [b for b in budget["batches"] if b["id"] == a.cases_file.stem]
        assert len(reservation) == 1 and reservation[0]["status"] == "reserved"
        assert reservation[0]["reserved_s"] >= 540, "missing batch reservation"
        assert a.reference_dir, "refinement requires archived baseline gates"
        refstatus = json.loads((a.reference_dir / "status.json").read_text())
        assert refstatus["status"] == "completed" and refstatus["map_points"] == 9
        refmanifest = json.loads((a.reference_dir / "manifest.json").read_text())
        for key, file in (("solver_sha256", "tools/openmkm_dynamic/run_cstr_case.py"),
                          ("mechanism_sha256", "tools/cantera/mechanisms/aramco20.yaml")):
            assert hashlib.sha256((ROOT / file).read_bytes()).hexdigest() == refmanifest[key]
        selected = json.loads(a.cases_file.read_text())
        assert 0 < len(selected) <= 19
        assert len({(r["T_C"], r["tau_s"]) for r in selected}) == len(selected)
        jobs = [(1400, .1, "aramco", 40, "anchor")]
        jobs += [(r["T_C"], r["tau_s"], "aramco", 20, f"T{r['T_C']}-tau{r['tau_s']}") for r in selected]
    save(out, "manifest", dict(
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        jobs=jobs, budget_s=540, per_worker_s=90,
        feed="CH4:0.5, CO2:0.5", pressure_Pa=101325.,
        closure="constant pressure prescribed constant T, equal inlet/outlet mass/tau; variable volume",
        note="period_s is a 5-tau convergence observation block, not a heating period",
        solver_sha256=hashlib.sha256((ROOT / "tools/openmkm_dynamic/run_cstr_case.py").read_bytes()).hexdigest(),
        mechanism_sha256=hashlib.sha256((ROOT / "tools/cantera/mechanisms/aramco20.yaml").read_bytes()).hexdigest()))
    done, rows = [], []
    active = None
    try:
        for T, tau, mech, pts, name in jobs:
            active = name
            remaining = 540 - (time.monotonic() - start)
            if remaining < 10:
                raise TimeoutError("total budget exhausted")
            save(out, "status", dict(status="running", active=name, completed=done))
            with (out / (name + ".log")).open("w") as log:
                subprocess.run([sys.executable, "-u", __file__, "--output-dir", str(out),
                    "--worker", str(T), str(tau), mech, str(pts), name],
                    stdout=log, stderr=subprocess.STDOUT, check=True, timeout=min(90, remaining))
            m = json.loads((out / (name + "-metrics.json")).read_text())
            done.append(name)
            if name == "anchor":
                reference = json.loads((a.reference_dir / "gate-aramco-40-metrics.json").read_text())
                assert m["mol_per_feed_carbon"].keys() == reference["mol_per_feed_carbon"].keys()
                for s, n in m["mol_per_feed_carbon"].items():
                    assert abs(n - reference["mol_per_feed_carbon"][s]) < 1e-5, "archive anchor mismatch: " + s
            if name.startswith("gate") and pts == 40:
                base = json.loads((out / f"gate-{mech}-20-metrics.json").read_text())
                for s, n in m["mol_per_feed_carbon"].items():
                    assert abs(n - base["mol_per_feed_carbon"][s]) < 1e-5, f"{mech} sampling gate: {s}"
                assert abs(m["CH4_conversion"] - base["CH4_conversion"]) < 1e-5
            if mech == "aramco" and name != "anchor" and (pts == 40 or not name.startswith("gate")):
                rows.append(m)
                save(out, "summary", rows)
            print(json.dumps(dict(case=name, wall_s=m["wall_s"], X=m["CH4_conversion"])), flush=True)
        save(out, "status", dict(status="completed", completed=done, map_points=len(rows), wall_s=time.monotonic()-start))
    except Exception as exc:
        save(out, "status", dict(status="stopped", active=active, completed=done, reason=str(exc), wall_s=time.monotonic()-start))
        raise


if __name__ == "__main__":
    main()
