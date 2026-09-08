"""NEXTorch GPs with ratio-constrained expected improvement, fixed 50 sccm.

The acquisition integrates the shared acetylene variable explicitly. Independent
GPs for the two carbon yields are a declared statistical assumption, not chemical
independence. Candidate-pool search is not a certified continuous global optimum.
"""
import argparse
import hashlib
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from scipy.special import ndtr
from numpy.polynomial.hermite import hermgauss

ROOT=Path(__file__).resolve().parents[2]
C=ROOT/'docs/research/composition-bo-2026-09-08'
BOUNDS=np.array([[1600.,2000.],[.1,.8],[.5,.8]])
TARGETS=[1.,1.5,1.75]
def read(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def physical_gate(d):
    if d.get('engine')!='3.2.0' or len(d.get('history',[]))<3:return False
    for h in d['history']:
        if abs(h['mass_residual'])>=1e-3 or max(abs(v) for v in h['elemental_residuals'].values())>=1e-3:return False
        if h['max_pressure_relative_error']>=1e-4 or h['max_temperature_error_K']>=1e-4:return False
    return all(h['state_change']<1e-7 and h['max_species_cycle_change']<1e-7 for h in d['history'][-2:])
def inventory():
    selected={}
    for p in (ROOT/'docs/research').rglob('*n800.json'):
        d=read(p);i=d.get('inputs',{});s=i.get('segments');feed=i.get('feed',{})
        if not s or set(feed)!={'CH4','CO2'} or i.get('flow_sccm')!=50:continue
        if i.get('standard_T_K')!=273.15 or i.get('standard_P_Pa')!=101325 or i.get('period_s')!=1:continue
        if i.get('pressure_target_Pa')!=101325 or abs(i['volume_m3']/9.228077898393764e-9-1)>1e-10:continue
        if s[0][0]!=.025 or s[2][0]!=.1 or s[0][1]!=723.15:continue
        v=np.array([s[0][2]-273.15,s[1][0],feed['CH4']])
        if (v<BOUNDS[:,0]-1e-10).any() or (v>BOUNDS[:,1]+1e-10).any():continue
        if not physical_gate(d):continue
        lo=p.with_name(p.name.replace('n800','n400'))
        if not lo.exists():continue
        l=read(lo)
        if not physical_gate(l):continue
        il=dict(l['inputs']);ih=dict(i);il.pop('samples_per_segment');ih.pop('samples_per_segment')
        if il!=ih:continue
        a,b=l['mol_per_feed_carbon'],d['mol_per_feed_carbon'];error=max(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b))
        if error>=1e-4:continue
        key=tuple(v)
        row=dict(x=v.tolist(),y=[100*d['carbon_yields'][k] for k in ['C2H2','CO']],source=str(p.relative_to(ROOT)),sha256=sha(p),paired_source=str(lo.relative_to(ROOT)),paired_sha256=sha(lo),phase_error=error)
        if key not in selected or error<selected[key]['phase_error']:selected[key]=row
    return sorted(selected.values(),key=lambda r:r['x'])

def acquisition(mu,sd,target,best,order=128):
    z,w=hermgauss(order);a=mu[:,0,None]+np.sqrt(2)*sd[:,0,None]*z
    sigma=np.maximum(sd[:,1,None],1e-12)
    probability=ndtr((target*1.02*a/2-mu[:,1,None])/sigma)-ndtr((target*.98*a/2-mu[:,1,None])/sigma)
    probability=np.where(a>0,probability,0)
    value=probability if best is None else probability*np.maximum(a-best,0)
    return value@w/np.sqrt(np.pi),probability@w/np.sqrt(np.pi)

def self_test():
    for t in TARGETS:
        score,p=acquisition(np.array([[40.,20*t]]),np.full((1,2),1e-6),t,30)
        assert abs(score[0]-10)<1e-5 and abs(p[0]-1)<1e-8
    mu=np.array([[40.,20.]]);sd=np.array([[5.,3.]])
    score,p=acquisition(mu,sd,1.,30,256)
    rng=np.random.default_rng(9);a=rng.normal(40,5,500000);b=rng.normal(20,3,500000)
    f=(a>0)&(2*b>=.98*a)&(2*b<=1.02*a)
    assert abs(score[0]-np.mean(np.maximum(a-30,0)*f))<.02
    assert abs(p[0]-f.mean())<.003
    print('Acquisition unit and Monte Carlo cross-checks passed')

def fit(x,y):
    from nextorch import bo
    e=bo.Experiment('composition-constrained-rph')
    e.input_data(x,y[:,None],X_ranges=[[0,1]]*3,unit_flag=True)
    e.set_optim_specs(maximize=True)
    return e
def predict(models,x):
    import torch
    means=[];sds=[]
    for e in models:
        with torch.no_grad():
            p=e.model.posterior(torch.tensor(x,dtype=e.X.dtype))
            means.append((p.mean*e.Y_std+e.Y_mean).numpy().ravel())
            sds.append((p.variance.sqrt()*e.Y_std).numpy().ravel())
    return np.array(means).T,np.array(sds).T

