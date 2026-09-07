# Short-residence refinement 03 completed

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34088470900
Generation commit: 14e6388. Both sampling/horizon gates and twelve new points
completed. See data/status.json for elapsed time, data/gates.json for errors,
and data/manifest.json for job inputs and source/model hashes.

REPORT.md combines 45 unique points from the initial, first refinement,
second-refinement continuation and current summaries. Reproduce with
tools/openmkm_dynamic/summarize_cjh_map.py --summaries using those four
data/summary.json paths and --output-dir docs/research/cjh-refine-03-2026-09-07.
No interpolated optimum is reported. Raw outputs remain unchanged.

C2H4 still peaks at the sampled lower residence-time boundary. C2H2 gains
little over the preceding map and peaks at the upper temperature boundary.
Neither boundary establishes a global optimum. New maxima have not yet
received their own enhanced sampling/horizon check. Initial-state and
integrator-tolerance tests, energy requirements and device feasibility remain
outside this completed chemical-only batch.
