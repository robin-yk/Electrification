# Four-objective archive optimization

Objectives: maximize total-feed-carbon acetylene yield; maximize acetylene mmol per kJ of positive thermal input; minimize absolute CO/C2H2 molar-ratio error; minimize additional cooling duty in W. All dominance tests use these four quantities without a weighted sum. Equal objective vectors remain tied.

Target ratios 1, 1.5 and 1.75 are separate demand scenarios. Reactor closures, feed families and thermal boundaries define separate pools. Gas-only cases remain separate from CFP storage and radiation accounting. Additional cooling is a thermal duty, not cooling-system electricity. Radiation reduction retains the imposed temperature waveform.

This is an exact Pareto selection over saved evaluations. It is an initialization and coverage assessment for a subsequent multi-objective Bayesian search. It does not propose or evaluate new conditions. Different temperatures, compositions, volumes and flows within a pool remain design choices, not matched controls. Supply-feasibility flags are retained without an imposed device-feasibility filter.

CO/C2H2 mismatch is minimized, without declaring any tolerance band feasible. For CH4/He the ratio is zero at every point, so this objective is constant; those fronts cannot supply the target CO-containing mixture without external CO. Cooling duty is also constant at zero for many cases, reducing the effective number of conflicting objectives in those subsets. Pareto membership supplies no unique ranking.

## Coverage

Eligible condition IDs: 330; thermal-scenario rows: 987. Documented coarse members are removed when their fine source is present. A50 is retained once through its original archived record. New accepted A100/A200/A400 pairs are included at fine resolution.

The source atlas indexes additional legacy and unsupported files. Those records have not acquired energy adapters through this operation. Consult its missing-and-excluded.json, legacy-pending.json and cached-branch-inventory.json; this report does not claim all historical calculations are eligible.

| Pool | Target CO/C2H2 | Evaluated | Nondominated |
|---|---:|---:|---:|
| CH4/CO2 | CSTR | 90% lower radiation | 1.0 | 324 | 16 |
| CH4/CO2 | CSTR | 90% lower radiation | 1.5 | 324 | 16 |
| CH4/CO2 | CSTR | 90% lower radiation | 1.75 | 324 | 13 |
| CH4/CO2 | CSTR | Full radiation | 1.0 | 324 | 25 |
| CH4/CO2 | CSTR | Full radiation | 1.5 | 324 | 22 |
| CH4/CO2 | CSTR | Full radiation | 1.75 | 324 | 21 |
| CH4/CO2 | CSTR | Gas only | 1.0 | 321 | 9 |
| CH4/CO2 | CSTR | Gas only | 1.5 | 321 | 9 |
| CH4/CO2 | CSTR | Gas only | 1.75 | 321 | 7 |
| CH4/He | Fixed-volume ideal PFR | 90% lower radiation | 1.0 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | 90% lower radiation | 1.5 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | 90% lower radiation | 1.75 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | Full radiation | 1.0 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | Full radiation | 1.5 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | Full radiation | 1.75 | 6 | 4 |
| CH4/He | Fixed-volume ideal PFR | Gas only | 1.0 | 6 | 1 |
| CH4/He | Fixed-volume ideal PFR | Gas only | 1.5 | 6 | 1 |
| CH4/He | Fixed-volume ideal PFR | Gas only | 1.75 | 6 | 1 |

## Retained candidates

Each scenario lists all candidate IDs. Exact objectives and operating inputs are in pareto.json.

### CH4/CO2 | CSTR | 90% lower radiation; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.38067 | 0.5252 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.35232 | 0.6533 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.32343 | 1.0938 | 0.000 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.27184 | 0.7994 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.18419 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.16126 | 1.1471 | 0.000 |
| CJH-8dc97a1805 | CJH | 19.885 | 0.11999 | 1.0582 | 0.000 |
| RPH-d9641af44c | RPH | 38.660 | 0.09910 | 0.9801 | 29.575 |
| RPH-320f64837c | RPH | 38.627 | 0.09881 | 0.9803 | 29.754 |
| RPH-67af3f8abf | RPH | 38.606 | 0.09836 | 0.9805 | 30.071 |
| CJH-bc5d6a31ed | CJH | 2.345 | 0.07515 | 1.0556 | 0.000 |
| RPH-844dc4d847 | RPH | 29.447 | 0.07121 | 0.9880 | 41.704 |
| CJH-4b532997ce | CJH | 2.192 | 0.06719 | 1.0218 | 0.000 |
| RPH-7ed226179f | RPH | 20.351 | 0.05062 | 0.9912 | 47.997 |
| CJH-97e69aa84d | CJH | 1.500 | 0.02235 | 1.0070 | 0.000 |
| CJH-aa976b0a58 | CJH | 1.146 | 0.01134 | 0.9977 | 0.000 |

