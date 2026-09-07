"""Two-stage, bounded 450 C floor screen; no optimizer or automatic retry."""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as base
import run_rph_fixed_pulse as pulse

PEAKS = [1200, 1400, 1600, 1800]
HOLDS = [.025, .05, .10, .20, .30, .40, .50]
PILOT = [(1200, .025), (1800, .025), (1800, .50)]

def waveform(peak, hold):
    assert peak in PEAKS and hold in HOLDS
    lo, hi = 723.15, peak + 273.15
    return [(.025, lo, hi), (hold, hi, hi), (.1, hi, lo), (.875-hold, lo, lo)]

def tag(peak, hold):
    return f'T{peak}-hold{hold:g}'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['pilot','screen'], default='pilot')
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--worker', action='store_true')
    ap.add_argument('--inert', action='store_true')
    ap.add_argument('--peak', type=int, default=1800)
    ap.add_argument('--hold', type=float, default=.025)
    ap.add_argument('--samples', type=int, default=400)
    a=ap.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    if a.worker:
        name='inert' if a.inert else tag(a.peak,a.hold)+f'-n{a.samples}'
        pulse.worker(out,name,a.samples,inert=a.inert,waveform=waveform(a.peak,a.hold))
        return
    batch='rph-450-'+a.stage+'-01'; cap=240 if a.stage=='pilot' else 540
    ledger=base.read(base.ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
    assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s']
    assert ledger['reserved_s']==cap
    assert any(b['id']==batch and b['reserved_s']==cap for b in ledger['batches'])
    if a.stage=='screen':
        prior=base.ROOT/'docs/research/rph-450-pilot-01-2026-09-07/data'
        assert base.read(prior/'status.json')['status']=='completed'
        manifest=base.read(prior/'manifest.json')
        for path,sha in manifest['hashes'].items():
            assert hashlib.sha256((base.ROOT/path).read_bytes()).hexdigest()==sha
    jobs=PILOT if a.stage=='pilot' else [(p,h) for p in PEAKS for h in HOLDS if (p,h) not in PILOT]
    paths=[Path(__file__),Path(pulse.__file__),Path(base.__file__),Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base.ROOT,text=True).strip(),
        hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},jobs=jobs,cap_s=cap))
    started=time.monotonic();done=[];active=None
    def run(p,h,n,inert=False):
        nonlocal active
        active='inert' if inert else tag(p,h)+f'-n{n}'
        remaining=cap-(time.monotonic()-started)
        assert remaining>0,'batch budget exhausted'
        cmd=[sys.executable,__file__,'--worker','--output-dir',str(out),'--peak',str(p),'--hold',str(h),'--samples',str(n)]
        if inert: cmd+=['--inert']
        with (out/(active+'.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,remaining))
        done.append(active)
    try:
        if a.stage=='pilot':run(1800,.025,400,True)
        for p,h in jobs:
            for n in [400,800]:run(p,h,n)
            x,y=[base.read(out/(tag(p,h)+f'-n{n}.json'))['mol_per_feed_carbon'] for n in [400,800]]
            err=max(abs(x.get(k,0)-y.get(k,0)) for k in set(x)|set(y))
            assert err<1e-4,f'phase refinement failed: {err}'
            base.write(out/(tag(p,h)+'-gates.json'),dict(max_species_refinement_error=err,threshold=1e-4))
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-started))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',active=active,completed=done,reason=str(e),wall_s=time.monotonic()-started))
        raise

if __name__=='__main__':main()
