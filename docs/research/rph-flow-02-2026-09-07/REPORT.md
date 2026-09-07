# Fixed-volume RPH flow comparison

Validated conditions: 12/12, including archived lower-flow points.

CH4/CO2 1:1, 450-1800 C prescribed gas temperature, 1 s period, rise/fall 0.025/0.10 s, 1 atm. Fixed equivalent gas volume. Standard flow uses 273.15 K/1 atm. Carbon yield denominator is total inlet carbon. CFP mass is 28.8 mg.

| Hold s | Flow sccm | C2H2 C% | CO C% | C2H4 C% | C6H6 C% | CH4 C% | CO2 C% | Other C% | C sum % | C2H2 g/h | CO g/h | C2H2 g/g/h | CO g/g/h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 50 | 2.624117 | 5.386152 | 0.1324002 | 0.1933326 | 44.65851 | 46.1142 | 0.8872639 | 99.99598 | 0.04572594 | 0.2019266 | 1.587706 | 7.011342 |
| 0.1 | 100 | 2.508393 | 4.016217 | 0.1765641 | 0.1837162 | 45.12205 | 46.95862 | 1.032446 | 99.99801 | 0.08741885 | 0.3011356 | 3.035377 | 10.4561 |
| 0.1 | 200 | 2.202636 | 2.715834 | 0.2426987 | 0.1847892 | 45.69434 | 47.85263 | 1.106088 | 99.99901 | 0.1535261 | 0.407266 | 5.330768 | 14.14118 |
| 0.1 | 400 | 1.71726 | 1.628518 | 0.3336715 | 0.1782879 | 46.39365 | 48.67025 | 1.07787 | 99.99952 | 0.2393898 | 0.4884246 | 8.312144 | 16.95919 |
| 0.1 | 800 | 1.133009 | 0.8450945 | 0.4328272 | 0.1405476 | 47.20997 | 49.2985 | 0.9398145 | 99.99976 | 0.3158877 | 0.506921 | 10.96832 | 17.60142 |
| 0.1 | 1600 | 0.578271 | 0.3587045 | 0.478482 | 0.07075199 | 48.11325 | 49.70226 | 0.6981694 | 99.99988 | 0.3224489 | 0.4303302 | 11.19614 | 14.94202 |
| 0.5 | 50 | 11.17343 | 24.13168 | 0.3664801 | 0.3484391 | 27.58163 | 32.78622 | 3.611147 | 99.99904 | 0.1947001 | 0.9046957 | 6.760421 | 31.41305 |
| 0.5 | 100 | 10.99632 | 18.29069 | 0.5600838 | 0.4640903 | 29.05386 | 36.25375 | 4.380872 | 99.99965 | 0.3832277 | 1.371434 | 13.30652 | 47.61924 |
| 0.5 | 200 | 9.897722 | 12.5412 | 0.8705026 | 0.6175577 | 31.10217 | 40.13007 | 4.840695 | 99.99992 | 0.6898819 | 1.880676 | 23.95423 | 65.30125 |
| 0.5 | 400 | 7.880524 | 7.609822 | 1.326338 | 0.7139354 | 33.83599 | 43.80213 | 4.831264 | 100 | 1.098562 | 2.282336 | 38.14452 | 79.24776 |
| 0.5 | 800 | 5.29638 | 3.99217 | 1.861517 | 0.6243357 | 37.23768 | 46.69019 | 4.297746 | 100 | 1.476654 | 2.394661 | 51.2727 | 83.14795 |
| 0.5 | 1600 | 2.75056 | 1.713628 | 2.177676 | 0.3335258 | 41.19718 | 48.57852 | 3.248929 | 100 | 1.533736 | 2.055803 | 53.25473 | 71.38206 |

Flow changes residence time at fixed volume. The imposed waveform does not establish that the heater can supply the increased heat load. All species, exact volume and conditions remain in report.json and raw files.

## High-flow response

Productivity below is g-product g-CFP^-1 h^-1, with the same 28.8 mg CFP basis.

At hold 0.1 s, doubling flow from 800 to 1600 sccm changes C2H2 productivity by +2.08% and CO by -15.11%.

At hold 0.5 s, doubling flow from 800 to 1600 sccm changes C2H2 productivity by +3.87% and CO by -14.15%.

The sampled CO maximum is at 800 sccm for both holds, with a decline by 1600 sccm. C2H2 remains increasing but shows small incremental gains over this interval; its maximum has not been bracketed. No exact optimum or diffusion limitation is inferred.
