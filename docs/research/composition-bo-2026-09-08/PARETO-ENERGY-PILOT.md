# Yield and energy frontier continuation

The user requested continuation of the Figure 3 yield/energy Pareto study on
11 September 2026. The existing 60-minute ledger has 845.03 seconds charged.
Each batch retains its 300-second cap. This pilot adds three energy replays,
each at 400 and 800 phase samples, before training an energy surrogate.
Estimated pilot cost: 1 to 5 minutes, single thread.

Use the existing fixed-volume, pressure-controlled AramcoMech 2.0 CSTR:
50 sccm at 273.15 K and 101325 Pa; 0.009228077898393763 cm3 gas volume;
1 atm; 450 C minimum; 1 s period; 25 ms rise and 100 ms fall.
Training-support cases are 1800 C with (hold seconds, methane mole fraction)
(0.1, 0.5), (0.5, 0.7), and (0.5, 0.8). Their previously verified chemistry
is reused as a strict replay check. This selection is deterministic support
design, not a Bayesian recommendation or a newly improved optimum.

The thermal evaluator is unchanged: CFP mass 28.8 mg, area 0.000608 m2,
emissivity 0.57, ambient 298.15 K, and retained net radiation fraction 0.1.
Positive thermal input includes gas demand, CFP storage and net radiation;
negative intervals define additional heat removal. Preserve full energy
histories for both radiation scenarios. Cooling electricity is unmodeled.

Reuse the recorded inert and reacting energy checks from energy-incumbents-01.
Require all physical_gate checks, phase species error below 1e-4,
replay species difference below 1e-8, input/cooling grid changes below 0.5%,
and energy-balance residual below 1e-6 J. Stop on any failure. Record elapsed
time, failures, source and generator hashes. No automatic retry or overwrite.

Outputs: pareto-energy-pilot-01/{0,1,2}/n{400,800}.json, energy histories,
summaries, manifest and status. The next decision is whether these energy
data support ratio-constrained expected hypervolume improvement. Figure 3
will gain directly verified feasible points only; other figures remain intact.

Preflight failure: importing composition_bo solely for its physical gate
also imported SciPy, absent in the dedicated Cantera environment. No mechanism
loaded and no integration started. The replay now carries the identical pure
Python checks without importing the optimization environment. No installation
was needed. The failed invocation took 0.15 seconds before ledger activation.
