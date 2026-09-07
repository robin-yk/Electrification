"""Six approved flow conditions, preceded by inert and archived-anchor checks."""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as base
import run_rph_fixed_pulse as pulse
from run_rph_screen_450 import waveform

def tag(flow,hold,n):return f'Q{flow:g}-hold{hold:g}-n{n}'

def plan(extend):
    return ('rph-flow-02',240,[800,1600],400) if extend else ('rph-flow-01',300,[100,200,400],50)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--extend',action='store_true')
    ap.add_argument('--worker',action='store_true');ap.add_argument('--inert',action='store_true')
    ap.add_argument('--flow',type=float,default=50);ap.add_argument('--hold',type=float,default=.1)
    ap.add_argument('--samples',type=int,default=800);a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.worker:
        pulse.worker(out,'inert' if a.inert else tag(a.flow,a.hold,a.samples),a.samples,
            inert=a.inert,waveform=waveform(1800,a.hold),flow_sccm=a.flow)
        return
    batch,cap,flows,anchor_flow=plan(a.extend)
    ledger=base.read(base.ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
    assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s']
    assert ledger['reserved_s']==cap
    assert any(b['id']==batch and b['reserved_s']==cap for b in ledger['batches'])
    ref=base.ROOT/('docs/research/rph-flow-01-2026-09-07/data/Q400-hold0.1-n800.json' if a.extend else 'docs/research/rph-450-screen-01-2026-09-07/data/T1800-hold0.1-n800.json')
    prior=base.read(ref)
    prior_manifest=base.read(ref.parent/'manifest.json')
    assert hashlib.sha256(base.MECH.read_bytes()).hexdigest()==prior_manifest['hashes'][str(base.MECH.relative_to(base.ROOT))]
    paths=[Path(__file__),Path(pulse.__file__),Path(base.__file__),Path(__file__).with_name('run_rph_screen_450.py'),Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH,ref]
    jobs=[(q,h) for q in flows for h in [.1,.5]]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base.ROOT,text=True).strip(),
        hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},jobs=jobs,cap_s=cap))
    started=time.monotonic();done=[];active=None
    def run(q,h,n,inert=False):
        nonlocal active
        active='inert' if inert else tag(q,h,n)
        remaining=cap-(time.monotonic()-started);assert remaining>0,'batch cap reached'
        cmd=[sys.executable,__file__,'--output-dir',str(out),'--worker','--flow',str(q),'--hold',str(h),'--samples',str(n)]
        if inert:cmd+=['--inert']
        with (out/(active+'.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,remaining))
        done.append(active)
        return base.read(out/(active+'.json'))
    def error(x,y):
        a,b=x['mol_per_feed_carbon'],y['mol_per_feed_carbon']
        return max(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b))
    try:
        run(max(flows),.1,800,True)
        anchor=run(anchor_flow,.1,800)
        e=error(anchor,prior);assert e<1e-8,f'archive reproduction failed: {e}'
        assert anchor['inputs']==prior['inputs'],'anchor input mismatch'
        base.write(out/'anchor-gates.json',dict(max_species_error=e,threshold=1e-8))
        for q,h in jobs:
            low=run(q,h,400);high=run(q,h,800)
            e=error(low,high);assert e<1e-4,f'phase refinement failed: {e}'
            base.write(out/f'Q{q}-hold{h:g}-gates.json',dict(max_species_refinement_error=e,threshold=1e-4))
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-started))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',active=active,completed=done,reason=str(e),wall_s=time.monotonic()-started));raise

if __name__=='__main__':main()
