# RPH comparison and cost-control archive

This directory preserves the downloaded computation results in Git, independently
of GitHub Actions artifact retention. Raw files and historical Wiki notes were
copied byte-for-byte. Earlier progress statements inside those notes describe
their original timestamp, not the current integration status.

## Status

- [Machine-readable completion inventory](completion.json): 11 of 12 reacting
  outputs exist. The missing output is `8300048-aramco-refined.json` (401 substeps).
  The resume run timed out before writing that result; this is not proof of
  numerical nonconvergence. No yield is fabricated for the missing result.
- [Combined summary](data/three-rph-pairs-2026-09-06/summary.json) and
  [resume log](data/three-rph-pairs-2026-09-06/resume.log).
- [Early-stop verification](data/early-stop-validation-2026-09-06/validation.json):
  three comparisons passed. This does not validate all pulse conditions.
- [Detailed operations design](low-cost-research-operations-2026-09-06.md), distinct
  from the executable run card. Proposed checkpoint/notification infrastructure
  remains unimplemented.
- [Historical comparison report](gri-aramco-three-rph-pairs-2026-09-06.md).

The source runs are [initial comparison](https://github.com/robin-yk/Electrification-Suite/actions/runs/34075748186),
[resume](https://github.com/robin-yk/Electrification-Suite/actions/runs/34077150687),
and [early stopping](https://github.com/robin-yk/Electrification-Suite/actions/runs/34078455559).
Source commits, conditions and mechanism hashes remain in their original
manifests. The archive commit is not the simulation commit.

## Integrity and scope

`checksums.json` gives SHA256 for every copied file. Rebuild this inventory with
`tools/openmkm_dynamic/archive_research_results.py --source WIKI_PROJECT --destination ARCHIVE`.
The archiver refuses to overwrite a differing file. Results are gas-phase
predictions with prescribed temperature, not experimental validation, soot
prediction, or a coupled electrical/thermal reactor model. See the run card and
original manifests for exact closures and acceptance criteria.

The newer C2/CO pilot run 34083149100 is separate from this 12-output comparison.
Its in-flight outputs are not part of this snapshot. No calculation is started
by generating or committing this archive.
