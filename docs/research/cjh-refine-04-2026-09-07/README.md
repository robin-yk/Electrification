# Ethylene boundary refinement 04 completed

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34092910653
Generation commit: 98ed754. Both strengthened sampling/horizon gates and
twelve new points completed. Raw status records elapsed time, gates.json
records agreement, and manifest.json records inputs and source/model hashes.

REPORT.md combines 57 unique points using summarize_cjh_map.py --summaries
with data/summary.json from the baseline, refinement 01, refinement 02 resume,
refinement 03 and this archive; --output-dir is this directory. No raw data
are overwritten. Verify the archive using archive_checksums.py --verify.

The sampled C2H2 maximum moved to an intermediate temperature, while C2H4
still peaks at the lowest sampled residence time and highest temperature.
Next candidate checks must precede new-point interpretation. These are
homogeneous chemical predictions at prescribed gas T, not demonstrated power,
geometry, heat-transfer or mixing conditions. The refined gates do not test
initial-state dependence or integrator tolerances, or prove mechanism accuracy.
