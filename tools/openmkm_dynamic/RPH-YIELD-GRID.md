# Acetylene carbon-yield grid before Bayesian search

Objective: maximize cycle-integrated C2H2 carbon yield on total CH4+CO2 feed
carbon. CO, C6, other species and CFP-normalized mass rates remain outputs,
not extra objectives. User approved another 3600 s with <=600 s per batch.
The preceding ledger is preserved separately; unused time is not borrowed.

Correct the earlier arithmetic: 3 peak temperatures x 5 hot holds x 5 flows
is 75 combinations, not 225. No extra axis is invented to match that count.
Peaks 1400/1600/1800 C; holds .10/.30/.50/.65/.80 s; flows
12.5/25/50/100/200 sccm. Keep floor450 C, period1 s, rise.025 s, fall.10 s,
cold hold .875-hot hold, fixed volume9.228077898393764e-9 m3, pressure1atm,
equimolar undiluted CH4/CO2, Aramco2.0 and existing prescribed-T solver.
Standard flow is at273.15K/101325Pa. No energy or device claims.

Reuse existing43 RPH points only after source hashes and all physical inputs
match. Preserve off-grid data for later GP fitting but do not count them as
grid coverage. The current high-yield boundary and sparse cross-axis coverage
motivate the factorial grid; they do not establish a global optimum.

Pilot four new combinations: (peak,hold,flow)=(1400,.8,12.5),
(1600,.8,25),(1800,.8,200),(1800,.3,25). Before chemistry check inert
long-hold low/high-flow boundaries and reproduce the existing50/.5/1800
anchor. Then paired400/800 samples for every point, all-species error<1e-4,
unchanged periodic state, temperature, pressure, elemental and mass checks.
Stop on failure; no relaxed gates or retries. Pilot cap240 s. Use its measured
time and response range before remaining batches of at most18 points/540 s.
No fresh CJH matches are required for this yield screen.

Archive manifest, source hashes, raw species and diagnostics in
docs/research/rph-yield-grid-2026-09-07/{stage}/data. Commit code/card and
reservation before dispatch; preserve data and reconcile after every batch.
After grid completion audit boundary maxima and missing/failed points, then
fit NEXTorch to the cumulative validated data. Use repaired multistart
acquisition with an independent candidate-quality check. Commit the exact
recommendation before direct Aramco verification. No Bayesian chemistry is
queued before the grid is reviewed. Budget applies to fitting and simulations.
