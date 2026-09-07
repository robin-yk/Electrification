# One acetylene carbon-yield recommendation

User specified C2H2, not total C2. Maximize a single objective: percentage
of total CH4+CO2 inlet carbon recovered as outlet C2H2 over a converged
period. CO and CFP-normalized productivity remain diagnostic outputs, not
optimization objectives. This changes the objective, not merely its units.

Fit the 39 validated 450 C observations, including the first productivity
recommendation. Source-hash check and distinct-input check precede fitting.
Use NEXTorch single-objective EI, seed 20260908, raw percent yield standardized
by the library. Same bounds: peak 1200-1800 C, hold .025-.50 s, log-scaled
flow 50-1600 sccm. Floor 450 C, period 1 s, rise/fall .025/.10 s, fixed
equivalent gas volume, 1 atm and CH4/CO2 1:1 remain unchanged. No extension
outside these bounds, no CO constraint or weighting, no new physical closure.

Reserve 240 s: proposal 90 s max, chemistry 150 s max. Commit proposer/card
before fitting and commit the frozen candidate before direct calculation.
Charge actual proposal time and reduce reservation before dispatch. Expect
roughly 4 s fitting and 33 s verification based on the preceding step, not
a guarantee. Inert at candidate waveform/flow, exact archived 400 sccm
reproduction, then 400/800 candidate pair. All existing numerical gates apply.
Stop on a failure or duplicate recommendation; no automatic rerun or relaxed
threshold. One validated point is not proof of an optimum or calibrated GP.

Archive under docs/research/rph-yield-01-2026-09-07. Retain original productivity
training and result files, frozen yield prediction, all actual species yields,
g/g-CFP/h diagnostics, source hashes and elapsed time. Compare actual yield
with the incumbent and append only a gate-passing result for future learning.
No unattended second point. Heartbeat remains paused.
