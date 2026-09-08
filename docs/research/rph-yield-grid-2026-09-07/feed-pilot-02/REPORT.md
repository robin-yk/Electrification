# Composition-only RPH pilot

Fixed: 1800 C peak, 450 C floor, 0.80 s hold, 1 s period, 50 sccm, 1 atm, 0.009228077898 cm3. Rise/fall: 0.025/0.10 s. Standard flow: 273.15 K, 101325 Pa. Carbon yields use total inlet carbon; productivity uses 0.0288 g CFP.

| CH4 feed (%) | CH4 conversion (%) | C2H2 carbon yield (%) | CO carbon yield (%) | CO/C2H2 (mol/mol) | C2H2 (g/gCFP/h) |
|---:|---:|---:|---:|---:|---:|
| 50.00000 | 70.45204 | 17.58553 | 38.19072 | 4.34343 | 10.64002 |
| 60.00000 | 69.89776 | 23.67952 | 32.26530 | 2.72517 | 14.32715 |

Paired phase error: 1.236057e-05. Calculation time: 17.690 s.

The equimolar point is reused from the source-hashed archive. This single new point does not locate a feed-ratio root or a yield optimum.

Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_feed_pilot.py`.
