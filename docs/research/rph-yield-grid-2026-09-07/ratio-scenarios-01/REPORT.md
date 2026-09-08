# Acetylene and CO ratio scenarios from existing RPH data

92 unique accepted equimolar conditions. No new reaction integration or constrained optimization.

Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_ratio_scenarios.py`.

Ratio is cycle-integrated CO/C2H2 mol/mol. Carbon yields use total inlet carbon. Relative tolerance is a design choice, not a reported literature optimum.

| Target C2H2:CO | Tolerance | Accepted matches | Best sampled C2H2 carbon yield (%) | Actual CO/C2H2 | Peak (C) | Hold (s) | Flow (sccm) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1:1 | 2% | 7 | 0.92155 | 0.99617 | 1400.00 | 0.8000 | 50.000 |
| 1:1.5 | 2% | 6 | 5.29638 | 1.50751 | 1800.00 | 0.5000 | 800.000 |
| 1:1.75 | 2% | 4 | 6.50318 | 1.75467 | 1600.00 | 0.6500 | 100.000 |
| 1:1 | 5% | 9 | 0.92155 | 0.99617 | 1400.00 | 0.8000 | 50.000 |
| 1:1.5 | 5% | 7 | 5.29638 | 1.50751 | 1800.00 | 0.5000 | 800.000 |
| 1:1.75 | 5% | 4 | 6.50318 | 1.75467 | 1600.00 | 0.6500 | 100.000 |
| 1:1 | 10% | 9 | 0.92155 | 0.99617 | 1400.00 | 0.8000 | 50.000 |
| 1:1.5 | 10% | 9 | 5.29638 | 1.50751 | 1800.00 | 0.5000 | 800.000 |
| 1:1.75 | 10% | 5 | 6.50318 | 1.75467 | 1600.00 | 0.6500 | 100.000 |

Unconstrained incumbent: 17.58553% C2H2 carbon yield; CO/C2H2 = 4.34343 mol/mol.

A missing match means this inventory does not cover the ratio band, not that the band is chemically inaccessible. Best sampled matches are not constrained optima. Feed composition is fixed at CH4:CO2 = 1:1 in these data. Raw-file hashes, inputs, productivity, and nearest points for empty bands are retained in report.json.
