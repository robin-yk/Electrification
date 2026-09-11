# Ratio-constrained Bayesian optimization checkpoint

Two batches of three NEXTorch-based RPH recommendations have been verified directly. All six pass the numerical criteria. The first three fail the assigned 2% relative product-ratio tolerance and do not update the feasible incumbents. Including them in the next fit produces three second-batch recommendations that satisfy their targets and improve on the composition-only baselines.

| Target CO/C2H2 | Baseline C2H2 carbon yield % | Round-2 direct yield % | Direct CO/C2H2 |
|---|---:|---:|---:|
| 1 | 36.065076 | 37.142972 | 0.990773 |
| 1.5 | 31.592038 | 33.859865 | 1.479561 |
| 1.75 | 29.578811 | 31.888052 | 1.736139 |

Carbon yields use total inlet carbon. Fixed flow is 50 sccm at 273.15 K and 101325 Pa; gas volume is 0.009228 cm3. The finite search domain is 1600-2000 C peak, .1-.8 s hot hold and .5-.8 methane fraction. Floor is 450 C; rise/fall/period are .025/.10/1 s. The selected six points all use .8 s hot hold.

NEXTorch fits separate carbon-yield GPs. A custom acquisition integrates positive acetylene improvement with ratio feasibility using the same acetylene realization. Independent output GPs are an approximation. Candidate-pool search, seeds, bounds, paired data hashes and predictions are saved in each round directory. The first fit uses 25 paired observations; the second uses 28. The sparse-domain acetylene holdout RMSE remains substantial and is reported, not hidden. See RUNCARD.md, software-environment.json and development-check.json for method details.

Reproduce proposal selection with `python tools/openmkm_dynamic/composition_bo.py --round N` only in a new authorized round with an idle reconciled budget. Never overwrite an existing round. The generator has synthetic acquisition tests via `--test`. Direct verification uses `verify_composition_bo.py` against the saved proposals. `round-*/verification/status.json` retains predicted/actual outputs, ratio error and feasibility separately from numerical gates.

Actions runs: round 1 = 34253444041; round 2 = 34253982984; CJH support = 34254266423. The four paired CJH support points are initial design data, not constrained CJH optima. No energy comparison is available. This checkpoint demonstrates feasible improvement, not global optimality, superiority to equal-budget random search, or RPH superiority over optimized CJH.

The budget includes proposal fitting and direct verification, including failed calculations if any. Setup/upload and agent work are excluded and must not be described as zero-cost overhead. The separate earlier local mechanism-loading failure and successful cloud support remain archived outside this ledger.
