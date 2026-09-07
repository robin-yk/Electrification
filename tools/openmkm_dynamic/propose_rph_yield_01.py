"""Single-objective acetylene carbon-yield recommendation, not productivity."""
import hashlib
import importlib.metadata
import json
import signal
import subprocess
import time
from pathlib import Path
import numpy as np
from propose_rph_nextorch_01 import ROOT,encode,decode,write

DEST=ROOT/'docs/research/rph-yield-01-2026-09-07'

def training():
    archive=json.loads((ROOT/'docs/research/rph-nextorch-01-2026-09-07/observations-39.json').read_text())
    rows=[]
    for old in archive['points']:
        raw=old['source'];f=ROOT/raw
        assert hashlib.sha256(f.read_bytes()).hexdigest()==archive['sources'][raw]
        d=json.loads(f.read_text());i=d['inputs'];s=i['segments']
        assert i['feed']=={'CH4':.5,'CO2':.5} and i['period_s']==1
        assert i['pressure_target_Pa']==101325 and i['samples_per_segment']==800
        assert s[0][1]==723.15 and s[0][0]==.025 and s[2][0]==.1
        rows.append(dict(peak_C=s[1][1]-273.15,hold_s=s[1][0],flow_sccm=i['flow_sccm'],
            x=encode(s[1][1]-273.15,s[1][0],i['flow_sccm']),y=[100*d['carbon_yields']['C2H2']],source=raw))
    assert len(rows)==39 and len({tuple(r['x']) for r in rows})==39
    return rows,archive['sources']

def main():
    start=time.monotonic();DEST.mkdir(parents=True,exist_ok=True);status='stopped';reason=None
    def timeout(*_):raise TimeoutError('90 s yield-proposal cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(90)
    try:
        ledger=json.loads((ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json').read_text())
        assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s']
        assert any(b['id']=='rph-yield-01' and b['reserved_s']==240 for b in ledger['batches'])
        import torch
        from nextorch import bo
        torch.set_num_threads(1);torch.manual_seed(20260908);np.random.seed(20260908)
        rows,sources=training();x=np.array([r['x'] for r in rows]);y=np.array([r['y'] for r in rows])
        e=bo.Experiment('rph-yield-01');e.input_data(x,y,X_ranges=[[0,1]]*3,unit_flag=True)
        e.set_optim_specs(maximize=True)
        xn,_,_=e.generate_next_point(acq_func_name='EI',n_candidates=1)
        unit=xn.detach().cpu().numpy()[0]
        assert np.isfinite(unit).all() and (unit>=0).all() and (unit<=1).all()
        assert np.min(np.linalg.norm(x-unit,axis=1))>1e-5,'duplicate recommendation; do not rerun archive'
        p,h,q=decode(unit)
        with torch.no_grad():
            post=e.model.posterior(xn);mean=post.mean[0]*e.Y_std+e.Y_mean;sd=post.variance[0].sqrt()*e.Y_std
        write(DEST/'training.json',dict(points=rows,sources=sources,objectives=['C2H2_carbon_yield_pct'],
            units='percent of total inlet carbon',formula='100 * 2 * integrated C2H2 outflow / integrated (CH4 + CO2) inlet'))
        write(DEST/'proposal.json',dict(peak_C=float(p),hold_s=float(h),flow_sccm=float(q),normalized_x=unit.tolist(),
            predicted_carbon_yield_pct=mean.tolist(),posterior_sd_percentage_points=sd.tolist(),
            incumbent=max(rows,key=lambda r:r['y'][0]),training_n=39,seed=20260908,acquisition='EI',
            objective_mean=e.Y_mean.tolist(),objective_std=e.Y_std.tolist(),
            versions={k:importlib.metadata.version(k) for k in ['nextorch','botorch','gpytorch','torch','numpy','scipy']},
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            uncertainty_note='Single-objective GP posterior, not validated chemical uncertainty; CO is diagnostic only'))
        torch.save(e.model.state_dict(),DEST/'model-state.pt');status='completed';print((DEST/'proposal.json').read_text())
    except Exception as exc:reason=str(exc);raise
    finally:
        signal.alarm(0);write(DEST/'proposal-status.json',dict(status=status,reason=reason,wall_s=time.monotonic()-start))

if __name__=='__main__':main()
