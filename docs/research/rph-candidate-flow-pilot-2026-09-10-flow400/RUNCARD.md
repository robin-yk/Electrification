# Candidate A at 400 sccm

Extend the accepted 50, 100 and 200 sccm sequence to 400 sccm. Determine whether the reaction-heat fraction continues to rise while acetylene yield and CO/C2H2 decline. This is a sequential flow scan, not Bayesian optimization.

Keep the archived A gas-temperature waveform and CH4/CO2 composition unchanged: CH4 mole fraction 0.7989377379417419, gas volume 0.009228077898393764 cm3, pressure target 101325 Pa, period 1 s, peak hold 0.8 s, gas temperature approximately 1224.49 to 1819.16 degrees C. Standard flow uses 273.15 K and 101325 Pa. The gas volume is a model input, distinct from CFP solid volume. Flow changes at fixed volume change residence time.

Use the same Aramco mechanism, mole-reactor closure, tolerances, pressure controller and sparse preconditioning as the accepted A200 pair. Run four and eight samples per archived segment, only after the A200 gate passes. Preserve the inert ramp, periodic convergence, mass and elemental residuals below 1e-4, paired species error below 1e-4 mol/mol feed carbon and paired positive-input error below 1%. Stop on any failed gate.

Command: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/rph_candidate_flow_pilot.py --flow400`.

Budget: one thread, 300-second hard cap for the pair, no automatic retry. No higher flow is queued. Preserve diagnostics on failure. Retain full and 90%-reduced radiation scenarios with additional cooling separately. These scenarios retain the prescribed waveform. Store both resolutions, source hashes, gate results and the updated comparison locally; do not alter the atlas or manuscript automatically.
