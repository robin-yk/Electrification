# CJH short-residence boundary extension

Question: do the sampled C2H2 and C2H4 maxima turn down below 0.003 s?
The prior 33-point map cannot answer this because both maxima lie at its
lower residence-time boundary. The manifest records the preceding maxima
directly from summaries; this is a boundary diagnostic, not a GP learning curve.

Plan: cjh-refine-03.json. Two gates repeat 1700 C/0.003 s and 1500 C/0.003 s
with 80 output samples per 5-tau block, at least 20 blocks, 1e-10 convergence
thresholds and five stable blocks. Require species mol/feed-C and conversion
agreement <1e-5; negligible positive-only omissions <=1e-12 are handled by
the corrected comparator. Existing mass/element/convergence gates remain.
Failure stops follow-on points; no automatic retry.

Twelve new points span 1300-1800 C and 0.0003-0.003 s as listed in the JSON.
The same runner now accepts a committed plan rather than duplicating the
orchestrator for every batch. It rejects duplicate prior points and validates
reference condition/mechanism identity. No chemistry solver change.

Closures unchanged: AramcoMech 2.0, CH4/CO2=50/50, 1 atm, homogeneous
constant-pressure CSTR, energy off, fixed equal inlet/outlet mass flows from
initial mass/tau, variable volume. Sparse preconditioner, one thread. Gas
temperature prescribed; neither heating energy nor submillisecond device
realizability is established. Initial-state and integrator tolerance tests
remain open. New points use base settings, not the two gate settings.

Cost: reserve 540 s from the existing 3600 s authorization, worker <=120 s,
expected 3-5 minutes. One batch in flight. Unknown costs remain reserved;
all failed work counts. No raw cache reused in this batch.

Outputs: raw JSON/log/parameters, metrics, source/model hashes, comparison
gates, status and summary. Archive docs/research/cjh-refine-03-2026-09-07/;
regenerate the cumulative report from all four summaries and verify checksums.
Existing data remain immutable. No global-optimum or device-validation claim.
