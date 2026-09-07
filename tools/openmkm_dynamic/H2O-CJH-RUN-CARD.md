# CH4/H2O constant-temperature CJH map

Purpose: answer whether the CH4/CO2 map's shape survives changing the oxidant to
steam. One variable moves. Everything else, including the mechanism, the reactor
closure, the convergence settings and the (T, tau) grid, is held at the archived
CH4/CO2 values so the two maps are a pair. This is not an optimization, not a
device claim, and not an experimental validation of AramcoMech 2.0 for either
feed. User requested execution on 2026-09-07 and approved the 33-point grid.

## Inputs

Feed CH4:0.5, H2O:0.5 by mole, against the archived reference feed
CH4:0.5, CO2:0.5. Constant pressure at one atmosphere. Prescribed constant gas
temperature, energy equation off. Equal inlet and outlet mass flow reset each
segment to instantaneous reactor mass divided by residence time. AramcoMech 2.0
with the sparse Jacobian path. The generator asserts that the solver and
mechanism SHA256 match the manifest of `docs/research/aramco-cjh-2026-09-07`,
and that its own grid equals the union of the three archived summaries, so a
changed model or a drifted grid stops the run before any case starts.

Grid, 33 conditions, identical to the archive:

| T (°C) | τ (s) |
|---|---|
| 1000 | 0.01, 0.1, 1 |
| 1200 | 0.01, 0.03, 0.1, 0.3, 1 |
| 1300 | 0.01, 0.03 |
| 1400 | 0.01, 0.03, 0.1, 0.3, 1 |
| 1500 | 0.003, 0.01, 0.03, 0.1 |
| 1600 | 0.003, 0.01, 0.03, 0.1, 1 |
| 1700 | 0.003, 0.01, 0.03, 0.1 |
| 1800 | 0.01, 0.03, 0.1, 0.3, 1 |

## Execution

One subprocess per case. Order: the cold nonreacting check, then the two gated
map points, then their four gates, then the remaining 29 map points. Gates close
before the bulk of the map is spent, so a failed gate stops the rest.

Map points use 20 phase points, minimum 3 cycles, maximum 100, boundary
tolerance 1e-8 on every species and 3 stable cycles. There are 38 executions:
1 cold, 33 map, 2 sampling gates, 2 horizon gates.

Measured cost on this machine, single threaded: 9.64 s for 1400 °C at τ 0.1 s.
Estimated total 7 to 12 minutes. Hard limits: 1800 s for the batch and 180 s per
case. No automatic retry. On any failure the run stops, preserves the completed
outputs, and writes the reason into `status.json`.

## Acceptance gates

1. Cold limit at 26.85 °C returns CH4 conversion below 1e-8.
2. Outlet mass partition residual below 1e-6, carbon group partition closes, and
   the periodic boundary converges. Enforced per case inside `run_three_pairs.execute`.
3. C, H and O element residuals, inventory change included, below 0.5 % of inlet.
4. Sampling gate at 1400 °C / 0.1 s and 1700 °C / 0.01 s: doubling to 40 phase
   points moves no species by more than 1e-5 mol per inlet carbon and CH4
   conversion by no more than 1e-5.
5. Horizon gate at the same two conditions: 20 minimum cycles with 1e-10
   tolerances and 5 stable cycles agree with the map settings to the same bounds.

These are numerical screening bounds. They do not bound mechanism error.

## Outputs

`docs/research/h2o-cjh-2026-09-07/`: per-case raw solver output, parameters,
metrics and log; `manifest.json` with the commit and the solver and mechanism
hashes; `gates.json`; `summary.json`; `status.json`; a deterministic `REPORT.md`;
and `checksums.json`. Carbon yields are per total inlet carbon. That denominator
is not the same quantity in the two feeds: with CO2 half the inlet carbon arrives
as CO2, with H2O all of it arrives as CH4. Reports carry CH4 conversion beside
every yield so the reader can renormalize. The acetic-acid stoichiometric ceiling
recorded by `product_metrics` is a CH4-plus-CO2 combination bound and carries no
meaning for this feed; the report does not quote it.

No soot model is included, so benzene is where the calculation stops rather than
where the carbon stops.

## Cache and invalidation

No result is reused and no existing artifact is overwritten or invalidated. The
CH4/CO2 map, its reports and the published plates are untouched. Changes are
confined to this card, `run_h2o_cjh_map.py`, and one backwards-compatible feed
parameter added to `run_aramco_cjh_baseline.py` whose defaults reproduce the
archived behavior exactly.

Generator: `python tools/openmkm_dynamic/run_h2o_cjh_map.py --output-dir <dir>`.
