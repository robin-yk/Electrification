# Fixed-volume CJH feed-ratio pilot

User requested five CH4:CO2 ratios for Figure 2. Prescribed gas temperature
1750 C, 1 atm target, 50 sccm total at 0 C/1 atm, no dilution. Fix volume
to the archived 1:1, 1750 C, 1 ms equivalent CSTR value, computed from the
full outlet molar inventory. This is not the physical CFP heated region.

New closure: fixed volume, fixed inlet mass flow for each feed mixture,
pressure-regulated outlet. Energy off. Residence time is an output.
Use IdealGasMoleReactor and a pressure controller with K=1e-8 kg/s/Pa.
Require pressure within 1e-4 relative, volume invariant, mass flow within
1e-6, elemental outlet/inlet flux residuals below 1e-5, and stationarity
below 1e-8 for five consecutive observations, minimum twenty observations.
Observations are 5 ms apart. Sparse preconditioner; single thread.

Run cold GRI analytic control, Aramco 1:1 anchor against archived full-species
mol/feed-C within 1e-5, then tighter rtol/atol at the anchor within 1e-5.
Only if all pass, run 1:4, 1:2, 2:1, 4:1. Seven integrations including
controls, five physical operating conditions. Pilot estimated 2-6 minutes,
540 s reserved, 100 s worker cap, no retries. Any gate failure halts the batch.
This is a small requested compositional pilot, not a new bulk search.

Preserve raw species, carbon yields, g/h, conditional g/gCFP/h using 28.8 mg,
pressure, volume, residence time, elemental residuals, convergence histories,
input hashes, logs and elapsed time. No solid carbon, inlet heating, heat
loss, or electrical feasibility claim. Existing map and solver are unchanged.
Record sources and this generator before execution. Compare pressure-controller
or initial-state alternatives separately if the stated gates do not settle
model matching; do not silently relax acceptance tolerances.
