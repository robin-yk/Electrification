# Joule v6 porous-heater figure run

Author approved approximately 6000 lumped points, at most 16 steady fields and
4 transient legs, stopping if projected cost exceeds 10 CPU minutes.

Question: which envelope geometries approach a selected 1200 C target under
150 V / 40 A / 2 kW ceilings, and what does 2D add to lumped screening?
No optimality or experimental-monolith validation is claimed.

Closures: opt-in porous storage, skeleton SiC density/cp/resistivity, explicit
isotropic effective k (60 W/m/K baseline; 20 and 120 sensitivities), phi=0.5,
default quartz enclosure, He purge only, no reaction or channel enthalpy sink.
Reacting and elemental gates are not applicable to this nonreacting heater.

Gates: existing independent porous calorimetry and 112-test suite passed.
Start with a small 0D grid; compare a selected 30x60 field with 45x90.
Require convergence, relative steady closure <1e-5 and peak refinement <5 K.
Check two connected transient excursions at dt=2.5 and 1.25 s; require <2 K
endpoint difference and relative stepwise energy closure <1e-4.
Pilot elapsed time controls continuation. No training or adaptive sample
expansion: fixed grids describe sensitivities, not a learned optimum.

Output: docs/research/joule-v6-2026-09-07/data-v6-final.json, containing full inputs,
solver and generator hashes, counts, timing, fields and histories. Save after
each expensive case. The author requested a full rerun after model changes;
do not reuse numerical arrays from the stopped data.json pilot. Recalculate
analytic checks, MMS and all three literature cases using current code.
Literature cases retain their own geometry and property mappings. Material
screening maps are equivalent cylinders, including CFP; they are not a
resolved paper-strip or channel model and must be labelled accordingly. Stop on a
failed gate or budget. Only v6 figures are new; do not replace archived data.
Command: node tools/verification/joule-v6.mjs
