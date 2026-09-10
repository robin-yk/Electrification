# RPH flow pilot: accepted comparison

Paired RPH resolutions passed the declared gates at each listed flow. The 50 sccm condition also reproduced the archived species results. See the gate files for errors and the status files for elapsed times.

RPH uses the same archived gas-temperature waveform and composition at each flow. The CJH row is the existing compromise at a different composition and flow, not a matched-control pair. All rows use the same fixed gas volume. Carbon yield is normalized by total inlet carbon; CO/C2H2 is molar.

| Mode | Flow (sccm) | Radiation remaining | C2H2 yield (%) | CO/C2H2 | Reaction heat (W) | Positive input (W) | Reaction heat / input (%) | Additional cooling (W) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RPH | 50 | 1.0 | 38.660 | 0.980 | 4.313 | 348.259 | 1.238 | 0.000 |
| RPH | 50 | 0.1 | 38.660 | 0.980 | 4.313 | 72.518 | 5.947 | 29.575 |
| RPH | 100 | 1.0 | 34.934 | 0.832 | 7.855 | 356.492 | 2.203 | 0.000 |
| RPH | 100 | 0.1 | 34.934 | 0.832 | 7.855 | 79.950 | 9.824 | 28.774 |
| RPH | 200 | 1.0 | 29.701 | 0.686 | 13.791 | 371.793 | 3.709 | 0.000 |
| RPH | 200 | 0.1 | 29.701 | 0.686 | 13.791 | 93.747 | 14.711 | 27.270 |
| RPH | 400 | 1.0 | 23.114 | 0.554 | 23.018 | 399.682 | 5.759 | 0.000 |
| RPH | 400 | 0.1 | 23.114 | 0.554 | 23.018 | 118.792 | 19.377 | 24.425 |
| CJH | 400 | 1.0 | 20.728 | 1.094 | 22.215 | 421.876 | 5.266 | 0.000 |
| CJH | 400 | 0.1 | 20.728 | 1.094 | 22.215 | 95.311 | 23.308 | 0.000 |

Read the yield, product ratio and reaction-heat fraction together when selecting a flow. The CJH row provides the existing design comparator.

The radiation-reduction rows retain the imposed waveform. Additional cooling is listed separately and is not converted into cooling-system electricity. These rows are conditional thermal postprocessing, not a passive-insulation simulation.

The redundant CVODES resets were removed before these runs. Paired resolutions completed with unchanged tolerances and sparse preconditioning. The atlas and manuscript remain unchanged.

Regenerate with `python tools/openmkm_dynamic/report_rph_flow_pilot.py --flow400`.
