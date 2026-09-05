#!/usr/bin/env python3
"""The temperature step must not create or destroy any species.

Run by hand, GRI only, a few seconds:

    python3 tools/openmkm_dynamic/test_step_closure.py

Before step_temperature existed the march set gas.TP and called
syncState(), which keeps the reactor volume and rescales the mass: gas of
the current composition was discarded on heating and invented on cooling.
The element audit closed anyway, because the swap conserves elements as
long as the vessel holds feed-composition gas, so the first check fills the
vessel with argon and turns the chemistry off. Carbon then enters only
through the inlet, and in minus out minus inventory change must be zero to
within the rectangle rule of the outflow integral. Against the old march
this residual is tens of percent; with the fix it is under one.

The second check is the unit fact behind it: across one heating step the
species mass that left the vessel equals the species mass expelled, and
across one cooling step the mass gained is feed.
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_cstr_case import (add_common_args, build_params, integrate,
                           make_reactor, step_temperature)

FAILURES = []


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def params(**over):
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    parser.add_argument("--period-s", type=float)
    args = parser.parse_args(["--mechanism", "gri30.yaml", "--feed", "CH4:0.05, AR:0.95",
                              "--t-min-c", "500", "--t-peak-c", "1800", "--period-s", "1.0",
                              "--duty", "0.05", "--residence-time-s", "0.2",
                              "--min-cycles", "1", "--max-cycles", "1", "--frozen"])
    p = build_params(args)
    p.update(over)
    return p


def march_closure(ct):
    print("frozen march from an argon-filled vessel")
    p = params(initial="AR:1.0")
    _, _, cycles, audit = integrate(ct, "gri30.yaml", p)
    r = audit["elements"]["C"]["residual_fraction_of_in"]
    check("carbon in - out - inventory closes to the outflow rule", abs(r) < 0.01,
          f"residual {100 * r:+.2f} % of carbon in")
    check("nothing reacted, so the conversion is the flush transient only",
          -0.01 < cycles[-1]["ch4_conversion"] < 1.0)


def step_conservation(ct):
    print("one temperature step")
    p = params()
    gas, reactor, _, _, _ = make_reactor(ct, "gri30.yaml", p)
    gas.TPX = 773.15, p["pressure_Pa"], "CH4:0.02, C2H2:0.01, AR:0.97"
    reactor.syncState()
    y_feed = np.zeros(gas.n_species)
    y_feed[gas.species_index("CH4")], y_feed[gas.species_index("AR")] = 0.02, 0.98
    m0 = reactor.mass * np.asarray(gas.Y)
    expelled, drawn = step_temperature(reactor, gas, 2073.15, p["pressure_Pa"], y_feed)
    m1 = reactor.mass * np.asarray(gas.Y)
    check("heating: species left as expelled gas, nothing else",
          np.allclose(m0, m1 + expelled, rtol=0, atol=1e-12 * m0.sum()) and drawn == 0.0,
          f"expelled {100 * expelled.sum() / m0.sum():.1f} % of the mass")
    expelled2, drawn2 = step_temperature(reactor, gas, 773.15, p["pressure_Pa"], y_feed)
    m2 = reactor.mass * np.asarray(gas.Y)
    check("cooling: species gained are feed, nothing else",
          np.allclose(m2, m1 + drawn2 * y_feed, rtol=0, atol=1e-12 * m2.sum())
          and expelled2.sum() == 0.0,
          f"drew {100 * drawn2 / m2.sum():.1f} % of the mass as feed")
    # Mass is not restored, the vessel now holds lighter feed-rich gas; the
    # moles are, because PV/RT does not care what the gas is.
    mw = np.asarray(gas.molecular_weights)
    n0, n2 = (m0 / mw).sum(), (m2 / mw).sum()
    check("the round trip restores the moles", abs(n2 - n0) < 1e-10 * n0,
          f"{n0:.6e} -> {n2:.6e} kmol")


if __name__ == "__main__":
    import cantera as ct
    warnings.simplefilter("ignore")
    march_closure(ct)
    step_conservation(ct)
    print("all ok" if not FAILURES else f"{len(FAILURES)} failed: {FAILURES}")
    sys.exit(1 if FAILURES else 0)
