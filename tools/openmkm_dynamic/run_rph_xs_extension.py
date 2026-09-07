"""Four approved higher-conversion RPH conditions and matched CJH roots."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import time
import run_cjh_feed_ratio_01 as base
import run_rph_fixed_pulse as pulse
import match_cjh_rph_39 as match

JOBS=[(50,.65),(50,.8),(25,.5),(12.5,.5)]
CAP=400

def waveform(hold):
    assert 0<hold<.875
    return [(.025,723.15,2073.15),(hold,2073.15,2073.15),(.1,2073.15,723.15),(.875-hold,723.15,723.15)]

def tag(q,h):return f'Q{q:g}-T1800-h{h:g}'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--worker',choices=['pulse','match']);ap.add_argument('--flow',type=float,default=50)
    ap.add_argument('--hold',type=float,default=.5);ap.add_argument('--samples',type=int,default=800)
    ap.add_argument('--inert',action='store_true');a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    name=tag(a.flow,a.hold)
    if a.worker=='pulse':
        pulse.worker(out,name+('-inert' if a.inert else f'-n{a.samples}'),a.samples,
            inert=a.inert,waveform=waveform(a.hold),flow_sccm=a.flow)
        return
    if a.worker=='match':
        f=out/(name+'-n800.json');d=base.read(f)
        row=dict(id=name,source=str(f.relative_to(base.ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            flow_sccm=a.flow,peak_C=1800,hold_s=a.hold,target_X=1-d['mol_per_feed_carbon']['CH4']/.5)
        assert 0<row['target_X']<1
        match.solve(out,row);return
    ledger=base.read(base.ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
    assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s'] and ledger['reserved_s']==CAP
    assert any(b['id']=='rph-xs-extension-01' and b['reserved_s']==CAP for b in ledger['batches'])
    paths=[Path(__file__),Path(base.__file__),Path(pulse.__file__),Path(match.__file__),
        Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        solver_hashes=match.solver_hash(),hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        jobs=JOBS,cap_s=CAP))
    start=time.monotonic();done=[];active=None
    def run(q,h,mode='pulse',n=800,inert=False):
        nonlocal active
        active=tag(q,h)+('-inert' if inert else '-match' if mode=='match' else f'-n{n}')
        left=CAP-(time.monotonic()-start);assert left>0,'batch cap reached'
        cmd=[sys.executable,__file__,'--output-dir',str(out),'--worker',mode,'--flow',str(q),'--hold',str(h),'--samples',str(n)]
        if inert:cmd+=['--inert']
        with (out/(active+'.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(150,left))
        done.append(active)
    def error(x,y):return max(abs(x.get(k,0)-y.get(k,0)) for k in set(x)|set(y))
    try:
        # Recheck both new boundary conditions before reacting integrations.
        run(50,.8,inert=True);run(12.5,.5,inert=True)
        run(50,.5)
        anchor=base.read(out/(tag(50,.5)+'-n800.json'))
        prior=base.read(base.ROOT/'docs/research/rph-450-pilot-01-2026-09-07/data/T1800-hold0.5-n800.json')
        assert anchor['inputs']==prior['inputs']
        e=error(anchor['mol_per_feed_carbon'],prior['mol_per_feed_carbon']);assert e<1e-8
        base.write(out/'anchor-gates.json',dict(max_species_error=e,threshold=1e-8))
        for q,h in JOBS:
            for n in [400,800]:run(q,h,n=n)
            x,y=[base.read(out/(tag(q,h)+f'-n{n}.json')) for n in [400,800]]
            e=error(x['mol_per_feed_carbon'],y['mol_per_feed_carbon']);assert e<1e-4,f'phase refinement failed: {e}'
            base.write(out/(tag(q,h)+'-gates.json'),dict(max_species_refinement_error=e,threshold=1e-4))
            run(q,h,mode='match')
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-start))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',active=active,completed=done,reason=str(e),wall_s=time.monotonic()-start));raise

if __name__=='__main__':main()
