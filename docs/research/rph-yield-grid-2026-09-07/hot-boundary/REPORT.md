# RPH peak-temperature boundary check

Hold 0.80 s; total feed 50 sccm, equimolar CH4/CO2; floor 450 C; period 1 s; unchanged fixed gas volume and pressure. All yields use total inlet carbon. Prescribed gas temperature, not heater temperature.

Batch status: stopped. Elapsed 118.22 s. Only paired, gate-passing points are tabulated.

| Peak C | CH4 conversion % | C2H2 C% | C2H4 C% | CO C% | C6 total C% | Benzene C% | CH4 C% | CO2 C% | Other C% | C sum % | C2H2 g/gCFP/h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1800 | 70.45204 | 17.58553 | 0.54204 | 38.19072 | 0.69089 | 0.46477 | 14.77398 | 22.79034 | 5.42799 | 100.00149 | 10.64002 |

Benzene is included in C6 total; do not add it twice. Other C excludes the displayed C6 group. Gas-phase C6 is not a soot measurement. This extrapolation does not validate high-temperature kinetics experimentally.

## Sources

- 1800 C: `docs/research/rph-xs-extension-01-2026-09-07/data/Q50-T1800-h0.8-n800.json`; SHA256 `d518ec5004bb193e77c97535515890268f96a0fc9dc8ba41b0fb39fd0c06d611`.
