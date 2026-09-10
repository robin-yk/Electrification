# Porsin methane-helium scoping check

User requested an approximate attempt before a full reproduction.

Question: does an Aramco gas parcel at 1900 C and 10% CH4 in He approach the abstract's approximately 80% methane conversion and 80% acetylene selectivity over tens of milliseconds?

Source: Porsin et al., Theoretical Foundations of Chemical Engineering 48 (2014), 397-403, https://doi.org/10.1134/S0040579514040241. Coil temperature is substituted for uniform gas temperature solely for this scoping test. Pressure is assumed 1 atm. Outputs at 20 and 40 ms are prescribed brackets, not fitted times. The 40 ms point is a boundary diagnostic, since the author's original text estimates contact time below 40 ms.

Closure: isothermal constant-pressure closed parcel as an ideal PFR material-history approximation. This new closure remains separate from the current CSTR optimization archive. Gas-phase AramcoMech 2.0, no solids, surface chemistry, transport, or quench. No CFP energy calculation.

Run order: load mechanism once, nonreacting 300 K composition/element check, standard reacting trajectory, tighter-tolerance trajectory with tenfold smaller maximum time step. Two time outputs per reacting trajectory. Mass and elemental errors below 1e-7; carbon yield sum within 1e-5 percentage points; paired metric differences below 0.05 percentage points. Numerical acceptance is separate from closeness to the literature target.

Cost: single thread, total 300-second wall cap; expected 1-5 minutes including mechanism loading. Stop on any failed gate. No queued follow-on sweep. Generator and run card committed before execution. Outputs are permanent JSON with complete species fractions, carbon yields, hashes, solver settings and explicit failures.

Command: `cantera-env/bin/python tools/openmkm_dynamic/porsin_scoping.py` using the installed runtime under `/Users/robin_yeonsu`. No existing manuscript, figures or optimization data are invalidated or modified.
