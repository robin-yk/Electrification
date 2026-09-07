"""One reproducible qEHVI proposal from the 38 validated 450 C conditions."""
import hashlib
import importlib.metadata
import json
import signal
import subprocess
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/research/rph-nextorch-01-2026-09-07'
OBJECTIVES=['C2H2','CO']

def encode(p,h,q):return [(p-1200)/600,(h-.025)/.475,np.log(q/50)/np.log(32)]
def decode(x):return [1200+600*x[0],.025+.475*x[1],50*32**x[2]]
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def training():
    points={};sources={}
    for rel in ['docs/research/rph-450-screen-01-2026-09-07/report.json','docs/research/rph-flow-02-2026-09-07/report.json']:
        report=json.loads((ROOT/rel).read_text())
        for raw,sha in report['sources'].items():
            f=ROOT/raw;assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
            d=json.loads(f.read_text());i=d['inputs'];s=i['segments']
            assert i['feed']=={'CH4':.5,'CO2':.5} and i['period_s']==1
            assert i['pressure_target_Pa']==101325 and i['standard_T_K']==273.15
            assert s[0][0]==.025 and s[2][0]==.1 and s[0][1]==723.15
            assert i['samples_per_segment']==800
            peak=s[1][1]-273.15;hold=s[1][0];flow=i['flow_sccm']
            key=(peak,hold,flow)
            point=dict(peak_C=peak,hold_s=hold,flow_sccm=flow,x=encode(*key),
                y=[d['product_g_per_g_CFP_h'][k] for k in OBJECTIVES],source=raw)
            if key in points:assert np.allclose(points[key]['y'],point['y'],rtol=0,atol=1e-10)
            points[key]=point;sources[raw]=sha
    assert len(points)==38
    return sorted(points.values(),key=lambda r:(r['peak_C'],r['hold_s'],r['flow_sccm'])),sources

def main():
    started=time.monotonic();DEST.mkdir(parents=True,exist_ok=True);status='stopped';reason=None
    def timeout(*_):raise TimeoutError('90 s NEXTorch wall-time cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(90)
    try:
        ledger=json.loads((ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json').read_text())
        assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s']
        assert any(b['id']=='rph-nextorch-01' and b['reserved_s']==240 for b in ledger['batches'])
        import torch
        from nextorch import bo
        torch.set_num_threads(1);torch.manual_seed(20260907);np.random.seed(20260907)
        rows,sources=training();x=np.array([r['x'] for r in rows]);y=np.array([r['y'] for r in rows])
        e=bo.EHVIMOOExperiment('rph-nextorch-01')
        e.input_data(x,y,X_ranges=[[0,1]]*3,unit_flag=True)
        ref=(-e.Y_mean/e.Y_std).tolist()
        e.set_ref_point(ref);e.set_optim_specs(maximize=True)
        xn,_,acq=e.generate_next_point(n_candidates=1)
        unit=xn.detach().cpu().numpy()[0]
        assert np.isfinite(unit).all() and (unit>=0).all() and (unit<=1).all()
        assert np.min(np.linalg.norm(x-unit,axis=1))>1e-5,'duplicate proposal'
        p,h,q=decode(unit)
        with torch.no_grad():
            posterior=e.model.posterior(xn)
            mean=posterior.mean[0]*e.Y_std+e.Y_mean
            sd=posterior.variance[0].sqrt()*e.Y_std
        versions={k:importlib.metadata.version(k) for k in ['nextorch','botorch','gpytorch','torch','numpy','scipy']}
        write(DEST/'training.json',dict(points=rows,sources=sources,objectives=OBJECTIVES,units='g-product/g-CFP/h',CFP_mass_g=.0288))
        write(DEST/'proposal.json',dict(peak_C=float(p),hold_s=float(h),flow_sccm=float(q),
            normalized_x=unit.tolist(),predicted_g_per_g_CFP_h=mean.tolist(),posterior_sd=sd.tolist(),
            training_n=len(rows),seed=20260907,acquisition='qEHVI',reference_raw=[0,0],reference_standardized=ref,
            objective_mean=e.Y_mean.tolist(),objective_std=e.Y_std.tolist(),versions=versions,
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            flow_transform='logarithmic, 50 to 1600 sccm; other inputs linear',
            uncertainty_note='GP posterior uncertainty, not validated physical or chemical uncertainty'))
        torch.save(e.model.state_dict(),DEST/'model-state.pt')
        status='completed';print((DEST/'proposal.json').read_text())
    except Exception as exc:reason=str(exc);raise
    finally:
        signal.alarm(0)
        write(DEST/'proposal-status.json',dict(status=status,reason=reason,wall_s=time.monotonic()-started))

if __name__=='__main__':main()
