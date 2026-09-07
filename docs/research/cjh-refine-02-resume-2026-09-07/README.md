# Verified refinement 02 completion

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34085563713
Generation commit: 3be6f1b. All three gates passed before twelve new points.
Two completed raw gate solutions were reused from run 34085150481 after
archive hash, input, mechanism, convergence and balance checks. Their original
execution time remains charged separately; continuation wall time includes
cache verification and all new work. See data/status.json and the budget ledger.

REPORT.md, analysis.json and pareto.svg combine the initial, first-refinement
and current summaries. Regenerate with summarize_cjh_map.py --summaries
docs/research/aramco-cjh-2026-09-07/data/summary.json
docs/research/cjh-refine-01-2026-09-07/data/summary.json
docs/research/cjh-refine-02-resume-2026-09-07/data/summary.json
--output-dir docs/research/cjh-refine-02-resume-2026-09-07.

data/gates.json reports all-species mol/feed-C and conversion differences.
The checks increase output sampling and steady-state observation duration;
they do not vary integrator tolerances or initial composition. The new points
use the base settings, so maxima introduced here need their own refinement.
Both sampled product maxima are at the current lower residence-time boundary.
The computed map is neither a global optimum nor an energy-validated device.

The stopped-run original archive is ../cjh-refine-02-2026-09-07/.
That original status remains stopped even though its comparison was corrected
and its completed integrations were reused in this successful continuation.
