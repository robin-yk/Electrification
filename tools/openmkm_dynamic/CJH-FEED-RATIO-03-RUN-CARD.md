# Two-point composition refinement

User authorized CH4 mole fractions 0.4 and 0.6 (20/30 and 30/20 sccm).
Reuse the validated worker from 8c4aa17 without chemical, physical or numeric
changes: 1750 C, total 50 sccm at 0 C/1 atm, fixed equivalent volume from the
archived 1:1 reference, target 1 atm. Mass residence time remains an output.
Require prior completed pilot, both matching gates and unchanged mechanism.
Two new integrations only, volume-scaled atol mode 2. Retain per-case stationarity,
mass, elemental, pressure and volume gates. Stop on failure; no automatic retry.
Reserve 180 s batch, worker <=100 s, expected approximately 10 s based on prior
seven-case 27 s batch. Output cjh-feed-ratio-03 separately. Display CH4/(CH4+CO2)
as mol% with numerical spacing. Update seven-point Figure 2 only from verified
outputs; no global optimum or physical heating-volume claim.