### CH4/CO2 | CSTR | 90% lower radiation; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.38067 | 0.5252 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.35232 | 0.6533 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.32343 | 1.0938 | 0.000 |
| ch4-0.65-Q200 | CJH | 26.587 | 0.28984 | 1.3927 | 0.000 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.27184 | 0.7994 | 0.000 |
| CJH-e8d1774609 | CJH | 10.408 | 0.23323 | 1.5118 | 0.000 |
| ch4-0.65-Q100-tight | CJH | 30.630 | 0.21395 | 1.7557 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.18419 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.16126 | 1.1471 | 0.000 |
| CJH-ec5e08804e | CJH | 32.674 | 0.14668 | 1.7418 | 0.000 |
| RPH-b9dc03ac89 | RPH | 5.296 | 0.10983 | 1.5075 | 66.015 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.08719 | 1.4596 | 30.678 |
| CJH-7c9712daac | CJH | 3.747 | 0.03153 | 1.5048 | 0.000 |
| CJH-3e2ae556e1 | CJH | 3.747 | 0.03153 | 1.5048 | 0.000 |
| CJH-9a482db75f | CJH | 3.747 | 0.03153 | 1.5048 | 0.000 |
| CJH-fd357394e0 | CJH | 3.742 | 0.03149 | 1.5041 | 0.000 |

### CH4/CO2 | CSTR | 90% lower radiation; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.38067 | 0.5252 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.35232 | 0.6533 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.32343 | 1.0938 | 0.000 |
| ch4-0.65-Q200 | CJH | 26.587 | 0.28984 | 1.3927 | 0.000 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.27184 | 0.7994 | 0.000 |
| CJH-6a77cde07f | CJH | 15.408 | 0.25700 | 1.9410 | 0.000 |
| ch4-0.65-Q100-tight | CJH | 30.630 | 0.21395 | 1.7557 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.18419 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.16126 | 1.1471 | 0.000 |
| CJH-ec5e08804e | CJH | 32.674 | 0.14668 | 1.7418 | 0.000 |
| CJH-bce8c7ee33 | CJH | 37.428 | 0.12950 | 2.1046 | 0.000 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.08719 | 1.4596 | 30.678 |
| RPH-7d97add74c | RPH | 33.369 | 0.08202 | 1.7112 | 30.792 |

### CH4/CO2 | CSTR | Full radiation; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.09005 | 0.5252 | 0.000 |
| A400-n8 | RPH | 23.114 | 0.08600 | 0.5535 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.07307 | 1.0938 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.06327 | 0.6533 | 0.000 |
| A200-n8 | RPH | 29.701 | 0.05940 | 0.6858 | 0.000 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.03919 | 0.7994 | 0.000 |
| A100-n8 | RPH | 34.934 | 0.03643 | 0.8323 | 0.000 |
| CJH-3e3aa46e7f | CJH | 2.501 | 0.02747 | 1.0643 | 0.000 |
| CJH-36b82b199a | CJH | 2.489 | 0.02736 | 1.0637 | 0.000 |
| CJH-287d55f989 | CJH | 2.489 | 0.02736 | 1.0637 | 0.000 |
| CJH-364d21b7be | CJH | 2.489 | 0.02736 | 1.0637 | 0.000 |
| CJH-bc5d6a31ed | CJH | 2.345 | 0.02598 | 1.0556 | 0.000 |
| CJH-271056971b | CJH | 1.854 | 0.02435 | 1.0547 | 0.000 |
| CJH-ab4f92e31f | CJH | 1.854 | 0.02435 | 1.0547 | 0.000 |
| CJH-28ead07f62 | CJH | 1.854 | 0.02435 | 1.0547 | 0.000 |
| CJH-6412ec5a2f | CJH | 1.853 | 0.02434 | 1.0546 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.02297 | 0.8500 | 0.000 |
| RPH-d9641af44c | RPH | 38.660 | 0.02064 | 0.9801 | 0.000 |
| RPH-320f64837c | RPH | 38.627 | 0.02063 | 0.9803 | 0.000 |
| RPH-67af3f8abf | RPH | 38.606 | 0.02063 | 0.9805 | 0.050 |
| CJH-4f5253b305 | CJH | 47.217 | 0.01956 | 1.1471 | 0.000 |
| RPH-844dc4d847 | RPH | 29.447 | 0.01924 | 0.9880 | 0.202 |
| RPH-7ed226179f | RPH | 20.351 | 0.01761 | 0.9912 | 0.175 |
| CJH-97e69aa84d | CJH | 1.500 | 0.00303 | 1.0070 | 0.000 |
| CJH-aa976b0a58 | CJH | 1.146 | 0.00135 | 0.9977 | 0.000 |

