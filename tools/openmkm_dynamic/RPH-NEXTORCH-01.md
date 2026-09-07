# First NEXTorch recommendation and direct verification

User approved beginning NEXTorch after 38 distinct 450 C RPH conditions.
Make ONE recommendation, then verify with Aramco. No unattended loop or
bulk Bayesian campaign. Claim: test a surrogate-guided point and measure
prediction error and observed Pareto change, not establish a global optimum.

Inputs: peak 1200-1800 C, hot hold .025-.50 s, total flow 50-1600 sccm.
Map the first two linearly and flow logarithmically to [0,1]. Fix floor
450 C, period 1 s, rise/fall .025/.10 s, CH4/CO2 1:1, 1 atm, archived
equivalent gas volume and all reactor/numerical closures. Temperature is
prescribed gas temperature, not predicted heater temperature or power.
Use exactly the 38 gate-passing 800-sample outputs, SHA256 checked and
deduplicated from the 28-point screen and 12-point flow reports. Exclude
600 C floor data and all older closure variants.

Objectives: C2H2 and CO g-product/g-CFP/h, CFP .0288 g. NEXTorch 0.4.0,
qEHVI, raw reference [0,0] translated into NEXTorch's standardized response
coordinates. Standardize each raw objective, no log transform or weight sum.
Flow log scaling sets the input distance metric; it does not change yields.
Seed 20260907, CPU one thread. Archive source hashes, versions, training
values, model state, posterior means/SD and proposed coordinates before
reaction dispatch. Posterior SD is not established chemistry uncertainty.

Existing synthetic qEHVI/update check passed. Check input transforms,
continuous waveform, source integrity and count before fitting. Sparse
cross-axis coverage remains a limitation; one sequential point tests the
surrogate. This is not a learning-curve-qualified bulk optimization.
Exact proposed settings are frozen in proposal.json before dispatch.

Reserve 240 s: at most 90 s for local proposal generation including fitting,
then at most 150 s for inert at proposal conditions, archived 400 sccm
reproduction (<1e-8 mol/mol C), new candidate 400/800 pair (<1e-4).
All existing elemental/mass/pressure/temperature/periodic gates unchanged.
Expected reaction time about 30-40 s from recent integrations, not guaranteed.
Charge actual proposal time first and reduce the reservation to 150 s before
dispatch; charge all failure times, no automatic retries or threshold changes.
No change to the production reactor is needed.

Archive under docs/research/rph-nextorch-01-2026-09-07. Commit this generator
and card before fitting, commit proposal before chemistry, archive raw
reaction results and deterministic prediction comparison afterward. Update
Wiki RPH status, not unrelated HTML figures or other apps. Automated hourly
continuation remains paused; no second point until the first is reviewed.
