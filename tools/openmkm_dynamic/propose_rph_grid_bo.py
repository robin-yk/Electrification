"""One audited EI recommendation after complete factorial yield screening."""
import hashlib
import itertools
import json
from pathlib import Path
import signal
import subprocess
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
CAMP=ROOT/'docs/research/rph-yield-grid-2026-09-07'
DEST=CAMP/'bo-01'
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    start=time.monotonic();DEST.mkdir(exist_ok=True);status='stopped';reason=None
    def alarm(*_):raise TimeoutError('120 second proposal cap')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(120)
    try:
        b=json.loads((CAMP/'budget.json').read_text());assert b['active_stage']=='bo-propose' and b['reserved_s']==120
        assert b['spent_s']+120<=b['total_budget_s']
        t=json.loads((CAMP/'observations.json').read_text());assert t['grid_completed']==75
        rows=[r for r in t['points'] if 1400<=r['peak_C']<=1800 and .1<=r['hold_s']<=.8 and 12.5<=r['flow_sccm']<=200]
        assert len(rows)==75
        for r in rows:assert hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest()==r['sha256']
        x=np.array([[(r['peak_C']-1400)/400,(r['hold_s']-.1)/.7,np.log(r['flow_sccm']/12.5)/np.log(16)] for r in rows])
        y=np.array([[r['C2H2_Y_pct']] for r in rows])
        import torch
        from nextorch import bo
        from robust_acquisition import search
        torch.set_num_threads(1);torch.manual_seed(20260909)
        e=bo.Experiment('yield-grid-bo');e.input_data(x,y,X_ranges=[[0,1]]*3,unit_flag=True);e.set_optim_specs(maximize=True)
        acq=bo.get_acq_func(e.model,'EI',best_f=e.Y.max())
        def vg(v):
            z=torch.tensor(v,dtype=e.X.dtype,requires_grad=True);a=acq(z.reshape(1,1,3)).sum()
            return a.item(),torch.autograd.grad(a,z)[0].detach().numpy().astype(float)
        sobol=torch.quasirandom.SobolEngine(3,scramble=True,seed=17).draw(4096).numpy()
        seeds=np.unique(np.vstack([x,sobol,list(itertools.product([0.,1.],repeat=3))]),axis=0)
        point,score,details=search(vg,seeds,24)
        test=torch.quasirandom.SobolEngine(3,scramble=True,seed=43).draw(8192)
        with torch.no_grad():reference=float(acq(test.reshape(-1,1,3)).max())
        incumbent=max(vg(v)[0] for v in x)
        audit=dict(score=score,independent_reference=reference,best_training_acquisition=incumbent,details=details)
        write(DEST/'search-audit.json',audit)
        assert np.isfinite(point).all() and (point>=0).all() and (point<=1).all()
        assert score>=max(reference,incumbent)*(1-1e-5),'acquisition quality failure'
        assert np.min(np.linalg.norm(x-point,axis=1))>1e-5,'duplicate recommendation'
        with torch.no_grad():
            post=e.model.posterior(torch.tensor(point,dtype=e.X.dtype).reshape(1,3))
            mean=(post.mean[0]*e.Y_std+e.Y_mean).tolist();sd=(post.variance[0].sqrt()*e.Y_std).tolist()
        write(DEST/'training.json',dict(rows=rows,x=x.tolist(),y=y.tolist(),bounds=[[1400,1800],[.1,.8],[12.5,200]],flow_transform='log',objective='C2H2 total-feed-carbon yield percent'))
        write(DEST/'proposal.json',dict(peak_C=float(1400+400*point[0]),hold_s=float(.1+.7*point[1]),flow_sccm=float(12.5*16**point[2]),
            normalized_x=point.tolist(),predicted_Y_pct=mean,posterior_sd_pp=sd,training_n=75,
            incumbent_Y_pct=float(y.max()),acquisition='EI',reaction_verified=False,
            commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            limitation='Optimum search conditional on declared bounds and fixed waveform family; uncertainty is GP posterior, not chemical validation. Off-domain observations retained but not fitted.'))
        torch.save(e.model.state_dict(),DEST/'model-state.pt');status='completed';print((DEST/'proposal.json').read_text())
    except Exception as exc:reason=str(exc);raise
    finally:signal.alarm(0);write(DEST/'status.json',dict(status=status,reason=reason,wall_s=time.monotonic()-start))
if __name__=='__main__':main()
