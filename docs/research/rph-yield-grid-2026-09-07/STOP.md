# Periodic-output gate failure

Run34174250027 stopped stage3 at1600 C, .80 s hot hold,12.5 sccm,
800 samples per segment. Two preceding pairs passed. Coverage59/75;
85 cumulative validated RPH conditions including26 off-grid observations.
The400-sample result alone is not accepted as a new verified point.

At cycle8, maximum output change2.4284775207439324e-7 exceeds1e-7;
cycle7 was1.3663329864743723e-7. End-state change1.358e-12 is small.
Pressure relative error2.920e-5, temperature error2.232e-7 K, and mass/
element residual magnitude6.901e-5 all satisfy their existing thresholds.
These facts do not establish kinetic divergence. The discrepancy is between
cycle-integrated output stability and a nearly repeated endpoint state.
Possible quadrature/integrator effects require a separate numerical diagnosis;
neither is established by these logs alone.

Preserve raw failure, do not relax the1e-7 gate, and do not silently restart
stage3 (which would repeat completed cases). A diagnostic comparing integrated
output with identical phase sampling and tighter tolerances must precede any
reviewed continuation. No new diagnosis integration was run in this turn.

Charge55.162603814 s for failed stage3. New campaign total699.843320419 s
of3600 s. No active reservation. The Bayesian proposer is prepared but has
not been run; it explicitly requires75/75 coverage and its own reservation.
