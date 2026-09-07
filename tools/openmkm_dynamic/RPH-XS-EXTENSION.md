# Extend the matched conversion/selectivity comparison

User approved four RPH points and their temperature-only matched CJH states.
Question: does acetylene selectivity persist as conversion increases through
longer hot exposure or lower flow? Preserve undiluted equimolar CH4/CO2,
1 atm, the existing fixed gas volume, Aramco 2.0, and prescribed gas temperature.
No device-energy or carbon-source attribution claim.

All peaks 1800 C, floor 450 C, period 1 s, rise .025 s, fall .10 s.
At 50 sccm add holds .65 and .80 s. At hold .50 s add 25 and 12.5 sccm.
Cold hold is .875 minus hot hold. Standard flow uses 273.15 K and 101325 Pa.
The 39-pair study is the pilot: the 1800 C selectivity curve is still near
50 percent at its high-conversion boundary, motivating these four points.

Use existing pulse and matched-CJH solvers unchanged. Check inert cases at
longest hold and lowest flow, then reproduce the archived 50 sccm/.50 s
reacting anchor with identical inputs and all-species error below 1e-8.
For each new point run 400/800 segment sampling with all-species difference
below 1e-4, retaining original cycle, mass, elemental, pressure and temperature
gates. Only then match CJH and pass its existing stricter tolerance gate.
Stop on any failed gate. No automatic retries, queue or budget increase.

The remaining campaign allowance is 428.256340658026 s. Reserve 400 s for
the full batch; worker cap 150 s or remaining time, whichever is smaller.
Prior points suggest roughly a few minutes, but this is not guaranteed at
new lower flows. Preserve partial results if the cap is reached.

Commit this card, runner and workflow before chemistry. Record hashes and
commit in the output manifest. Archive all raw states under
docs/research/rph-xs-extension-01-2026-09-07/data, reconcile actual time,
and plot separately from the frozen 39-pair inventory. Selectivity uses
product carbon divided by consumed methane carbon, explicitly qualified
because CO2 is a second carbon source. No additional chemistry for plotting.
