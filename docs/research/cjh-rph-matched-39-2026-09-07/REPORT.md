# CJH versus RPH at matched methane conversion

Completed verified matches: 3/39.

For each pair, feed composition, standard flow, gas volume and pressure are identical. Only steady CJH gas temperature is varied. Carbon yields use total inlet carbon. RPH floor is 450 C and period is 1 s. C6 total includes every gas-phase species with six carbon atoms; it is not a soot prediction.

| Flow sccm | RPH peak C | Hot hold s | CH4 X % | Matched CJH C | C2H2 CJH C% | C2H2 RPH C% | C6H6 CJH C% | C6H6 RPH C% | Total C6 CJH C% | Total C6 RPH C% | Low-X warning |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 1200 | 0.025 | 0.005771366 | 1077.368 | 1.268109e-07 | 6.234936e-06 | 1.786355e-18 | 1.02211e-10 | 3.997089e-18 | 1.306385e-10 | True |
| 50 | 1800 | 0.5 | 44.83673 | 1530.03 | 7.85086 | 11.17343 | 7.429026 | 0.3484391 | 7.647642 | 0.493601 | False |
| 1600 | 1800 | 0.5 | 17.60564 | 1715.415 | 1.854419 | 2.75056 | 0.3108931 | 0.3335258 | 0.3340724 | 0.3811789 | False |

Low-X warning means the RPH 400/800 phase-conversion difference exceeds one tenth of target conversion. Those trace-conversion comparisons require caution even when the CJH root is tightly matched. No blanket RPH selectivity advantage is assumed. CO, other C2 species, strict match errors and provenance are retained in report.json.
