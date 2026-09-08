"""Verify the committed EI recommendation with unchanged paired gates."""
import subprocess
import sys
import time
from pathlib import Path
import run_rph_yield_grid as grid
base=grid.base
out=grid.CAMPAIGN/'bo-01/verification'
def main():
    ledger=base.read(grid.CAMPAIGN/'budget.json')
    assert ledger['active_stage']=='bo-verify' and ledger['reserved_s']==240
    assert ledger['spent_s']+240<=ledger['total_budget_s']
    proposal=grid.CAMPAIGN/'bo-01/proposal.json';r=base.read(proposal)
    assert base.read(proposal.with_name('status.json'))['status']=='completed'
    out.mkdir(exist_ok=True);assert not (out/'status.json').exists()
    p,h,q=r['peak_C'],r['hold_s'],r['flow_sccm']
    paths=[Path(__file__),Path(grid.__file__),Path(grid.pulse.__file__),Path(base.__file__),base.MECH,proposal]
    base.write(out/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(f.relative_to(base.ROOT)):grid.sha(f) for f in paths},proposal=r))
    start=time.monotonic();done=[];active=None
    try:
        for n in [400,800]:
            active=grid.tag(p,h,q)+f'-n{n}'
            left=240-(time.monotonic()-start);assert left>0
            cmd=[sys.executable,str(Path(grid.__file__)),'--worker','--output-dir',str(out),'--peak',str(p),'--hold',str(h),'--flow',str(q),'--samples',str(n)]
            with (out/(active+'.log')).open('w') as f:
                subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,left))
            done.append(active)
        lo,hi=[base.read(out/(name+'.json')) for name in done]
        error=grid.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon'])
        assert error<1e-4
        base.write(out/'gates.json',dict(error=error,threshold=1e-4))
        base.write(out/'result.json',dict(proposal=r,actual_Y_pct=100*hi['carbon_yields']['C2H2'],improvement_pp=100*hi['carbon_yields']['C2H2']-r['incumbent_Y_pct'],source=done[-1]+'.json',sha256=grid.sha(out/(done[-1]+'.json'))))
        status='completed';reason=None
    except Exception as e:status='stopped';reason=str(e)
    elapsed=time.monotonic()-start
    base.write(out/'status.json',dict(status=status,reason=reason,active=active,completed=done,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger['reserved_s']=0;ledger['active_stage']=None
    ledger['batches'].append(dict(stage='bo-verify',status=status,reason=reason,wall_s=elapsed))
    base.write(grid.CAMPAIGN/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)
if __name__=='__main__':main()
