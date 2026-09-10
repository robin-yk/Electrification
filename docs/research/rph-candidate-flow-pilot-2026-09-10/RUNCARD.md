# Candidate A flow pilot

Question: Does doubling flow improve the reaction-heat fraction while retaining acetylene yield and an approximately equimolar CO/acetylene product?

First reproduce archived A at 50 sccm, then evaluate 100 sccm. Each has 4 and 8 quadrature samples per archived waveform segment. Stop before 100 sccm if reference or refinement gates fail. Candidate B and higher peaks remain pending.

Closure: AramcoMech 2.0, prescribed archived gas-temperature history, fixed gas volume 0.009228077898 cm3, pressure controller near 1 atm, constant standard inlet flow at 273.15 K and 101325 Pa. The temperature history is held fixed when flow changes. Cold inlet enthalpy is used for inverse heat accounting. CFP mass 28.8 mg, emissivity 0.57, two-face area 6.08 cm2, surroundings 298.15 K. Full and 90%-reduced radiation are conditional energy scenarios. Cooling is retained separately.

The historical periodic solver is ported to the installed Cantera 3.1 interface. A closed inert linear ramp is checked first. Sparse adaptive preconditioning and the historical derivative approximations are retained. The archived A chemical result must reproduce within 1e-4 mol/mol inlet carbon. Paired species error must be below 1e-4, positive-energy error below 1%, mass and elemental residuals below 1e-4, temperature error below 1e-4 K, and pressure error below 1e-4 relative.

Cost: at most 300 seconds for the entire first pilot, one process and one BLAS thread. Runtime for this port is unknown until measured. No automatic retry or larger batch. Hashes, diagnostics, full species, phase energies, and completed results are retained locally. No manuscript or atlas regeneration until the gates pass.

Run with cantera-env Python: tools/openmkm_dynamic/rph_candidate_flow_pilot.py.
