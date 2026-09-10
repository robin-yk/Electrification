"""Fixed-volume ideal-PFR flow screen with a gas-parcel material trajectory."""
import os,sys,json,time
from pathlib import Path
from cantera_quickstart import ROOT,MECH,digest,supervise
OUT=ROOT/'docs/research/parcel-flow-screen-2026-09-10'
def save(name,obj):
    (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
if '--worker' not in sys.argv:
    OUT.mkdir(exist_ok=True)
    if (OUT/'result.json').exists():
        raise SystemExit('Saved result exists; inspect before running again.')
    env=dict(os.environ,TZ='UTC0',LC_ALL='C',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    save('launch',dict(script_sha256=digest(Path(__file__)),mechanism_sha256=digest(MECH),timeout_s=300,environment={k:env[k] for k in ['TZ','LC_ALL','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']}))
    with (OUT/'execution.log').open('w') as log:
        status=supervise([sys.executable,'-u',__file__,'--worker'],env,log,300)
    save('supervisor',status)
    print(json.dumps(status))
    if status['exit_code']: raise SystemExit(status['exit_code'])
    result=json.loads((OUT/'result.json').read_text())
    print(json.dumps({k:result[k] for k in ['volume_cm3','rows','peak_flow_sccm','checks']}))
    raise SystemExit()
import numpy as np
import cantera as ct
start=time.monotonic()
gas=ct.Solution(str(MECH))
T=1773.15; P=101325.
gas.TPX=298.15,P,{'CH4':.1,'HE':.9}
mass_g=10*gas.mean_molecular_weight
nin=10*gas.X.copy(); href=gas.partial_molar_enthalpies/1000
Hin=float(nin@href)
atoms=np.array([[gas.n_atoms(s,e) for s in gas.species_names] for e in gas.element_names])
c=atoms[gas.element_index('C')]; ich4=gas.species_index('CH4'); iac=gas.species_index('C2H2')
def trajectory(tight=False,cold=False):
    temp=300 if cold else T
    gas.TPX=temp,P,{'CH4':.1,'HE':.9}
    reactor=ct.IdealGasConstPressureMoleReactor(gas,energy='off',volume=1e-6)
    net=ct.ReactorNet([reactor]); net.preconditioner=ct.AdaptivePreconditioner()
    net.rtol=1e-11 if tight else 1e-9;net.atol=1e-24 if tight else 1e-22
    net.max_time_step=1e-4 if tight else 1e-3
    times=np.r_[0,np.geomspace(1e-7,.04,1600 if tight else 800)] if not cold else np.array([0,.001])
    composition=[]; errors=[]
    for t in times:
        if t: net.advance(t)
        assert abs(reactor.T-temp)<1e-6 and abs(reactor.thermo.P/P-1)<1e-7
        n=reactor.thermo.X*(mass_g/reactor.thermo.mean_molecular_weight)
        errors.append(float(np.max(abs(atoms@(n-nin)))))
        composition.append(n.copy())
    assert max(errors)<1e-6
    return times,np.array(composition),max(errors)
tc,nc,ec=trajectory(cold=True)
assert abs(nc[-1,ich4]-1)<1e-8
t,n,e=trajectory()
tt,nn,ee=trajectory(tight=True)
def exposure(times,moles):
    expansion=moles.sum(axis=1)/10
    return np.r_[0,np.cumsum(np.diff(times)*(expansion[:-1]+expansion[1:])/2)]
u=exposure(t,n); uu=exposure(tt,nn)
# Fixed volume selected by 50 standard cm3/min and 40 ms parcel duration.
fin50=50/22414/60
volume=fin50*(ct.gas_constant/1000)*T/P*uu[-1]
assert abs(volume/(fin50*(ct.gas_constant/1000)*T/P)-uu[-1])<1e-12
# Nonreacting limit recovers V = volumetric flow * elapsed time.
assert np.allclose(exposure(tc,np.tile(nin,(len(tc),1))),tc)
rad=.57*5.670374419e-8*.000608*(T**4-298.15**4)*.1
def row(flow,times,moles,ex):
    target=uu[-1]*50/flow
    tau=float(np.interp(target,ex,times))
    ns=np.array([np.interp(tau,times,moles[:,i]) for i in range(gas.n_species)])
    assert max(abs(atoms@(ns-nin)))<1e-6
    gas.TPX=T,P,ns
    qgas=float(ns@(gas.partial_molar_enthalpies/1000)-Hin)
    qrx=float(ns@href-Hin)
    fch4=flow/22414/60*.1
    power=qgas*fch4+rad
    return dict(flow_sccm=flow,reaction_time_ms=tau*1000,X_CH4_pct=100*(1-ns[ich4]),
        Y_C2H2_pct=200*ns[iac],C6_carbon_yield_pct=float(100*np.sum(c[c==6]*ns[c==6])),
        gas_W=qgas*fch4,rxn_W=qrx*fch4,radiation_W=rad,input_W=power,
        eta_rxn_pct=100*qrx*fch4/power,C2H2_mmol_h=ns[iac]*fch4*3.6e6,
        C2H2_mmol_kJ=ns[iac]*fch4*1e6/power,
        C2H2_mmol_g_CFP_h=ns[iac]*fch4*3.6e6/.0288,
        outlet_mol_per_mol_CH4=dict(zip(gas.species_names,map(float,ns))))
rows=[]; full=[];delta=0
for flow in [50*2**i for i in range(9)]:
    a=row(flow,t,n,u);b=row(flow,tt,nn,uu)
    delta=max(delta,max(abs(a[k]-b[k]) for k in ['X_CH4_pct','Y_C2H2_pct','eta_rxn_pct']))
    assert delta<.1,delta
    full.append(b)
    rows.append({k:v for k,v in b.items() if k!='outlet_mol_per_mol_CH4'})
    if len(rows)>=3 and rows[-1]['C2H2_mmol_kJ']<rows[-2]['C2H2_mmol_kJ']<rows[-3]['C2H2_mmol_kJ']:
        break
reference=json.loads((ROOT/'docs/research/parcel-temperature-screen-2026-09-10/results/T1500-standard.json').read_text())['rows'][-1]
assert abs(rows[0]['Y_C2H2_pct']-reference['Y_C2H2_carbon_pct'])<.05
save('species',full)
save('trajectory',dict(times_s=tt.tolist(),expansion=(nn.sum(axis=1)/10).tolist(),integrated_expansion_s=uu.tolist()))
checks=dict(max_atom_error=max(e,ee,ec),max_refinement_difference_pp=delta,nonreacting_volume_gate='passed',prior_1500_yield_gate='passed')
save('result',dict(volume_cm3=volume*1e6,rows=rows,peak_flow_sccm=max(rows,key=lambda r:r['C2H2_mmol_kJ'])['flow_sccm'],checks=checks,wall_s=time.monotonic()-start,cantera=ct.__version__,T_K=T,pressure_Pa=P,standard_T_K=273.15,standard_P_Pa=P,feed={'CH4':.1,'HE':.9},CFP_mass_g=.0288,emissivity=.57,radiating_area_m2=.000608,radiation_remaining=.1,source_reference_sha256=digest(ROOT/'docs/research/parcel-temperature-screen-2026-09-10/results/T1500-standard.json')))
lines=['# Fixed-volume CH4/He flow screen','',
    'Ideal isothermal PFR represented by a constant-pressure gas-parcel trajectory. Gas and assumed CFP temperatures are 1500 C; feed is 10 mol% CH4 and 90 mol% He at 1 atm. Inlet energy reference is 298.15 K. Standard flow uses 273.15 K and 1 atm.',
    '',f'Fixed gas volume: {volume*1e6:.6f} cm3, derived from 50 sccm and 40 ms with reaction-driven molar expansion integrated along the parcel history. The volume is a modeling choice, not a measured hot region. It differs from the earlier fixed-volume CSTR.',
    '', 'Constant radiating area 0.000608 m2, emissivity 0.57, surroundings 298.15 K, and radiation remaining fraction 0.1 are retained for all flows. Heat-transfer capacity and flow-dependent gas/heater temperature differences are not solved. The comparison assumes the gas can remain isothermal at every flow. No recuperation or other heat losses are included.',
    '', 'Two trajectories with 800 and 1600 logarithmic time intervals locate exit states by cumulative molar expansion. Both solver tolerances and quadrature spacing are refined. Species are interpolated on the refined trajectory. Full selected compositions are saved in species.json. No CSTR residence-time substitution is used.',
    '', 'Stop after two consecutive declines in acetylene mmol/kJ, with an upper cap of 12800 sccm. A sampled peak is a bracket for further work, not a continuous optimum.',
    '', '| Flow (sccm) | Time (ms) | C2H2 yield (%) | C2H2 (mmol/h) | Input (W) | Reaction heat (%) | C2H2 (mmol/kJ) |',
    '|---|---|---|---|---|---|---|']
for r in rows:
    lines.append('| '+' | '.join(f'{r[k]:.4g}' for k in ['flow_sccm','reaction_time_ms','Y_C2H2_pct','C2H2_mmol_h','input_W','eta_rxn_pct','C2H2_mmol_kJ'])+' |')
lines+=['', 'Reproduce: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/parcel_flow_screen.py`. Completed results block accidental reruns.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
