# Joule3D integration

## Enclosed cylindrical model (current main-page entry)

`enclosure.js` builds a coupled r/theta/z finite-volume system from the shared
Joule2D radial/axial operators. Each angular sector receives its fraction of
every volume, conductance, radiation exchange, gas enthalpy flux and storage
term. Periodic angular faces couple both temperature and electrical potential.
This is not an array of independent 2D solutions or a revolved 2D picture.

The main Joule 3D tab now opens `enclosure.html`. Import the cylindrical design
from the parent page, choose the grid and run. Compare with 2D uses the same
radial/axial grid and boundary data. The original Cartesian solid-only model
is preserved at `index.html`; the earlier import adapter is still available
for that legacy model but no longer drives the main tab.

### Feature transfer

| Joule2D capability | Enclosed 3D status |
|---|---|
| Cited presets, custom material, rho(T), k(T), cp(T) | Shared material functions, no freezing |
| Solid fraction, radial porosity contrast | Shared effective-property conventions |
| Gap, wall, external air, axial gas pads | All included, with thermal storage |
| Purge and inlet temperature | Same prescribed 50 sccm He closure; optional purge off |
| End ambient/electrode/adiabatic choices | Shared boundary assembly |
| Gap and outside radiation | Shared closures, applied sector locally |
| CC/CV/automatic supply and I/V/P/J limits | Shared operating-point function; fixed-drive violations reported |
| Electrical contact resistance | Shared supply loss accounting; external-lead dissipation |
| Uniform or solved Joule source | Solved r/theta/z potential and conservative source normalization |
| Steady, startup, quench, pulse | Implemented; pulse edges explicitly resolved |
| Initial steady field | Recomputed in 3D, or last 3D field reused on identical mesh |
| Growing time step / steady stop | Available for constant drive and quench |
| Dynamic settings import | Separate parent-page button transfers drive and time settings |
| Temperature, potential, Joule source, current density | Slice and cross-section views; J is a gradient diagnostic |
| Time trace, field/history export, settings persistence | Canvas, CSV and JSON |
| Screening, parameter sweeps, material reference | Existing shared parent-page workflows retained, not new 3D sweeps |
| Rectangular surface-equivalent cylinder | Parent-page opt-in uses the same 2D transform; approximation labeled and saved |
| Full Cartesian enclosure and offset electrode patches | Not implemented; legacy solid-only model remains separate |

### Claims and limitations

The supply resistance still uses mean element temperature, as in 2D. The
3D potential distributes a normalized bulk heating budget. Its field resistance
is reported separately and does not replace the supply resistance. A current
density diagnostic and a normalized heat map need not obey local q = rho J²
after this normalization. Do not claim fully field-coupled supply feedback.

Contact power is booked as heat leaving through external leads. It is not
deposited in the thermal domain. This makes the power ledger explicit while
retaining the existing 2D treatment; finite electrode solids and contact-heat
partition remain future physical improvements.

Sector-local concentric gap radiation preserves the 2D closure. It is not
a nonlocal view-factor solution for asymmetric temperatures or surfaces.
Prescribed gas thermal transport is not a momentum/pressure CFD solution.
Storage uses the same midpoint heat-capacity quadrature as 2D; the accumulated
stored-energy increment is not an independently integrated enthalpy table.

The current tests establish cylindrical code parity, angular conservation and
an angular Fourier-mode refinement check. They do not establish experimental
validation or arbitrary-geometry convergence. The existing 2D manuscript
results and validation status have not been transferred to this new model.

### Reproduce checks

`node --test tests/joule-enclosure3d.test.js` checks steady 2D parity and loss
channels, conservative angular transport, variable-conductivity current flow,
second-order angular Fourier-mode conduction, porous/electrode parity,
temperature-dependent transient parity, pulse energy and rejected inputs.
The paired steady test prints its measured temperature differences and closure.

`npx playwright test tests/e2e/joule3d.spec.js` checks parent import, worker
execution, paired comparison, warm-start quench, field selection and CSV export.
`npm test` checks the whole repository and `npm run build` checks deployment
assets. The existing 2D solver and manuscript figure generators are unchanged.

## Original solid-only model

The original standalone page has its own steady and pulsed controls. Its
capabilities below describe that legacy page, not the new enclosed model.

This solver was imported from Yeonsu's Joule3D working draft dated 2026-09-06.
The numerical core is a DOM-free ES module used by Node tests and a module
worker. No new runtime library is required. The page includes rotating fields,
cuts, electrode positioning, CSV field export and JSON settings export.

Use current 0D design transfers dense rectangular or cylindrical geometry,
properties evaluated at 25 °C as constants, ambient conditions, emissivity,
and voltage/current/power limits. Porous geometry is rejected. Material J
limits, contact resistance, enclosure, gas and pulse settings are not imported.
The user must review the independent 3D boundaries before solving. A 3D result
does not inherit the 2D published-case reproduction status.

The model has one homogeneous solid, ideal end terminals and ambient heat
loss. It excludes containment-wall storage, gas transport, electrical contact
resistance and surface-to-surface radiation. Curved surfaces are voxelized.
Material presets are illustrative; their values are not validated data.

Run `node --test tests/joule3d.test.js tests/joule3d-import.test.js` for the
legacy solid-only numerical regression and import checks.
