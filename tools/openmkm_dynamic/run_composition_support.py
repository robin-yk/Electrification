"""Four-point non-equimolar design support; not a BO recommendation."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/research/composition-support-2026-09-08'
JOBS=[(.7,1600,.8),(.7,1800,.5),(.8,1600,.8),(.8,1800,.5)]
CAP=300
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    global OUT
    ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);ap.add_argument('--samples',type=int,default=400);ap.add_argument('--inert',action='store_true');ap.add_argument('--cloud',action='store_true');a=ap.parse_args()
    if a.cloud:OUT=ROOT/'docs/research/composition-support-cloud-2026-09-08'
    OUT.mkdir(exist_ok=True)
    if a.worker is not None:
        import run_rph_yield_grid as g
        x,t,h=JOBS[a.worker]
        out=OUT/str(a.worker);out.mkdir(exist_ok=True)
        g.pulse.worker(out,'inert' if a.inert else f'n{a.samples}',a.samples,inert=a.inert,waveform=g.waveform(t,h),feed_ch4=x,flow_sccm=50,rtol=1e-11)
        return
    assert not (OUT/'status.json').exists(),'Do not overwrite or automatically retry a completed/stopped batch'
    import hashlib
    paths=[Path(__file__),ROOT/'tools/openmkm_dynamic/run_rph_fixed_pulse.py',ROOT/'tools/openmkm_dynamic/run_rph_fixed_gate.py',ROOT/'tools/openmkm_dynamic/run_rph_yield_grid.py',ROOT/'tools/openmkm_dynamic/run_cjh_feed_ratio_01.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']
    write(OUT/'manifest.json',dict(jobs=JOBS,cap_s=CAP,selection='manual factorial support for missing composition-waveform interactions; not Bayesian',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}))
    start=time.monotonic();done=[];state='running';reason=None
    def run(index,n,inert=False):
        out=OUT/str(index);out.mkdir(exist_ok=True)
        cmd=[sys.executable,__file__,'--worker',str(index),'--samples',str(n)]
        if a.cloud:cmd+=['--cloud']
        if inert:cmd+=['--inert']
        left=CAP-(time.monotonic()-start)
        assert left>0,'Aggregate cap reached'
        with (out/('inert.log' if inert else f'n{n}.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=min(90,left),check=True)
    try:
        run(0,400,True)
        for index,(x,t,h) in enumerate(JOBS):
            run(index,400);run(index,800)
            lo,hi=[json.loads((OUT/str(index)/f'n{n}.json').read_text()) for n in [400,800]]
            lm,hm=lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']
            err=max(abs(lm.get(k,0)-hm.get(k,0)) for k in set(lm)|set(hm))
            assert err<1e-4,f'Phase refinement failed: {err}'
            write(OUT/str(index)/'gates.json',dict(phase_error=err,threshold=1e-4))
            done.append(dict(index=index,CH4_fraction=x,peak_C=t,hold_s=h,C2H2_Y_pct=100*hi['carbon_yields']['C2H2'],CO_Y_pct=100*hi['carbon_yields']['CO'],CO_per_C2H2=hm['CO']/hm['C2H2'],phase_error=err,source=str((OUT/str(index)/'n800.json').relative_to(ROOT))))
            write(OUT/'status.json',dict(status='running',completed=done,wall_s=time.monotonic()-start))
        state='completed'
    except Exception as exc:
        state='stopped';reason=type(exc).__name__+': '+str(exc)
    finally:
        write(OUT/'status.json',dict(status=state,reason=reason,completed=done,wall_s=time.monotonic()-start,cap_s=CAP))
    print((OUT/'status.json').read_text())
    if state!='completed':raise SystemExit(1)
if __name__=='__main__':main()
