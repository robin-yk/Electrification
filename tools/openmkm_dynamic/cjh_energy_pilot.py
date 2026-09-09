"""Bounded fixed-volume CJH verification, compatible with Cantera 3.1."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import json, time, hashlib, platform
from pathlib import Path
import cantera as ct
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/research/cjh-energy-pareto-2026-09-09'
OUT.mkdir(parents=True,exist_ok=True)
MECH=ROOT/'tools/cantera/mechanisms/aramco20.yaml'
def save(name,value):
    (OUT/(name+'.json')).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def run(name,cold=False,tight=False):
    start=time.monotonic(); T=300 if cold else 2023.15
    gas=ct.Solution('gri30.yaml' if cold else str(MECH))
    gas.TPX=T,101325,{'CH4':.5,'CO2':.5}
    mw=gas.molecular_weights; y0=gas.Y.copy()
    atoms=np.array([[gas.n_atoms(k,e) for k in range(gas.n_species)] for e in ('C','H','O')])
    mdot=50/22414/60*gas.mean_molecular_weight/1000
    gas.TP=298.15,101325; hin=gas.enthalpy_mass;gas.TP=T,101325
    inlet=ct.Reservoir(gas); outlet=ct.Reservoir(gas)
    r=ct.IdealGasMoleReactor(gas,energy='off',volume=9.228077898393764e-9)
    mfc=ct.MassFlowController(inlet,r,mdot=mdot)
    pc=ct.PressureController(r,outlet,primary=mfc,K=1e-8)
    net=ct.ReactorNet([r]);net.rtol=1e-11 if tight else 1e-9
    net.atol=(1e-17 if tight else 1e-15)*r.volume
    net.preconditioner=ct.AdaptivePreconditioner()
    net.derivative_settings={'skip-third-bodies':True,'skip-falloff':True}
    previous=None;stable=0
    for block in range(1,101):
        net.advance(.005*block)
        y=r.thermo.Y.copy();state=np.r_[y,r.mass]
        err=1 if previous is None else max(float(np.max(abs(y-previous[:-1]))),abs(r.mass/previous[-1]-1))
        previous=state;stable=stable+1 if err<1e-8 else 0
        if block>=20 and stable>=5:break
    fin=mdot*(atoms@(y0/mw));fout=pc.mass_flow_rate*(atoms@(y/mw))
    residual=float(np.max(abs((fout-fin)/fin)))
    assert stable>=5 and residual<1e-5
    assert abs(r.thermo.P/101325-1)<1e-4 and abs(pc.mass_flow_rate/mdot-1)<1e-6
    if cold:assert max(abs(y-y0))<1e-8
    m=(pc.mass_flow_rate*y/mw)/fin[0]
    ac=float(m[gas.species_index('C2H2')])*50/22414*60*1000
    rad=.57*5.670374419e-8*.000608*(T**4-298.15**4)
    qgas=pc.mass_flow_rate*r.thermo.enthalpy_mass-mdot*hin
    data=dict(name=name,T_K=T,flow_sccm=50,feed_CH4=.5,volume_m3=r.volume,
              pressure_Pa=r.thermo.P,standard_T_K=273.15,standard_P_Pa=101325,
              C2H2_mmol_h=ac,radiation_W=rad,cold_gas_duty_W=qgas,input_W=rad+qgas,
              efficiency_mmol_kJ=ac/(3.6*(rad+qgas)),element_residual=residual,
              stable_blocks=stable,rtol=net.rtol,atol=net.atol,wall_s=time.monotonic()-start,
              mol_per_feed_carbon=dict(zip(gas.species_names,map(float,m))))
    save(name,data);print(name,round(data['wall_s'],2),flush=True);return data
if __name__=='__main__':
    start=time.monotonic()
    save('manifest',dict(python=platform.python_version(),cantera=ct.__version__,numpy=np.__version__,
         script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         mechanism_sha256=hashlib.sha256(MECH.read_bytes()).hexdigest(),
         role='verification pilot; no broad campaign',cases=['cold','standard','tight']))
    try:
        run('cold',cold=True);a=run('standard');b=run('tight',tight=True)
        delta=max(abs(a['mol_per_feed_carbon'][k]-b['mol_per_feed_carbon'][k]) for k in a['mol_per_feed_carbon'])
        assert delta<1e-5
        save('status',dict(status='passed',paired_species_error=delta,wall_s=time.monotonic()-start))
    except Exception as e:
        save('status',dict(status='failed',reason=str(e),wall_s=time.monotonic()-start));raise