### CH4/CO2 | CSTR | Full radiation; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.09005 | 0.5252 | 0.000 |
| A400-n8 | RPH | 23.114 | 0.08600 | 0.5535 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.07307 | 1.0938 | 0.000 |
| CJH-e8d1774609 | CJH | 10.408 | 0.06740 | 1.5118 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.06327 | 0.6533 | 0.000 |
| A200-n8 | RPH | 29.701 | 0.05940 | 0.6858 | 0.000 |
| RPH-b9dc03ac89 | RPH | 5.296 | 0.05066 | 1.5075 | 56.047 |
| ch4-0.65-Q200 | CJH | 26.587 | 0.05008 | 1.3927 | 0.000 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.03919 | 0.7994 | 0.000 |
| A100-n8 | RPH | 34.934 | 0.03643 | 0.8323 | 0.000 |
| ch4-0.65-Q100-tight | CJH | 30.630 | 0.02998 | 1.7557 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.02297 | 0.8500 | 0.000 |
| RPH-d9641af44c | RPH | 38.660 | 0.02064 | 0.9801 | 0.000 |
| RPH-320f64837c | RPH | 38.627 | 0.02063 | 0.9803 | 0.000 |
| RPH-67af3f8abf | RPH | 38.606 | 0.02063 | 0.9805 | 0.050 |
| CJH-4f5253b305 | CJH | 47.217 | 0.01956 | 1.1471 | 0.000 |
| CJH-ec5e08804e | CJH | 32.674 | 0.01799 | 1.7418 | 0.000 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.01790 | 1.4596 | 0.000 |
| CJH-7c9712daac | CJH | 3.747 | 0.00378 | 1.5048 | 0.000 |
| CJH-3e2ae556e1 | CJH | 3.747 | 0.00378 | 1.5048 | 0.000 |
| CJH-9a482db75f | CJH | 3.747 | 0.00378 | 1.5048 | 0.000 |
| CJH-fd357394e0 | CJH | 3.742 | 0.00378 | 1.5041 | 0.000 |

### CH4/CO2 | CSTR | Full radiation; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| ch4-0.80-Q400 | CJH | 25.900 | 0.09005 | 0.5252 | 0.000 |
| A400-n8 | RPH | 23.114 | 0.08600 | 0.5535 | 0.000 |
| ch4-0.65-Q400 | CJH | 20.728 | 0.07307 | 1.0938 | 0.000 |
| CJH-e8d1774609 | CJH | 10.408 | 0.06740 | 1.5118 | 0.000 |
| ch4-0.80-Q200 | CJH | 33.871 | 0.06327 | 0.6533 | 0.000 |
| A200-n8 | RPH | 29.701 | 0.05940 | 0.6858 | 0.000 |
| CJH-6a77cde07f | CJH | 15.408 | 0.05512 | 1.9410 | 0.000 |
| ch4-0.65-Q200 | CJH | 26.587 | 0.05008 | 1.3927 | 0.000 |
| RPH-b6bc83f97c | RPH | 7.881 | 0.04091 | 1.9313 | 58.015 |
| ch4-0.80-Q100 | CJH | 40.227 | 0.03919 | 0.7994 | 0.000 |
| A100-n8 | RPH | 34.934 | 0.03643 | 0.8323 | 0.000 |
| ch4-0.65-Q100-tight | CJH | 30.630 | 0.02998 | 1.7557 | 0.000 |
| CJH-15d38bb947 | CJH | 41.810 | 0.02297 | 0.8500 | 0.000 |
| RPH-d9641af44c | RPH | 38.660 | 0.02064 | 0.9801 | 0.000 |
| RPH-320f64837c | RPH | 38.627 | 0.02063 | 0.9803 | 0.000 |
| RPH-67af3f8abf | RPH | 38.606 | 0.02063 | 0.9805 | 0.050 |
| CJH-4f5253b305 | CJH | 47.217 | 0.01956 | 1.1471 | 0.000 |
| CJH-ec5e08804e | CJH | 32.674 | 0.01799 | 1.7418 | 0.000 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.01790 | 1.4596 | 0.000 |
| RPH-7d97add74c | RPH | 33.369 | 0.01680 | 1.7112 | 0.000 |
| CJH-bce8c7ee33 | CJH | 37.428 | 0.01553 | 2.1046 | 0.000 |

