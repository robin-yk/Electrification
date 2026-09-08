"""Paired CJH feed-temperature support under the shared BO campaign budget."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
C=ROOT/'docs/research/composition-bo-2026-09-08'
OUT=C/'cjh-support'
JOBS=[(1600,.7),(1900,.7),(1600,.8),(1900,.8)]
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);ap.add_argument('--tight',type=int,default=2);a=ap.parse_args();OUT.mkdir(exist_ok=True)
    if a.worker is not None:
        import run_cjh_feed_ratio_01 as b
        t,x=JOBS[a.worker];d=OUT/str(a.worker);d.mkdir(exist_ok=True)
        b.worker(d,f'a{a.tight}',x,tight=a.tight,temperature_K=t+273.15);return
    assert not (OUT/'status.json').exists()
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    ledger['active']='cjh-support';write(C/'budget.json',ledger)
    start=time.monotonic();done=[];state='stopped';reason=None
    paths=[Path(__file__),ROOT/'tools/openmkm_dynamic/run_cjh_feed_ratio_01.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']
    write(OUT/'manifest.json',dict(jobs=JOBS,cap_s=300,selection='manual initial design, not BO',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}))
    try:
        for i,(t,x) in enumerate(JOBS):
            d=OUT/str(i);d.mkdir(exist_ok=True)
            for k in [2,3]:
                left=300-(time.monotonic()-start);assert left>0
                with (d/f'a{k}.log').open('w') as f:subprocess.run([sys.executable,__file__,'--worker',str(i),'--tight',str(k)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(90,left))
            lo,hi=[read(d/f'a{k}.json') for k in [2,3]]
            a,b=lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon'];e=max(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b));assert e<1e-5
            write(d/'gates.json',dict(integrator_refinement_error=e,threshold=1e-5))
            done.append(dict(T_C=t,CH4_fraction=x,y=[100*hi['carbon_yields'][k] for k in ['C2H2','CO']],ratio=b['CO']/b['C2H2'],source=str((d/'a3.json').relative_to(ROOT))))
        state='completed'
    except Exception as e:reason=type(e).__name__+': '+str(e)
    finally:
        elapsed=time.monotonic()-start;write(OUT/'status.json',dict(status=state,reason=reason,completed=done,wall_s=elapsed));ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage='cjh-support',status=state,wall_s=elapsed));write(C/'budget.json',ledger)
    print((OUT/'status.json').read_text())
    if state!='completed':raise SystemExit(1)
if __name__=='__main__':main()
