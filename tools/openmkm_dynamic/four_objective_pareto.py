"""Finite-archive four-objective optimization; no new reaction evaluations."""
import json, math, hashlib, sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
D=R/'docs/research'; O=D/'four-objective-pareto-2026-09-10'
def read(p):return json.loads(p.read_text())
def front(points):
    return [i for i,a in enumerate(points) if not any(all(x<=y for x,y in zip(b,a)) and any(x<y for x,y in zip(b,a)) for j,b in enumerate(points) if j!=i)]
if '--test' in sys.argv:
    assert front([[1,1,1,1],[2,2,2,2],[0,3,1,1],[1,1,1,1]])==[0,2,3]
    print('PASS: dominance, tradeoff, equality');sys.exit()
O.mkdir(exist_ok=True)
inputs=[]
def load(p):
    inputs.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    return read(p)
rows=load(D/'all-energy-atlas-2026-09-10/plot-data.json'); excluded=[]
# Remove documented coarse/fine aliases by source filename, preserving distinct waveforms.
fine_paths={str(Path(r['source'])) for r in rows if 'fine' in Path(r['source']).name}
kept=[]
for r in rows:
    source=Path(r['source'])
    if 'coarse' in source.name and str(source.with_name(source.name.replace('coarse','fine'))) in fine_paths:
        excluded.append(dict(id=r['id'],scenario=r['scenario'],reason='paired fine source retained'));continue
    kept.append(r)
rows=kept
# Add only new, accepted flow conditions. A50 reproduction is an alias of archived A.
for flow in [100,200,400]:
    folder=D/f'rph-candidate-flow-pilot-2026-09-10-flow{flow}'
    assert load(folder/f'A{flow}-gate.json')['passed']
    p=folder/f'A{flow}-n8.json'; d=load(p); i=d['inputs']
    for s in d['scenarios']:
        rows.append(dict(id=f'A{flow}-n8',mode='RPH',family='CH4/CO2',closure='Fixed-volume CSTR; prescribed temperature',source=str(p),feed=i['feed'],flow_sccm=flow,volume_cm3=i['volume_m3']*1e6,period_s=i['period_s'],Tmax_C=max(max(v[1:]) for v in i['segments'])-273.15,Y_C2H2_pct=d['Y_C2H2_pct'],CO_C2H2=d['CO_C2H2'],scenario='Full radiation' if s['radiation_remaining']==1 else '90% lower radiation',status='paired native pilot',**s))
valid=[]
for r in rows:
    # Flow references in this atlas are 273.15 K and 101325 Pa; feeds here use mole fractions.
    flow=r.get('flow_sccm'); p=r.get('input_W'); cooling=r.get('cooling_W'); ratio=r.get('CO_C2H2')
    if flow is None or p is None or cooling is None or ratio is None or p<=0:
        excluded.append(dict(id=r['id'],scenario=r['scenario'],reason='missing flow, positive heat, cooling or product ratio'));continue
    feed=r['feed']; total=sum(feed.values())
    if set(feed)-{'CH4','CO2','HE','He','H2','H2O','N2','AR','Ar'}:
        excluded.append(dict(id=r['id'],scenario=r['scenario'],reason='feed carbon adapter unavailable'));continue
    carbon=(feed.get('CH4',0)+feed.get('CO2',0))/total
    mol_s=flow*1e-6/60*101325/(8.314462618*273.15)
    rate=mol_s*carbon*r['Y_C2H2_pct']/200*1000
    r=dict(r,C2H2_mmol_s=rate,C2H2_mmol_kJ=rate*1000/p,standard_T_K=273.15,standard_P_Pa=101325)
    if not all(math.isfinite(x) for x in [r['Y_C2H2_pct'],r['C2H2_mmol_kJ'],ratio,cooling]):
        excluded.append(dict(id=r['id'],reason='nonfinite objective'));continue
    # Keep unlike reactor closures and thermal boundaries in separate optimization pools.
    r['pool']=r['family']+' | '+('CSTR' if 'CSTR' in r['closure'] else r['closure'])+' | '+r['scenario']
    valid.append(r)
