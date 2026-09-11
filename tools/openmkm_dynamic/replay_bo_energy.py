"""Bounded energy logging for the three feasible yield incumbents."""
from cantera_runtime import prepare_runtime
RUNTIME=prepare_runtime()
import argparse,json,hashlib,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=ROOT/'docs/research/composition-bo-2026-09-08'
OUT=C/'energy-incumbents-01'
JOBS=[(3,0),(5,1),(5,2)]
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def summarize(folder,n):
    from element_drive import cfp_heat_capacity
    d=read(folder/f'n{n}.json');e=read(folder/f'n{n}-energy.json');i=d['inputs'];period=i['period_s']
    prev=i['segments'][0][1];totals={str(f):[0.,0.,0.] for f in [1,.1]}
    for s in e['phase_steps']:
        mid=(prev+s['T_K'])/2
        store=28.8e-6*cfp_heat_capacity(mid-273.15)*(s['T_K']-prev)
        rad=.57*5.670374419e-8*.000608*(mid**4-298.15**4)*s['dt_s']
        for f in [1,.1]:
            q=s['Q_J']+store+f*rad
            totals[str(f)][0]+=max(q,0);totals[str(f)][1]+=max(-q,0);totals[str(f)][2]+=f*rad
        prev=s['T_K']
    rate=d['mol_per_feed_carbon']['C2H2']*i['flow_sccm']/22414/60*1000
    return dict(Y_C2H2_pct=200*d['mol_per_feed_carbon']['C2H2'],ratio=d['mol_per_feed_carbon']['CO']/d['mol_per_feed_carbon']['C2H2'],
        Q_rxn_W=e['Q_rxn_W'],gas_net_W=e['net_heat_J']/period,delta_U_J=e['delta_U_J'],
        scenarios={f:dict(input_W=a/period,cooling_W=b/period,radiation_W=c/period,C2H2_mmol_kJ=rate*1000/(a/period),eta_rxn_pct=100*e['Q_rxn_W']/(a/period)) for f,(a,b,c) in totals.items()})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);ap.add_argument('--n',type=int,default=400);a=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.worker is not None:
        import run_rph_fixed_pulse as p
        folder=OUT/str(a.worker);folder.mkdir(exist_ok=True)
        if a.worker==-1:p.worker(folder,f'n{a.n}',a.n,inert=True,rtol=1e-11,capture_energy=True)
        else:
            rnd,j=JOBS[a.worker];old=read(C/f'round-{rnd:02d}/verification/{j}/n800.json');i=old['inputs']
            p.worker(folder,f'n{a.n}',a.n,period=i['period_s'],waveform=i['segments'],flow_sccm=i['flow_sccm'],feed_ch4=i['feed']['CH4'],rtol=old['solver_rtol'],capture_energy=True)
        return
    assert not (OUT/'status.json').exists(),'No automatic rerun'
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    files=[Path(__file__),ROOT/'tools/openmkm_dynamic/run_rph_fixed_pulse.py',ROOT/'tools/openmkm_dynamic/element_drive.py',ROOT/'tools/openmkm_dynamic/cantera_runtime.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']
    save(OUT/'manifest.json',dict(runtime=RUNTIME,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},cap_s=300))
    start=time.monotonic();done=[];state='stopped';reason=None
    ledger['active']='energy-incumbents-01';save(C/'budget.json',ledger)
    try:
        for j in [-1,0,1,2]:
            folder=OUT/str(j);folder.mkdir(exist_ok=True)
            for n in [400,800]:
                left=300-(time.monotonic()-start);assert left>0
                with (folder/f'n{n}.log').open('w') as f:subprocess.run([sys.executable,__file__,'--worker',str(j),'--n',str(n)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(90,left))
            lo,hi=[read(folder/f'n{n}.json') for n in [400,800]]
            el,eh=[read(folder/f'n{n}-energy.json') for n in [400,800]]
            assert abs(el['net_heat_J']-eh['net_heat_J'])/max(abs(eh['net_heat_J']),1e-8)<.005
            if j==-1:
                assert abs(eh['Q_rxn_W'])<1e-5
                save(folder/'gates.json',dict(inert_reaction_heat_W=eh['Q_rxn_W'],balance_J=eh['energy_balance_residual_J']))
                continue
            rnd,index=JOBS[j];oldpath=C/f'round-{rnd:02d}/verification/{index}/n800.json';old=read(oldpath)
            m=hi['mol_per_feed_carbon'];om=old['mol_per_feed_carbon'];lm=lo['mol_per_feed_carbon']
            err=max(abs(m.get(k,0)-om.get(k,0)) for k in set(m)|set(om));assert err<1e-8
            assert max(abs(m.get(k,0)-lm.get(k,0)) for k in set(m)|set(lm))<1e-4
            sl,sh=[summarize(folder,n) for n in [400,800]]
            for f in sh['scenarios']:
                for k in ['input_W','cooling_W']:
                    assert abs(sl['scenarios'][f][k]-sh['scenarios'][f][k])/max(abs(sh['scenarios'][f][k]),1)<.005
            row=dict(round=rnd,index=index,source=str(oldpath),source_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest(),replay_species_error=err,**sh)
            save(folder/'summary.json',row);done.append(row)
            save(OUT/'status.json',dict(status='running',completed=done,wall_s=time.monotonic()-start))
        state='completed'
    except Exception as e:reason=f'{type(e).__name__}: {e}'
    finally:
        elapsed=time.monotonic()-start
        save(OUT/'status.json',dict(status=state,reason=reason,completed=done,wall_s=elapsed))
        ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage='energy-incumbents-01',status=state,wall_s=elapsed));save(C/'budget.json',ledger)
    print(json.dumps(dict(status=state,reason=reason,completed=done,wall_s=elapsed)))
if __name__=='__main__':main()
