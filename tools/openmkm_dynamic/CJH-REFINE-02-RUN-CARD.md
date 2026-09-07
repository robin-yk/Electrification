# CJH verification and refinement 02

Purpose: check the sampled C2H2 maximum, C2H4 maximum and intermediate
Pareto candidate before adding twelve chemical-only operating points.
User approved continuation within an additional 3600 s total, <=600 s/batch.
This batch reserves 540 s, workers <=120 s, expected 3-5 minutes.

Model unchanged: AramcoMech 2.0, CH4/CO2 50/50, 1 atm, prescribed constant
gas temperature, homogeneous constant-pressure CSTR. Fixed equal mass flows
are initialized from reactor mass/tau; volume can change. Temperature and
residence time are independent chemical-screening inputs, not a verified
CFP geometry or power setting. Sparse preconditioner remains enabled.

Three gates: 1600 C/0.01 s, 1400 C/0.01 s and 1400 C/0.3 s. Compare the
archived 20-point result against 80-point observation sampling, at least
20 blocks of 5 tau, five stable blocks, and 1e-10 state/output stopping
thresholds. Require all outlet species mol/feed-C and conversion differences
<1e-5, plus existing convergence, mass and elemental gates. These checks
do not change integrator rtol/atol or test alternate initial composition.
Failure stops before any new map point, with no automatic retry.

New points: 1500 and 1700 C at 0.003, 0.01, 0.03, 0.1 s; 1600 C at
0.003 and 0.03 s; 1300 C at 0.01 and 0.03 s. The 0.003 s points explicitly
extend the prior lower residence-time bound. Other axes stay fixed.
The observed deviation of the new 1600 C point from linear prediction on
the original grid is calculated in manifest.json to document sample need.
This is a grid-refinement diagnostic, not a surrogate learning curve.

Generator: run_cjh_refine_02.py; unchanged core run_cstr_case.py. The baseline
wrapper gains an allowlisted optional convergence override only. Existing
outputs remain immutable. There is no automatic cache overwrite or restart.
Tests cover acceptance/rejection of comparison gates and bounded job counts.

Outputs: status, manifest with source commit and model hashes, three gate
comparisons, full raw species audits and parameters/logs, twelve-point
summary. Archive under docs/research/cjh-refine-02-2026-09-07/, generate
combined map with summarize_cjh_map.py, and verify archive_checksums.py.
Reconcile actual wall time including failed work; unknown time retains
reservation. Reserve no next batch until this one is reconciled.

No global optimum, validated reactor, soot prediction, alternative initial
state robustness, or experimentally proven mechanism superiority is claimed.

## Diagnosed continuation

Run 34085150481 stopped on a positive-only output dictionary-key mismatch
after two successful gate integrations. See the immutable failure archive
docs/research/cjh-refine-02-2026-09-07/. The corrected comparator accepts
only negligible unmatched entries <=1e-12 mol/feed-C and retains the 1e-5
agreement threshold. A failing-first test establishes this correction.
Batch cjh-refine-02-resume reserves a separate 540 s and reuses the two raw
gate solutions after hash/input/convergence verification. Expected 2-4 minutes.
The third gate and all twelve new points remain unchanged. This is a manually
diagnosed continuation, not a blind retry; previously consumed time is charged.
