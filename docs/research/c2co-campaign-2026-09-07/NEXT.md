# Bounded C2/CO research continuation

## Current: match CJH to all 39 RPH conversions

27/39 verified matches are archived. Group 2 completed in 296.121172857 s
(run 34170083871). Reserve 450 s for group 3, the final 12 conditions.
No other calculation may spend this reservation. Reconcile after completion.

15/39 verified matches are archived. Group 1 completed in 353.486917347 s
(run 34169440821). Reserve 450 s for group 2, the next 12 conditions.
No other calculation may spend this reservation. Reconcile before group 3.
The cumulative generated report includes the pilot and group 1.

Pilot completed 34169130250 in 164.414281501 s; all controls and three matches
passed. Reserve 450 s for group 1 (12 matches). Same-flow cached steady
temperatures now narrow the bracket, but final root and strict check remain
direct integrations. Pilot shows C6 suppression is not universal: at 1600
sccm/.5 s/1800 C RPH has slightly more total C6 than the matched steady case.
Do not generalize before the remaining map. Low-conversion cases are flagged.

User approved temperature-only steady matching with each flow, feed, volume
and pressure unchanged. Pilot run 34169130250 is dispatched, cap 240 s.
Read CJH-RPH-MATCH-39.md. Archive and reconcile before reserving the remaining
three groups of 12. No other task may spend the reservation. Do not claim 39
matches until all final stricter-tolerance match files exist. Flag low-X cases.

## Current: repaired yield search passed, no chemistry dispatched

User requested acquisition repair. Completed in 4.593653625 s; reservation
released. Read rph-yield-search-02-2026-09-07/REPORT.md and proposal.json.
The frozen 39-point model recommends about 1766 C/.5 s/62 sccm with predicted
C2H2 yield about 11.06%. It passes independent 8192-point/anchor EI checks,
but is not an Aramco result. Use repair_rph_yield_search.py as the reviewed
replacement search entry, not the old failed proposer. Original artifacts
remain unchanged. Direct verification is pending; no auto retry or new run
is queued. Heartbeat stays paused and validated point count stays 39.

## Current: single-objective C2H2 carbon yield

STOPPED before chemistry. Proposal completed but frozen-model acquisition
audit failed: chosen EI is below both the incumbent and a 2048-point Sobol
alternative. Read rph-yield-01-2026-09-07/REPORT.md and acquisition-audit.json.
No Aramco run or new validated point. Charge proposal plus both audit process
times; reservation released. Still 39 validated 450 C observations. Keep
heartbeat paused and do not dispatch this candidate. A reviewed acquisition
search correction and an explicit quality gate must precede any retry.
The initial high-uncertainty interpretation was insufficient; no chemical
meaning should be assigned to the rejected recommendation. Historical
reservation text below is no longer active.

User specified C2H2 only. Read RPH-YIELD-01.md. Reserve 240 s for proposal
and one direct verification, charge proposal before reducing reservation to
150 s. Fit 39 validated points to carbon yield, not productivity. No second
point or automatic loop. Preserve the separate qEHVI productivity record.

## Current: one user-approved NEXTorch point

COMPLETED: verification 34162441788 passed inert, archive and paired gates
in 32.762974469 s, plus 3.626738917 s proposal time. Actual productivity
and frozen prediction comparison are in rph-nextorch-01-2026-09-07/REPORT.md.
observations-39.json contains the original 38 plus the validated new point
for a future fit. No second recommendation or loop was run. Budget reconciled,
no reservation or active run; heartbeat remains paused. Prediction errors
at this point are not cross-domain calibration. This supersedes the historical
reservation text below. Do not rerun the fixed 38-point proposer as a new step.

Proposal completed in 3.626738917 s and charged. Frozen proposal.json selects
1800 C, .5 s hold, 1215.7433532794082 sccm. Reserve now only 150 s for the
direct verification. Model/training/proposal must land on main before dispatch.
Do not refit or generate another candidate until this output is reviewed.

Read RPH-NEXTORCH-01.md. Reserve 240 s for proposal generation (90 s max)
and one directly verified recommendation (150 s max). Charge local proposal
time and reduce reservation to 150 before reaction dispatch. No automated
loop, extra point or restart is authorized. Keep heartbeat paused. Archive
proposal and model before chemistry; compare actual output with prediction.

## Current: approved extension to 1600 sccm

