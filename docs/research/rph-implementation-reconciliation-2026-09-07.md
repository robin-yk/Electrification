# RPH implementation reconciliation

## Scope

Read-only branch/data survey followed by isolated algebraic state-update tests.
No ReactorNet integration, new chemistry, optimization, or correction of archived
outputs was performed. Sources: main 65c2b7c and legacy branch 7515535e83284b7568e7481098bb9b7a90b29b62.
The survey covered 12 remote branch tips, not every historical commit.

## Reuse map

| Component | Source | Decision |
|---|---|---|
| Temperature-step expelled/drawn species accounting | legacy run_cstr_case.step_temperature | Isolate and test; do not apply as fixed 50 sccm |
| Sparse mole reactor and preconditioner | main run_cstr_case.make_reactor | Retain; no evidence that speed benchmark validates a different closure |
| State plus cycle-output convergence | main periodic_gate | Retain when combining implementations |
| Peak-aware phase grid | existing phase_grid | Reuse; grid nodes must correspond to the actual waveform |
| SI-calibrated element waveform | legacy calibrate_element_si and archived c2pulse trajectories | Preserve calibration and raw trajectory; element T is not independently measured gas T |
| Species outflow and inventory audit | both branch implementations | Count inlet and outlet separately; retain pure-species and grouped outputs |
| Matched-conversion baseline | legacy pulse_vs_steady and dense steady grids | Reuse only with matching feed, closure and denominator; no extrapolation |

## Algebraic tests performed

Command: python -m unittest discover -s tools/openmkm_dynamic -p test_temperature_step_accounting.py
Cantera 3.2.0, GRI thermodynamic state objects only. Three tests passed.
Both IdealGasConstPressureReactor and IdealGasConstPressureMoleReactor are checked.

1. A bare TP/syncState update changes species inventory without a flow ledger.
2. The isolated legacy correction closes each species across heating and cooling.
3. An identity temperature step requires no added flow.

Tests use different feed and reactor compositions. A pure inert gas equal to its
feed cannot expose substitution of products by feed or vice versa. Element closure
alone also cannot establish that individual species have been handled correctly.
No claim is made about sparse dynamic convergence: object-state equivalence does
not test the preconditioned ODE integration.

## Three distinct reactor formulations

The uncorrected step marcher resets T/P, then assigns both mass flows to m/tau.
The corrected legacy marcher additionally expels reactor gas on heating and draws
feed on cooling. The experimental inlet flow cannot simultaneously be called
strictly constant if that extra drawn feed is counted as supply.

The new fixed-volume model specifies constant inlet mass flow and uses an outlet
pressure controller while imposing continuous T(t). It must not also call the
legacy expulsion/draw helper: that would count a second, unrequested flow path.
Its failed inert pressure gate remains unresolved, not repaired by this audit.

## Evidence to reuse before more calculation

The legacy branch contains 13 corrected CH4/He drive cases, 12 older premise
trapezoid cases, 9 S9 voltage/residence-time cases, and two pathway networks.
The S9 si-op case at tau 0.2 s still reports the old 20.3193% conversion;
do not substitute it for the corrected pathway's approximately 16.5% value.
The 13-case CH4/He family includes fixed-1800-C half/double periods already.
Those are useful shape evidence, not completed CH4/CO2 fixed-flow comparisons.

The main archives include five Aramco three-pair results (one refined result
missing), two adaptive-stop Aramco results, and five C2/CO pilot outputs.
Convergence against their own legacy reference does not resolve the temperature
step accounting discrepancy. Keep them labeled as legacy numerical results until
a same-condition corrected comparison quantifies its effect.

## Next gate, not dispatched

Keep the production marcher and archived figures unchanged. First choose a pinned
corrected legacy anchor and its archived SI waveform to test any combined sparse
and corrected-step implementation. This is separate from constant-feed model
development. For fixed feed, diagnose the pressure transient without adding
temperature-step feed or relaxing the pressure gate. No sweep or automatic retry
is justified by the algebraic tests above.
