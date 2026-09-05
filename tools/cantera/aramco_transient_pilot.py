#!/usr/bin/env python3
"""Cost pilot: what would the transient pipeline cost with AramcoMech 2.0?

Answers one question before anyone commits to an Aramco ground-truth
campaign: how much slower is one transient CSTR cycle under AramcoMech 2.0
(493 species, 2716 reactions) than under GRI-Mech 3.0 (53 species, 325
reactions), and how much of that does Cantera's sparse preconditioned path
(--jacobian sparse in run_cstr_case.py) buy back?

Two representative cases bracket the design space, taken from the canonical
design set so the temperatures, periods and residence times are real:

  cjh-like  design 188  period 8.196 s   10 cycles to converge, peak 1784 C
  rph-like  design  27  period 0.0109 s  379 cycles to converge, peak 1359 C

This is a COST pilot, not ground truth. Two deliberate simplifications:
the stored "physical" waveform is replaced by a trapezoid between the same
t_min/t_peak (the element-drive profile is mechanism-independent and does
not change solver cost class), and each config runs a fixed small cycle
budget instead of converging (per-cycle cost is measured after the first
warmup cycle). The physics cross-check is that dense and sparse agree on
CH4 conversion at the final common cycle; agreement to about 7 significant
digits was observed for both mechanisms. Nothing here may be promoted to
data/canonical/.

Measured on the 2026-09 pilot (single thread, container hardware; ratios
travel better than seconds):

  case      gri-dense  aramco-dense  aramco-sparse   dense x   sparse x
  cjh-like  0.23 s/cy  14.9 s/cy     4.26 s/cy       65        19
  rph-like  0.12 s/cy   8.7 s/cy     2.78 s/cy       73        23

So a full Aramco re-run of the 349-case transient set projects to about
20x the measured GRI cost of ~1.7 h, i.e. ~1.5 days single-threaded, and
the GRI worst case (251 s) projects to ~90 min, inside CI job limits.

Run:  python tools/cantera/aramco_transient_pilot.py
Writes tools/cantera/data/aramco-transient-pilot.json.
"""
import json
import sys
import time
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "openmkm_dynamic"))
from run_cstr_case import make_reactor, waveform_temperature  # noqa: E402

import cantera as ct  # noqa: E402

ARAMCO = str(REPO / "tools" / "cantera" / "mechanisms" / "aramco20.yaml")
DESIGN = REPO / "tools/openmkm_dynamic/data/canonical/design-physical.jsonl"
OUT = Path(__file__).with_name("data") / "aramco-transient-pilot.json"

# design_index -> (name, fixed cycle budget); t_min/t_peak/duty/period/tau are
# loaded from the canonical row so the pilot cannot drift from real inputs.
PICKS = {188: ("cjh188", 4), 27: ("rph027", 6)}
COMMON = dict(waveform="trapezoid", ramp_up_fraction=0.05,
              ramp_down_fraction=0.05, pressure_Pa=101325.0,
              feed="CH4:1, CO2:1", points_per_cycle=100,
              closure="const-pressure")
CONFIGS = {
    "gri-dense": ("gri30.yaml", "dense"),
    "gri-sparse": ("gri30.yaml", "sparse"),
    "aramco-sparse": (ARAMCO, "sparse"),
    "aramco-dense": (ARAMCO, "dense"),
}


def load_cases():
    cases = {}
    for line in open(DESIGN):
        d = json.loads(line)
        pick = PICKS.get(d.get("design_index"))
        if pick:
            name, cycles = pick
            i = d["inputs"]
            cases[name] = {**COMMON, "cycles": cycles, "design_index":
                           d["design_index"],
                           **{k: i[k] for k in ("t_min_K", "t_peak_K", "duty",
                                                "period_s", "tau_s")}}
    missing = {n for n, _ in PICKS.values()} - set(cases)
    if missing:
        raise SystemExit(f"design rows not found for {sorted(missing)}")
    return cases


def run_config(mech, jacobian, p, n_cycles):
    gas, reactor, mfc_in, mfc_out, net = make_reactor(
        ct, mech, {**p, "jacobian": jacobian})
    i_ch4 = gas.species_index("CH4")
    y_feed = gas.Y[i_ch4]
    n_sub = p["points_per_cycle"]
    dt = p["period_s"] / n_sub
    t = 0.0
    cycle_times, conv = [], None
    for _cycle in range(n_cycles):
        t0 = time.perf_counter()
        w_ch4 = w_feed = 0.0
        for k in range(n_sub):
            phase = (k + 0.5) / n_sub
            gas.TP = waveform_temperature(phase, p), p["pressure_Pa"]
            reactor.syncState()
            mdot = reactor.mass / p["tau_s"]
            mfc_in.mass_flow_rate = mdot
            mfc_out.mass_flow_rate = mdot
            net.reinitialize()
            t += dt
            net.advance(t)
            y = reactor.phase.Y
            w_ch4 += mdot * y[i_ch4] * dt
            w_feed += mdot * y_feed * dt
        cycle_times.append(time.perf_counter() - t0)
        conv = 1.0 - w_ch4 / w_feed
    steady = cycle_times[1:] or cycle_times
    return {"cycle_s": [round(x, 3) for x in cycle_times],
            "per_cycle_s": sum(steady) / len(steady),
            "last_cycle_conversion": float(conv)}


def main():
    warnings.simplefilter("ignore")
    cases = load_cases()
    results = {"generated": time.strftime("%Y-%m-%d"),
               "cantera": ct.__version__,
               "note": "single-threaded cost pilot; ratios are the result, "
                       "absolute seconds are machine-specific; not ground "
                       "truth (trapezoid waveform, fixed cycle budget)",
               "cases": {}}
    t0 = time.perf_counter()
    ct.Solution(ARAMCO)
    results["aramco_load_s"] = round(time.perf_counter() - t0, 2)
    for name, case in cases.items():
        entry = {"inputs": case}
        for label, (mech, jacobian) in CONFIGS.items():
            r = run_config(mech, jacobian, case, case["cycles"])
            entry[label] = r
            print(f"{name} {label}: per-cycle {r['per_cycle_s']:.3f} s, "
                  f"X={r['last_cycle_conversion']:.7f}", flush=True)
        for label in ("gri-sparse", "aramco-dense", "aramco-sparse"):
            entry[label]["x_vs_gri_dense"] = round(
                entry[label]["per_cycle_s"] / entry["gri-dense"]["per_cycle_s"], 2)
        results["cases"][name] = entry
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(results, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
