# Reviewed acquisition search repair

User requested reinforcement after the rejected EI recommendation. Repair
only the acquisition search on the frozen 39-point GP. Do not refit the
model, change objectives/bounds, or run Aramco in this task.

Use 4096 deterministic Sobol seeds, all training points and box corners.
Run bounded local optimization from the 24 highest scoring seeds and retain
the best seed if a local result is worse. Audit against a separate 8192-point
Sobol set and the existing incumbent. Reject nonfinite, out-of-bounds or
duplicate recommendations. Passing the audit is not proof of a global EI
maximum and does not validate chemical yield.

Keep the rejected proposal and model untouched. Archive repaired proposal,
search diagnostics, source hashes and time under rph-yield-search-02-2026-09-07.
Cap 90 seconds, single thread, charged to the existing ledger; no automatic
retry on failure. Unit tests cover bad local optimization, continuous
refinement and invalid scores. Commit code/card before the frozen-model test.
