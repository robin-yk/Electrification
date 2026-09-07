# Bounded stopping-policy validation

The user requested computation minimization and a low-token research design.
Do not interrupt the ongoing three-pair pilot or change its numerical controls.
The chemical mechanism, temperature waveform, reactor closure and phase grid
remain identical. Add an opt-in termination policy, not a reduced mechanism.

Existing evidence: 6300012 reaches boundary tolerance by cycle 2, and 6000015
by cycle 3, while the pilot enforced at least 20 cycles. Third-case GRI required
28 cycles, so a smaller minimum is not a universal acceleration.

Scope: one GRI and two Aramco base-grid repeats of archived cases solely to
validate early stopping. Require three consecutive stable full-species boundary
and cycle-averaged outflow states at absolute mass-fraction tolerance 1e-8.
Minimum 3, maximum 100 cycles. Reference C2H2/C2H4/C2H6/C6H6/CO and C2/C6 group
carbon yields and methane conversion must agree within absolute 1e-6. Existing
element and carbon partition gates remain. Stop on failure; no automatic retries.
Legacy solver defaults remain unchanged. No broad sweep or optimization starts.

Expected validation cost 2 to 4 runner minutes, computation-step cap 5 minutes,
job cap 7 to preserve partial artifacts. Combined calculation-step upper bounds:
first completed job under 25 minutes, continuation at most 29, this gate at
most 5, under the approved 60-minute computation envelope. Parallel execution
uses separate runners but does not increase the approved condition set beyond
these explicit validation repeats. Python BLAS/OMP single-threaded.

Generator: tools/openmkm_dynamic/validate_early_stop.py, committed before run.
Reference: artifact three-rph-pairs from run 34075748186. Outputs: isolated
out/early-stop, uploaded as rph-early-stop-validation, with source commit,
policy, full results, comparison errors, cycles and machine-specific elapsed
times. Compare cycle-count reduction directly; cross-run wall-time ratios are
indicative because runner hardware is not controlled. Do not overwrite the
original 20-cycle outputs or describe the new policy as validated before passing.

Unit test was run first and failed because periodic_gate did not exist. After
implementation it checks the legacy default, output-drift rejection, consecutive
acceptance and nonfinite rejection. Additional cache-key tests check identity
sensitivity. The compact digest is a reader, not an authoritative approval gate.
