# Peak-bracketing refinement 05 completed

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34097793177
Generation commit: 1c1f714. Two strengthened sampling/horizon gates and all
twelve new points completed. Time and completion are in data/status.json;
agreement and negligible positive-only omissions are in data/gates.json.

REPORT.md combines 69 unique conditions; SAMPLING-PROGRESS.md reports the
successive best-yield gains, not predictive validation. Reproduce using
summarize_cjh_map.py and summarize_cjh_progress.py with --summaries pointing
to the baseline and refinements 01, 02-resume, 03, 04, 05 data/summary.json,
and --output-dir this directory. Raw outputs are immutable; verify checksums.

The C2H4 low-residence decline at 1800 C is now observed, so continued
automatic extension toward shorter tau is not justified. The last batch does
not improve the sampled C2H2 maximum and changes the C2H4 maximum only
slightly. This does not establish an everywhere-converged map or global peak.

Next priority is explicit integrator-tolerance and alternate-initial-composition
validation with matched feed and flow convention. Neither has been tested by
the current sampling/horizon gates. No new calculation is dispatched with
this archive; no budget is reserved. The larger chemical/energy/device study
remains unfinished and the authorized budget is not reset.
