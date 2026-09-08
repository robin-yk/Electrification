"""Composition screen at the current equimolar incumbent, not joint optimization."""
import argparse
import subprocess
import sys
import time
from pathlib import Path
import run_rph_yield_grid as g
b=g.base;C=g.CAMPAIGN;D=C/'feed-pilot-01';XS=[.6]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--index',type=int);ap.add_argument('--samples',type=int);a=ap.parse_args()
    if a.samples:
        g.pulse.worker(D/str(a.index),f'n{a.samples}',a.samples,waveform=g.waveform(1800,.8),flow_sccm=50,rtol=1e-11,feed_ch4=XS[a.index]);return
    ledger=b.read(C/'budget.json');cap=180
    assert ledger['active_stage'] is None and ledger['reserved_s']==0 and ledger['spent_s']+cap<=ledger['total_budget_s']
    assert not D.exists();D.mkdir()
    anchor=b.read(C/'hot-boundary-02/report.json')['rows'][0];source=b.ROOT/anchor['source'];assert g.sha(source)==anchor['sha256']
    r=b.read(source);assert r['inputs']['feed']=={'CH4':.5,'CO2':.5} and r['inputs']['segments']==[list(s) for s in g.waveform(1800,.8)] and r['inputs']['flow_sccm']==50
    files=[Path(__file__),Path(g.pulse.__file__),Path(g.__file__),b.MECH,source]
    b.write(D/'manifest.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hashes={str(f.relative_to(b.ROOT)):g.sha(f) for f in files},fractions=XS,reused_anchor=anchor,cap_s=cap,rtol=1e-11))
    ledger.update(active_stage='rph-feed-pilot-01',reserved_s=cap);b.write(C/'budget.json',ledger)
    start=time.monotonic();done=[];status='stopped';reason=None
    try:
        # Analytic inlet balance: both feed species carry one carbon atom.
        import cantera as ct
        gas=ct.Solution(str(b.MECH));checks=[]
        for x in XS:
            gas.TPX=723.15,101325,{'CH4':x,'CO2':1-x}
            mol=50/22414/60;mdot=mol*gas.mean_molecular_weight/1000
            recovered=mdot/gas.mean_molecular_weight*1000
            assert abs(recovered/mol-1)<1e-12
            checks.append(dict(x=x,inlet_mol_s=mol,inlet_carbon_mol_s=mol,mdot_kg_s=mdot))
        b.write(D/'inlet-checks.json',checks)
        for i in range(len(XS)):
            out=D/str(i);out.mkdir()
            for n in [400,800]:
                left=cap-(time.monotonic()-start);assert left>0
                with (out/f'n{n}.log').open('w') as log:subprocess.run([sys.executable,__file__,'--index',str(i),'--samples',str(n)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=min(90,left))
            lo,hi=[b.read(out/f'n{n}.json') for n in [400,800]]
            err=g.error(lo['mol_per_feed_carbon'],hi['mol_per_feed_carbon']);assert err<1e-4
            b.write(out/'gates.json',dict(phase_error=err,threshold=1e-4));done.append(i)
        status='completed'
    except Exception as e:reason=str(e)
    elapsed=time.monotonic()-start;b.write(D/'status.json',dict(status=status,reason=reason,completed=done,wall_s=elapsed))
    ledger['spent_s']+=elapsed;ledger.update(active_stage=None,reserved_s=0);ledger['batches'].append(dict(stage='rph-feed-pilot-01',status=status,reason=reason,wall_s=elapsed));b.write(C/'budget.json',ledger)
    if status!='completed':raise RuntimeError(reason)
if __name__=='__main__':main()
