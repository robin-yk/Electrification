# RPH flow pilot: accepted comparison

Both RPH resolutions passed the declared gates. The 50 sccm condition also reproduced the archived species results. See the gate files for errors and the status files for elapsed times.

RPH uses the same archived gas-temperature waveform and composition at both flows. The CJH row is the existing compromise at a different composition and flow, not a matched-control pair. All rows use the same fixed gas volume. Carbon yield is normalized by total inlet carbon; CO/C2H2 is molar.

| Mode | Flow (sccm) | Radiation remaining | C2H2 yield (%) | CO/C2H2 | Reaction heat (W) | Positive input (W) | Reaction heat / input (%) | Additional cooling (W) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RPH | 50 | 1.0 | 38.660 | 0.980 | 4.313 | 348.259 | 1.238 | 0.000 |
| RPH | 50 | 0.1 | 38.660 | 0.980 | 4.313 | 72.518 | 5.947 | 29.575 |
| RPH | 100 | 1.0 | 34.934 | 0.832 | 7.855 | 356.492 | 2.203 | 0.000 |
| RPH | 100 | 0.1 | 34.934 | 0.832 | 7.855 | 79.950 | 9.824 | 28.774 |
| CJH | 400 | 1.0 | 20.728 | 1.094 | 22.215 | 421.876 | 5.266 | 0.000 |
| CJH | 400 | 0.1 | 20.728 | 1.094 | 22.215 | 95.311 | 23.308 | 0.000 |

Doubling RPH flow improves heat allocation while reducing acetylene yield and the CO/acetylene ratio. The existing CJH compromise retains a higher reaction-heat fraction; RPH retains a higher acetylene carbon yield. No dominance over that CJH compromise is established.

The radiation-reduction rows retain the imposed waveform. Additional cooling is listed separately and is not converted into cooling-system electricity. These rows are conditional thermal postprocessing, not a passive-insulation simulation.

The redundant CVODES resets were removed before these runs. Both resolutions completed with unchanged tolerances and sparse preconditioning. No higher flow or new optimization was run. The atlas and manuscript remain unchanged.

Regenerate with `python tools/openmkm_dynamic/report_rph_flow_pilot.py`.
