"""Repair acquisition maximization on the frozen GP; do not refit or run chemistry."""
import hashlib
import itertools
import json
import signal
import time
from pathlib import Path
import numpy as np
from propose_rph_nextorch_01 import ROOT,decode,write

DEST=ROOT/'docs/research/rph-yield-search-02-2026-09-07'

def main():
    start=time.monotonic();DEST.mkdir(parents=True,exist_ok=True);status='stopped';reason=None
    def timeout(*_):raise TimeoutError('90 s acquisition repair cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(90)
    try:
        ledger=json.loads((ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json').read_text())
        assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s']
        assert any(b['id']=='rph-yield-search-02' and b['reserved_s']==90 for b in ledger['batches'])
        import torch
        from nextorch import bo
        from robust_acquisition import search
        torch.set_num_threads(1)
        old=ROOT/'docs/research/rph-yield-01-2026-09-07'
        t=json.loads((old/'training.json').read_text());p=json.loads((old/'proposal.json').read_text())
        for path,sha in t['sources'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
        x=np.array([r['x'] for r in t['points']]);y=np.array([r['y'] for r in t['points']])
        e=bo.Experiment('search-repair');e.input_data(x,y,X_ranges=[[0,1]]*3,unit_flag=True)
        m=bo.SingleTaskGP(e.X,e.Y);m.load_state_dict(torch.load(old/'model-state.pt',map_location='cpu'));m.eval()
        acq=bo.get_acq_func(m,'EI',best_f=e.Y.max())
        def vg(v):
            z=torch.tensor(v,dtype=e.X.dtype,requires_grad=True)
            a=acq(z.reshape(1,1,3)).sum();g=torch.autograd.grad(a,z)[0]
            return a.item(),g.detach().numpy().astype(float)
        # Include training anchors and corners, not only random interior starts.
        sobol=torch.quasirandom.SobolEngine(3,scramble=True,seed=11).draw(4096).numpy()
        seeds=np.unique(np.vstack([sobol,x,np.array(list(itertools.product([0.,1.],repeat=3)))]),axis=0)
        point,score,details=search(vg,seeds,24)
        # Independent reference set is not used to seed or improve this result.
        check=torch.quasirandom.SobolEngine(3,scramble=True,seed=29).draw(8192)
        with torch.no_grad():
            reference=float(acq(check.reshape(-1,1,3)).max())
        old_score=vg(p['normalized_x'])[0];incumbent_score=vg(p['incumbent']['x'])[0]
        audit=dict(score=score,previous_score=old_score,incumbent_score=incumbent_score,
            independent_reference_best=reference,independent_reference_n=8192,seed_n=len(seeds),
            details=details,passed=bool(score>=max(reference,incumbent_score)*(1-1e-5)))
        write(DEST/'search-audit.json',audit)
        assert audit['passed'],'independent acquisition quality gate failed'
        assert np.min(np.linalg.norm(x-point,axis=1))>1e-5,'duplicate recommendation'
        with torch.no_grad():
            z=torch.tensor(point,dtype=e.X.dtype).reshape(1,3);post=m.posterior(z)
            mean=(post.mean[0]*e.Y_std+e.Y_mean).tolist();sd=(post.variance[0].sqrt()*e.Y_std).tolist()
        peak,hold,flow=decode(point)
        files=[old/'model-state.pt',old/'training.json',Path(__file__),Path(__file__).with_name('robust_acquisition.py')]
        write(DEST/'proposal.json',dict(peak_C=float(peak),hold_s=float(hold),flow_sccm=float(flow),
            normalized_x=point.tolist(),predicted_carbon_yield_pct=mean,posterior_sd_percentage_points=sd,
            acquisition='EI',training_n=39,refitted=False,reaction_verified=False,
            input_hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
        status='completed';print((DEST/'proposal.json').read_text());print(json.dumps({k:v for k,v in audit.items() if k!='details'}))
    except Exception as exc:reason=str(exc);raise
    finally:
        signal.alarm(0);write(DEST/'status.json',dict(status=status,reason=reason,wall_s=time.monotonic()-start,reaction_runs=0))

if __name__=='__main__':main()
