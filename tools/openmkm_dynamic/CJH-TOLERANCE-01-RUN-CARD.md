# Explicit integrator tolerance pilot

Question: are representative C2H2 and C2H4 candidates robust to tighter
CVODES rtol/atol, beyond output sampling and stationarity tests?
Conditions: 1750 C/0.001 s and 1750 C/0.00006 s, each at default and
tight rtol=1e-11, atol=1e-19. Read and record actual defaults; assert the
selected values really are tighter. Four integrations, no new map points.

Use the unchanged production solver and mechanism, verified by baseline
hashes. An explicit diagnostic adapter wraps make_reactor solely to inspect
or set the ReactorNet tolerances before integration; no gas, reactor, feed,
mass flow or chemistry changes. Unit tests check default identity, setting
changes and rejection of a not-tighter comparison. This is a tolerance
diagnostic, not an independently implemented chemical solver.

Run default at 80 samples per 5-tau block and >=20 blocks, five stable blocks
with 1e-10 state/output thresholds. Compare against the archived map first,
then tight against default. Require species mol/feed-C and conversion
differences <1e-5; unmatched positive-only entries <=1e-12. Existing mass,
element and convergence gates remain. Any failure stops subsequent jobs.

Closures unchanged: AramcoMech 2.0, CH4/CO2=50/50, 1 atm, homogeneous
constant-pressure CSTR, prescribed gas T, variable volume and matched equal
inlet/outlet mass/tau flows, energy off, one thread, sparse preconditioner.
Initial composition stays equal to feed. Inspection found that integrate()
copies feed accounting from the initial reactor phase; changing that phase
before the copy would contaminate the inlet basis. A separate initial-state
test must explicitly preserve the true inlet composition and mass-flow basis.
Existing feed-initialized results are not affected by this potential misuse.

Reserve 540 s, worker <=120 s, expected 2-4 minutes. One active batch,
no automatic retries and no cache reuse; all failed elapsed time charged.
Outputs: raw parameters/results/logs, integrator defaults/effective values,
comparisons, manifest/source hashes and status. Archive at
docs/research/cjh-tolerance-01-2026-09-07/ and verify checksums.
Do not infer initial-state independence, mechanism accuracy, global optima
or reactor energy/geometry feasibility from this numerical pilot.
