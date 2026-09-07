# Fixed-volume periodic entry pilot

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
