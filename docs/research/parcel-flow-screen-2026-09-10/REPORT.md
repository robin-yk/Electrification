# Fixed-volume CH4/He flow screen

Ideal isothermal PFR represented by a constant-pressure gas-parcel trajectory. Gas and assumed CFP temperatures are 1500 C; feed is 10 mol% CH4 and 90 mol% He at 1 atm. Inlet energy reference is 298.15 K. Standard flow uses 273.15 K and 1 atm.

Fixed gas volume: 0.233910 cm3, derived from 50 sccm and 40 ms with reaction-driven molar expansion integrated along the parcel history. The volume is a modeling choice, not a measured hot region. It differs from the earlier fixed-volume CSTR.

Constant radiating area 0.000608 m2, emissivity 0.57, surroundings 298.15 K, and radiation remaining fraction 0.1 are retained for all flows. Heat-transfer capacity and flow-dependent gas/heater temperature differences are not solved. The comparison assumes the gas can remain isothermal at every flow. No recuperation or other heat losses are included.

Two trajectories with 800 and 1600 logarithmic time intervals locate exit states by cumulative molar expansion. Both solver tolerances and quadrature spacing are refined. Species are interpolated on the refined trajectory. Full selected compositions are saved in species.json. No CSTR residence-time substitution is used.

Stop after two consecutive declines in acetylene mmol/kJ, with an upper cap of 12800 sccm. A sampled peak is a bracket for further work, not a continuous optimum.

| Flow (sccm) | Time (ms) | C2H2 yield (%) | C2H2 (mmol/h) | Input (W) | Reaction heat (%) | C2H2 (mmol/kJ) |
|---|---|---|---|---|---|---|
| 50 | 40 | 80.36 | 5.378 | 21.54 | 3.125 | 0.06934 |
| 100 | 20.23 | 73.52 | 9.84 | 23.59 | 5.352 | 0.1159 |
| 200 | 10.28 | 58.39 | 15.63 | 27.4 | 7.908 | 0.1585 |
| 400 | 5.233 | 38.84 | 20.79 | 34.31 | 9.656 | 0.1684 |
| 800 | 2.662 | 20.48 | 21.93 | 46.6 | 9.006 | 0.1307 |
| 1600 | 1.346 | 4.654 | 9.968 | 68.26 | 4.767 | 0.04056 |

Reproduce: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/parcel_flow_screen.py`. Completed results block accidental reruns.