COMPLETED: run 34161531681 passed all gates in 95.931335446 s. Four new
paired points, inert control and exact 400 sccm reproduction are archived in
rph-flow-02-2026-09-07/data. Generated report combines 12 conditions. Budget
reconciled; no reservation or active run. CO productivity decreases between
800 and 1600 sccm for both holds, while C2H2 gains become small but positive.
Do not call 800 sccm the exact optimum or C2H2 plateau an established
asymptote. No automatic extension beyond 1600 sccm is queued. Text below
describes the completed dispatch only.

Reserve 240 s for rph-flow-02: 800/1600 sccm at both .1/.5 s holds.
Read the extension in RPH-FLOW-01.md. Run only --extend, stop on failed
gates, then archive and reconcile. No other batch may spend this reservation.
This supersedes the flow-01 completion hold below for these four points only.

## Current: user-approved flow pilot

COMPLETED: run 34160516964, 113.365813586 s. Inert, archive reproduction
and all six paired conditions passed. Eight-condition report includes the two
existing 50 sccm anchors. Raw files and generated report are under
docs/research/rph-flow-01-2026-09-07. Budget reconciled, no reservation or
run in flight. Higher flow lowered C2H2/CO carbon yields but raised g/h in
this sampled range. Do not mistake constant prescribed gas T for a proven
power-feasible operating point. No pressure/period/BO run has been launched.
Reservation text below describes the completed dispatch only. Initial HTTP
404 was workflow registration delay and created no run; one dispatch exists.

Reserve 300 s for rph-flow-01, six new 100/200/400 sccm cases at 1800 C and
0.10/0.50 s hot hold. Read tools/openmkm_dynamic/RPH-FLOW-01.md. This overrides
the completed-grid hold below only for this flow pilot. No pressure/period/BO
batch is queued. Archive, check gates, reconcile the budget before further work.

## Current: approved 450 C floor screening

COMPLETED: run 34158956433 passed all 25 remaining pairs in 365.772934778 s.
All 28 conditions now have paired, gate-passing outputs; report.json and
REPORT.md are generated in rph-450-screen-01-2026-09-07. Budget reconciled;
no reservation or run in flight. Do not repeat this grid or start NEXTorch
automatically. Interpret this map first. C2H2/CO maxima lie at the hot/long
boundary, while the highest sampled C2H4 occurs at 1400 C/0.5 s.
Hot-hold trends are nearly linear within each sampled temperature; account
for changing mean gas temperature and the fixed very small gas volume before
attributing improvement to pulse chemistry. The reservation paragraphs below
describe the now-completed dispatch, not a pending authorization.

This section supersedes historical next-task statements below. User approved
28 peak/hold conditions before NEXTorch. Pilot 34158782803 passed all gates,
45.426795879 s, archived under rph-450-pilot-01-2026-09-07/data.
Reserve 540 s for rph-450-screen-01, the other 25 conditions with paired
400/800 checks. No other batch may start. Read RPH-450-SCREEN.md.
Pilot span is resolved numerically and large across both axes; the three
corners cannot locate the interior transition. Proceed with the approved
grid, not an extra BO or learning-curve campaign. The seven pilot integrations
took about 6.5 s each including overhead, suggesting roughly 325 s for the
remaining 50 integrations; hard cap stays 540 s. Stop on any failed gate.
Archive, generate report_rph_screen_450.py, reconcile budget before further work.

## Latest dispatch superseding the hold below

Completed fixed-flow baseline/refinement 34156729563 and paired period runs
34157035244. All gates passed. No run in flight or reserved; see budget.json.
The 0.5/1/2 s results and deterministic report are in rph-fixed-period-01 archive.
Half-period improves C2H2/CO by only about 0.26/0.29% relative to 1 s. Do not
automatically densify the period axis. Next candidate axis is feed or hot hold,
after a committed bounded card; Bayesian/global optimization is not completed.
This paragraph supersedes stale active/reserved statements and pressure holds below.

User explicitly requested proceeding with fixed-50-sccm CH4/CO2 RPH.
Run 34156729563 completed and is archived; batch rph-fixed-period-01 reserves 240 s.
Accidental prior-version dispatch 34156921810 was cancelled; 16 s charged.
Finite inert expansion predicts the earlier pressure offset, so reviewed
continuation increases controller K tenfold without changing any gate.
Archive and reconcile this run before any follow-on. Only inert, baseline
and refined checks are queued. Stop on failure; no automatic retry.

## Current priority: user-approved minimal fixed-volume RPH gates

User subsequently required legacy-code reconciliation before new calculations.
Read ../rph-implementation-reconciliation-2026-09-07.md first. Three algebraic
species-inventory tests passed, with no ReactorNet integration. The isolated
temperature_step_accounting helper is not connected to production: cooling draws
extra feed and is incompatible with strictly fixed total inlet 50 sccm.
Do not dispatch a retry or treat the earlier periodic pressure failure as solved.

