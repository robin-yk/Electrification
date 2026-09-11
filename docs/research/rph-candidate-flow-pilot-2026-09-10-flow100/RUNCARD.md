# Candidate A at doubled flow

Question: does doubling feed from 50 to 100 sccm improve reaction-heat allocation while retaining useful acetylene yield and CO/C2H2 ratio?

Prerequisite: attempt02/A50-gate.json must pass. Use the archived A temperature waveform, composition, fixed gas volume, pressure controller, mechanism, and tolerances unchanged. Run only 100 sccm at four and eight samples per archived segment. Standard flow is referenced to 273.15 K and 101325 Pa. Fixed volume means residence time changes with flow.

Command: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/rph_candidate_flow_pilot.py --flow100`.

Hard cap: 300 seconds total, one thread. No automatic retries or queued higher flows. Require inert ramp, periodic species convergence, mass and elemental closure, species refinement below 1e-4 mol/mol inlet carbon and positive-input refinement below 1%. Store both resolutions and energy steps. Radiation factors 1.0 and 0.1 are postprocessing scenarios with the prescribed waveform retained; retain additional cooling explicitly.

Compare the higher-resolution result with A50 and the existing CJH compromise under the same radiation scenario. Do not update the atlas until the gate passes.
