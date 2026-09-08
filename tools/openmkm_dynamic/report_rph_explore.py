"""Preserve source-linked exploration observations separately from EI history."""
import hashlib
import run_cjh_feed_ratio_01 as b
C=b.ROOT/'docs/research/rph-yield-grid-2026-09-07';D=C/'explore-01'
proposal=b.read(D/'proposal.json');records=[]
assert b.read(D/'verify-run.json')['status']=='completed'
training=b.read(D/'training.json')['rows'].copy()
for i,p in enumerate(proposal['proposals']):
    source=D/'verification'/str(i)/'n800.json';r=b.read(source);gate=b.read(source.with_name('gates.json'))
    assert gate['phase_error']<gate['threshold']
    warning=gate['phase_error']>.9*gate['threshold']
    record=dict(**p,source=str(source.relative_to(b.ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),C2H2_Y_pct=100*r['carbon_yields']['C2H2'],carbon_yields=r['carbon_yields'],product_g_per_g_CFP_h=r['product_g_per_g_CFP_h'],inputs=r['inputs'],solver_rtol=r['solver_rtol'],phase_error=gate['phase_error'],phase_threshold=gate['threshold'],near_phase_threshold=warning,selection_class='exploration, not EI',cycles=r['cycles'])
    records.append(record);training.append(record)
assert len(training)==71
b.write(D/'observations-for-next-fit.json',dict(rows=training,n=71,fitted=False,note='Existing model uses 69 observations. These exploration points are not EI improvements.'))
b.write(D/'report.json',dict(rows=records,prior_best_Y_pct=proposal['incumbent_Y_pct'],runtime_s=b.read(D/'verify-run.json')['wall_s']))
lines=['# Two in-domain exploration observations','','These points were selected by posterior uncertainty and maximin distance, not EI. Both pass the unchanged 400/800 phase gate and worker convergence/closure gates. No new best was found.','','| Selection | Peak °C | Hold s | Flow sccm | Predicted yield % | Calculated yield % | Phase error |','|---|---:|---:|---:|---:|---:|---:|']
for r in records:lines.append(f"| {r['kind']} | {r['peak_C']:.2f} | {r['hold_s']:.2f} | {r['flow_sccm']:.2f} | {r['predicted_Y_pct']:.5f} | {r['C2H2_Y_pct']:.5f} | {r['phase_error']:.8g} |")
lines+=['','The short-hold point is within 10% of the phase-error threshold and retains a warning. Passing this absolute gate does not establish tighter relative precision for a minor product. Both calculations overpredict acetylene in the GP, showing that the unobserved corner was less accurately predicted than the second EI neighborhood. Two observations do not establish full-domain model accuracy or rule out undiscovered maxima.','','The 69-point model is preserved. observations-for-next-fit.json contains 71 source-linked observations for a future fit; no 71-point GP has been trained. No third point was run. Raw results, manifest and budget are committed. Actions run: 34180507103.',f"\nDirect calculation elapsed time: {b.read(D/'verify-run.json')['wall_s']:.3f} s."]
(D/'REPORT.md').write_text('\n'.join(lines)+'\n')
