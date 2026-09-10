# CH4/He temperature screen

Question: locate the temperature and reaction-time window for acetylene formation before returning to CH4/CO2 flow-through calculations.

User approved seven temperatures and requested screening precision. Use 1200 to 1800 C in 100 C increments, with outputs at 1, 5, 20, and 40 ms. These are seven trajectories and 28 samples, plus one representative refined trajectory and one nonreacting gate. Existing 1800/1900 C checks establish the starting closure and solver settings. The new early-time samples require integration of the 1800 C trajectory; existing endpoint results remain preserved.

Closure: CH4 10 mol%, He 90 mol%, constant 101325 Pa, closed isothermal gas parcel, AramcoMech 2.0. No gas-flow rate, fixed gas volume, heater, surface chemistry, or solid carbon model. Times are parcel reaction times.

Use the existing adaptive preconditioner, standard tolerances 1e-9/1e-22, and representative refinement 1e-11/1e-24. First run the nonreacting gate and 1800 C paired trajectory. Stop on a failed check. Preserve full species and carbon outputs at all sample times. Do not label unrefined points as individually convergence-tested.

Budget: 300 seconds external wall-time cap for the complete batch, estimated under one minute from the preceding 23-second two-temperature verified pilot. Load the mechanism once with TZ=UTC0 and LC_ALL=C. No queued expansion. Existing output directory prevents accidental repetition.

Run: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/parcel_temperature_screen.py` from the repository root. Outputs: results/ and generated REPORT.md in this folder. Existing manuscript figures and earlier result files are unchanged.
