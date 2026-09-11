# Candidate A reproduction, attempt 02

Purpose: test whether retaining CVODES history across consecutive isothermal segments removes the archived-condition reproduction failure. The failure cause remains unresolved.

Only A at 50 sccm is queued, with four and eight samples per archived segment. The 384-segment temperature history, mechanism, fixed volume, pressure control, feed, tolerances, and sparse preconditioner remain unchanged. Reset CVODES only when the prescribed slope changes. This removes redundant resets within the 128 consecutive hold segments while preserving output sampling.

Run: `cantera-env/bin/python tools/openmkm_dynamic/rph_candidate_flow_pilot.py --attempt02` from the repository using the absolute interpreter path.

Hard wall limit: 300 seconds for the entire paired attempt. No automatic retries. No 100 sccm run in this attempt. Preserve the original failed directory. Estimated cost: at most five single-thread minutes.

Acceptance: inert ramp, periodic convergence, mass and elemental closure, paired species difference below 1e-4 mol/mol feed carbon, paired positive-input difference below 1%, and archived species reproduction below 1e-4. Stop on any failure. Store outputs, diagnostics, source hashes, and terminal status here. The atlas and manuscript remain unchanged until these checks pass.

Regression: `test_rph_slope_history.py` checks that a sequence containing repeated slopes causes three resets rather than seven.
