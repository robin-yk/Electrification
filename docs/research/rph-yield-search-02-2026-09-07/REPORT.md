# Repaired acetylene-yield acquisition search

The 39-point GP, objective and bounds were held fixed. No model refit or Aramco integration was performed.

Recommendation: 1766.08574 C, hold 0.5 s, flow 61.965393 sccm.
Predicted C2H2 carbon yield: 11.061186%; posterior SD: 0.312789 percentage points. This is not a validated yield or calibrated uncertainty.

| Search comparison | EI score (standardized yield) |
|---|---|
| Previous recommendation | 0.000119645301 |
| Repaired recommendation | 0.0229122676 |
| Existing incumbent | 0.00287760864 |
| Independent 8192-point reference maximum | 0.0161214713 |

Use all training anchors and corners plus 4096 Sobol seeds; refine the best 24 starts. Never replace a better seed with a worse local result. Require finite, bounded, nonduplicate output and a passing independent reference comparison.

The new point has a lower posterior mean than the existing best observed yield; EI still values the chance of improvement under posterior uncertainty. Passing these finite checks does not establish the global acquisition maximum. The rejected proposal remains preserved in the previous archive.

The reviewed replacement entry point is tools/openmkm_dynamic/repair_rph_yield_search.py. The earlier 39-point proposer and its failed audit remain historical and cannot authorize a chemistry run. Direct verification of the repaired point remains pending.
