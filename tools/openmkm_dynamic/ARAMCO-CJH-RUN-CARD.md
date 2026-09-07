# Aramco isothermal baseline pilot

Author requested additional computation after prioritizing CJH over more RPH.
Existing GRI 50/50 CJH grid has 5996 points and is not regenerated.
New Aramco grid: T=1000/1400/1800 C, tau=0.01/0.1/1 s; CH4/CO2=50/50,
1 atm, prescribed uniform constant gas temperature. No electric/thermal model.
Equal inlet/outlet mass/tau, variable-volume constant-pressure CSTR.

Reuse the unchanged audited transient integrator at zero amplitude. Its period
field is only a five-residence-time observation block, not a pulse. Require
full-state and integrated-outlet stationarity <1e-8 for three consecutive blocks,
min 3/max 100 blocks. This is not an algebraic steady solve. Dense GRI and sparse
preconditioned Aramco retain existing methods. No arbitrary 40-tau acceptance.

Sequence: cold 300 K GRI; reacting 1400 C/0.1 s GRI 20/40 samples per block,
then Aramco 20/40; then the eight remaining grid points. At most 13 integrations.
Sampling comparison at constant T checks integration/output stationarity, not a
varying temperature grid. All species mol per inlet C and CH4 conversion must
agree within 1e-5 for paired runs. Mass partition <1e-6, elemental residual <0.5%,
carbon partition pass. Stop on failure. Other nodes are pilot results, not all
independently tolerance-validated or tested for multiple steady states.

Single thread, batch ceiling 540 s and worker ceiling 90 s including mechanism
loading. Setup excluded. No automatic retries or follow-on batch. Budget is a
hard limit, not a promise of completion. Generator/card committed before run.
Prior RPH pilot completed all jobs in 300.59 s; constant-T costs remain to measure.

Outputs: all-species rates, stationarity and balance audits, hashes, manifest,
conditional mg product per mg CFP per hour at 50 sccm (0 C, 1 atm), CFP 28.8 mg.
Use feed-normalized yields before rescaling, never arbitrary reactor throughput.
The conditional normalization does not prove device feasibility. C2 products
are explicitly C2H2+C2H4+C2H6. H2O/AA limits are predictions, not validation.

No changes to canonical grids. New output directory and no cross-model cache.
Completed cases preserved on timeout; integration checkpoint remains absent.
Artifact: aramco-cjh-baseline. Archive raw results/checksums in Git after finish.
Reproduce: python tools/openmkm_dynamic/run_aramco_cjh_baseline.py --output-dir out/aramco-cjh
