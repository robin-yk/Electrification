"""Join the validated new flow pairs with the two archived 50 sccm points."""
import hashlib
from run_cjh_feed_ratio_01 import ROOT,read,write

def main():
    root=ROOT/'docs/research';dest=root/'rph-flow-01-2026-09-07';data=dest/'data'
    assert read(data/'anchor-gates.json')['max_species_error']<1e-8
    rows=[];sources={}
    for h in [.1,.5]:
        for q in [50,100,200,400]:
            if q==50:
                folder=root/f'rph-450-{"screen" if h==.1 else "pilot"}-01-2026-09-07/data'
                f=folder/f'T1800-hold{h:g}-n800.json';gate=folder/f'T1800-hold{h:g}-gates.json'
            else:
                f=data/f'Q{q}-hold{h:g}-n800.json';gate=data/f'Q{q}-hold{h:g}-gates.json'
            if not (f.exists() and gate.exists()):continue
            g=read(gate);assert g['max_species_refinement_error']<1e-4
            d=read(f);assert d['inputs']['flow_sccm']==q
            sources[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
            rows.append(dict(flow_sccm=q,hold_s=h,carbon_yields_pct={k:100*v for k,v in d['carbon_yields'].items()},
                product_g_h=d['product_g_h'],product_g_per_g_CFP_h=d['product_g_per_g_CFP_h'],
                inputs=d['inputs'],cycles=d['cycles'],max_refinement_error=g['max_species_refinement_error']))
    write(dest/'report.json',dict(rows=rows,validated_conditions=len(rows),sources=sources))
    lines=['# Fixed-volume RPH flow comparison','',f'Validated conditions: {len(rows)}/8, including two reused 50 sccm points.',
        '', 'CH4/CO2 1:1, 450-1800 C prescribed gas temperature, 1 s period, rise/fall 0.025/0.10 s, 1 atm. Fixed equivalent gas volume. Standard flow uses 273.15 K/1 atm. Carbon yield denominator is total inlet carbon. CFP mass is 28.8 mg.',
        '', '| Hold s | Flow sccm | C2H2 C% | CO C% | C2H4 C% | C6H6 C% | CH4 C% | CO2 C% | Other C% | C sum % | C2H2 g/h | CO g/h | C2H2 g/g/h | CO g/g/h |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    major=['C2H2','CO','C2H4','C6H6','CH4','CO2']
    for r in rows:
        c=r['carbon_yields_pct'];g=r['product_g_h'];s=r['product_g_per_g_CFP_h']
        vals=[r['hold_s'],r['flow_sccm']]+[c.get(k,0) for k in major]+[sum(v for k,v in c.items() if k not in major),sum(c.values()),g.get('C2H2',0),g.get('CO',0),s.get('C2H2',0),s.get('CO',0)]
        lines.append('| '+' | '.join(f'{v:.7g}' for v in vals)+' |')
    lines+=['','Flow changes residence time at fixed volume. The imposed waveform does not establish that the heater can supply the increased heat load. All species, exact volume and conditions remain in report.json and raw files.']
    (dest/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__=='__main__':main()
