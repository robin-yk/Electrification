# Candidate A reproduction failure

The run stopped after 109.50 s during reproduction of the archived 50 sccm case. No 100 sccm case was started. No new accepted candidate or energy-efficiency result was produced.

The analytic temperature-ramp check passed. Cycle 1 took 76.02 s and passed the sampled elemental, mass, temperature, and pressure checks. Periodic convergence was not established.

CVODES failed its repeated error test at simulation time 1.44409 s, during cycle 2, with error code -3 and an attempted step of 3.51481e-11 s. Full errors are retained in execution.log. This is a numerical integration failure in the Cantera 3.1 port, not a chemical performance result. Adaptive sparse preconditioning was enabled.

Before another flow case, reproduce the archived condition with an independently checked solver configuration. Preserve the failed attempt and compare any revised numerical tolerances against the archived species distribution and energy quadrature. Candidate B and higher peaks remain untested in this pilot.

Operational correction: progress messages initially relied on the last cycle diagnostic and missed the terminal failed status. Future progress checks must read status.json before treating progress.json as an active run.
