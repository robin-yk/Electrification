"""Bounded acetylene-yield grid with full-input reuse and paired gates."""
import argparse
import hashlib
import itertools
from pathlib import Path
import subprocess
import sys
import time
import run_cjh_feed_ratio_01 as base
import run_rph_fixed_pulse as pulse

CAMPAIGN=base.ROOT/'docs/research/rph-yield-grid-2026-09-07'
PEAKS=[1400,1600,1800]
HOLDS=[.1,.3,.5,.65,.8]
FLOWS=[12.5,25,50,100,200]
PILOT=[(1400,.8,12.5),(1600,.8,25),(1800,.8,200),(1800,.3,25)]

def waveform(p,h):return [(.025,723.15,p+273.15),(h,p+273.15,p+273.15),(.1,p+273.15,723.15),(.875-h,723.15,723.15)]
def tag(p,h,q):return f'T{p:g}-h{h:g}-Q{q:g}'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def error(a,b):return max(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b))

def inventory():
    old=base.read(base.ROOT/'docs/research/cjh-rph-matched-39-2026-09-07/report.json')['rows']
    old+=base.read(base.ROOT/'docs/research/rph-xs-extension-01-2026-09-07/report.json')['raw_pairs']
    reused={}
    for r in old:
        f=base.ROOT/r['source'];assert sha(f)==r['sha256']
        d=base.read(f);i=d['inputs'];p,h,q=r['peak_C'],r['hold_s'],r['flow_sccm']
        assert i['feed']=={'CH4':.5,'CO2':.5} and i['volume_m3']==base.volume_reference()
        assert i['standard_T_K']==273.15 and i['standard_P_Pa']==101325 and i['pressure_target_Pa']==101325
        assert i['pressure_controller_K']==pulse.PRESSURE_K and i['period_s']==1 and i['samples_per_segment']==800
        assert i['segments']==[list(s) for s in waveform(p,h)]
        if p in PEAKS and h in HOLDS and q in FLOWS:reused[(p,h,q)]=r['source']
    jobs=[x for x in itertools.product(PEAKS,HOLDS,FLOWS) if x not in reused]
    assert len(reused)+len(jobs)==75 # 3 peaks x 5 holds x 5 flows
    return reused,jobs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',default='pilot');ap.add_argument('--output-dir',type=Path)
    ap.add_argument('--inventory',action='store_true');ap.add_argument('--worker',action='store_true')
    ap.add_argument('--peak',type=float,default=1800);ap.add_argument('--hold',type=float,default=.5)
    ap.add_argument('--flow',type=float,default=50);ap.add_argument('--samples',type=int,default=800)
    ap.add_argument('--inert',action='store_true');a=ap.parse_args()
    if a.worker:
        out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
        name=tag(a.peak,a.hold,a.flow)+('-inert' if a.inert else f'-n{a.samples}')
        pulse.worker(out,name,a.samples,inert=a.inert,waveform=waveform(a.peak,a.hold),flow_sccm=a.flow);return
    reused,jobs=inventory()
    if a.inventory:
        print(dict(total=75,reused=len(reused),new=len(jobs),pilot=PILOT));return
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    ledger=base.read(CAMPAIGN/'budget.json');cap=ledger['reserved_s']
    assert 0<cap<=600 and ledger['spent_s']+cap<=ledger['total_budget_s']
    assert ledger['active_stage']==a.stage
    if a.stage=='pilot':chosen=PILOT
    else:
        assert base.read(CAMPAIGN/'pilot/data/status.json')['status']=='completed'
        rest=[j for j in jobs if j not in PILOT];k=int(a.stage)-1;chosen=rest[k*18:(k+1)*18]
    assert chosen and all(j in jobs for j in chosen)
    paths=[Path(__file__),Path(base.__file__),Path(pulse.__file__),Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        hashes={str(f.relative_to(base.ROOT)):sha(f) for f in paths},jobs=chosen,cap_s=cap,
        reused=[dict(peak=p,hold=h,flow=q,source=s,sha256=sha(base.ROOT/s)) for (p,h,q),s in reused.items()]))
    start=time.monotonic();done=[];active=None
    def run(p,h,q,n=800,inert=False):
        nonlocal active
        active=tag(p,h,q)+('-inert' if inert else f'-n{n}')
        left=cap-(time.monotonic()-start);assert left>0,'batch cap reached'
        cmd=[sys.executable,__file__,'--worker','--output-dir',str(out),'--peak',str(p),'--hold',str(h),'--flow',str(q),'--samples',str(n)]
        if inert:cmd+=['--inert']
        with (out/(active+'.log')).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,left))
        done.append(active);return base.read(out/(active+'.json'))
    try:
        if a.stage=='pilot':
            run(1800,.8,12.5,inert=True);run(1800,.8,200,inert=True)
            anchor=run(1800,.5,50)
            prior=base.read(base.ROOT/'docs/research/rph-450-pilot-01-2026-09-07/data/T1800-hold0.5-n800.json')
            e=error(anchor['mol_per_feed_carbon'],prior['mol_per_feed_carbon'])
            assert anchor['inputs']==prior['inputs'] and e<1e-8
            base.write(out/'anchor-gates.json',dict(error=e,threshold=1e-8))
        for p,h,q in chosen:
            lo=run(p,h,q,400);hi=run(p,h,q,800)
            e=error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']);assert e<1e-4,f'phase refinement failed: {e}'
            base.write(out/(tag(p,h,q)+'-gates.json'),dict(error=e,threshold=1e-4))
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-start))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',active=active,completed=done,reason=str(e),wall_s=time.monotonic()-start));raise

if __name__=='__main__':main()
