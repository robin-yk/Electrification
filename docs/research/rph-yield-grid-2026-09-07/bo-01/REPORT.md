# First Bayesian acetylene-yield iteration

Training: 67 accepted conditions. Bounds: 1400 to 2000 C, .10 to .80 s hot hold, 12.5 to 200 sccm (log flow). Fixed gas-temperature waveform family, volume, pressure and equimolar feed.

Development holdout: 12 points, RMSE 0.1126 percentage points, maximum error 0.3275. This single split does not establish accuracy throughout the domain or experimental validity.

EI recommendation: 1682.142944 C, 0.800000 s, 12.500000 sccm. Predicted total-feed-carbon C2H2 yield 17.62852%, GP posterior SD 1.04970 percentage points.

Direct verification status: stopped; elapsed 16.17 s.

Failure: Command '['/opt/hostedtoolcache/Python/3.11.16/x64/bin/python', '/home/runner/work/Electrification-Suite/Electrification-Suite/tools/openmkm_dynamic/run_rph_yield_grid.py', '--worker', '--output-dir', '/home/runner/work/Electrification-Suite/Electrification-Suite/docs/research/rph-yield-grid-2026-09-07/bo-01/verification', '--peak', '1682.14294405234', '--hold', '0.7999999999999999', '--flow', '12.5', '--samples', '800']' returned non-zero exit status 1.. No direct-verified recommendation yield is admitted.

Sources: training.json, development-validation.json, proposal.json, search-audit.json, verification/manifest.json, verification/status.json and raw paired outputs. Earlier preflight bookkeeping failures are preserved and charged in the budget.
