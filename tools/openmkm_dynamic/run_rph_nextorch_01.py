"""Verify one frozen NEXTorch recommendation; no autonomous optimization loop."""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as base
import run_rph_fixed_pulse as pulse

PROPOSAL=base.ROOT/'docs/research/rph-nextorch-01-2026-09-07/proposal.json'

def waveform(p,h):
    assert 1200<=p<=1800 and .025<=h<=.5
    lo,hi=723.15,p+273.15
    return [(.025,lo,hi),(h,hi,hi),(.1,hi,lo),(.875-h,lo,lo)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--worker',choices=['inert','anchor','candidate','refined']);a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    d=base.read(PROPOSAL);p,h,q=d['peak_C'],d['hold_s'],d['flow_sccm'];assert 50<=q<=1600
    if a.worker:
        if a.worker=='anchor':p,h,q=1800,.1,400
        pulse.worker(out,a.worker,400 if a.worker=='candidate' else 800,
            inert=a.worker=='inert',waveform=waveform(p,h),flow_sccm=q)
        return
    ledger=base.read(base.ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
    assert ledger['reserved_s']==150 and ledger['spent_s']+150<=ledger['total_budget_s']
    assert any(b['id']=='rph-nextorch-01' and b['reserved_s']==150 for b in ledger['batches'])
    assert base.read(PROPOSAL.with_name('proposal-status.json'))['status']=='completed'
    training=base.read(PROPOSAL.with_name('training.json'))
    for path,sha in training['sources'].items():assert hashlib.sha256((base.ROOT/path).read_bytes()).hexdigest()==sha
    ref=base.ROOT/'docs/research/rph-flow-02-2026-09-07/data/Q400-hold0.1-n800.json'
    paths=[Path(__file__),Path(pulse.__file__),Path(base.__file__),Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH,PROPOSAL,ref]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base.ROOT,text=True).strip(),
        hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},cap_s=150))
    started=time.monotonic();done=[];active=None
    def err(x,y):
        x,y=x['mol_per_feed_carbon'],y['mol_per_feed_carbon']
        return max(abs(x.get(k,0)-y.get(k,0)) for k in set(x)|set(y))
    try:
        for active in ['inert','anchor','candidate','refined']:
            remaining=150-(time.monotonic()-started);assert remaining>0
            with (out/(active+'.log')).open('w') as f:
                subprocess.run([sys.executable,__file__,'--output-dir',str(out),'--worker',active],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,remaining))
            done.append(active)
            if active=='anchor':
                e=err(base.read(out/'anchor.json'),base.read(ref));assert e<1e-8
                base.write(out/'anchor-gates.json',dict(max_species_error=e,threshold=1e-8))
            if active=='refined':
                e=err(base.read(out/'candidate.json'),base.read(out/'refined.json'));assert e<1e-4
                base.write(out/'candidate-gates.json',dict(max_species_refinement_error=e,threshold=1e-4))
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-started))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',active=active,completed=done,reason=str(e),wall_s=time.monotonic()-started));raise

if __name__=='__main__':main()
