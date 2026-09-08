# High-temperature boundary check

## Reviewed second attempt

The user explicitly requested a corrected rerun after the local timeout.
Use the established Ubuntu GitHub Actions environment, not the local macOS
runtime. Add flushed mechanism-load and integration-stage timings without
changing any solver tolerances or acceptance gates. Preserve the first attempt.
Write the second attempt to hot-boundary-02/data. The same 540-second batch
and 100-second worker caps apply. If it fails, stop and retain the stage logs.

User approved three points: 1900, 2000, 2100 C peak gas temperature;
hold .80 s, flow 50 sccm. Compare the archived 1800 C point.
Keep the existing 450 C floor, 1 s period, .025 s rise, .10 s fall,
equimolar undiluted feed, fixed volume and pressure. Unchanged Aramco solver.
This is a numerical high-temperature extrapolation, not a claim that the
mechanism is experimentally validated here or that the heater can realize it.
No graphite/soot prediction is inferred from gas-phase C6 output.

Separate approved boundary batch, not a retry of the stopped low-flow grid.
First pass inert 2100 C, then reacting 1900 C at 400 and 800 samples.
Require all existing state/output, temperature, pressure, elemental and mass
gates plus all-species phase refinement below 1e-4 before 2000 and 2100 C.
Stop on any failure. No tolerance relaxation or automatic retry.
Cap 540 seconds from the remaining authorized 3600-second ledger;
expected minutes, capped per subprocess at 100 seconds. Charge failed work.
Archive every species, diagnostics, source hashes and gates in
docs/research/rph-yield-grid-2026-09-07/hot-boundary/data.
Do not change the grid coverage count or HTML until results are reviewed.
