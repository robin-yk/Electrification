"""Direct paired-grid energy validation of saved multiobjective proposals."""
from cantera_runtime import prepare_runtime
RUNTIME=prepare_runtime()
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
from pareto_energy_pilot import physical_gate
from replay_bo_energy import summarize
ROOT=Path(__file__).resolve().parents[2];C=ROOT/'docs/research/composition-bo-2026-09-08';D=C/'pareto-bo-01';OUT=D/'verification'
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);ap.add_argument('--n',type=int,default=400);a=ap.parse_args()
    qs=read(D/'proposals.json')['proposals'];OUT.mkdir(exist_ok=True)
    if a.worker is not None:
        from run_rph_fixed_pulse import worker
        from run_rph_yield_grid import waveform
        q=qs[a.worker];t,h,x=q['x'];folder=OUT/str(a.worker);folder.mkdir(exist_ok=True)
        worker(folder,f'n{a.n}',a.n,waveform=waveform(t,h),flow_sccm=50,feed_ch4=x,rtol=1e-11,capture_energy=True);return
    assert read(D/'status.json')['status']=='completed' and not (OUT/'status.json').exists()
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    files=[Path(__file__),D/'proposals.json',ROOT/'tools/openmkm_dynamic/run_rph_fixed_pulse.py',ROOT/'tools/openmkm_dynamic/replay_bo_energy.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']
    save(OUT/'manifest.json',dict(runtime=RUNTIME,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
    ledger['active']='pareto-verify-01';save(C/'budget.json',ledger);start=time.monotonic();done=[];reason=None;state='stopped'
    try:
        for j,q in enumerate(qs):
            folder=OUT/str(j);folder.mkdir(exist_ok=True)
            for n in [400,800]:
                left=300-(time.monotonic()-start);assert left>0
                with (folder/f'n{n}.log').open('w') as f:subprocess.run([sys.executable,__file__,'--worker',str(j),'--n',str(n)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(120,left))
            lo,hi=[read(folder/f'n{n}.json') for n in [400,800]];assert physical_gate(lo) and physical_gate(hi)
            l,m=lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon'];error=max(abs(l.get(k,0)-m.get(k,0)) for k in set(l)|set(m));assert error<1e-4
            sl,sh=[summarize(folder,n) for n in [400,800]]
            for f in sh['scenarios']:
                for k in ['input_W','cooling_W']:assert abs(sl['scenarios'][f][k]-sh['scenarios'][f][k])/max(abs(sh['scenarios'][f][k]),1)<.005
            e=read(folder/'n800-energy.json');assert abs(e['energy_balance_residual_J'])<1e-6
            row=dict(index=j,proposal=q,phase_error=error,feasible=abs(sh['ratio']/q['target']-1)<=.02,**sh)
            save(folder/'summary.json',row);done.append(row);save(OUT/'status.json',dict(status='running',completed=done,wall_s=time.monotonic()-start))
        state='completed'
    except Exception as e:reason=f'{type(e).__name__}: {e}'
    finally:
        elapsed=time.monotonic()-start;save(OUT/'status.json',dict(status=state,reason=reason,completed=done,wall_s=elapsed));ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage='pareto-verify-01',status=state,wall_s=elapsed));save(C/'budget.json',ledger)
    print(json.dumps(dict(status=state,reason=reason,n=len(done),wall_s=elapsed)))
    if reason:raise SystemExit(1)
if __name__=='__main__':main()
