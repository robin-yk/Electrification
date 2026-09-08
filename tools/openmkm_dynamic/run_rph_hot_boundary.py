"""Three user-approved high-temperature points, with unchanged acceptance gates."""
import subprocess
import sys
import time
from pathlib import Path
import run_rph_yield_grid as grid
base=grid.base
OUT=grid.CAMPAIGN/'hot-boundary/data'

def main():
    ledger=base.read(grid.CAMPAIGN/'budget.json')
    assert ledger['active_stage']=='hot-boundary' and ledger['reserved_s']==540
    assert ledger['spent_s']+540<=ledger['total_budget_s']
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'status.json').exists(), 'Do not overwrite or retry a prior batch'
    paths=[Path(__file__),Path(grid.__file__),Path(grid.pulse.__file__),Path(base.__file__),Path(__file__).with_name('run_rph_fixed_gate.py'),base.MECH]
    base.write(OUT/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(p.relative_to(base.ROOT)):grid.sha(p) for p in paths},peaks_C=[1900,2000,2100],hold_s=.8,flow_sccm=50,cap_s=540,claim='Prescribed gas-temperature extrapolation, not experimental mechanism validation'))
    started=time.monotonic();done=[];active=None
    def run(p,n,inert=False):
        nonlocal active
        active=grid.tag(p,.8,50)+('-inert' if inert else f'-n{n}')
        left=540-(time.monotonic()-started)
        assert left>0
        cmd=[sys.executable,str(Path(grid.__file__)),'--worker','--output-dir',str(OUT),'--peak',str(p),'--hold','.8','--flow','50','--samples',str(n)]
        if inert:cmd+=['--inert']
        with (OUT/(active+'.log')).open('w') as f:
            subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(100,left))
        done.append(active)
        return base.read(OUT/(active+'.json'))
    try:
        run(2100,800,True)
        for p in [1900,2000,2100]:
            lo=run(p,400);hi=run(p,800)
            e=grid.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon'])
            assert e<1e-4, f'phase refinement failed: {e}'
            base.write(OUT/(grid.tag(p,.8,50)+'-gates.json'),dict(error=e,threshold=1e-4))
        status='completed';reason=None
    except Exception as e:
        status='stopped';reason=str(e)
    elapsed=time.monotonic()-started
    base.write(OUT/'status.json',dict(status=status,reason=reason,active=active,completed=done,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger['reserved_s']=0;ledger['active_stage']=None
    ledger['batches'].append(dict(stage='hot-boundary',status=status,wall_s=elapsed,reason=reason))
    base.write(grid.CAMPAIGN/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)

if __name__=='__main__':main()