Run 34146144797 completed rph-fixed-gate-01 in 5.493213569 seconds.
Analytic closed ramp passed; constant-temperature species comparison error is zero.
Periodic gate run 34146617236 STOPPED at the first inert cycle after
0.314552381 seconds. Raw diagnostics are archived and budget reconciled.
Pressure relative error 1.945303e-4 exceeds 1e-4; temperature and balances pass.
No reacting or refined integration was launched. No batch is reserved.
Do not dispatch follow-on cases or automatically retry. Diagnose finite pressure
controller response versus numerical interpolation/solver effects before any
manually reviewed correction. Do not loosen the threshold to pass the test.
Use /private/tmp/aramco-feed-ratio-20260907
and this ledger. No new CJH map is queued. This instruction supersedes
historical priorities below. Read tools/openmkm_dynamic/RPH-FIXED-GATE-01.md.
After success, periodic waveform and flow-integral validation remain required
before the proposed baseline pulse and half/double-period comparisons.
An initial dispatch HTTP 404 preceded workflow registration and launched no run.

User authorized hourly continuation, an additional total 3600 seconds of
single-thread calculation time, and at most 600 seconds per batch on 2026-09-07.
The initial CJH run 34084078933 was already running when approval arrived and
is excluded. The initial RPH run is likewise excluded. budget.json is the
authoritative ledger. Build/setup/Node regression time is separate; do not
claim this is an account billing or LLM-token cap.

Hourly thread heartbeat automation ID: c2-co, created and ACTIVE. The user
subsequently supported a larger CJH map after seeing the 95-second baseline.
Provisional target: approximately 100 CJH points, only while successive batches
remain justified by measured map variation/error and within the 3600-second cap.

## Latest continuation decision (supersedes the historical queue below)

The user redirected work to reactor-volume/throughput interpretation and
feed composition. Completed fixed-volume pilots: run 34139549926 (five feed
ratios plus controls) and 34140378445 (40 and 60 mol% CH4). Seven composition
points now exist at 1750 C, total 50 sccm (273.15 K, 1 atm), fixed equivalent
gas volume about 0.009228 cm3. Mass residence time is an output, not held fixed.
The HTML Figure 2 uses numerical CH4/(CH4+CO2) mol% spacing and conditional
28.8 mg CFP productivity. The original 69-point variable-volume map remains
separate; do not sum the maps as independent validation of one closure.

Nominal absolute mole tolerance failed at the tiny reactor volume. Diagnostic
run 34139030070 showed that volume-scaled atol restores stationarity and
archive agreement without relaxing gates. The corrected pilot also passed
the stricter paired anchor. All failures and completed results are archived
and charged in budget.json. No batch is reserved or in flight.

The original checkout /private/tmp/electrification-suite-runtime-check has
uncommitted initial-state work and a stale draft budget. Preserve it; do not
dispatch from or reconcile against that draft. Current worktree:
 /private/tmp/aramco-feed-ratio-20260907
The current main budget ledger is authoritative.

Existing Aramco equal-conversion pathway analysis was found in a DIFFERENT
repository: robin-yk/Electrification, branch claude/electrification-main.
Read docs/C2-PULSE.md and
tools/openmkm_dynamic/data/c2pulse/pathway-ch4co2-tau0.2.json before proposing
duplicate matched-conversion runs. The diagram is
docs/figures/pathway-ch4co2-tau0.2.svg: 5/5/90 CH4/CO2/He, tau 0.2 s,
CJH 1191.99 C, CH4 conversion about 16.5%, RPH peak 1800 C.
Its normalization is carbon fed as methane, not total feed carbon.
The source document explicitly flags an older three-row matched table as
partially uncorrected; do not confuse that table with the corrected pathway
figure. Do not silently transfer that reactor formulation to the new
fixed-volume series.

Next safe task: compare the existing pathway source, normalization and
reactor formulation against current archives. No new sweep or duplicate
equal-conversion calculation is justified before that read-only comparison.
Initial-state work below remains historical pending work, not the immediate
dispatch queue.

## Research order

Current state: 69 unique CJH conditions completed. Latest combined map and
SAMPLING-PROGRESS.md are in ../cjh-refine-05-2026-09-07/. Run 34097793177
passed both gates and all twelve new points. All elapsed time is reconciled
in budget.json. Tolerance run 34108821968 completed all four comparisons;
archive ../cjh-tolerance-01-2026-09-07/ contains the generated report and
raw settings. No batch is reserved or active. Tolerance robustness is supported
at these two candidates only; initial-state independence remains untested.
The low-tau C2H4 decline has
now been observed. C2H2 best yield did not improve and C2H4 improved only
slightly in this last batch. Do not continue automatic low-tau extensions.

