"""NEXTorch posterior sampling for constrained yield/energy improvement."""
import os
os.environ.update(TZ='UTC0',LC_ALL='C',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse, hashlib, json, signal, time
from pathlib import Path
import numpy as np
import torch
from scipy.special import ndtri
from composition_bo import inventory, fit, predict, BOUNDS, C, ROOT
WIKI=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki')
D=WIKI/'B2 working-paper/manuscripts-B2/dynamic-temperature-pulsing/drafts'
OUT=C/'pareto-bo-01'
def read(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def gains(a,b,front):
    """Hypervolume increase from one point, reference (0,0), both maximized."""
    result=np.zeros_like(a);last=0.
    for x in sorted(set([float(p[0]) for p in front])):
        level=max(p[1] for p in front if p[0]>=x)
        result+=np.maximum(np.minimum(a,x)-last,0)*np.maximum(b-level,0);last=x
    return result+np.maximum(a-last,0)*np.maximum(b,0)
def propose():
    torch.set_num_threads(1);torch.manual_seed(20260911)
    assert abs(gains(np.array([3.]),np.array([3.]),[[2.,2.]])[0]-5)<1e-12
    assert gains(np.array([1.]),np.array([1.]),[[2.,2.]])[0]==0
    base=read(D/'aramco-v3/eligible-records.json')+read(D/'aramco-v3/bo-energy/records.json')
    energy=[]
    for r in base:
        s=r.get('segments',[])
        if r['mode']!='RPH' or r['radiation_remaining']!=.1 or r['flow_sccm']!=50 or len(s)!=4:continue
        if s[0][0]!=.025 or s[2][0]!=.1 or s[0][1]!=723.15 or r['period_s']!=1:continue
        energy.append(dict(x=[r['Tmax_C'],s[1][0],r['feed']['CH4']],input_W=r['input_W'],source=r['source']))
    old_n=len(energy)
    support=C/'pareto-energy-pilot-02';assert read(support/'status.json')['status']=='completed'
    for row in read(support/'status.json')['completed']:
        raw=read(support/str(row['index'])/'n800.json');s=raw['inputs']['segments']
        energy.append(dict(x=[s[0][2]-273.15,s[1][0],raw['inputs']['feed']['CH4']],input_W=row['scenarios']['0.1']['input_W'],source=str(support/str(row['index'])/'n800.json')))
    ex=(np.array([r['x'] for r in energy])-BOUNDS[:,0])/np.ptp(BOUNDS,axis=1)
    ey=np.log([r['input_W'] for r in energy])
    # A development prediction check, performed before adding the three support points.
    check=fit(ex[:old_n],ey[:old_n]);cm,cs=predict([check],ex[old_n:])
    rel=np.abs(np.exp(cm[:,0])-np.exp(ey[old_n:]))/np.exp(ey[old_n:])
    save(OUT/'development-check.json',dict(relative_errors=rel.tolist(),threshold=.25,training_n=old_n,scope='Energy-support predictive check; reused for subsequent training'))
    assert max(rel)<.25,'Energy support prediction error exceeds 25%; expand energy training first'
    rows=inventory();x=np.clip((np.array([r['x'] for r in rows])-BOUNDS[:,0])/np.ptp(BOUNDS,axis=1),0,1);y=np.array([r['y'] for r in rows])
    models=[fit(x,y[:,j]) for j in range(2)]+[fit(ex,ey)]
    pool=torch.quasirandom.SobolEngine(3,scramble=True,seed=20260911).draw(4096).double().numpy()
    pool=np.vstack([pool,np.column_stack([pool[:,0],np.zeros(len(pool)),pool[:,2]]),np.column_stack([pool[:,0],np.ones(len(pool)),pool[:,2]])])
    pool=pool[np.min(np.linalg.norm(pool[:,None,:]-x[None,:,:],axis=2),axis=1)>1e-4]
    mu,sd=predict(models,pool)
    z=ndtri(np.clip(torch.quasirandom.SobolEngine(3,scramble=True,seed=91).draw(512).double().numpy(),1e-8,1-1e-8))
    proposals=[]
    for target in [1.,1.5,1.75]:
        frontier=[[r['Y_C2H2_pct']/40,r['C2H2_mmol_kJ']/.25] for r in base if r['pool']=='CH4/CO2 | CSTR | 90% lower radiation' and abs(r['CO_C2H2']/target-1)<=.02]
        scores=[];prob=[]
        for start in range(0,len(pool),256):
            draws=mu[start:start+256,None,:]+sd[start:start+256,None,:]*z[None,:,:]
            a=draws[:,:,0];co=draws[:,:,1];power=np.exp(draws[:,:,2])
            feasible=(a>0)&(a<=100)&(co>=0)&(a+co<=100)&(2*co>=target*.98*a)&(2*co<=target*1.02*a)
            # 50 sccm, one carbon per feed molecule, mmol/s from carbon yield percent.
            productivity=(a/200)*(50/22414/60*1000)*1000/power
            imp=gains(a/40,productivity/.25,frontier)*feasible
            scores.extend(imp.mean(axis=1));prob.extend(feasible.mean(axis=1))
        scores=np.array(scores)
        for q in proposals:scores[np.linalg.norm(pool-np.array(q['normalized_x']),axis=1)<.015]=-1
        k=int(np.argmax(scores));assert scores[k]>0
        proposals.append(dict(target=target,x=(BOUNDS[:,0]+pool[k]*np.ptp(BOUNDS,axis=1)).tolist(),normalized_x=pool[k].tolist(),predicted_y=mu[k,:2].tolist(),predicted_input_W=float(np.exp(mu[k,2])),score=float(scores[k]),feasibility_probability=float(prob[k]),reaction_verified=False))
    save(OUT/'training.json',dict(chemical=rows,energy=energy,bounds=BOUNDS.tolist(),archive_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'aramco-v3/eligible-records.json',D/'aramco-v3/bo-energy/records.json']},assumption='Independent GPs for C2H2 yield, CO yield and log positive thermal input. Derived energy productivity shares sampled C2H2 with the ratio constraint.'))
    save(OUT/'proposals.json',dict(proposals=proposals,acquisition='512 Sobol posterior samples of ratio-constrained hypervolume improvement against the existing CJH/RPH archive',reference=[0,0],objective_scales=[40,.25],seed=20260911,candidate_n=len(pool)))
    for j,m in enumerate(models):torch.save(m.model.state_dict(),OUT/f'model-{j}.pt')
    print(json.dumps(dict(training_chemistry=len(rows),training_energy=len(energy),proposals=proposals)))
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'status.json').exists()
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    ledger['active']='pareto-propose-01';save(C/'budget.json',ledger);start=time.monotonic();state='stopped';reason=None
    def timeout(*args):raise TimeoutError('300-second proposal cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(300)
    try:propose();state='completed'
    except Exception as e:reason=f'{type(e).__name__}: {e}'
    finally:
        signal.alarm(0);elapsed=time.monotonic()-start;save(OUT/'status.json',dict(status=state,reason=reason,wall_s=elapsed));ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage='pareto-propose-01',status=state,wall_s=elapsed));save(C/'budget.json',ledger)
    if reason:print(reason);raise SystemExit(1)
if __name__=='__main__':main()
