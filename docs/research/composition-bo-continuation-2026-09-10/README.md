# Ratio-constrained BO continuation

The archive preserves four sequential NEXTorch batches and their paired Cantera evaluations. It is copied from source checkpoint `1dfea92` in the historical continuation worktree. Original source checkpoint: `20f1db1`; runtime guard and third batch: `904aa94`. The original source paths in manifests are relative to that checkpoint's repository root.

All 12 recommendations pass their numerical gates. Ratio feasibility is separate. Best feasible acetylene carbon yields for CO/C2H2 targets 1, 1.5, and 1.75 are 37.34467%, 35.78823%, and 34.21158%. Figure 4 in manuscript v3 and Table S20 include all 12 evaluations. Full inputs, fitted-model states, predictions, raw outputs, hashes, and failed runtime attempts remain in `archive/`.

Reproduce from source checkpoint `1dfea92`, using `.venvs/nextorch-rph` for proposals and a Cantera 3.2.0 interpreter for verification. `cantera_runtime.py` enforces UTC0, C locale, and single-thread settings before execution. Never overwrite saved rounds. The next available round is 5; additional rounds require the campaign's cost and acceptance checks.
