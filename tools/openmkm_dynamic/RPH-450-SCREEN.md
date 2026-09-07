# Fixed-flow RPH screen at a 450 C floor

User approved 28 conditions on 7 September 2026 before NEXTorch optimization.
Question: how do peak gas temperature and hot hold affect product distribution?
Peak temperatures: 1200/1400/1600/1800 C. Hot holds:
0.025/0.05/0.10/0.20/0.30/0.40/0.50 s. Period 1 s; linear rise 0.025 s,
fall 0.10 s; cold hold 0.875 minus hot hold. Floor 450 C throughout.
CH4/CO2 1:1, 50 sccm at 273.15 K and 1 atm; fixed archived equivalent gas
volume; pressure controller K=1e-7. This prescribes gas temperature, not power.
Aramco 2.0, Cantera 3.2.0, sparse preconditioner and volume-scaled tolerance.
No heat-transfer, electrode, solid-carbon or electrical model is added.

Reuse the analytic and constant-temperature gates for the unchanged reactor;
test custom-floor initialization and all 28 waveforms. The new pilot runs an
inert maximum-ramp case, then reacting 1200 C/0.025 s, 1800 C/0.025 s and
1800 C/0.50 s, each at 400 and 800 samples per segment. All existing pressure,
temperature, cycle convergence, mass and elemental gates remain unchanged.
Require all-species output refinement below 1e-4 mol/mol inlet carbon.
Stop immediately at any failed gate. No automatic retries or relaxed limits.

Pilot cap 240 s. Review pilot variation and measured runtime before reserving
the remaining 25 conditions, each also paired at 400/800 resolution, cap 540 s.
Prior measured period runs averaged about 5 s per reacting integration; 56
integrations would be about 280 s at that rate, not a runtime guarantee for the
new floor and longer holds. Existing cumulative 3600 s authorization applies.
The pilot establishes variation across the new axes; no claim of a predictive
learning curve or Bayesian optimum. Additional sampling beyond the approved
grid requires evidence of unresolved trends and a new budget decision.

Cache: do not mix 600 C floor outputs into the 450 C grid. Preserve all prior
archives. Reuse completed pilot points only with identical source hashes.
Archive raw species outflows, carbon yields, g/h and g/g-CFP/h (28.8 mg basis),
diagnostics, refinement gates, code/mechanism hashes and elapsed time under
docs/research/rph-450-{pilot,screen}-01-2026-09-07/data. Generator and card
are committed before dispatch; results must be committed after download.
Only this screen's table/report and the Wiki RPH status are affected. No old
HTML figure or pathway is invalidated, and no unrelated app is changed.
