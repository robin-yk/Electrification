"""Collect validated grid coverage and retain off-grid observations."""
import itertools
from pathlib import Path
import hashlib
import run_cjh_feed_ratio_01 as base
from run_rph_yield_grid import CAMPAIGN,PEAKS,HOLDS,FLOWS,tag

def main():
    original=base.read(base.ROOT/'docs/research/cjh-rph-matched-39-2026-09-07/report.json')['rows']
    original+=base.read(base.ROOT/'docs/research/rph-xs-extension-01-2026-09-07/report.json')['raw_pairs']
    points={}
    def add(f,p,h,q,expected=None):
        sha=hashlib.sha256(f.read_bytes()).hexdigest()
        if expected:assert sha==expected
        d=base.read(f);key=(p,h,q)
        if key in points:return
        points[key]=dict(peak_C=p,hold_s=h,flow_sccm=q,source=str(f.relative_to(base.ROOT)),sha256=sha,
            inputs=d['inputs'],X_CH4_pct=100*(1-d['mol_per_feed_carbon']['CH4']/.5),
            C2H2_Y_pct=100*d['carbon_yields'].get('C2H2',0),CO_Y_pct=100*d['carbon_yields'].get('CO',0),
            C6H6_Y_pct=100*d['carbon_yields'].get('C6H6',0),
            C2H2_g_gCFP_h=d['product_g_per_g_CFP_h'].get('C2H2',0),
            CO_g_gCFP_h=d['product_g_per_g_CFP_h'].get('CO',0))
    for r in original:add(base.ROOT/r['source'],r['peak_C'],r['hold_s'],r['flow_sccm'],r['sha256'])
    for folder in CAMPAIGN.glob('*/data'):
        mf=folder/'manifest.json'
        if not mf.exists():continue
        for p,h,q in base.read(mf)['jobs']:
            gate=folder/(tag(p,h,q)+'-gates.json')
            if not gate.exists():continue
            g=base.read(gate);assert g['error']<g['threshold']
            add(folder/(tag(p,h,q)+'-n800.json'),p,h,q)
    grid=list(itertools.product(PEAKS,HOLDS,FLOWS))
    covered=[points[k] for k in grid if k in points]
    missing=[k for k in grid if k not in points]
    allrows=sorted(points.values(),key=lambda r:(r['peak_C'],r['hold_s'],r['flow_sccm']))
    best=max(allrows,key=lambda r:r['C2H2_Y_pct'])
    base.write(CAMPAIGN/'observations.json',dict(grid_total=len(grid),grid_completed=len(covered),missing=missing,
        validated_total=len(allrows),points=allrows,best_observed=best))
    lines=['# Acetylene carbon-yield screening','',f'Grid coverage: {len(covered)}/75. Validated cumulative RPH conditions: {len(allrows)}. Off-grid observations are retained separately in observations.json.',
        '', 'Objective: cycle-integrated C2H2 carbon yield divided by total CH4+CO2 inlet carbon. Fixed floor450 C, period1 s, rise0.025 s, fall0.10 s, equimolar undiluted feed, fixed gas volume and pressure. No CJH calculation or Bayesian chemistry is part of this grid.',
        '', '| Peak C | Hold s | Flow sccm | CH4 X % | C2H2 Y C% | CO Y C% | C6H6 Y C% | C2H2 g/gCFP/h |',
        '|---|---|---|---|---|---|---|---|']
    for r in covered:lines.append('| '+' | '.join(f'{r[k]:.7g}' for k in ['peak_C','hold_s','flow_sccm','X_CH4_pct','C2H2_Y_pct','CO_Y_pct','C6H6_Y_pct','C2H2_g_gCFP_h'])+' |')
    lines+=['',f'Best observed C2H2 carbon yield across the cumulative data: {best["C2H2_Y_pct"]:.7g}% at {best["peak_C"]:g} C, {best["hold_s"]:g} s hold, {best["flow_sccm"]:g} sccm. This is a sampled maximum, not a global optimum.',
        '', 'All species and cycle diagnostics remain in linked raw sources. Only points with completed refinement gates are admitted. Reproduce with `python tools/openmkm_dynamic/report_rph_yield_grid.py`.']
    (CAMPAIGN/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(dict(grid_completed=len(covered),validated_total=len(allrows),best_yield_pct=best['C2H2_Y_pct']))

if __name__=='__main__':main()
