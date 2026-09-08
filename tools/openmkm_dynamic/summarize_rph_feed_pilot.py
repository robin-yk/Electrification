"""Compare one accepted composition pilot with its hashed equimolar anchor."""
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/research/rph-yield-grid-2026-09-07/feed-pilot-02'
def read(p):return json.loads(p.read_text())
def main():
    status=read(D/'status.json');assert status['status']=='completed'
    manifest=read(D/'manifest.json');anchor=manifest['reused_anchor'];p=ROOT/anchor['source']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==anchor['sha256']
    old=read(p);new=read(D/'0/n800.json');lo=read(D/'0/n400.json')
    assert {k:v for k,v in old['inputs'].items() if k!='feed'}=={k:v for k,v in new['inputs'].items() if k!='feed'}
    keys=set(new['mol_per_feed_carbon'])|set(lo['mol_per_feed_carbon'])
    phase=max(abs(new['mol_per_feed_carbon'].get(k,0)-lo['mol_per_feed_carbon'].get(k,0)) for k in keys)
    assert phase<1e-4
    rows=[]
    for raw in [old,new]:
        m=raw['mol_per_feed_carbon'];y=raw['carbon_yields'];i=raw['inputs']
        rows.append(dict(CH4_feed_pct=100*i['feed']['CH4'],
            X_CH4_pct=100*(1-m.get('CH4',0)/i['feed']['CH4']),
            X_CO2_pct=100*(1-m.get('CO2',0)/i['feed']['CO2']),
            C2H2_Y_pct=100*y.get('C2H2',0),CO_Y_pct=100*y.get('CO',0),
            C2H4_Y_pct=100*y.get('C2H4',0),C6H6_Y_pct=100*y.get('C6H6',0),
            CO_per_C2H2=m['CO']/m['C2H2'],C2H2_g_gCFP_h=raw['product_g_per_g_CFP_h']['C2H2']))
    report=dict(rows=rows,phase_error=phase,wall_s=status['wall_s'],final_cycle=new['history'][-1],
        scope='Composition-only pilot. Not a ratio-constrained or Bayesian optimum.')
    (D/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Composition-only RPH pilot','',
        'Fixed: 1800 C peak, 450 C floor, 0.80 s hold, 1 s period, 50 sccm, 1 atm, 0.009228077898 cm3. Rise/fall: 0.025/0.10 s. Standard flow: 273.15 K, 101325 Pa. Carbon yields use total inlet carbon; productivity uses 0.0288 g CFP.', '',
        '| CH4 feed (%) | CH4 conversion (%) | C2H2 carbon yield (%) | CO carbon yield (%) | CO/C2H2 (mol/mol) | C2H2 (g/gCFP/h) |',
        '|---:|---:|---:|---:|---:|---:|']
    for r in rows:lines.append('| '+' | '.join(f'{r[k]:.5f}' for k in ['CH4_feed_pct','X_CH4_pct','C2H2_Y_pct','CO_Y_pct','CO_per_C2H2','C2H2_g_gCFP_h'])+' |')
    lines+=['',f'Paired phase error: {phase:.8g}. Calculation time: {status["wall_s"]:.3f} s.', '',
        'The equimolar point is reused from the source-hashed archive. This single new point does not locate a feed-ratio root or a yield optimum.', '',
        'Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_feed_pilot.py`.']
    (D/'REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
