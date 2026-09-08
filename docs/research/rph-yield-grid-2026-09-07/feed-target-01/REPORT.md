# Directly verified feed-ratio proposals

1800 C peak, 450 C floor, 0.80 s hold, 1 s period, 0.025/0.10 s rise/fall, 50 sccm, 1 atm, 0.009228077898 cm3. Undiluted CH4/CO2. Total inlet carbon yield basis; 0.0288 g CFP productivity basis. Ratios use cycle-integrated outlet amounts.

| Target C2H2:CO | CH4 feed (%) | Actual CO/C2H2 | Relative error (%) | C2H2 carbon yield (%) | CO carbon yield (%) | Within 2% |
|---|---:|---:|---:|---:|---:|---|
| 1:1.75 | 69.29380 | 1.73755 | -0.711 | 29.57881 | 25.69740 | True |
| 1:1.5 | 72.40858 | 1.47691 | -1.540 | 31.59204 | 23.32922 | True |
| 1:1 | 79.25499 | 0.99220 | -0.780 | 36.06508 | 17.89183 | True |

Calculation time: 59.746 s. Status: completed.

Accepted ratio matches are fixed-waveform baseline observations, not exact roots or constrained yield optima. Tolerance bands are design assumptions. No Bayesian selection was used.

Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_feed_targets.py`.
