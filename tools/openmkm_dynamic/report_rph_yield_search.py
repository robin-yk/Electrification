"""Summarize the repaired search without implying direct chemical verification."""
import json
from repair_rph_yield_search import DEST

def main():
    p=json.loads((DEST/'proposal.json').read_text());a=json.loads((DEST/'search-audit.json').read_text())
    assert a['passed']
    lines=['# Repaired acetylene-yield acquisition search','',
        'The 39-point GP, objective and bounds were held fixed. No model refit or Aramco integration was performed.',
        '',f"Recommendation: {p['peak_C']:.5f} C, hold {p['hold_s']:g} s, flow {p['flow_sccm']:.6f} sccm.",
        f"Predicted C2H2 carbon yield: {p['predicted_carbon_yield_pct'][0]:.6f}%; posterior SD: {p['posterior_sd_percentage_points'][0]:.6f} percentage points. This is not a validated yield or calibrated uncertainty.",
        '', '| Search comparison | EI score (standardized yield) |','|---|---|',
        f"| Previous recommendation | {a['previous_score']:.9g} |",f"| Repaired recommendation | {a['score']:.9g} |",
        f"| Existing incumbent | {a['incumbent_score']:.9g} |",f"| Independent 8192-point reference maximum | {a['independent_reference_best']:.9g} |",
        '', 'Use all training anchors and corners plus 4096 Sobol seeds; refine the best 24 starts. Never replace a better seed with a worse local result. Require finite, bounded, nonduplicate output and a passing independent reference comparison.',
        '', 'The new point has a lower posterior mean than the existing best observed yield; EI still values the chance of improvement under posterior uncertainty. Passing these finite checks does not establish the global acquisition maximum. The rejected proposal remains preserved in the previous archive.',
        '', 'The reviewed replacement entry point is tools/openmkm_dynamic/repair_rph_yield_search.py. The earlier 39-point proposer and its failed audit remain historical and cannot authorize a chemistry run. Direct verification of the repaired point remains pending.']
    (DEST/'REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
