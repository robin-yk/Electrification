"""Reproduce the first Bayesian iteration report from its frozen artifacts."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
d=root/'docs/research/rph-yield-grid-2026-09-07/bo-01'
def read(p):return json.loads(p.read_text())
p=read(d/'proposal.json');v=read(d/'development-validation.json');s=read(d/'verification/status.json')
lines=['# First Bayesian acetylene-yield iteration','',
f"Training: {p['training_n']} accepted conditions. Bounds: 1400 to 2000 C, .10 to .80 s hot hold, 12.5 to 200 sccm (log flow). Fixed gas-temperature waveform family, volume, pressure and equimolar feed.",'',
f"Development holdout: 12 points, RMSE {v['rmse_pp']:.4f} percentage points, maximum error {v['max_error_pp']:.4f}. This single split does not establish accuracy throughout the domain or experimental validity.",'',
f"EI recommendation: {p['peak_C']:.6f} C, {p['hold_s']:.6f} s, {p['flow_sccm']:.6f} sccm. Predicted total-feed-carbon C2H2 yield {p['predicted_Y_pct'][0]:.5f}%, GP posterior SD {p['posterior_sd_pp'][0]:.5f} percentage points.",'',
f"Direct verification status: {s['status']}; elapsed {s['wall_s']:.2f} s."]
if s['status']=='completed':
    r=read(d/'verification/result.json');raw=read(d/'verification'/r['source'])
    lines+=['',f"Actual paired-verified C2H2 yield: {r['actual_Y_pct']:.5f}%. Previous best: {p['incumbent_Y_pct']:.5f}%. Change: {r['improvement_pp']:+.5f} percentage points.",
        f"C2H2 productivity: {raw['product_g_per_g_CFP_h']['C2H2']:.5f} g/gCFP/h using 28.8 mg CFP. CO carbon yield: {100*raw['carbon_yields']['CO']:.5f}%.",
        '', 'This is one direct-verified Bayesian iteration, not a demonstrated global optimum. The recommendation lies at the hold-time upper bound and flow lower bound.']
else:lines+=['',f"Failure: {s['reason']}. No direct-verified recommendation yield is admitted."]
lines+=['','Sources: training.json, development-validation.json, proposal.json, search-audit.json, verification/manifest.json, verification/status.json and raw paired outputs. Earlier preflight bookkeeping failures are preserved and charged in the budget.']
(d/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
