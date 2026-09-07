"""Match steady CJH temperature to each verified RPH methane conversion."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
import run_cjh_feed_ratio_01 as base

def inventory():
    t=base.read(base.ROOT/'docs/research/rph-nextorch-01-2026-09-07/observations-39.json')
    rows=[]
    for r in t['points']:
        f=base.ROOT/r['source'];assert hashlib.sha256(f.read_bytes()).hexdigest()==t['sources'][r['source']]
        d=base.read(f);i=d['inputs'];assert i['volume_m3']==base.volume_reference()
        assert i['feed']=={'CH4':.5,'CO2':.5} and i['pressure_target_Pa']==101325
        target=1-d['mol_per_feed_carbon']['CH4']/.5
        assert 0<target<1
        rows.append(dict(id=f"Q{i['flow_sccm']:.9g}-T{r['peak_C']:.9g}-h{r['hold_s']:.9g}",
            source=r['source'],sha256=t['sources'][r['source']],flow_sccm=i['flow_sccm'],peak_C=r['peak_C'],hold_s=r['hold_s'],target_X=target))
    assert len(rows)==39
    return sorted(rows,key=lambda r:(r['flow_sccm'],r['peak_C'],r['hold_s']))

def partition(rows,stage):
    selected=[r for r in rows if (r['flow_sccm'],r['peak_C'],r['hold_s']) in [(50,1200,.025),(50,1800,.5),(1600,1800,.5)]]
    if stage=='pilot':return selected
    rest=[r for r in rows if r not in selected];k=int(stage)-1
    return rest[k*12:(k+1)*12]

def solver_hash():
    paths=[Path(base.__file__),base.MECH]
    return {str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def solve(out,row):
    from scipy.optimize import brentq
    import cantera as ct
    gas=ct.Solution(str(base.MECH))
    q=row['flow_sccm'];target=row['target_X'];used=[]
    caches=[out]+sorted((base.ROOT/'docs/research').glob('cjh-rph-match-*-2026-09-07/data'))
    valid=[out]
    for folder in caches[1:]:
        manifest=folder/'manifest.json'
        if manifest.exists() and base.read(manifest).get('solver_hashes')==solver_hash():valid.append(folder)
    def evaluate(T,tight=2):
        name=f"steady-Q{q:.12g}-T{T:.12g}-a{tight}"
        for folder in valid:
            f=folder/(name+'.json')
            if f.exists():
                d=base.read(f);used.append(str(f));return d
        base.worker(out,name,.5,tight=tight,temperature_K=T+273.15,flow_sccm=q,pressure_K=1e-7)
        f=out/(name+'.json');d=base.read(f);used.append(str(f));return d
    tolerance=max(1e-7,target*1e-4)
    def residual(T):return evaluate(T)['CH4_conversion']-target
    lo,hi=450.,row['peak_C']
    flo,fhi=residual(lo),residual(hi)
    assert flo*fhi<=0,f'no matched-temperature bracket: {flo}, {fhi}'
    T=brentq(residual,lo,hi,xtol=1e-5,rtol=1e-10,maxiter=40)
    normal=evaluate(T);tight=evaluate(T,3)
    delta=base.compare(normal['mol_per_feed_carbon'],tight['mol_per_feed_carbon'])
    assert abs(tight['CH4_conversion']-target)<tolerance,'matched conversion refinement failed'
    rph=base.read(base.ROOT/row['source'])
    def yields(d):
        cy=d['carbon_yields']
        answer={k:100*cy.get(k,0) for k in ['C2H2','C2H4','C2H6','C6H6','CO']}
        answer['C6_total']=100*sum(v for k,v in cy.items() if gas.n_atoms(k,'C')==6)
        return answer
    # Phase quadrature errors can be material relative to tiny RPH conversions.
    sf=base.ROOT/row['source'];coarse=sf.with_name(sf.name.replace('n800','n400'))
    if sf.name=='refined.json':coarse=sf.with_name('candidate.json')
    phase_dx=None
    if coarse.exists():phase_dx=abs(rph['mol_per_feed_carbon']['CH4']-base.read(coarse)['mol_per_feed_carbon']['CH4'])/.5
    result=dict(**row,CJH_T_C=T,CJH_X=tight['CH4_conversion'],match_tolerance=tolerance,
        match_error=tight['CH4_conversion']-target,refinement_species_error=delta,
        RPH_yield_pct=yields(rph),CJH_yield_pct=yields(tight),
        RPH_phase_conversion_difference=phase_dx,low_conversion_warning=phase_dx is not None and target<10*phase_dx,
        inputs=tight['inputs'],CJH_mass_residence_time_s=tight['mass_residence_time_s'],
        evaluated_files=sorted(set(used)),raw_CJH=used[-1])
    base.write(out/(row['id']+'-matched.json'),result)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['pilot','1','2','3'],required=True)
    ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--worker');a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);rows=inventory()
    if a.worker in ['cold-control','archive-control']:
        base.worker(out,a.worker,.5,tight=2,cold=a.worker=='cold-control',pressure_K=1e-7)
        if a.worker=='archive-control':base.compare(base.read(base.ROOT/'docs/research/cjh-feed-ratio-02-2026-09-07/data/anchor.json')['mol_per_feed_carbon'],base.read(out/(a.worker+'.json'))['mol_per_feed_carbon'])
        return
    if a.worker:solve(out,next(r for r in rows if r['id']==a.worker));return
    cap=240 if a.stage=='pilot' else 450;batch='cjh-rph-match-'+a.stage
    ledger=base.read(base.ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
    assert ledger['spent_s']+ledger['reserved_s']<=ledger['total_budget_s'] and ledger['reserved_s']==cap
    assert any(b['id']==batch and b['reserved_s']==cap for b in ledger['batches'])
    if a.stage!='pilot':assert base.read(base.ROOT/'docs/research/cjh-rph-match-pilot-2026-09-07/data/status.json')['status']=='completed'
    jobs=partition(rows,a.stage)
    base.write(out/'manifest.json',dict(solver_hashes=solver_hash(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=base.ROOT,text=True).strip(),jobs=jobs,cap_s=cap))
    start=time.monotonic();done=[];active=None
    try:
        ids=(['cold-control','archive-control'] if a.stage=='pilot' else [])+[row['id'] for row in jobs]
        for active in ids:
            left=cap-(time.monotonic()-start);assert left>0
            with (out/(active+'.log')).open('w') as f:
                subprocess.run([sys.executable,__file__,'--stage',a.stage,'--output-dir',str(out),'--worker',active],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(180,left))
            done.append(active)
        base.write(out/'status.json',dict(status='completed',completed=done,wall_s=time.monotonic()-start))
    except Exception as e:
        base.write(out/'status.json',dict(status='stopped',completed=done,active=active,reason=str(e),wall_s=time.monotonic()-start));raise

if __name__=='__main__':main()
