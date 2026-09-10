"""Bounded isothermal gas-parcel check against a Porsin abstract target."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import json, time, hashlib, platform, argparse
from pathlib import Path
import numpy as np
import cantera as ct

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--temperature-c',type=int,default=1900)
parser.add_argument('--temperatures-c',type=int,nargs='+')
parser.add_argument('--output',type=Path)
parser.add_argument('--times-s',type=float,nargs='+',default=[.02,.04])
parser.add_argument('--refine-temperatures-c',type=int,nargs='+')
args=parser.parse_args()
if any(t<=0 for t in args.times_s) or sorted(set(args.times_s))!=args.times_s:
    parser.error('Output times must be positive and strictly increasing.')
folder='retry-600s' if args.temperature_c==1900 else f'T{args.temperature_c}-600s'
OUT=args.output or ROOT/'docs/research/porsin-scoping-2026-09-10'/folder
temperatures=args.temperatures_c or [args.temperature_c]
MECH=ROOT/'tools/cantera/mechanisms/aramco20.yaml'
OUT.mkdir(parents=True,exist_ok=True)
def save(name,data):
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
start=time.monotonic()
save('manifest',dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    mechanism_sha256=hashlib.sha256(MECH.read_bytes()).hexdigest(),cantera=ct.__version__,
    python=platform.python_version(),temperatures_C=temperatures,pressure_Pa=101325,
    environment={k:os.environ.get(k) for k in ('TZ','LC_ALL','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
    feed={'CH4':.1,'HE':.9},times_s=args.times_s,
    refine_temperatures_C=args.refine_temperatures_c or temperatures,
    closure='Isothermal constant-pressure closed gas parcel, ideal PFR material-history approximation. Not CSTR.',
    assumptions=['Coil temperature substituted for uniform gas temperature',
      '1 atm assumed pending precise experimental pressure',
      '20 and 40 ms chosen to bracket the abstract contact-time scale',
      'No gas heating, cooling, surface reactions, or condensed carbon'],
    target={'X_CH4_pct':80,'S_C2H2_carbon_pct':80},target_role='approximate abstract benchmark, not a digitized matched experimental point'))
try:
    save('status',dict(status='loading_mechanism'))
    gas=ct.Solution(str(MECH))
    save('timing',dict(mechanism_load_s=time.monotonic()-start))
    print('Mechanism loaded in',time.monotonic()-start,'s',flush=True)
    atoms=np.array([[gas.n_atoms(k,e) for k in range(gas.n_species)] for e in gas.element_names])
    mw=gas.molecular_weights
    ci=gas.element_index('C'); ch4=gas.species_index('CH4'); ac=gas.species_index('C2H2')
    def run(label,T,times,tight=False):
        run_start=time.monotonic()
        gas.TPX=T,101325,{'CH4':.1,'HE':.9}
        r=ct.IdealGasConstPressureMoleReactor(gas,energy='off',volume=1e-6)
        initial_mass=r.mass
        n0=r.mass*r.thermo.Y/mw
        e0=atoms@n0
        active=e0>1e-25
        net=ct.ReactorNet([r])
        net.rtol=1e-11 if tight else 1e-9
        net.atol=1e-24 if tight else 1e-22
        net.max_time_step=1e-4 if tight else 1e-3
        net.preconditioner=ct.AdaptivePreconditioner()
        outputs=[]
        for t in times:
            net.advance(t)
            n=r.mass*r.thermo.Y/mw; e=atoms@n
            error=float(np.max(abs((e[active]-e0[active])/e0[active])))
            mass_error=abs(r.mass/initial_mass-1)
            assert error<1e-7 and mass_error<1e-7,(error,mass_error)
            assert abs(r.T-T)<1e-7 and abs(r.thermo.P/101325-1)<1e-7
            conversion=1-n[ch4]/n0[ch4]
            cy=atoms[ci]*n/e0[ci]
            row=dict(time_s=t,T_C=T-273.15,X_CH4_pct=100*conversion,
                Y_C2H2_carbon_pct=100*cy[ac],
                S_C2H2_carbon_pct=100*cy[ac]/conversion if conversion>1e-10 else None,
                element_error=error,mass_error=mass_error,
                carbon_yields_pct={s:100*float(cy[k]) for k,s in enumerate(gas.species_names) if atoms[ci,k]>0},
                C6_carbon_yield_pct=100*float(sum(cy[k] for k in range(len(cy)) if atoms[ci,k]==6)),
                mole_fractions={s:float(v) for s,v in zip(gas.species_names,r.thermo.X)},
                rtol=net.rtol,atol=net.atol,max_time_step=net.max_time_step)
            assert abs(sum(row['carbon_yields_pct'].values())-100)<1e-5
            outputs.append(row)
        save(label,dict(rows=outputs,solver_stats=net.solver_stats,wall_s=time.monotonic()-run_start))
        print(label,[(x['time_s'],x['X_CH4_pct'],x['S_C2H2_carbon_pct']) for x in outputs],flush=True)
        return outputs
    save('status',dict(status='nonreacting_gate',wall_s=time.monotonic()-start))
    cold=run('cold',300,[.001])
    assert abs(cold[0]['X_CH4_pct'])<1e-6
    summaries=[]
    for temperature in temperatures:
        prefix=f'T{temperature}-' if args.temperatures_c else ''
        save('status',dict(status='reacting_standard',T_C=temperature,wall_s=time.monotonic()-start))
        a=run(prefix+'standard',temperature+273.15,args.times_s)
        if args.refine_temperatures_c and temperature not in args.refine_temperatures_c:
            summaries.extend({k:r[k] for k in ('T_C','time_s','X_CH4_pct','Y_C2H2_carbon_pct','S_C2H2_carbon_pct','C6_carbon_yield_pct')} for r in a)
            continue
        save('status',dict(status='reacting_tight',T_C=temperature,wall_s=time.monotonic()-start))
        b=run(prefix+'tight',temperature+273.15,args.times_s,True)
        delta=max(abs(x[k]-y[k]) for x,y in zip(a,b) for k in ['X_CH4_pct','Y_C2H2_carbon_pct','S_C2H2_carbon_pct','C6_carbon_yield_pct'])
        species_delta=max(abs(x['mole_fractions'][s]-y['mole_fractions'][s]) for x,y in zip(a,b) for s in gas.species_names)
        assert delta<.05 and species_delta<1e-6,(delta,species_delta)
        regression=None
        if temperature==1900:
            reference=ROOT/'docs/research/porsin-scoping-2026-09-10/retry-600s/tight.json'
            ref=json.loads(reference.read_text())['rows']
            matched=[(x,y) for x in ref for y in b if x['time_s']==y['time_s']]
            regression=max(abs(x['mole_fractions'][s]-y['mole_fractions'][s]) for x,y in matched for s in gas.species_names) if matched else None
            assert regression is None or regression<1e-6,regression
        save(prefix+'comparison',dict(max_metric_difference_percentage_points=delta,
            max_species_difference=species_delta,legacy_1900_species_difference=regression,rows=b,
            numerical_gate='passed',experimental_reproduction='not established: assumed uniform temperature and contact-time brackets'))
        summaries.extend({k:r[k] for k in ('T_C','time_s','X_CH4_pct','Y_C2H2_carbon_pct','S_C2H2_carbon_pct','C6_carbon_yield_pct')} for r in b)
    save('brief',dict(rows=summaries,numerical_gate='passed',refinement_scope=args.refine_temperatures_c or temperatures,wall_s=time.monotonic()-start))
    save('status',dict(status='completed',wall_s=time.monotonic()-start))
except Exception as e:
    save('status',dict(status='failed',reason=str(e),wall_s=time.monotonic()-start))
    raise
