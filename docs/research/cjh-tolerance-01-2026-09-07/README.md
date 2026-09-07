# Explicit tolerance pilot completed

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34108821968
Generation commit: bd1d6f1. All four comparisons passed: default versus
archive and tighter versus default at each of two operating points.
The production chemistry solver and mechanism were unchanged.

REPORT.md is generated from raw status, comparisons and recorded integrator
settings by tools/openmkm_dynamic/summarize_cjh_validation.py with this
archive directory as its argument. Verify archive_checksums.py --verify.
Raw output, source hashes, logs and reference paths remain unmodified.

The result supports tolerance robustness at the two tested CJH candidates,
not the entire 69-point map or any RPH trajectory. Both tests start from feed
composition. Initial-state dependence and mechanism/physical validity remain
unresolved. No new condition was added and no follow-on simulation is active.
