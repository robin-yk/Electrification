# CJH ethylene boundary and temperature-gap check

Question: does C2H4 yield decline below the present short-residence boundary,
and how do intermediate temperatures change the C2H2/CO tradeoff?
Prior 45-point report: docs/research/cjh-refine-03-2026-09-07/REPORT.md.
The C2H4 maximum is at the lowest sampled tau, whereas the C2H2 maximum
increased only slightly after the previous expansion. The new batch therefore
targets the unresolved C2H4 boundary and 50 C temperature gaps, not an
unjustified uniform grid. Generator computes preceding maxima in its manifest.

Inputs: cjh-refine-04.json. First gate the 1800 C/0.001 s C2H2 candidate
and 1600 C/0.0003 s C2H4 candidate. Use the unchanged refinement runner,
80 samples per 5-tau block, >=20 blocks, five stable blocks and 1e-10
state/output thresholds. Require all species mol/feed-C and conversion
agreement <1e-5. Positive-only unmatched entries must be <=1e-12.
All existing mass, elemental and stationarity checks apply. Stop on failure.

Twelve new points: 1600/1700/1800 C at 0.0001 and 0.00003 s;
1750 C at 0.0003/0.001 s; 1650 C at 0.0001/0.0003 s;
1550 C at 0.0003/0.001 s. No points above 1800 C are proposed.
Model unchanged: AramcoMech 2.0, CH4/CO2 50/50, 1 atm, prescribed gas T,
constant-pressure homogeneous CSTR with fixed equal initial mass/tau flows
and variable volume. One thread and sparse preconditioner remain enabled.
Microsecond residence times are chemical probes, not demonstrated heater
or reactor designs. Integrator-tolerance and initial-state robustness remain
unverified; sampling/horizon gates do not establish those properties.

Reserve 540 s from the existing authorized budget, worker <=120 s, expected
3-5 minutes. No automatic retries, no simultaneous batch and no cache reuse.
Completed and failed work counts. Archive raw data, status, source/model
hashes, gates, cumulative report and checksums at
docs/research/cjh-refine-04-2026-09-07/. Prior data stay unchanged.
No global-optimum, experimental mechanism validation or device claim.
