# RPH peak-temperature boundary check

Hold 0.80 s; total feed 50 sccm, equimolar CH4/CO2; floor 450 C; period 1 s; unchanged fixed gas volume and pressure. All yields use total inlet carbon. Prescribed gas temperature, not heater temperature.

Batch status: stopped. Elapsed 44.39 s. Only paired, gate-passing points are tabulated.

| Peak C | CH4 conversion % | C2H2 C% | C2H4 C% | CO C% | C6 total C% | Benzene C% | CH4 C% | CO2 C% | Other C% | C sum % | C2H2 g/gCFP/h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1800 | 70.45204 | 17.58553 | 0.54204 | 38.19072 | 0.69089 | 0.46477 | 14.77398 | 22.79034 | 5.42799 | 100.00149 | 10.64002 |
| 1900 | 75.17824 | 16.13676 | 0.33827 | 48.73796 | 0.32442 | 0.19228 | 12.41088 | 17.69609 | 4.35674 | 100.00113 | 9.76345 |
| 2000 | 78.34017 | 14.00257 | 0.22041 | 56.91492 | 0.21851 | 0.14337 | 10.82991 | 14.41656 | 3.39795 | 100.00084 | 8.47217 |

Benzene is included in C6 total; do not add it twice. Other C excludes the displayed C6 group. Gas-phase C6 is not a soot measurement. This extrapolation does not validate high-temperature kinetics experimentally.

## Sources

- 1800 C: `docs/research/rph-xs-extension-01-2026-09-07/data/Q50-T1800-h0.8-n800.json`; SHA256 `d518ec5004bb193e77c97535515890268f96a0fc9dc8ba41b0fb39fd0c06d611`.
- 1900 C: `docs/research/rph-yield-grid-2026-09-07/hot-boundary-02/data/T1900-h0.8-Q50-n800.json`; SHA256 `77d96a017a39c4ff82e0ed5e51f22687e12f4a137ac0b1c9c8f999bdcbc430d7`.
- 2000 C: `docs/research/rph-yield-grid-2026-09-07/hot-boundary-02/data/T2000-h0.8-Q50-n800.json`; SHA256 `6a6a5b3ada1b10d9ce057c65e55901b20b7b60dbd73f7255ef5b749dd56b91e4`.
