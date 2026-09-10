# Candidate A at 200 sccm

Purpose: extend the accepted 50 and 100 sccm comparison by one flow level. Measure the tradeoff between acetylene carbon yield, CO/C2H2 molar ratio and reaction heat divided by positive thermal input.

Use the archived A waveform and feed, unchanged from the accepted A100 pair: fixed gas volume 0.009228077898393764 cm3, pressure target 101325 Pa, CH4 mole fraction 0.7989377379417419 with CO2 balance, period 1 s, high-temperature hold 0.8 s, approximately 1224.49 to 1819.16 degrees C prescribed gas temperature. The standard flow reference is 273.15 K and 101325 Pa. Increasing flow at fixed volume reduces residence time.

Run only 200 sccm at four and eight samples per archived segment. Reuse the unchanged Aramco mechanism, mole-reactor closure, pressure controller, tolerances and sparse preconditioner. Require the preceding A100 gate to pass. No higher flow is queued.

Command: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/rph_candidate_flow_pilot.py --flow200`.

Cost limit: 300 seconds total, single-thread execution. Stop on failure and preserve diagnostic files. Acceptance gates are the inert ramp, periodic integrated species convergence, mass and elemental residuals below 1e-4 at acceptance, paired species difference below 1e-4 mol/mol feed carbon and paired positive-input difference below 1%. Retain both resolutions and phase-energy steps.

Full radiation and 90%-reduced radiation are thermal postprocessing scenarios retaining the imposed waveform. Report additional cooling separately. The atlas and manuscript are unchanged by this pilot. Compare the accepted point with previous results before planning another run.
