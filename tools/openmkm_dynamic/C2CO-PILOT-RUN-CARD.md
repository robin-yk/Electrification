# Bounded C2 and CO chemical pilot

User requested starting after an operating-condition table on 2026-09-07.
This is a small gated pilot, not a Bayesian campaign or reactor design claim.
No existing archived three-pair case uses these feeds and trapezoid settings.

All cases: 1 atm, prescribed gas temperature, period 1 s, low 600 C,
rise 25 ms, hot plateau 50 ms, fall 100 ms, low plateau 825 ms.
These ramps and low temperature are assumptions, not measured CFP traces.

| Case | CH4/CO2/He mol% | Peak C | Mass residence time s |
|---|---|---|---|
| P1 | 50/50/0 | 1800 | 0.1 |
| P2 | 5/5/90 | 1800 | 0.1 |
| P3 | 50/50/0 | 1400 | 0.1 |
| P4 | 50/50/0 | 1800 | 0.01 |

Constant-pressure homogeneous CSTR, equal inlet/outlet mass flow m/tau,
gas volume not fixed; this is not a 50 sccm quartz-tube reproduction.
Energy equation off; no insulation, wall power, heat transfer or solid carbon.
GRI dense and Aramco sparse preconditioned solvers retain existing code.

Run order: 300 K GRI nonreacting gate; P1 GRI 200/400; P1 Aramco 200/400;
then P2-P4 Aramco 200 only. At most 8 integrations. Stop on first failure.
Whole batch capped at 540 s, each worker at 120 s including mechanism load.
Cost estimate is bounded, not a promise to finish all cases. Single thread,
no retry. Source and card committed before dispatch. Existing full solver tests
and new denominator tests must pass before push. No solver code changes.

Gates: full-state and full-outflow differences <1e-8 three consecutive cycles,
min 3/max 100 cycles; C/H/O residual <0.5%, mass partition <1e-6,
carbon partition passes. P1 200/400 yield differences <=max(0.002, 2% refined),
CH4 conversion difference <=0.002. P2-P4 remain provisional without refinement.
Cold CH4 conversion absolute <1e-8. Time-limit stop is not numerical failure.

Outputs: full species integrals, trajectories, provenance, parameters, metrics,
refinement differences and status. H2O/H2 use mol per inlet carbon, not carbon
yield. AA bound is 3 min(nC2H2,nCO,nH2O)/nC,in, stoichiometric only.
No downstream kinetics, separations, make-up feed or commercial claims.

Cache: new output directory; no cross-model reuse. Completed outputs retained;
no integration checkpoint yet. No canonical artifacts invalidated or overwritten.
GitHub artifact c2co-chemical-pilot; download into Wiki project data with run ID.
Reproduce: python tools/openmkm_dynamic/run_c2co_pilot.py --output-dir out/c2co-pilot