Next: implement the planned initial-state diagnostic only after reading
tools/openmkm_dynamic/CJH-INITIAL-STATE-DESIGN.md. It is a design, not an
executable run card or a reservation. Add failing-first tests, explicit version
transition and baseline reproduction before launching a bounded pilot. Inspection
found integrate() copies feed accounting from the initial reactor phase; an
alternate-state test must separate the true inlet basis rather than silently
alter that copy. Existing feed-initialized results remain unaffected.
Prioritize a numerical validation pilot, not more map
points. Inspect solver initialization and integrator settings; design a bounded
test at representative C2H2/C2H4 candidates with explicit rtol/atol and a
different initial reactor composition while keeping feed, pressure, prescribed
gas T and mass-flow/tau convention matched. Initial composition must not
silently change inlet feed or the effective mass-flow basis. If core solver
changes are needed, add failing-first tests, retain immutable old archives,
document the changed hash and reestablish baseline agreement before any
new mechanism/closure claim. Do not bypass model-hash guards. First commit
a run card and reserve budget before dispatch. If matching the model requires
an unresolved physical choice, ask the user rather than infer equivalence.

The sampled-gain table is not a predictive learning curve, and neither peak
is a global-optimum claim. Do not spend toward 100 points merely to reach
a count. Use the
corrected quantitative union comparator, not strict positive-only key equality.
Record sample need from the preceding map before reserving or launching.
Alternate initial-state robustness remains untested. Tolerance checks at two
candidates must not be generalized to the whole map or RPH. Keep the
mechanism and reactor closure fixed for the next map comparison. Do not call
the current boundary candidates global optima or launch blind retries.

1. Archive and analyze the completed Aramco 3-by-3 CJH baseline. Preserve
   carbon yields, all-species inventories, C2H2/CO Pareto membership, C2H4,
   and conditional mg product per mg CFP per hour (50 sccm, 28.8 mg CFP).
2. Fill CJH temperature and residence-time gaps, not a full uniform grid.
   First refinement: 1200 and 1600 C at 0.01/0.1/1 s; 1400 and 1800 C at
   0.03/0.3 s; 1200 C at 0.03/0.3 s. One baseline anchor is repeated before
   the 12 new points to verify the current implementation reproduces archive.
3. Validate promising CJH candidates for numerical tolerance, observation
   horizon and initial-condition dependence before treating rank changes as
   chemical findings. Use measured map errors/changes to justify more points.
4. Only after the CJH baseline is adequate, select small RPH comparison batches
   with explicitly matched feeds and documented temperature comparators.
   Do not regenerate the 5996 existing GRI CJH points. GRI is not a rank filter.
5. Preserve chemical-only claim boundaries. Heat balance, insulation, gas/CFP
   temperature coupling and spatial validation remain separate later modules.
   Do not launch a large Bayesian campaign without demonstrating sample need.

## Each continuation

Read repository AGENTS.md/CLAUDE.md and the Wiki rules. Read this file, ledger,
and compact status first, not full conversation/raw logs. Check active run once;
if unchanged, return quietly. On completion download artifacts immediately,
verify gates and hashes, generate a deterministic report, archive in Git and
update Wiki. Reconcile budget before reserving another batch. Never spend a
reservation twice or start a second concurrent batch. Unknown costs stay reserved.
Commit generator/card/inputs before launch and test before push. Before each
batch report its conditions and cap. Failures stop follow-on simulations;
read-only diagnosis may continue. No blind retries. Record missing outputs.

Keep updates concise and only report changed results, completion, failure or a
needed user decision. Pause the hourly automation when user says stop, budget
is exhausted, or a blocking scientific decision requires user input. Do not
delete existing results, force-push, or modify unrelated apps. Integrate tested
research changes to main via fast-forward after checking origin/main.

## Paths

Repository currently: /private/tmp/electrification-suite-runtime-check.
Remote: https://github.com/robin-yk/Electrification-Suite.
Wiki project: /Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-B2/dynamic-temperature-pulsing.
Full plan: c2co-reactor-design-research-roadmap.md in that Wiki project.
If the temporary checkout disappears, locate an existing clean clone or clone
the remote into a persistent user-owned location. Do not infer that missing
local state resets the remote budget ledger.