def propose(dest):
    import torch
    torch.set_num_threads(1);torch.manual_seed(20260908)
    self_test();rows=inventory();assert len(rows)>=12
    x=(np.array([r['x'] for r in rows])-BOUNDS[:,0])/np.ptp(BOUNDS,axis=1)
    x=np.clip(x,0,1);y=np.array([r['y'] for r in rows])
    # Hold out the new interaction points, never report this as sealed validation.
    test=np.array(['composition-support-cloud' in r['source'] for r in rows])
    assert test.sum()==4
    checks=[fit(x[~test],y[~test,j]) for j in range(2)]
    mu,sd=predict(checks,x[test]);rmse=np.sqrt(np.mean((mu-y[test])**2,axis=0))
    write(dest/'development-check.json',dict(truth=y[test].tolist(),predicted=mu.tolist(),sd=sd.tolist(),rmse_pp=rmse.tolist(),scope='interaction support holdout; sparse-domain diagnostic, not sealed or chemical validation'))
    # Stop if the surrogate cannot even resolve broad changes within 10 pp.
    assert np.max(rmse)<10,'Interaction development RMSE exceeds 10 pp; stop BO and improve coverage'
    models=[fit(x,y[:,j]) for j in range(2)]
    pool=torch.quasirandom.SobolEngine(3,scramble=True,seed=20260908).draw(8192).double().numpy()
    # Include faces so an optimum on a permitted boundary is not missed by design.
    pool=np.vstack([pool,*[np.column_stack([pool[:,0],np.full(len(pool),h),pool[:,2]]) for h in [0.,1.]]])
    pool=pool[np.min(np.linalg.norm(pool[:,None,:]-x[None,:,:],axis=2),axis=1)>1e-4]
    mu,sd=predict(models,pool);assert np.isfinite(mu).all() and np.isfinite(sd).all()
    proposals=[]
    for target in TARGETS:
        valid=(y[:,0]>0)&(2*y[:,1]>=target*.98*y[:,0])&(2*y[:,1]<=target*1.02*y[:,0])
        best=float(y[valid,0].max()) if valid.any() else None
        score,prob=acquisition(mu,sd,target,best)
        if proposals:
            for prev in proposals:score[np.linalg.norm(pool-np.array(prev['normalized_x']),axis=1)<.015]=-1
        k=int(score.argmax());assert score[k]>0
        high,p2=acquisition(mu[k:k+1],sd[k:k+1],target,best,256)
        assert abs(high[0]-score[k])<max(.02,.05*score[k]),'Acquisition quadrature convergence failed'
        proposals.append(dict(target=target,x=(BOUNDS[:,0]+pool[k]*np.ptp(BOUNDS,axis=1)).tolist(),normalized_x=pool[k].tolist(),predicted_y=mu[k].tolist(),posterior_sd_pp=sd[k].tolist(),feasibility_probability=float(prob[k]),score=float(score[k]),incumbent=best,acquisition='Gauss-Hermite integrated feasible EI' if best is not None else 'feasibility probability',reaction_verified=False))
    write(dest/'training.json',dict(rows=rows,bounds=BOUNDS.tolist(),outputs=['C2H2 carbon yield percent','CO carbon yield percent'],statistical_assumption='independent NEXTorch GPs; shared C2H2 variable in feasibility and improvement'))
    write(dest/'proposals.json',dict(proposals=proposals,training_n=len(rows),candidate_pool_n=len(pool),seed=20260908,relative_tolerance=.02,claim='candidate-pool Bayesian recommendations, not verified optima',development_rmse_pp=rmse.tolist()))
    for j,e in enumerate(models):torch.save(e.model.state_dict(),dest/f'model-{j}.pt')
    print((dest/'proposals.json').read_text())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=1);ap.add_argument('--test',action='store_true');a=ap.parse_args()
    if a.test:self_test();return
    dest=C/f'round-{a.round:02d}';dest.mkdir(parents=True,exist_ok=True)
    assert not (dest/'status.json').exists(),'No overwrite or automatic retry'
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    ledger['active']=f'propose-{a.round}';write(C/'budget.json',ledger)
    start=time.monotonic();state='stopped';reason=None
    def timeout(*_):raise TimeoutError('300 s proposal cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(300)
    try:propose(dest);state='completed'
    except Exception as e:reason=type(e).__name__+': '+str(e)
    finally:
        signal.alarm(0);elapsed=time.monotonic()-start
        write(dest/'status.json',dict(status=state,reason=reason,wall_s=elapsed))
        ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage=f'propose-{a.round}',status=state,wall_s=elapsed));write(C/'budget.json',ledger)
    if state!='completed':print(reason);raise SystemExit(1)
if __name__=='__main__':main()
