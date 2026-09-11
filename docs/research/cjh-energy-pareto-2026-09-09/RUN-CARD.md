# CJH energy verification pilot

Evaluate two objectives on a fixed reactor: maximize outlet acetylene mmol/h and mmol/kJ; separately minimize radiation kJ/mmol at a given acetylene rate. No CO ratio or minimum production constraint is imposed.

First verify one archived operating point: 1750 °C, 50 sccm (0 °C, 1 atm), equimolar CH4/CO2, effective volume 0.009228077898393764 cm³, pressure-controlled ideal-gas CSTR. Prescribe constant gas temperature and equate CFP temperature to gas temperature. Use 28.8 mg CFP, two-face area 0.000608 m², emissivity 0.57, surroundings and inlet-energy reference 25 °C. Input equals outlet-minus-inlet enthalpy flow plus radiation; this excludes electrodes and wall heat transfer. Reaction enthalpy is already included in the gas enthalpy difference.

Use persistent Cantera 3.1 runtime and Aramco mechanism. New-runtime verification must pass a cold case, reacting standard/tight pair, stationarity, elemental error <1e-5, mass-flow error <1e-6, pressure error <1e-4 and paired species difference <1e-5. Preserve full species output and source/environment hashes. Check against archived anchor before accepting new design calculations.

Budget: one cold plus one reacting condition at two tolerances, single-threaded, total wall cap 300 seconds. Stop on a failed gate. No queued grid or BO jobs. This is a verification pilot, not citable optimization data. Existing archive plots remain explicitly separate from this pilot. All script, mechanism and output paths are in the persistent repository; no temporary execution checkout is used.