### CH4/CO2 | CSTR | Gas only; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| CJH-15d38bb947 | CJH | 41.810 | 0.83667 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.82675 | 1.1471 | 0.000 |
| RPH-d9641af44c | RPH | 38.660 | 0.79688 | 0.9801 | 0.000 |
| RPH-320f64837c | RPH | 38.627 | 0.79673 | 0.9803 | 0.000 |
| RPH-67af3f8abf | RPH | 38.606 | 0.79671 | 0.9805 | 0.000 |
| RPH-844dc4d847 | RPH | 29.447 | 0.73165 | 0.9880 | 0.000 |
| RPH-7ed226179f | RPH | 20.351 | 0.64640 | 0.9912 | 0.000 |
| CJH-97e69aa84d | CJH | 1.500 | 0.07648 | 1.0070 | 0.000 |
| CJH-aa976b0a58 | CJH | 1.146 | 0.06257 | 0.9977 | 0.000 |

### CH4/CO2 | CSTR | Gas only; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| CJH-15d38bb947 | CJH | 41.810 | 0.83667 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.82675 | 1.1471 | 0.000 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.73648 | 1.4596 | 0.000 |
| CJH-e8d1774609 | CJH | 10.408 | 0.32097 | 1.5118 | 0.000 |
| RPH-b9dc03ac89 | RPH | 5.296 | 0.27307 | 1.5075 | 0.000 |
| CJH-7c9712daac | CJH | 3.747 | 0.17115 | 1.5048 | 0.000 |
| CJH-3e2ae556e1 | CJH | 3.747 | 0.17115 | 1.5048 | 0.000 |
| CJH-9a482db75f | CJH | 3.747 | 0.17115 | 1.5048 | 0.000 |
| CJH-fd357394e0 | CJH | 3.742 | 0.17097 | 1.5041 | 0.000 |

### CH4/CO2 | CSTR | Gas only; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| CJH-15d38bb947 | CJH | 41.810 | 0.83667 | 0.8500 | 0.000 |
| CJH-4f5253b305 | CJH | 47.217 | 0.82675 | 1.1471 | 0.000 |
| RPH-467a6cdda5 | RPH | 35.396 | 0.73648 | 1.4596 | 0.000 |
| CJH-ec5e08804e | CJH | 32.674 | 0.71452 | 1.7418 | 0.000 |
| RPH-7d97add74c | RPH | 33.369 | 0.70558 | 1.7112 | 0.000 |
| CJH-bce8c7ee33 | CJH | 37.428 | 0.70165 | 2.1046 | 0.000 |
| ch4-0.65-Q100-tight | CJH | 30.630 | 0.67213 | 1.7557 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | 90% lower radiation; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.16837 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.15849 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.11586 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.06934 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | 90% lower radiation; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.16837 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.15849 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.11586 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.06934 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | 90% lower radiation; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.16837 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.15849 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.11586 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.06934 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Full radiation; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.02764 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.02149 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.01378 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.00761 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Full radiation; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.02764 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.02149 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.01378 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.00761 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Full radiation; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-400 | CJH | 38.841 | 0.02764 | 0.0000 | 0.000 |
| He-flow-200 | CJH | 58.395 | 0.02149 | 0.0000 | 0.000 |
| He-flow-100 | CJH | 73.516 | 0.01378 | 0.0000 | 0.000 |
| He-flow-50 | CJH | 80.361 | 0.00761 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Gas only; target 1.0

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-50 | CJH | 80.361 | 0.69994 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Gas only; target 1.5

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-50 | CJH | 80.361 | 0.69994 | 0.0000 | 0.000 |

### CH4/He | Fixed-volume ideal PFR | Gas only; target 1.75

| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |
|---|---|---:|---:|---:|---:|
| He-flow-50 | CJH | 80.361 | 0.69994 | 0.0000 | 0.000 |

Reproduce: `python tools/openmkm_dynamic/four_objective_pareto.py`. Test: append `--test`.
