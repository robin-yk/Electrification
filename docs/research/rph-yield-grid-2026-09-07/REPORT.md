# Acetylene carbon-yield screening

Grid coverage: 21/75. Validated cumulative RPH conditions: 47. Off-grid observations are retained separately in observations.json.

Objective: cycle-integrated C2H2 carbon yield divided by total CH4+CO2 inlet carbon. Fixed floor450 C, period1 s, rise0.025 s, fall0.10 s, equimolar undiluted feed, fixed gas volume and pressure. No CJH calculation or Bayesian chemistry is part of this grid.

| Peak C | Hold s | Flow sccm | CH4 X % | C2H2 Y C% | CO Y C% | C6H6 Y C% | C2H2 g/gCFP/h |
|---|---|---|---|---|---|---|---|
| 1400 | 0.1 | 50 | 1.206772 | 0.1192325 | 0.05877709 | 0.1324683 | 0.0721409 |
| 1400 | 0.3 | 50 | 3.485402 | 0.3484679 | 0.1731296 | 0.391526 | 0.2108384 |
| 1400 | 0.5 | 50 | 5.763996 | 0.5777011 | 0.2874815 | 0.6505834 | 0.3495346 |
| 1400 | 0.8 | 12.5 | 27.78585 | 3.51746 | 3.957512 | 6.70887 | 0.5320546 |
| 1600 | 0.1 | 50 | 7.015844 | 1.558813 | 1.733808 | 0.765791 | 0.9431505 |
| 1600 | 0.3 | 50 | 19.31666 | 4.388522 | 4.931907 | 2.046004 | 2.655249 |
| 1600 | 0.5 | 50 | 31.61727 | 7.218197 | 8.129955 | 3.326237 | 4.367327 |
| 1600 | 0.8 | 25 | 58.44293 | 14.50825 | 20.74192 | 4.706127 | 4.389067 |
| 1800 | 0.1 | 50 | 10.68298 | 2.624117 | 5.386152 | 0.1933326 | 1.587706 |
| 1800 | 0.1 | 100 | 9.755894 | 2.508393 | 4.016217 | 0.1837162 | 3.035377 |
| 1800 | 0.1 | 200 | 8.611315 | 2.202636 | 2.715834 | 0.1847892 | 5.330768 |
| 1800 | 0.3 | 25 | 29.22762 | 6.609616 | 18.11709 | 0.2580453 | 1.999554 |
| 1800 | 0.3 | 50 | 27.75986 | 6.898753 | 14.75894 | 0.270885 | 4.17405 |
| 1800 | 0.5 | 12.5 | 48.69349 | 9.635067 | 34.2569 | 0.2977246 | 1.45741 |
| 1800 | 0.5 | 25 | 46.98471 | 10.63416 | 29.51802 | 0.2961483 | 3.217069 |
| 1800 | 0.5 | 50 | 44.83673 | 11.17343 | 24.13168 | 0.3484391 | 6.760421 |
| 1800 | 0.5 | 100 | 41.89229 | 10.99632 | 18.29069 | 0.4640903 | 13.30652 |
| 1800 | 0.5 | 200 | 37.79566 | 9.897722 | 12.5412 | 0.6175577 | 23.95423 |
| 1800 | 0.65 | 50 | 57.64439 | 14.37947 | 31.16121 | 0.4066053 | 8.700214 |
| 1800 | 0.8 | 50 | 70.45204 | 17.58553 | 38.19072 | 0.464772 | 10.64002 |
| 1800 | 0.8 | 200 | 59.68392 | 15.66907 | 19.91016 | 0.9421364 | 37.9219 |

Best observed C2H2 carbon yield across the cumulative data: 17.58553% at 1800 C, 0.8 s hold, 50 sccm. This is a sampled maximum, not a global optimum.

All species and cycle diagnostics remain in linked raw sources. Only points with completed refinement gates are admitted. Reproduce with `python tools/openmkm_dynamic/report_rph_yield_grid.py`.
