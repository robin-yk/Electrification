"""Inventory local calculation archives and normalize supported energy records."""
import os
for k,v in dict(TZ='UTC0',LC_ALL='C',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1').items(): os.environ[k]=v
import json,hashlib,math,collections,subprocess,time
from pathlib import Path
import numpy as np
import cantera as ct
from element_drive import cfp_heat_capacity
R=Path(__file__).resolve().parents[2]
W=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-B2/dynamic-temperature-pulsing')
E=W/'energy-audit-data'; O=R/'docs/research/all-energy-atlas-2026-09-10';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,d): (O/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
start=time.monotonic();inventory=[];raw={};phase={};issues=[]
roots=[R/'docs/research',R/'tools/openmkm_dynamic/data',R/'tools/cantera',W]
for root in roots:
    if not root.exists():continue
    for p in root.rglob('*'):
        if not p.is_file() or O in p.parents or p.suffix not in ('.json','.jsonl','.csv','.npz'):continue
        record=dict(path=str(p),bytes=p.stat().st_size,suffix=p.suffix)
        if p.stat().st_size>30_000_000:
            record['status']='large file inventoried; not parsed';inventory.append(record);continue
        record['sha256']=sha(p)
        if p.suffix!='.json':record['status']='indexed; adapter not applied';inventory.append(record);continue
        try:d=read(p)
        except Exception as err:record['status']='parse error';record['error']=str(err);inventory.append(record);continue
        record['status']='indexed JSON';record['top_keys']=list(d)[:18] if isinstance(d,dict) else []
        if isinstance(d,dict) and 'mol_per_feed_carbon' in d and 'inputs' in d:
            entry=raw.setdefault(record['sha256'],dict(data=d,paths=[]));entry['paths'].append(str(p));record['status']='flow result candidate'
        if isinstance(d,dict) and 'phase_steps' in d and 'inlet_enthalpy_flow_W' in d:
            phase[str(p)]=d;record['status']='phase energy candidate'
        inventory.append(record)
save('file-inventory.json',inventory)
refs=subprocess.check_output(['git','for-each-ref','--format=%(refname)','refs/remotes'],cwd=R,text=True).splitlines()
branch_files=[]
for ref in refs:
    lines=subprocess.check_output(['git','ls-tree','-r','--name-only',ref,'--','docs/research','tools/openmkm_dynamic/data'],cwd=R,text=True).splitlines()
    branch_files.extend(dict(ref=ref,path=p,status='cached branch indexed; no numerical adapter applied unless a local archive supplies it') for p in lines if p.endswith(('.json','.jsonl','.csv','.npz')))
save('cached-branch-inventory.json',branch_files)
gas=ct.Solution(str(R/'tools/cantera/mechanisms/aramco20.yaml'));gas.TP=298.15,101325
h=dict(zip(gas.species_names,gas.partial_molar_enthalpies/1000));carbon={s:gas.n_atoms(s,'C') for s in gas.species_names}
plots=[];cases=[];aliases=[]
def add(base,y,qrx,qgas,rad,phase_powers=None):
    case=dict(base,Y_C2H2_pct=y,Q_rxn_W=qrx,Q_gas_net_W=qgas,radiation_unscaled_W=rad)
    cases.append(case)
    for factor in [0,1,.1]:
        if phase_powers is None:
            power=qgas+factor*rad;cooling=max(0,-power)
        else:
            power=sum(max(g+s+factor*r,0) for g,s,r,dt in phase_powers)/base['period_s']
            cooling=sum(max(-g-s-factor*r,0) for g,s,r,dt in phase_powers)/base['period_s']
            if factor==0:
                power=sum(max(g,0) for g,s,r,dt in phase_powers)/base['period_s']
                cooling=sum(max(-g,0) for g,s,r,dt in phase_powers)/base['period_s']
        if power<=0 or not all(math.isfinite(v) for v in [y,qrx,power]):continue
        if factor!=0 and phase_powers is not None:
            store=sum(s for g,s,r,dt in phase_powers)/base['period_s']
            assert abs(power-cooling-qgas-factor*rad-store)<1e-5
        plots.append(dict(case,scenario={0:'Gas only',1:'Full radiation',.1:'90% lower radiation'}[factor],radiation_remaining=factor,input_W=power,cooling_W=cooling,eta_rxn_pct=100*qrx/power))
# Archived CJH energies use a checked 298.15 K reference in the source audit.
audit=read(E/'saved-energy-audit.json'); ar={r['source']:r for r in audit['rows']}
cjh=read(E/'archive-energy-extension/results.json')['rows'];unique={}
for r in cjh:
    key=json.dumps([r['T_C'],r['flow_sccm'],r['feed'],r['volume_cm3'],r['pressure_Pa']],sort_keys=True)
    if key not in unique or r['element_residual']<unique[key]['element_residual']:unique[key]=r
for k,r in unique.items():
    a=ar.get(r['source']);i=a['inputs'] if a else None
    if not a or r['element_residual']>1e-4:
        issues.append(dict(source=r['source'],reason='missing reaction-heat audit or elemental gate failed'));continue
    fin=r['flow_sccm']*1e-6/60*i['standard_P_Pa']/(8.314462618*i['standard_T_K'])
    cin=sum(carbon.get(s,0)*v for s,v in r['feed'].items());y=200*(r['C2H2_mmol_h']/3.6e6)/(fin*cin)
    assert abs(a['net_reaction_reference_W']+a['outlet_sensible_from_298K_W']-r['gas_duty_W'])<1e-5
    base=dict(id='CJH-'+hashlib.sha256(k.encode()).hexdigest()[:10],mode='CJH',family='CH4/CO2',closure='Fixed-volume CSTR',source=r['source'],source_sha256=r['source_sha256'],feed=r['feed'],flow_sccm=r['flow_sccm'],volume_cm3=r['volume_cm3'],GHSV_h_inverse=r['flow_sccm']*60/r['volume_cm3'],Tmax_C=r['T_C'],pressure_Pa=r['pressure_Pa'],CO_C2H2=r['CO_to_C2H2'],period_s=None,status='archived elemental screening; device feasibility not inferred',electrical_screen_pass=r['screen_pass'])
    add(base,y,a['net_reaction_reference_W'],r['gas_duty_W'],r['radiation_W'])
# New six-point CJH pilot and current native CJH records, excluding repeats.
for p in sorted((R/'docs/research').glob('cjh-energy*/*tight.json')):
    d=read(p)
    if 'net_reaction_heat_298_W' not in d:continue
    T=d['T_K']-273.15;feed={'CH4':d['feed_CH4'],'CO2':1-d['feed_CH4']}
    key=json.dumps([T,d['flow_sccm'],feed,d['volume_m3']*1e6,d['pressure_Pa']],sort_keys=True) if 'volume_m3'in d else ''
    if any(abs(c['Tmax_C']-T)<1e-6 and c['flow_sccm']==d['flow_sccm'] and c['feed']==feed for c in cases):continue
    m=d['mol_per_feed_carbon'];vol=d['volume_m3']*1e6
    add(dict(id=p.stem,mode='CJH',family='CH4/CO2',closure='Fixed-volume CSTR',source=str(p),source_sha256=sha(p),feed=feed,flow_sccm=d['flow_sccm'],volume_cm3=vol,GHSV_h_inverse=d['flow_sccm']*60/vol,Tmax_C=T,pressure_Pa=d['pressure_Pa'],CO_C2H2=m['CO']/m['C2H2'] if m['C2H2']>0 else None,period_s=None,status='paired native pilot'),200*m['C2H2'],d['net_reaction_heat_298_W'],d['cold_gas_duty_W'],d['radiation_W'])
# Select highest-resolution member of each physical input signature.
group={}
for digest,entry in raw.items():
    d=entry['data'];i=d['inputs']
    if 'segments' not in i or 'feed' not in i or not isinstance(i['feed'],dict):continue
    physical={k:v for k,v in i.items() if k not in ['samples_per_segment','points_per_cycle','rtol','atol']}
    key=json.dumps(physical,sort_keys=True)
    score=(i.get('samples_per_segment',0),-d.get('solver_rtol',1))
    if key not in group or score>group[key][0]:group[key]=(score,digest,entry)
    aliases.append(dict(signature=hashlib.sha256(key.encode()).hexdigest(),sha256=digest,paths=entry['paths']))
for key,(_,digest,entry) in group.items():
    d=entry['data'];i=d['inputs'];feed=i['feed'];m=d['mol_per_feed_carbon']
    cin=sum(carbon.get(s,0)*v for s,v in feed.items())
    if cin<=0:issues.append(dict(source=entry['paths'][0],reason='nonreacting or zero carbon control'));continue
    ep=None
    for path in entry['paths']:
        candidate=str(Path(path).with_name(Path(path).stem+'-energy.json'))
        if candidate in phase:ep=candidate;break
    history=d.get('history',[]);hist=history[-1] if history else {}
    err=max([abs(v) for v in hist.get('elemental_residuals',{}).values()]+[abs(hist.get('mass_residual',1))])
    thermal_failed=any('high-flow-passive-pilot' in p for p in entry['paths'])
    if not ep or err>1e-4 or hist.get('max_species_cycle_change',1)>1e-6 or thermal_failed:
        issues.append(dict(source=entry['paths'][0],source_sha256=digest,reason='thermal iteration gate failed' if thermal_failed else 'missing phase-resolved energy' if not ep else 'cycle or elemental gate failed',Y_C2H2_pct=200*m.get('C2H2',0),mode='RPH',energy_available=bool(ep)));continue
    unknown=(set(m)|set(feed))-set(h)
    if unknown:issues.append(dict(source=entry['paths'][0],reason='species absent from Aramco thermodynamics',species=sorted(unknown)));continue
    energy=phase[ep];steps=energy['phase_steps'];period=i['period_s'];fin=i['flow_sccm']*1e-6/60*i['standard_P_Pa']/(8.314462618*i['standard_T_K'])
    hin=sum(feed.get(s,0)*h[s] for s in feed)*fin
    correction=energy['inlet_enthalpy_flow_W']-hin
    qrx=(sum(v*h[s] for s,v in m.items())*cin-sum(v*h[s] for s,v in feed.items()))*fin
    prev=i['segments'][0][1];powers=[]
    for s in steps:
        dt=s['dt_s'];mid=(prev+s['T_K'])/2
        storage=28.8e-6*cfp_heat_capacity(mid-273.15)*(s['T_K']-prev)
        rad=.57*5.670374419e-8*.000608*(mid**4-298.15**4)*dt
        q=s['Q_J']+correction*dt;powers.append((q,storage,rad,dt));prev=s['T_K']
    assert abs(sum(z[3] for z in powers)-period)<1e-6
    qgas=sum(z[0] for z in powers)/period;rad=sum(z[2] for z in powers)/period
    assert abs(qgas-(energy['net_heat_J']/period+correction))<1e-5
    temps=[s[j] for s in i['segments'] for j in [1,2]];mode='CJH' if max(temps)-min(temps)<1e-6 else 'RPH'
    family='CH4/CO2' if set(feed)<=set(['CH4','CO2']) else 'Other feed'
    vol=i['volume_m3']*1e6
    base=dict(id=mode+'-'+hashlib.sha256(key.encode()).hexdigest()[:10],mode=mode,family=family,closure='Fixed-volume CSTR; prescribed temperature',source=entry['paths'][0],source_sha256=digest,energy_source=ep,energy_source_sha256=sha(Path(ep)),feed=feed,flow_sccm=i['flow_sccm'],volume_cm3=vol,GHSV_h_inverse=i['flow_sccm']*60/vol,Tmax_C=max(temps)-273.15,Tmin_C=min(temps)-273.15,period_s=period,segments=i['segments'],pressure_Pa=i['pressure_target_Pa'],CO_C2H2=m.get('CO',0)/m['C2H2'] if m.get('C2H2',0)>0 else None,status='conditional prescribed-temperature energy reconstruction',element_residual=err)
    add(base,200*m.get('C2H2',0),qrx,qgas,rad,powers)
# Current CH4/He parcel results: no flow is assigned to the temperature map.
p=R/'docs/research/parcel-temperature-screen-2026-09-10/energy-pareto/data.json'
for r in read(p)['rows']:
    base=dict(id=f"He-{r['T_C']}-{r['time_ms']}",mode='CJH',family='CH4/He',closure='Isothermal parcel',source=str(p),source_sha256=sha(p),feed={'CH4':.1,'HE':.9},flow_sccm=None,volume_cm3=None,GHSV_h_inverse=None,Tmax_C=r['T_C'],reaction_time_ms=r['time_ms'],CO_C2H2=0,period_s=None,status='gas-only parcel energy; no flow assigned')
    cases.append(dict(base,Y_C2H2_pct=r['Y_C2H2_pct']))
    plots.append(dict(base,Y_C2H2_pct=r['Y_C2H2_pct'],eta_rxn_pct=r['eta_rxn_pct'],scenario='Gas only',radiation_remaining=0,input_W=None))
p=R/'docs/research/parcel-flow-screen-2026-09-10/result.json';dd=read(p)
for r in dd['rows']:
    add(dict(id='He-flow-'+str(r['flow_sccm']),mode='CJH',family='CH4/He',closure='Fixed-volume ideal PFR',source=str(p),source_sha256=sha(p),feed=dd['feed'],flow_sccm=r['flow_sccm'],volume_cm3=dd['volume_cm3'],GHSV_h_inverse=r['flow_sccm']*60/dd['volume_cm3'],Tmax_C=1500,reaction_time_ms=r['reaction_time_ms'],pressure_Pa=101325,CO_C2H2=0,period_s=None,status='paired parcel and volume quadrature; fixed radiation scenario'),r['Y_C2H2_pct'],r['rxn_W'],r['gas_W'],r['radiation_W']/.1)
save('case-table.json',cases);save('plot-data.json',plots);save('missing-and-excluded.json',issues);save('deduplication-aliases.json',aliases)
legacy=read(W/'calculation-register/legacy-periodic-index.json')
save('legacy-pending.json',[dict(source=r.get('source'),mechanism=r.get('mechanism'),reason='legacy closure requires separate flow/energy adapter; no assumed volume or power') for r in legacy])
summary=dict(local_files=len(inventory),cached_branch_entries=len(branch_files),raw_unique_flow_results=len(raw),physical_flow_groups=len(group),plotted_cases=len(cases),scenario_points=len(plots),cases_by_mode=dict(collections.Counter(c['mode'] for c in cases)),missing_or_excluded=len(issues),legacy_pending=len(legacy),new_reaction_integrations=0,wall_s=time.monotonic()-start)
save('summary.json',summary)
lines=['# Yield and reaction-heat atlas','', 'Local archive inventory and thermodynamic postprocessing. No reaction integration was performed.','', '![Atlas](atlas.png)','',json.dumps(summary,indent=2),'',
    'The x-axis is carbon in acetylene divided by total inlet carbon. The y-axis is net product-minus-feed reaction enthalpy at 298.15 K divided by positive supplied heat. Color is outlet CO/C2H2 molar ratio. CJH circles and RPH triangles distinguish steady and cyclic temperature histories.',
    '', 'RPH input is reconstructed stepwise from stored gas energy, the archived CFP heat-capacity function, and radiation. The recorded inlet enthalpy is corrected to 298.15 K before positive and negative energy are separated. Gas-only panels omit CFP storage and radiation. Full and reduced-radiation panels retain the same prescribed chemical histories; reduced radiation may require additional cooling, retained in the data.',
    '', 'The overview groups feeds and energy boundaries. It is not a matched-device Pareto comparison. Volume, temperature, flow, and composition vary within the CH4/CO2 panels. Screening points that exceed a power supply limit remain conditional demand estimates, with no device-feasibility claim. Explicitly failed high-flow thermal iterates are excluded. No aggregate Pareto front is claimed across unlike conditions.',
    '', 'Exact physical-input grouping removes coarse/fine duplicates, preferring higher temporal resolution. Byte-identical source copies share an inventory entry. Distinct prescribed waveforms remain distinct conditions. GHSV is standard inlet volumetric flow divided by gas volume; it is absent for unscaled parcels.',
    '', 'Local files and cached branch paths are inventoried separately. JSONL, NPZ, large files, and legacy models without energy adapters remain indexed; they are not represented as energy points. This output does not assert numerical inspection of every cached historical branch blob.',
    '', '## Files','', '- case-table.json: conditions and exact source links.','- plot-data.json: one row per condition and energy scenario.','- missing-and-excluded.json: unsupported or failed flow results.','- legacy-pending.json: earlier closure records awaiting an energy adapter.','- file-inventory.json and cached-branch-inventory.json: search coverage.','- deduplication-aliases.json: duplicate and refinement provenance.','', 'Reproduce with cantera-env Python: tools/openmkm_dynamic/build_energy_atlas.py. Plot with /usr/bin/python3 tools/openmkm_dynamic/draw_energy_atlas.py.']
(O/'REPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))
