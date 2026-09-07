# Proposed initial-state diagnostic, not dispatched

Objective: compare feed-initialized and gas-phase TP-equilibrated initial
reactor compositions at 1750 C/0.001 s and 1750 C/0.00006 s. Keep actual
inlet CH4/CO2=50/50, pressure, temperature, initial reactor mass and mass/tau
flow convention identical. TP equilibrium is an alternate numerical starting
state, not the hypothesized physical inlet or catalytic equilibrium model.

Inspection: integrate() obtains y_feed_ch4 and y_feed from the initial gas
phase. Those copies must precede any alternate reactor initialization, or be
obtained explicitly from a separate feed phase. The inlet reservoirs must not
change. Capture original reactor mass, set the alternate gas composition at
the same T/P, synchronize, then adjust initial volume to original mass/new
density. Verify initial mass, T/P and inlet composition before integrating.
Since this is already a variable-volume constant-pressure model, preserving
mass requires different initial volume; do not describe this as a fixed-geometry
test. The inlet and outlet rate convention in the time loop stays unchanged.

Prefer a small explicit optional initialization function in the solver after
feed accounting is frozen. Do not inject state changes through an unrelated
phase-grid callback. Default behavior must remain unchanged. Add failing-first
tests for unchanged default, preservation of feed accounting, mass and pressure,
and rejection of unsupported closure before implementing the option.

Any changed solver hash is a new version, not permission to bypass existing
guards. A dedicated version-transition pilot must record old/new hashes and
the exact change, reproduce archived feed-initialized results first, then test
the alternate state. Existing archive hashes and results remain immutable.
Do not patch old refinement scripts to accept arbitrary changed solver hashes.

Prospective four runs: new-version default and alternate state at each point.
Use existing accepted sampling/horizon checks and explicitly record integrator
tolerances. Require all species/CH4 conversion agreement <1e-5, elemental and
mass closure, and stationarity. Mismatch blocks a unique-state assertion;
diagnose rather than force the alternate result to match. One alternate state
does not prove uniqueness across every possible initial condition.

Before execution: implement/test the optional path and version-transition
guard, commit an executable run card with measured pilot time estimate,
reserve <=540 s from the existing ledger, and report conditions to the user.
This design does not reserve budget or authorize automatic dispatch by itself.
