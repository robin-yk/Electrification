"""Two in-domain exploration points from a 69-observation NEXTorch GP."""
import hashlib
import itertools
import subprocess
from pathlib import Path
import numpy as np
import run_cjh_feed_ratio_01 as b
C=b.ROOT/'docs/research/rph-yield-grid-2026-09-07'
D=C/'explore-01'
def choose(x,candidates,sd):
    distance=np.linalg.norm(candidates[:,None,:]-x[None,:,:],axis=2).min(axis=1)
    eligible=distance>=.10
    assert eligible.any()
    first=int(np.argmax(np.where(eligible,sd,-np.inf)))
    spread=np.minimum(distance,np.linalg.norm(candidates-candidates[first],axis=1))
    second=int(np.argmax(spread))
    assert first!=second and spread[second]>=.10
    return [first,second],distance,spread
def main():
    import torch
    from nextorch import bo
    assert not D.exists();D.mkdir()
    rows=b.read(C/'bo-02/training.json')['rows']
    source=C/'bo-02/verification/n800.json';raw=b.read(source);p=b.read(C/'bo-02/proposal.json')
    assert b.read(C/'bo-02/verify-run.json')['status']=='completed'
    gates=b.read(C/'bo-02/verification/gates.json');assert gates['phase_error']<1e-4
    rows.append(dict(peak_C=p['peak_C'],hold_s=p['hold_s'],flow_sccm=p['flow_sccm'],source=str(source.relative_to(b.ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),C2H2_Y_pct=100*raw['carbon_yields']['C2H2'],solver_rtol=raw['solver_rtol']))
    assert len(rows)==69
    for r in rows:assert hashlib.sha256((b.ROOT/r['source']).read_bytes()).hexdigest()==r['sha256']
    x=np.array([[(r['peak_C']-1400)/600,(r['hold_s']-.1)/.7,np.log(r['flow_sccm']/12.5)/np.log(16)] for r in rows])
    assert np.all(x>=-1e-12) and np.all(x<=1+1e-12)
    x=np.clip(x,0,1);y=np.array([[r['C2H2_Y_pct']] for r in rows])
    torch.set_num_threads(1);torch.manual_seed(20260910)
    e=bo.Experiment('yield-exploration-69');e.input_data(x,y,X_ranges=[[0,1]]*3,unit_flag=True);e.set_optim_specs(maximize=True)
    candidates=np.unique(np.vstack([torch.quasirandom.SobolEngine(3,scramble=True,seed=71).draw(8192).numpy(),list(itertools.product([0.,.5,1.],repeat=3))]),axis=0)
    means=[];sds=[]
    with torch.no_grad():
        for chunk in np.array_split(candidates,17):
            post=e.model.posterior(torch.tensor(chunk,dtype=e.X.dtype))
            means.extend((post.mean*e.Y_std+e.Y_mean).reshape(-1).tolist())
            sds.extend((post.variance.sqrt()*e.Y_std).reshape(-1).tolist())
    sd=np.array(sds);assert np.isfinite(sd).all() and np.isfinite(means).all()
    ids,distance,spread=choose(x,candidates,sd)
    proposals=[]
    for kind,i in zip(['max_posterior_sd','maximin_distance'],ids):
        z=candidates[i]
        proposals.append(dict(kind=kind,peak_C=float(1400+600*z[0]),hold_s=float(.1+.7*z[1]),flow_sccm=float(12.5*16**z[2]),normalized_x=z.tolist(),predicted_Y_pct=means[i],posterior_sd_pp=sds[i],nearest_training_distance=float(distance[i]),sequential_distance=float(spread[i])))
    b.write(D/'training.json',dict(rows=rows,x=x.tolist(),y=y.tolist(),bounds=[[1400,2000],[.1,.8],[12.5,200]],flow_transform='log',objective='C2H2 total-feed-carbon yield percent'))
    b.write(D/'proposal.json',dict(training_n=69,candidate_n=len(candidates),proposals=proposals,seed=71,min_normalized_distance=.10,incumbent_Y_pct=float(y.max()),selection='Exploration, not expected-improvement maximization',commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()))
    torch.save(e.model.state_dict(),D/'model-state.pt')
    print(proposals)
if __name__=='__main__':main()
