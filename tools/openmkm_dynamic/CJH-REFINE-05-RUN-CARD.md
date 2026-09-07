# CJH peak bracketing refinement 05

Question: bracket the C2H2 peak near 1750 C/1 ms and determine whether C2H4
declines below the present 30-microsecond lower-tau boundary at 1800 C.
Prior evidence: the cumulative 57-point report at
docs/research/cjh-refine-04-2026-09-07/REPORT.md. The C2H2 maximum moved to
an intermediate temperature, while C2H4 still peaks at a boundary. Do not
interpret either sampled maximum as a global optimum. The manifest computes
preceding maxima directly from archived summaries.

Plan: cjh-refine-05.json. Two gates repeat 1750 C/0.001 s and
1800 C/0.00003 s with 80 samples per 5-tau block, >=20 blocks, five stable
blocks and 1e-10 stationarity thresholds. Require species mol/feed-C and
conversion agreement <1e-5; unmatched positive-only entries <=1e-12.
All mass, elemental and convergence checks remain. Failure stops new points.

Twelve new points: 1800 C at 3/10/60 microseconds; 1750 C at
10/30/60/100 microseconds and 2/3 milliseconds; 1700 C at 60 microseconds;
1725 C at 1/2 milliseconds. Inputs remain prescribed gas temperature,
AramcoMech 2.0, CH4/CO2=50/50, 1 atm, constant-pressure homogeneous CSTR,
fixed equal mass flows initialized as mass/tau, variable volume, energy off.
The unchanged solver uses the sparse preconditioner and one thread.

Microsecond residence times are chemical probes, not demonstrated device
conditions. Heat-transfer, mixing, continuum/geometry applicability and power
requirements require separate checks before translating these points to an
actual reactor. Initial-state and integrator-tolerance tests remain open.

Reserve 540 s from the existing budget; workers <=120 s, expected 3-5 minutes.
One batch in flight, no automatic retry, all failed work charged, unknown
time retained as reserved. No raw cache reuse. Store full raw outputs,
parameters, gates, source/model hashes and status under
docs/research/cjh-refine-05-2026-09-07/; generate cumulative report/checksums.
Existing archives stay unchanged. No mechanism-accuracy or global claim.