results=[]
for pool in sorted({r['pool'] for r in valid}):
    group=[r for r in valid if r['pool']==pool]
    for target in [1.,1.5,1.75]:
        objectives=[[-r['Y_C2H2_pct'],-r['C2H2_mmol_kJ'],abs(r['CO_C2H2']-target),r['cooling_W']] for r in group]
        selected=front(objectives)
        results.append(dict(pool=pool,target_CO_C2H2=target,evaluated=len(group),pareto_count=len(selected),pareto=[dict(group[j],objective_minimization=objectives[j]) for j in selected]))
def save(name,data):(O/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
save('eligible-records.json',valid);save('excluded-records.json',excluded);save('pareto.json',results);save('input-manifest.json',inputs)
coverage=load(D/'all-energy-atlas-2026-09-10/summary.json')
inputs.append(dict(path=str(Path(__file__).resolve()),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
save('input-manifest.json',inputs)
save('summary.json',dict(eligible_unique_ids=len({r['id'] for r in valid}),eligible_scenario_rows=len(valid),excluded_scenario_rows=len(excluded),upstream_coverage=coverage,new_reaction_integrations=0,method='exact nondominance on finite archived records'))
lines=['# Four-objective archive optimization','',
'Objectives: maximize total-feed-carbon acetylene yield; maximize acetylene mmol per kJ of positive thermal input; minimize absolute CO/C2H2 molar-ratio error; minimize additional cooling duty in W. All dominance tests use these four quantities without a weighted sum. Equal objective vectors remain tied.','',
'Target ratios 1, 1.5 and 1.75 are separate demand scenarios. Reactor closures, feed families and thermal boundaries define separate pools. Gas-only cases remain separate from CFP storage and radiation accounting. Additional cooling is a thermal duty, not cooling-system electricity. Radiation reduction retains the imposed temperature waveform.','',
'This is an exact Pareto selection over saved evaluations. It is an initialization and coverage assessment for a subsequent multi-objective Bayesian search. It does not propose or evaluate new conditions. Different temperatures, compositions, volumes and flows within a pool remain design choices, not matched controls. Supply-feasibility flags are retained without an imposed device-feasibility filter.','',
'CO/C2H2 mismatch is minimized, without declaring any tolerance band feasible. For CH4/He the ratio is zero at every point, so this objective is constant; those fronts cannot supply the target CO-containing mixture without external CO. Cooling duty is also constant at zero for many cases, reducing the effective number of conflicting objectives in those subsets. Pareto membership supplies no unique ranking.','',
'## Coverage','',f"Eligible condition IDs: {len({r['id'] for r in valid})}; thermal-scenario rows: {len(valid)}. Documented coarse members are removed when their fine source is present. A50 is retained once through its original archived record. New accepted A100/A200/A400 pairs are included at fine resolution.",'',
'The source atlas indexes additional legacy and unsupported files. Those records have not acquired energy adapters through this operation. Consult its missing-and-excluded.json, legacy-pending.json and cached-branch-inventory.json; this report does not claim all historical calculations are eligible.','',
'| Pool | Target CO/C2H2 | Evaluated | Nondominated |','|---|---:|---:|---:|']
for s in results:lines.append(f"| {s['pool']} | {s['target_CO_C2H2']} | {s['evaluated']} | {s['pareto_count']} |")
lines+=['','## Retained candidates','', 'Each scenario lists all candidate IDs. Exact objectives and operating inputs are in pareto.json.']
for s in results:
    lines+=['',f"### {s['pool']}; target {s['target_CO_C2H2']}",'','| ID | Mode | Yield (%) | mmol/kJ | CO/C2H2 | Cooling W |','|---|---|---:|---:|---:|---:|']
    for r in sorted(s['pareto'],key=lambda r:-r['C2H2_mmol_kJ']):lines.append(f"| {r['id']} | {r['mode']} | {r['Y_C2H2_pct']:.3f} | {r['C2H2_mmol_kJ']:.5f} | {r['CO_C2H2']:.4f} | {r['cooling_W']:.3f} |")
lines+=['','Reproduce: `python tools/openmkm_dynamic/four_objective_pareto.py`. Test: append `--test`.']
(O/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps([dict(pool=s['pool'],target=s['target_CO_C2H2'],evaluated=s['evaluated'],pareto=s['pareto_count']) for s in results],indent=2))
