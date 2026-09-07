"""Render the validated 450 C grid from immutable integration outputs."""
import json
import hashlib
from pathlib import Path
from run_rph_screen_450 import PEAKS,HOLDS,tag
from run_cjh_feed_ratio_01 import ROOT,write

def main():
    folders=[ROOT/f'docs/research/rph-450-{s}-01-2026-09-07/data' for s in ['pilot','screen']]
    rows=[]; sources={}
    for p in PEAKS:
        for h in HOLDS:
            for folder in folders:
                f=folder/(tag(p,h)+'-n800.json'); g=folder/(tag(p,h)+'-gates.json')
                if not (f.exists() and g.exists()):continue
                d=json.loads(f.read_text()); gate=json.loads(g.read_text())
                assert gate['max_species_refinement_error']<gate['threshold']
                sources[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
                cy=d['carbon_yields']; rates=d['product_g_per_g_CFP_h']
                rows.append(dict(peak_C=p,hold_s=h,average_T_C=450+(p-450)*(h+.0625),
                    carbon_yields_pct={k:100*v for k,v in cy.items()},
                    carbon_sum_pct=100*sum(cy.values()),product_g_per_g_CFP_h=rates,
                    max_refinement_error=gate['max_species_refinement_error'],
                    inputs=d['inputs'],cycles=d['cycles']))
                break
    dest=ROOT/'docs/research/rph-450-screen-01-2026-09-07'
    dest.mkdir(parents=True,exist_ok=True)
    write(dest/'report.json',dict(validated_conditions=len(rows),planned_conditions=28,rows=rows,sources=sources))
    lines=['# RPH 450 C floor screening','',f'Validated conditions: {len(rows)}/28. Only paired, gate-passing outputs appear below.',
        '', 'Feed CH4/CO2 1:1, 50 sccm (273.15 K, 1 atm), fixed equivalent gas volume. Period 1 s; rise/fall 0.025/0.10 s. Gas temperature prescribed. Productivity uses 28.8 mg CFP.',
        '', '| Peak C | Hot hold s | Mean C | CH4 C% | CO2 C% | C2H2 C% | CO C% | C2H4 C% | C6H6 C% | Other C% | C total % | C2H2 g/g/h | CO g/g/h |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    major=['CH4','CO2','C2H2','CO','C2H4','C6H6']
    for r in rows:
        c=r['carbon_yields_pct'];q=r['product_g_per_g_CFP_h']
        v=[r['peak_C'],r['hold_s'],r['average_T_C']]+[c.get(k,0) for k in major]+[sum(v for k,v in c.items() if k not in major),r['carbon_sum_pct'],q.get('C2H2',0),q.get('CO',0)]
        lines.append('| '+' | '.join(f'{x:.6g}' for x in v)+' |')
    lines+=['','Carbon yields use total inlet carbon. Other carbon includes all remaining gas species, not H2 or H2O. The JSON retains every species and full conditions. This grid varies mean temperature together with hot hold; it is not an equal-energy comparison.']
    (dest/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__=='__main__':main()
