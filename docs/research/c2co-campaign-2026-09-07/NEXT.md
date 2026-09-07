# Bounded C2/CO research continuation

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

## Research order

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
