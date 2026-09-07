# CJH versus RPH at matched methane conversion

Completed verified matches: 15/39.

For each pair, feed composition, standard flow, gas volume and pressure are identical. Only steady CJH gas temperature is varied. Carbon yields use total inlet carbon. RPH floor is 450 C and period is 1 s. C6 total includes every gas-phase species with six carbon atoms; it is not a soot prediction.

| Flow sccm | RPH peak C | Hot hold s | CH4 X % | Matched CJH C | C2H2 CJH C% | C2H2 RPH C% | C6H6 CJH C% | C6H6 RPH C% | Total C6 CJH C% | Total C6 RPH C% | Low-X warning |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 1200 | 0.025 | 0.005771366 | 1077.368 | 1.268109e-07 | 6.234936e-06 | 1.786355e-18 | 1.02211e-10 | 3.997089e-18 | 1.306385e-10 | True |
| 50 | 1200 | 0.05 | 0.008250078 | 1091.488 | 3.161826e-07 | 1.222632e-05 | 2.618637e-17 | 2.32568e-10 | 5.215902e-17 | 2.955096e-10 | True |
| 50 | 1200 | 0.1 | 0.0131975 | 1110.52 | 1.062558e-06 | 2.420909e-05 | 9.171952e-16 | 4.932877e-10 | 1.617147e-15 | 6.253051e-10 | True |
| 50 | 1200 | 0.2 | 0.02311348 | 1133.907 | 4.594901e-06 | 4.817461e-05 | 6.578367e-14 | 1.014728e-09 | 1.035186e-13 | 1.284889e-09 | False |
| 50 | 1200 | 0.3 | 0.03300773 | 1149.147 | 1.175859e-05 | 7.21401e-05 | 9.991454e-13 | 1.536168e-09 | 1.480085e-12 | 1.944471e-09 | False |
| 50 | 1200 | 0.4 | 0.04289458 | 1160.524 | 2.350653e-05 | 9.610557e-05 | 7.32068e-12 | 2.057555e-09 | 1.041579e-11 | 2.603999e-09 | False |
| 50 | 1200 | 0.5 | 0.05279482 | 1169.635 | 4.067713e-05 | 0.000120071 | 3.508302e-11 | 2.579053e-09 | 4.844159e-11 | 3.263642e-09 | False |
| 50 | 1400 | 0.025 | 0.3522861 | 1254.926 | 0.004385387 | 0.03326864 | 1.445129e-05 | 0.03532163 | 1.630517e-05 | 0.03616262 | False |
| 50 | 1400 | 0.05 | 0.637122 | 1280.803 | 0.01491899 | 0.06192328 | 0.0003399009 | 0.06770387 | 0.0003702685 | 0.06928902 | False |
| 50 | 1400 | 0.1 | 1.206772 | 1306.894 | 0.04776666 | 0.1192325 | 0.005318247 | 0.1324683 | 0.005648269 | 0.1355418 | False |
| 50 | 1400 | 0.2 | 2.346087 | 1332.182 | 0.1368361 | 0.2338504 | 0.04571899 | 0.2619972 | 0.04774108 | 0.2680473 | False |
| 50 | 1400 | 0.3 | 3.485402 | 1347.079 | 0.2409451 | 0.3484679 | 0.1259398 | 0.391526 | 0.1305732 | 0.4005527 | False |
| 50 | 1400 | 0.4 | 4.624701 | 1358.096 | 0.3539827 | 0.4630847 | 0.2377981 | 0.5210548 | 0.2455213 | 0.533058 | False |
| 50 | 1800 | 0.5 | 44.83673 | 1530.03 | 7.85086 | 11.17343 | 7.429026 | 0.3484391 | 7.647642 | 0.493601 | False |
| 1600 | 1800 | 0.5 | 17.60564 | 1715.415 | 1.854419 | 2.75056 | 0.3108931 | 0.3335258 | 0.3340724 | 0.3811789 | False |

Low-X warning means the RPH 400/800 phase-conversion difference exceeds one tenth of target conversion. Those trace-conversion comparisons require caution even when the CJH root is tightly matched. No blanket RPH selectivity advantage is assumed. CO, other C2 species, strict match errors and provenance are retained in report.json.
