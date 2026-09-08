"""One bounded tighter-integration diagnostic, without admitting training data."""
import argparse
import subprocess
import sys
import time
from pathlib import Path
import run_rph_yield_grid as g

OUT=g.CAMPAIGN/'bo-01/tighter-01'
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int);a=p.parse_args()
    proposal=g.base.read(g.CAMPAIGN/'bo-01/proposal.json')
    if a.samples:
        g.pulse.worker(OUT,f'n{a.samples}',a.samples,waveform=g.waveform(proposal['peak_C'],proposal['hold_s']),flow_sccm=proposal['flow_sccm'],rtol=1e-11)
        return
    ledger=g.base.read(g.CAMPAIGN/'budget.json')
    assert ledger['active_stage'] is None and ledger['reserved_s']==0
    assert ledger['spent_s']+300<=ledger['total_budget_s']
    assert not OUT.exists()
    OUT.mkdir()
    paths=[Path(__file__),Path(g.pulse.__file__),Path(g.__file__),g.base.MECH]
    g.base.write(OUT/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(x.relative_to(g.base.ROOT)):g.sha(x) for x in paths},proposal=proposal,rtol=1e-11,cap_s=300,max_cycles=8,admit_training=False))
    ledger.update(active_stage='bo-tighter-01',reserved_s=300)
    g.base.write(g.CAMPAIGN/'budget.json',ledger)
    start=time.monotonic();done=[];status='stopped';reason=None
    try:
        for n in [400,800]:
            with (OUT/f'n{n}.log').open('w') as log:
                subprocess.run([sys.executable,__file__,'--samples',str(n)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=max(1,min(140,300-(time.monotonic()-start))))
            done.append(n)
        lo,hi=[g.base.read(OUT/f'n{n}.json') for n in [400,800]]
        err=g.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon'])
        assert err<1e-4
        g.base.write(OUT/'gates.json',dict(phase_error=err,threshold=1e-4,actual_Y_pct=100*hi['carbon_yields']['C2H2'],admit_training=False))
        status='completed'
    except Exception as e:reason=str(e)
    elapsed=time.monotonic()-start
    g.base.write(OUT/'status.json',dict(status=status,reason=reason,completed=done,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger.update(active_stage=None,reserved_s=0)
    ledger['batches'].append(dict(stage='bo-tighter-01',status=status,reason=reason,wall_s=elapsed))
    g.base.write(g.CAMPAIGN/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)
if __name__=='__main__':main()
