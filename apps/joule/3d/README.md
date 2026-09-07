# Joule3D integration

The Joule calculator offers 0D Single Design, 2D Thermal Field and 3D Solid
Field in one navigation. Dynamic continues to use the axisymmetric 2D model;
the 3D page has its own steady and pulsed controls.

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

Run `npm test` for numerical regression tests and `npx playwright test
tests/e2e/joule3d.spec.js` for the navigation, import and worker checks.
