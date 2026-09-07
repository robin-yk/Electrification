# Fixed-volume RPH flow pilot

User approved six new conditions on 7 September 2026: total inlet 100/200/400
sccm and hot hold 0.10/0.50 s. Reuse existing 50 sccm points only after archive
reproduction with the modified input interface. Question: does throughput
increase product g/h despite reduced conversion at fixed gas volume?

Keep CH4/CO2 1:1, floor/peak 450/1800 C, period 1 s, rise/fall 0.025/0.10 s,
1 atm target, controller K=1e-7, and the archived equivalent gas volume fixed.
Flow is referenced to 273.15 K/1 atm, not hot-gas volume. This changes residence
time, not reactor volume. The prescribed gas waveform supplies whatever heat
is required; power demand and feasibility are not evaluated. No pressure or
period scan is authorized by this card.

Use the existing analytic ramp test and input tests, then inert 400 sccm,
50 sccm/0.10 s reproduction (all-species difference <1e-8), and six paired
400/800 runs. Existing waveform, pressure, finite-cycle elemental/mass and
periodic-state gates are unchanged; refinement error <1e-4 mol/mol inlet C.
First new 100 sccm pair gates the remaining conditions. Stop on first failure,
keep diagnostics, no automatic retry. The solver only replaces literal flow
with a validated positive input; preserve old default values and archives.

Cap 300 s total, 100 s per worker, single thread. Fourteen integrations,
including controls and refinement, are estimated at about 100 s from the
preceding screen's 6-8 s integrations, not a guarantee at the new flow rates.
Reserve within the existing 3600 s cumulative authorization before dispatch.
No new learning-curve or Bayesian campaign is included.

Commit generator/card before dispatch. Archive all species, carbon yields,
g/h and conditional g/g-CFP/h at 28.8 mg, inputs, source/mechanism hashes,
diagnostics and timings in docs/research/rph-flow-01-2026-09-07/data.
Report all eight flow/hold combinations and residual feed carbon. Old 28-point
450 C results remain valid for their original inputs; their frozen source
hash guard intentionally prevents silently rerunning under changed code.
