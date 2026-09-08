"""Bounded second EI proposal and paired direct verification."""
import argparse
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as base
CAMP=base.ROOT/'docs/research/rph-yield-grid-2026-09-07'
D=CAMP/'bo-02'
def main():
    global D
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['propose','verify'],default='verify');ap.add_argument('--samples',type=int);ap.add_argument('--round',type=int,choices=[2,3],default=2);a=ap.parse_args()
    D=CAMP/f'bo-{a.round:02d}'
    if a.stage=='verify' or a.samples:
        import run_rph_yield_grid as g
    out=D/'verification'
    if a.samples:
        r=g.base.read(D/'proposal.json')
        g.pulse.worker(out,f'n{a.samples}',a.samples,waveform=g.waveform(r['peak_C'],r['hold_s']),flow_sccm=r['flow_sccm'],rtol=1e-11);return
    cap=120 if a.stage=='propose' else 300
    ledger=base.read(CAMP/'budget.json');assert ledger['active_stage'] is None and ledger['reserved_s']==0
    assert ledger['spent_s']+cap<=ledger['total_budget_s']
    ledger.update(active_stage='bo-propose' if a.stage=='propose' else 'bo02-verify',reserved_s=cap)
    base.write(CAMP/'budget.json',ledger)
    start=time.monotonic();status='stopped';reason=None
    try:
        if a.stage=='propose':
            assert not D.exists()
            subprocess.run([sys.executable,str(Path(__file__).with_name('propose_rph_grid_bo.py')),'--round',str(a.round)],check=True,timeout=120)
        else:
            assert g.base.read(D/'status.json')['status']=='completed' and not out.exists()
            out.mkdir()
            files=[Path(__file__),Path(g.pulse.__file__),Path(g.__file__),g.base.MECH,D/'proposal.json']
            g.base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(p.relative_to(g.base.ROOT)):g.sha(p) for p in files},rtol=1e-11,cap_s=cap))
            for n in [400,800]:
                with (out/f'n{n}.log').open('w') as log:
                    subprocess.run([sys.executable,__file__,'--round',str(a.round),'--samples',str(n)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=max(1,min(140,cap-(time.monotonic()-start))))
            lo,hi=[g.base.read(out/f'n{n}.json') for n in [400,800]]
            err=g.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']);assert err<1e-4
            g.base.write(out/'gates.json',dict(phase_error=err,threshold=1e-4,actual_Y_pct=100*hi['carbon_yields']['C2H2']))
        status='completed'
    except Exception as e:reason=str(e)
    elapsed=time.monotonic()-start
    D.mkdir(exist_ok=True)
    base.write(D/(a.stage+'-run.json'),dict(status=status,reason=reason,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger.update(active_stage=None,reserved_s=0)
    ledger['batches'].append(dict(stage=f'bo{a.round:02d}-'+a.stage,status=status,reason=reason,wall_s=elapsed))
    base.write(CAMP/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)
if __name__=='__main__':main()
