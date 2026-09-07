# First CJH gap-filling batch

The user approved an additional 60 minutes, <=10 minutes per batch, hourly
continuation. Reserve 540 seconds in docs/research/c2co-campaign-2026-09-07/budget.json
before dispatch. This batch has 12 new points in cjh-refine-01.json plus one
1400 C/0.1 s archive anchor. No simultaneous batch or automatic retry.

The initial 9-point Aramco map completed in 94.882232659 s including gates.
Temperature gaps are 400 C and residence-time gaps are factors of ten, so no
interpolation accuracy or optimum is established. New 1200/1600 C and
0.03/0.3 s samples address those gaps; this is a pilot refinement, not a
Bayesian claim. Estimated calculation duration 2-4 minutes, hard cap 9 minutes,
worker cap 90 seconds including loading. Stop on first failure.

Same feed, pressure, constant-temperature variable-volume CSTR closure,
solver and normalization as ARAMCO-CJH-RUN-CARD.md. Require original baseline
completion and identical solver/mechanism hashes, then reproduce all-species
anchor outputs within 1e-5 mol/mol inlet carbon before new points. Keep per-case
stationarity, mass and elemental gates. No transfer of device validation.

Outputs: raw JSON/logs, summary/status/manifest, all-species product rates,
conditional CFP mass-normalized rates. Commit archive and checksums after run.
Do not overwrite earlier grids. Reconcile failed and successful elapsed time
against budget. Unknown elapsed time retains the full reservation.

Command: python tools/openmkm_dynamic/run_aramco_cjh_baseline.py --output-dir out/cjh-refine-01 --cases-file tools/openmkm_dynamic/cjh-refine-01.json --reference-dir docs/research/aramco-cjh-2026-09-07/data
