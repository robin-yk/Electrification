"""Fixed-volume, fixed-feed, pressure-regulated isothermal CSTR: steam ratios.

The CH4/CO2 composition sweep of `run_cjh_feed_ratio_01.py` with the oxidant
taken as an argument, so the same reactor can be swept with steam. The physics,
the tolerances, the stationarity criterion and the gates are copied rather than
imported: editing the original would change the `script_sha256` recorded in the
archived CH4/CO2 manifests, and those records are meant to stay attestable.

Faithfulness of the copy is not asserted, it is measured. The batch runs the
archived CH4/CO2 1:1 condition through this script and gates it against the
archived result, so a transcription error stops the run before any steam case.

The reactor volume is the one the CH4/CO2 sweep used, so both sweeps describe
one reactor. Residence time is an output and moves with composition.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MECH = ROOT / "tools/cantera/mechanisms/aramco20.yaml"
REF = ROOT / "docs/research/cjh-refine-04-2026-09-07/data/T1750-tau0.001-metrics.json"
CO2_SWEEP = ROOT / "docs/research/cjh-feed-ratio-02-2026-09-07/data"
BUDGET_S = 600
WORKER_S = 100


def read(p):
    return json.loads(Path(p).read_text())


def write(p, x):
    Path(p).write_text(json.dumps(x, indent=2, allow_nan=False) + "\n")


def settings(x, oxidant, volume):
    assert 0 < x < 1 and volume > 0
    return dict(T_K=2023.15, P_Pa=101325., flow_sccm=50., standard_T_K=273.15,
                standard_P_Pa=101325., volume_m3=volume,
                feed={"CH4": x, oxidant: 1 - x}, oxidant=oxidant)


def volume_reference():
    """The equivalent volume the CH4/CO2 sweep fixed, from the same archive."""
    beta = sum(read(REF)["mol_per_feed_carbon"].values())
    return .001 * 50 / 60 * (2023.15 / 273.15) * beta * 1e-6


def compare(ref, actual):
    keys = set(ref) | set(actual)
    err = max(abs(ref.get(k, 0) - actual.get(k, 0)) for k in keys)
    assert err < 1e-5, f"reference mismatch {err}"
    return err


def worker(out, name, x, oxidant, tight=0, cold=False):
    print("stage: importing cantera", flush=True)
    import cantera as ct
    import numpy as np
    started = time.monotonic()
    p = settings(x, oxidant, volume_reference())
    if cold:
        p["T_K"] = 300.
    print("stage: loading mechanism", flush=True)
    gas = ct.Solution("gri30.yaml" if cold else str(MECH))
    print("stage: mechanism loaded", time.monotonic() - started, flush=True)
    gas.TPX = p["T_K"], p["P_Pa"], p["feed"]
    feedY = gas.Y.copy()
    mw = gas.molecular_weights.copy()
    atoms = np.array([[gas.n_atoms(k, e) for k in range(gas.n_species)] for e in ("C", "H", "O")])
    flow_mol_s = 50 / 22414 / 60
    mdot = flow_mol_s * gas.mean_molecular_weight / 1000
    inlet = ct.Reservoir(gas, clone=True)
    exhaust = ct.Reservoir(gas, clone=True)
    r = ct.IdealGasMoleReactor(gas, energy="off", volume=p["volume_m3"], clone=True)
    mfc = ct.MassFlowController(inlet, r, mdot=mdot)
    pc = ct.PressureController(r, exhaust, primary=mfc, K=1e-8)
    net = ct.ReactorNet([r])
    net.rtol = 1e-11 if tight == 3 else 1e-9
    net.atol = 1e-15 * p["volume_m3"] if tight == 2 else 1e-17 * p["volume_m3"]
    net.preconditioner = ct.AdaptivePreconditioner()
    net.derivative_settings = {"skip-third-bodies": True, "skip-falloff": True}
    last, stable, hist = None, 0, []
    # Physical comparison times are identical between normal and tight runs.
    for block in range(1, 101):
        net.advance(block * .005)
        if block == 1 or block % 20 == 0:
            print("stage: integration", block, time.monotonic() - started, flush=True)
        y = r.phase.Y.copy()
        residual = 1. if last is None else float(max(np.max(abs(y - last[:-1])), abs(r.mass / last[-1] - 1)))
        last = np.r_[y, r.mass]
        stable = stable + 1 if residual < 1e-8 else 0
        hist.append(dict(time_s=net.time, residual=residual, P_Pa=r.phase.P, mass_kg=r.mass,
                         Y_CH4=float(y[gas.species_index("CH4")]),
                         Y_C2H2=float(y[gas.species_index("C2H2")]),
                         flow_ratio=pc.mass_flow_rate / mdot))
        if block >= 20 and stable >= 5:
            break
    write(out / (name + "-diagnostic.json"), dict(inputs=p, rtol=net.rtol, atol=net.atol,
        stable=stable, history=hist, moles_kmol=r.mass / r.phase.mean_molecular_weight,
        solver_stats=net.solver_stats, wall_s=time.monotonic() - started))
    assert stable >= 5, "stationarity failed"
    assert abs(r.phase.P / p["P_Pa"] - 1) < 1e-4, "pressure drift"
    assert abs(r.volume / p["volume_m3"] - 1) < 1e-12, "volume drift"
    inlet_C = mdot * float(np.dot(atoms[0], feedY / mw))
    molratio = (pc.mass_flow_rate * y / mw) / inlet_C
    ratios = {k: float(v) for k, v in zip(gas.species_names, molratio) if v > 0}
    fin = mdot * (atoms @ (feedY / mw))
    fout = pc.mass_flow_rate * (atoms @ (y / mw))
    errors = (fout - fin) / fin
    assert np.max(abs(errors)) < 1e-5, f"element flow residual {errors}"
    assert abs(pc.mass_flow_rate / mdot - 1) < 1e-6, "mass flow mismatch"
    if cold:
        assert max(abs(y - feedY)) < 1e-8, "cold analytic failed"
    cy = {k: float(gas.n_atoms(k, "C") * v) for k, v in ratios.items()}
    rates = {k: float(v * flow_mol_s * 3600 * gas.molecular_weights[gas.species_index(k)])
             for k, v in ratios.items()}
    # g/mol numerical molecular weights, flow_mol_s is mol/s.
    feed_g_per_mol = float(x * gas.molecular_weights[gas.species_index("CH4")]
                           + (1 - x) * gas.molecular_weights[gas.species_index(oxidant)])
    # Carbon per mole of feed. CO2 carries one, H2O carries none, so the
    # per-inlet-carbon normalization of `ratios` means different things per feed
    # and every quantity below that divides by it has to say which.
    carbon_per_feed_mol = x + (1 - x) * gas.n_atoms(oxidant, "C")
    inlet_CH4 = x / carbon_per_feed_mol
    inlet_ox = (1 - x) / carbon_per_feed_mol
    write(out / (name + ".json"), dict(name=name, inputs=p, mechanism=gas.source, engine=ct.__version__,
        rtol=net.rtol, atol=net.atol, pressure_controller_K=1e-8,
        mass_flow_kg_s=mdot, outlet_mass_flow_kg_s=pc.mass_flow_rate,
        mass_residence_time_s=r.mass / mdot, pressure_Pa=r.phase.P, volume_m3=r.volume,
        mol_per_feed_carbon=ratios, carbon_yields=cy, product_g_h=rates,
        product_g_per_g_CFP_h={k: v / .0288 for k, v in rates.items()},
        carbon_per_feed_mol=carbon_per_feed_mol,
        CH4_conversion=1 - ratios.get("CH4", 0) / inlet_CH4,
        oxidant_conversion=1 - ratios.get(oxidant, 0) / inlet_ox,
        # H2 mass over feed mass, the basis the CH4/CO2 sweep did not report.
        H2_wt_pct_of_feed=100 * ratios.get("H2", 0.) * carbon_per_feed_mol * 2.016 / feed_g_per_mol,
        elemental_flow_residuals=dict(zip(("C", "H", "O"), map(float, errors))),
        history=hist, wall_s=time.monotonic() - started))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--worker", nargs=5, metavar=("NAME", "X", "OXIDANT", "TIGHT", "COLD"))
    a = ap.parse_args()
    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if a.worker:
        name, x, oxidant, tight, cold = a.worker
        worker(out, name, float(x), oxidant, int(tight), bool(int(cold)))
        return
    assert read(CO2_SWEEP / "status.json")["status"] == "completed", "CH4/CO2 sweep incomplete"
    assert hashlib.sha256(MECH.read_bytes()).hexdigest() == read(CO2_SWEEP / "manifest.json")["mechanism_sha256"], \
        "mechanism changed since the CH4/CO2 sweep"
    # The CO2 anchor runs first: it gates this script against the archived sweep.
    jobs = [("cold", .5, "H2O", 2, 1),
            ("co2-anchor", .5, "CO2", 2, 0),
            ("h2o-anchor", .5, "H2O", 2, 0),
            ("h2o-anchor-tight", .5, "H2O", 3, 0),
            ("h2o-ratio-1-4", .2, "H2O", 2, 0),
            ("h2o-ratio-1-2", 1 / 3, "H2O", 2, 0),
            ("h2o-ch4-40", .4, "H2O", 2, 0),
            ("h2o-ch4-60", .6, "H2O", 2, 0),
            ("h2o-ratio-2-1", 2 / 3, "H2O", 2, 0),
            ("h2o-ratio-4-1", .8, "H2O", 2, 0)]
    write(out / "manifest.json", dict(
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        mechanism_sha256=hashlib.sha256(MECH.read_bytes()).hexdigest(), jobs=jobs,
        reference=str(REF.relative_to(ROOT)), co2_sweep=str(CO2_SWEEP.relative_to(ROOT)),
        budget_s=BUDGET_S, worker_limit_s=WORKER_S,
        note=("Steam companion to the fixed-volume CH4/CO2 composition sweep. Same reactor "
              "volume, temperature and standard volumetric feed; residence time is an output. "
              "No device heating model and no soot model.")))
    started = time.monotonic()
    done, gates, active = [], [], None
    try:
        for name, x, oxidant, tight, cold in jobs:
            active = name
            write(out / "status.json", dict(status="running", completed=done, active=name))
            left = BUDGET_S - (time.monotonic() - started)
            assert left > 5, "batch exhausted"
            with (out / (name + ".log")).open("w") as log:
                subprocess.run([sys.executable, __file__, "--output-dir", str(out), "--worker",
                                name, repr(x), oxidant, str(tight), str(cold)],
                               check=True, timeout=min(WORKER_S, left), stdout=log,
                               stderr=subprocess.STDOUT)
            r = read(out / (name + ".json"))
            if name == "co2-anchor":
                gates.append(dict(name="archived CH4/CO2 chemistry reproduced",
                                  max_abs=compare(read(REF)["mol_per_feed_carbon"], r["mol_per_feed_carbon"])))
            if name == "h2o-anchor-tight":
                gates.append(dict(name="integrator refinement",
                                  max_abs=compare(read(out / "h2o-anchor.json")["mol_per_feed_carbon"],
                                                  r["mol_per_feed_carbon"])))
            done.append(name)
            write(out / "gates.json", gates)
            print(json.dumps(dict(case=name, wall_s=r["wall_s"])), flush=True)
        write(out / "status.json", dict(status="completed", completed=done, gates=len(gates),
                                        wall_s=time.monotonic() - started))
    except Exception as e:
        write(out / "status.json", dict(status="stopped", completed=done, active=active,
                                        reason=str(e), wall_s=time.monotonic() - started))
        raise


if __name__ == "__main__":
    main()
