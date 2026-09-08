"""One budgeted exploration fit and two sequential paired verifications."""
import argparse
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as b
C=b.ROOT/'docs/research/rph-yield-grid-2026-09-07';D=C/'explore-01'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['propose','verify'],default='verify');ap.add_argument('--samples',type=int);ap.add_argument('--index',type=int,default=0);a=ap.parse_args()
    if a.stage=='verify' or a.samples:import run_rph_yield_grid as g
    if a.samples:
        p=b.read(D/'proposal.json')['proposals'][a.index]
        g.pulse.worker(D/'verification'/str(a.index),f'n{a.samples}',a.samples,waveform=g.waveform(p['peak_C'],p['hold_s']),flow_sccm=p['flow_sccm'],rtol=1e-11);return
    ledger=b.read(C/'budget.json');cap=120 if a.stage=='propose' else 540
    assert ledger['active_stage'] is None and ledger['reserved_s']==0 and ledger['spent_s']+cap<=ledger['total_budget_s']
    ledger.update(active_stage='explore01-'+a.stage,reserved_s=cap);b.write(C/'budget.json',ledger)
    start=time.monotonic();status='stopped';reason=None;done=[]
    try:
        if a.stage=='propose':
            subprocess.run([sys.executable,str(Path(__file__).with_name('propose_rph_explore.py'))],check=True,timeout=120)
        else:
            assert b.read(D/'propose-run.json')['status']=='completed' and not (D/'verification').exists()
            out=D/'verification';out.mkdir()
            files=[Path(__file__),Path(g.pulse.__file__),Path(g.__file__),b.MECH,D/'proposal.json']
            b.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(p.relative_to(b.ROOT)):g.sha(p) for p in files},rtol=1e-11,cap_s=cap))
            for i in range(2):
                d=out/str(i);d.mkdir()
                for n in [400,800]:
                    with (d/f'n{n}.log').open('w') as log:subprocess.run([sys.executable,__file__,'--index',str(i),'--samples',str(n)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=max(1,min(120,cap-(time.monotonic()-start))))
                lo,hi=[b.read(d/f'n{n}.json') for n in [400,800]]
                err=g.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']);assert err<1e-4
                b.write(d/'gates.json',dict(phase_error=err,threshold=1e-4,actual_Y_pct=100*hi['carbon_yields']['C2H2']));done.append(i)
        status='completed'
    except Exception as e:reason=str(e)
    elapsed=time.monotonic()-start;D.mkdir(exist_ok=True)
    b.write(D/(a.stage+'-run.json'),dict(status=status,reason=reason,completed=done,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger.update(active_stage=None,reserved_s=0);ledger['batches'].append(dict(stage='explore01-'+a.stage,status=status,reason=reason,wall_s=elapsed));b.write(C/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)
if __name__=='__main__':main()
