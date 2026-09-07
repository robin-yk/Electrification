"""Compare frozen GP predictions with the independently integrated proposal."""
import hashlib
from run_cjh_feed_ratio_01 import ROOT,read,write

def hypervolume(points):
    p=sorted((max(0,x),max(0,y)) for x,y in points)
    area=0;previous=0
    for i,(x,_) in enumerate(p):
        area+=(x-previous)*max(y for _,y in p[i:]);previous=x
    return area

def main():
    dest=ROOT/'docs/research/rph-nextorch-01-2026-09-07';data=dest/'data'
    assert read(data/'status.json')['status']=='completed'
    assert read(data/'candidate-gates.json')['max_species_refinement_error']<1e-4
    d=read(data/'refined.json');p=read(dest/'proposal.json');t=read(dest/'training.json')
    species=t['objectives'];actual=[d['product_g_per_g_CFP_h'][k] for k in species]
    predicted=p['predicted_g_per_g_CFP_h'];old=[r['y'] for r in t['points']]
    before=hypervolume(old);after=hypervolume(old+[actual])
    comp=[dict(species=k,predicted=a,actual=b,prediction_error_pct_of_actual=100*(a-b)/b) for k,a,b in zip(species,predicted,actual)]
    new=dict(peak_C=p['peak_C'],hold_s=p['hold_s'],flow_sccm=p['flow_sccm'],x=p['normalized_x'],y=actual,
        source=str((data/'refined.json').relative_to(ROOT)))
    updated=dict(t);updated['points']=t['points']+[new];updated['sources']=dict(t['sources'])
    updated['sources'][new['source']]=hashlib.sha256((data/'refined.json').read_bytes()).hexdigest()
    write(dest/'observations-39.json',updated)
    result=dict(comparison=comp,hypervolume_before=before,hypervolume_after=after,
        hypervolume_improvement_pct=100*(after/before-1),
        dominated_by_existing=any(all(a>=b for a,b in zip(y,actual)) and any(a>b for a,b in zip(y,actual)) for y in old),
        inputs=d['inputs'],carbon_yields_pct={k:100*v for k,v in d['carbon_yields'].items()},
        source_sha256=updated['sources'][new['source']],next_training_n=39)
    write(dest/'report.json',result)
    lines=['# First NEXTorch RPH recommendation: direct verification','',
        f"Train on 38 conditions; verify one new point at {p['peak_C']:.6g} C, {p['hold_s']:.6g} s hot hold and {p['flow_sccm']:.9g} sccm.",
        '', 'Gas floor 450 C, period 1 s, rise/fall .025/.10 s, CH4/CO2 1:1, fixed gas volume and 1 atm. Productivity unit: g-product g-CFP^-1 h^-1 (28.8 mg CFP).',
        '', '| Species | NEXTorch prediction | Aramco verified | Prediction error (% of actual) |','|---|---|---|---|']
    for c in comp:lines.append(f"| {c['species']} | {c['predicted']:.6g} | {c['actual']:.6g} | {c['prediction_error_pct_of_actual']:+.3f} |")
    lines+=['',f"Observed two-objective hypervolume increases by {result['hypervolume_improvement_pct']:.4f}% relative to the existing 38 points, using a zero-productivity reference. This is a computed Pareto-coverage metric, not a percentage increase in both products.",
        '',f"Dominated by an existing point: {result['dominated_by_existing']}. The verified new observation is saved in observations-39.json for subsequent fitting. No second recommendation or automatic loop was run.",
        '', 'The paired integration passed existing numerical gates. One prediction check does not calibrate the GP across the unsampled domain or validate the gas-phase mechanism against experiment. The imposed temperature does not establish heater power feasibility.']
    (dest/'REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

if __name__=='__main__':main()
