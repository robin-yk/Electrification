# CH4/H2O composition sweep at fixed volume

Purpose: the CH4/CO2 composition sweep exists and the steam one does not, so
nothing says whether the strong composition dependence found with CO2 is a
property of the methane chemistry or of the oxidant. One variable moves, the
oxidant. This is a seven-composition sample, not an optimization, not a device
claim, and not an experimental validation of AramcoMech 2.0 for either feed.
User requested execution on 2026-09-07.

## Inputs

Feed CH4:x, H2O:(1-x) by mole against the archived CH4:x, CO2:(1-x) sweep.
Fixed gas temperature 1750 C, energy equation off. Total feed 50 sccm at 0 C and
1 atm. Fixed reactor volume, taken unchanged from the CH4/CO2 sweep's own
equivalent volume so both sweeps describe one reactor. Pressure controller holds
the outlet near 1 atm. Mass residence time is an output and moves with
composition; it is not held. AramcoMech 2.0 with the adaptive preconditioner.

Compositions, x = CH4 mole fraction: 0.2, 1/3, 0.4, 0.5, 0.6, 2/3, 0.8. These are
the seven the CH4/CO2 sweep used across its two batches, so the pair is complete.

## Execution

`run_h2o_feed_ratio.py`, one subprocess per case, ten executions: a cold control,
a CH4/CO2 anchor, a steam anchor, a tight-tolerance steam anchor, and six further
steam compositions. Order matters: the CH4/CO2 anchor runs second so its gate
closes before any steam case is spent.

The generator is a copy of `run_cjh_feed_ratio_01.py`, not an edit of it. Editing
the original would change the `script_sha256` recorded in the archived CH4/CO2
manifests, and those records are meant to stay attestable. The copy's
faithfulness is therefore not asserted but measured, by gate 2 below.

Measured cost of the CH4/CO2 sweep: 27.1 s for seven integrations. Ten are
estimated at 40 to 90 s. Hard limits: 600 s for the batch and 100 s per case. No
automatic retry. On failure the run stops, preserves completed outputs, and
writes the reason into `status.json`.

## Acceptance gates

1. Cold control at 300 K with GRI-Mech 3.0 returns the feed composition
   unchanged to 1e-8 in mass fraction.
2. The CH4/CO2 1:1 anchor reproduces
   `docs/research/cjh-refine-04-2026-09-07/data/T1750-tau0.001-metrics.json`
   to 1e-5 in every species per inlet carbon. This is what establishes that the
   copied generator is the same calculation as the archived one.
3. Tight-tolerance steam anchor, rtol 1e-11 and atol scaled to volume, agrees
   with the batch settings to the same 1e-5 bound.
4. Per case: stationarity residual below 1e-8 for five consecutive blocks;
   pressure within 1e-4 of target; volume drift below 1e-12; C, H and O flow
   residuals below 1e-5; inlet and outlet mass flow matched to 1e-6.

These are numerical screening bounds. They do not bound mechanism error.

## Outputs

`docs/research/h2o-feed-ratio-2026-09-07/`: per-case raw result, integration
diagnostic and log; `manifest.json` with the commit, script and mechanism hashes
and the reference paths; `gates.json`; `status.json`; a `REPORT.md`; and
`checksums.json`.

Carbon yields are per total inlet carbon, which is all methane with steam and
half CO2 with CO2, so the two sweeps are not one scale and the report carries
methane conversion and `carbon_per_feed_mol` beside every yield. Productivity in
g/h assumes 28.8 mg of carbon-fiber paper and does not establish heating
capacity. `H2_wt_pct_of_feed` is H2 mass over feed mass, the basis the CH4/CO2
sweep did not report; it is a reactor-outlet composition, with no separation,
recycle or heat integration modelled.

No soot model is included, so benzene is where the calculation stops rather than
where the carbon stops.

## Cache and invalidation

Nothing is reused, overwritten or invalidated. The CH4/CO2 sweep, its report and
every published plate are untouched, and no existing file is edited.

Generator: `python tools/openmkm_dynamic/run_h2o_feed_ratio.py --output-dir <dir>`.
