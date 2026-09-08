"""Report only accepted pairs and the archived 1800 C reference."""
import argparse
import re
import run_rph_yield_grid as grid
base=grid.base
ap=argparse.ArgumentParser()
ap.add_argument('--stage',default='hot-boundary-02')
out=grid.CAMPAIGN/ap.parse_args().stage
# Read atom counts only, without constructing the expensive kinetics object.
species_text=base.MECH.read_text().split('\nspecies:\n',1)[1].split('\nreactions:\n',1)[0]
carbon={}
for name,composition in re.findall(r'- name: ([^\n]+)\n  composition: \{([^}]+)\}',species_text):
    entries=dict(part.strip().split(': ') for part in composition.split(','))
    carbon[name.strip("'\"")]=int(entries.get('C',0))
assert len(carbon)==493 and carbon['C2H2']==2 and carbon['C6H6']==6
reference=base.read(grid.CAMPAIGN/'observations.json')['best_observed']
source=base.ROOT/reference['source']
assert grid.sha(source)==reference['sha256']
sources=[(1800,source)]
for p in [1900,2000,2100]:
    stem=grid.tag(p,.8,50)
    gate=out/'data'/f'{stem}-gates.json'
    if gate.exists():
        assert base.read(gate)['error']<1e-4
        sources.append((p,out/'data'/f'{stem}-n800.json'))
rows=[]
for p,f in sources:
    d=base.read(f);y=d['carbon_yields']
    rows.append(dict(peak_C=p,source=str(f.relative_to(base.ROOT)),sha256=grid.sha(f),
        X_CH4_pct=100*(1-d['mol_per_feed_carbon']['CH4']/.5),
        C2H2=100*y.get('C2H2',0),C2H4=100*y.get('C2H4',0),CO=100*y.get('CO',0),
        C6H6=100*y.get('C6H6',0),C6_total=100*sum(v for k,v in y.items() if carbon[k]==6),
        CH4=100*y.get('CH4',0),CO2=100*y.get('CO2',0),
        other_C=100*sum(v for k,v in y.items() if k not in ['CH4','CO2','CO','C2H2','C2H4'] and carbon[k]!=6),
        carbon_sum=100*sum(y.values()),C2H2_g_gCFP_h=d['product_g_per_g_CFP_h'].get('C2H2',0)))
status=base.read(out/'data/status.json')
base.write(out/'report.json',dict(status=status,rows=rows))
lines=['# RPH peak-temperature boundary check','',
 'Hold 0.80 s; total feed 50 sccm, equimolar CH4/CO2; floor 450 C; period 1 s; unchanged fixed gas volume and pressure. All yields use total inlet carbon. Prescribed gas temperature, not heater temperature.','',
 f"Batch status: {status['status']}. Elapsed {status['wall_s']:.2f} s. Only paired, gate-passing points are tabulated.",'',
 '| Peak C | CH4 conversion % | C2H2 C% | C2H4 C% | CO C% | C6 total C% | Benzene C% | CH4 C% | CO2 C% | Other C% | C sum % | C2H2 g/gCFP/h |',
 '|---|---|---|---|---|---|---|---|---|---|---|---|']
keys=['X_CH4_pct','C2H2','C2H4','CO','C6_total','C6H6','CH4','CO2','other_C','carbon_sum','C2H2_g_gCFP_h']
for r in rows:lines.append('| '+str(r['peak_C'])+' | '+' | '.join(f'{r[k]:.5f}' for k in keys)+' |')
lines+=['','Benzene is included in C6 total; do not add it twice. Other C excludes the displayed C6 group. Gas-phase C6 is not a soot measurement. This extrapolation does not validate high-temperature kinetics experimentally.','',
 '## Sources','']
for r in rows:lines.append(f"- {r['peak_C']} C: `{r['source']}`; SHA256 `{r['sha256']}`.")
(out/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:12]))
