"""Verify saved Bayesian recommendations without changing candidate inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
C=ROOT/'docs/research/composition-bo-2026-09-08'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,required=True);ap.add_argument('--worker',type=int);ap.add_argument('--samples',type=int,default=400);a=ap.parse_args()
    d=C/f'round-{a.round:02d}';proposals=read(d/'proposals.json')['proposals'];out=d/'verification';out.mkdir(exist_ok=True)
    if a.worker is not None:
        import run_rph_yield_grid as g
        p,h,x=proposals[a.worker]['x'];folder=out/str(a.worker);folder.mkdir(exist_ok=True)
        g.pulse.worker(folder,f'n{a.samples}',a.samples,waveform=g.waveform(p,h),flow_sccm=50,feed_ch4=x,rtol=1e-11);return
    assert read(d/'status.json')['status']=='completed'
    assert not (out/'status.json').exists(),'No automatic rerun'
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    ledger['active']=f'verify-{a.round}';write(C/'budget.json',ledger)
    start=time.monotonic();done=[];state='stopped';reason=None
    files=[Path(__file__),d/'proposals.json',ROOT/'tools/openmkm_dynamic/run_rph_fixed_pulse.py',ROOT/'tools/openmkm_dynamic/run_rph_fixed_gate.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']
    write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},cap_s=300))
    try:
        for i,q in enumerate(proposals):
            folder=out/str(i);folder.mkdir(exist_ok=True)
            for n in [400,800]:
                left=300-(time.monotonic()-start);assert left>0
                with (folder/f'n{n}.log').open('w') as f:
                    subprocess.run([sys.executable,__file__,'--round',str(a.round),'--worker',str(i),'--samples',str(n)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(90,left))
            lo,hi=[read(folder/f'n{n}.json') for n in [400,800]]
            lm,hm=lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']
            error=max(abs(lm.get(k,0)-hm.get(k,0)) for k in set(lm)|set(hm));assert error<1e-4,f'phase error {error}'
            write(folder/'gates.json',dict(phase_error=error,threshold=1e-4))
            actual=[100*hi['carbon_yields'][k] for k in ['C2H2','CO']];ratio=hm['CO']/hm['C2H2']
            done.append(dict(target=q['target'],x=q['x'],actual_y=actual,ratio=ratio,feasible=abs(ratio/q['target']-1)<=.02,relative_ratio_error=ratio/q['target']-1,predicted_y=q['predicted_y'],incumbent=q['incumbent'],phase_error=error,source=str((folder/'n800.json').relative_to(ROOT)),sha256=hashlib.sha256((folder/'n800.json').read_bytes()).hexdigest()))
            write(out/'status.json',dict(status='running',completed=done,wall_s=time.monotonic()-start))
        state='completed'
    except Exception as e:reason=type(e).__name__+': '+str(e)
    finally:
        elapsed=time.monotonic()-start;write(out/'status.json',dict(status=state,reason=reason,completed=done,wall_s=elapsed))
        ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage=f'verify-{a.round}',status=state,wall_s=elapsed));write(C/'budget.json',ledger)
    print((out/'status.json').read_text())
    if state!='completed':raise SystemExit(1)
if __name__=='__main__':main()
