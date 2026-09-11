# Yield and reaction-heat atlas

Local archive inventory and thermodynamic postprocessing. No reaction integration was performed.

![Atlas](atlas.png)

```json
{
  "local_files": 1817,
  "cached_branch_entries": 5311,
  "raw_unique_flow_results": 313,
  "physical_flow_groups": 166,
  "plotted_cases": 368,
  "scenario_points": 1048,
  "cases_by_mode": {
    "CJH": 336,
    "RPH": 32
  },
  "missing_or_excluded": 133,
  "legacy_pending": 3144,
  "new_reaction_integrations": 0,
  "wall_s": 27.588707583999998
}
```

The x-axis is carbon in acetylene divided by total inlet carbon. The y-axis is net product-minus-feed reaction enthalpy at 298.15 K divided by positive supplied heat. Color is outlet CO/C2H2 molar ratio. CJH circles and RPH triangles distinguish steady and cyclic temperature histories.

RPH input is reconstructed stepwise from stored gas energy, the archived CFP heat-capacity function, and radiation. The recorded inlet enthalpy is corrected to 298.15 K before positive and negative energy are separated. Gas-only panels omit CFP storage and radiation. Full and reduced-radiation panels retain the same prescribed chemical histories; reduced radiation may require additional cooling, retained in the data.

The overview groups feeds and energy boundaries. It is not a matched-device Pareto comparison. Volume, temperature, flow, and composition vary within the CH4/CO2 panels. Screening points that exceed a power supply limit remain conditional demand estimates, with no device-feasibility claim. Explicitly failed high-flow thermal iterates are excluded. No aggregate Pareto front is claimed across unlike conditions.

Exact physical-input grouping removes coarse/fine duplicates, preferring higher temporal resolution. Byte-identical source copies share an inventory entry. Distinct prescribed waveforms remain distinct conditions. GHSV is standard inlet volumetric flow divided by gas volume; it is absent for unscaled parcels.

Local files and cached branch paths are inventoried separately. JSONL, NPZ, large files, and legacy models without energy adapters remain indexed; they are not represented as energy points. This output does not assert numerical inspection of every cached historical branch blob.

## Files

- [Readable condition register](case-table.md): all 368 plotted condition records.
- Color scale: CO/C2H2 = 0–5; larger ratios share the upper color. Exact ratios remain in the records.
- case-table.json: conditions and exact source links.
- plot-data.json: one row per condition and energy scenario.
- missing-and-excluded.json: unsupported or failed flow results.
- legacy-pending.json: earlier closure records awaiting an energy adapter.
- file-inventory.json and cached-branch-inventory.json: search coverage.
- deduplication-aliases.json: duplicate and refinement provenance.

Reproduce with cantera-env Python: tools/openmkm_dynamic/build_energy_atlas.py. Plot with /usr/bin/python3 tools/openmkm_dynamic/draw_energy_atlas.py.
