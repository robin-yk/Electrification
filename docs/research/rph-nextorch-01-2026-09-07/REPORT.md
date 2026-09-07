# First NEXTorch RPH recommendation: direct verification

Train on 38 conditions; verify one new point at 1800 C, 0.5 s hot hold and 1215.74335 sccm.

Gas floor 450 C, period 1 s, rise/fall .025/.10 s, CH4/CO2 1:1, fixed gas volume and 1 atm. Productivity unit: g-product g-CFP^-1 h^-1 (28.8 mg CFP).

| Species | NEXTorch prediction | Aramco verified | Prediction error (% of actual) |
|---|---|---|---|
| C2H2 | 53.9473 | 54.6338 | -1.257 |
| CO | 77.5215 | 78.2319 | -0.908 |

Observed two-objective hypervolume increases by 2.7577% relative to the existing 38 points, using a zero-productivity reference. This is a computed Pareto-coverage metric, not a percentage increase in both products.

Dominated by an existing point: False. The verified new observation is saved in observations-39.json for subsequent fitting. No second recommendation or automatic loop was run.

The paired integration passed existing numerical gates. One prediction check does not calibrate the GP across the unsampled domain or validate the gas-phase mechanism against experiment. The imposed temperature does not establish heater power feasibility.
