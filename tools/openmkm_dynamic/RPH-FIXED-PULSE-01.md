# Fixed-volume periodic entry pilot

## Period pilot after successful pulse-02

Run 34156729563 passed inert, baseline and refinement gates in 15.732464199 s.
Next approved cases: period 0.5 and 2 s, all four segment fractions and all other
inputs unchanged. Each gets 400/800 samples per segment. Cap 240 s, worker 100 s.
Require the baseline archived status and all unchanged checks; stop before the
next period if the preceding refinement fails. This is a three-period comparison,
not Bayesian or global optimization. Outputs: rph-fixed-period-01-2026-09-07/data.

## Reviewed continuation: pulse-02

The user requested proceeding after the implementation audit. The inert pressure
deviation is consistent with finite controller conductance: for constant-P inert
gas, expansion outflow is m*dT/dt/T, giving deltaP approximately m*dT/dt/(T*K).
At t=0.00125 s the archived m=3.376694805e-9 kg, T=933.15 K and
dT/dt=48000 K/s predict 17.369 Pa versus observed 17.375 Pa.
Use K=1e-7 instead of 1e-8 to approximate the pressure target more closely.
This is a documented numerical boundary-control change, not a relaxed gate.
All acceptance limits, physical waveform, inlet flow and volume remain unchanged.
Archive separately under rph-fixed-pulse-02-2026-09-07. Cap remains 540 s.

Cap 540 seconds, single thread, each worker at most 180 seconds. Stop on failure.
Run inert N2 open-flow control, Aramco CH4/CO2 1:1 baseline, then refined pair.
Use existing gas waveform 600 to 1800 C, 1 s period, fractions .025/.05/.1/.825.
This is the previous computational pilot waveform, not an experimental gas
temperature measurement. Feed 50 sccm at 273.15 K/1 atm. Fixed volume is the
archived CJH equivalent volume. Inlet mdot is constant; pressure controller is
unchanged. Do not infer constant instantaneous residence time or electrical power.

Linear temperature derivative segments are integrated separately with explicit
corner restarts. Species outflow is trapezoid-integrated with 400/800 samples per
segment. Test finite-cycle inventory accumulation, not only inlet minus outlet.
Gates: temperature error <1e-4 K, relative pressure error <1e-4, mass and each
element finite-cycle residual <1e-3, state and species cycle changes <1e-7 for
two successive cycles (3 to 8 cycles), and all-species refinement error <1e-4
mol/mol inlet C. Small thresholds apply to numerical checks only.

Archive all completed raw outputs, failure diagnostics, source hashes and elapsed
time under docs/research/rph-fixed-pulse-01-2026-09-07/data. No automatic retry.
Do not queue half/double periods until both reacting resolutions pass.
