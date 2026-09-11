# Energy logging of feasible yield incumbents

Replay round 3 candidate 0 and round 5 candidates 1 and 2 with unchanged chemistry, reactor closure, waveform, flow, tolerances and preconditioner. Record the gas first law at every output interval: change in internal energy plus outlet enthalpy minus inlet enthalpy at 298.15 K. Fixed volume gives zero boundary work. The feed reservoir used by the prescribed-temperature chemical calculation is unchanged.

Cap: 300 seconds total, 90 seconds per process, charged to the existing 3600-second ledger. Stop on any failed gate and preserve completed files. First run a paired nitrogen control, then paired 400/800-sample reacting cases. Require the archived species result to agree within 1e-8, phase species difference below 1e-4, and energy/input/cooling refinement within 0.5%. Retain the existing mass, element and periodic-state checks.

Postprocess with the existing 28.8 mg CFP heat-capacity table, two-face area 0.000608 m2, emissivity 0.57 and 298.15 K surroundings. Compare full radiation and 90% reduced net radiation at the prescribed waveform. Positive thermal input and required cooling are recorded separately. CFP and prescribed gas temperatures are equated in this conditional demand calculation. This does not change the BO acquisition objective or charge cooling electricity. No older result or manuscript is overwritten.

Outputs: energy-incumbents-01/ manifest, logs, raw chemical results, per-step gas energies, convergence gates and summaries. Code and this card are committed before execution. No automatic retry.
