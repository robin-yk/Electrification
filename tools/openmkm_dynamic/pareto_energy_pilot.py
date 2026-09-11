"""Energy-support pilot for a ratio-constrained yield/energy frontier."""
from cantera_runtime import prepare_runtime
RUNTIME = prepare_runtime()
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
from replay_bo_energy import summarize
def physical_gate(d):
    """Same physical checks as composition_bo, without the SciPy dependency."""
    if d.get('engine')!='3.2.0' or len(d.get('history',[]))<3:return False
    for h in d['history']:
        if abs(h['mass_residual'])>=1e-3 or max(abs(v) for v in h['elemental_residuals'].values())>=1e-3:return False
        if h['max_pressure_relative_error']>=1e-4 or h['max_temperature_error_K']>=1e-4:return False
    return all(h['state_change']<1e-7 and h['max_species_cycle_change']<1e-7 for h in d['history'][-2:])
ROOT = Path(__file__).resolve().parents[2]
C = ROOT/'docs/research/composition-bo-2026-09-08'
OUT = C/'pareto-energy-pilot-01'
SOURCES = [
    'docs/research/rph-450-screen-01-2026-09-07/data/T1800-hold0.1-n800.json',
    'docs/research/composition-support-cloud-2026-09-08/1/n800.json',
    'docs/research/composition-support-cloud-2026-09-08/3/n800.json',
]
def read(p): return json.loads(p.read_text())
def save(p,d): p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);ap.add_argument('--n',type=int,default=400);a=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.worker is not None:
        from run_rph_fixed_pulse import worker
        old=read(ROOT/SOURCES[a.worker]);i=old['inputs'];folder=OUT/str(a.worker);folder.mkdir(exist_ok=True)
        worker(folder,f'n{a.n}',a.n,period=i['period_s'],waveform=i['segments'],flow_sccm=i['flow_sccm'],feed_ch4=i['feed']['CH4'],rtol=old['solver_rtol'],capture_energy=True)
        return
    assert not (OUT/'status.json').exists(), 'Do not overwrite a completed or failed pilot'
    ledger=read(C/'budget.json');assert ledger['active'] is None and ledger['spent_s']+300<=ledger['total_s']
    # Reuse the identical thermal evaluator's verified inert and reacting gates.
    gate=C/'energy-incumbents-01'
    assert read(gate/'status.json')['status']=='completed'
    assert abs(read(gate/'-1/n800-energy.json')['Q_rxn_W'])<1e-5
    files=[Path(__file__),ROOT/'tools/openmkm_dynamic/replay_bo_energy.py',ROOT/'tools/openmkm_dynamic/run_rph_fixed_pulse.py',ROOT/'tools/openmkm_dynamic/cantera_runtime.py',ROOT/'tools/openmkm_dynamic/element_drive.py',ROOT/'tools/cantera/mechanisms/aramco20.yaml']+[ROOT/s for s in SOURCES]
    save(OUT/'manifest.json',dict(runtime=RUNTIME,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},cap_s=300,selection='Energy training support, not Bayesian recommendations'))
    ledger['active']=OUT.name;save(C/'budget.json',ledger)
    start=time.monotonic();done=[];state='stopped';reason=None
    try:
        for j,source in enumerate(SOURCES):
            folder=OUT/str(j);folder.mkdir(exist_ok=True)
            for n in [400,800]:
                left=300-(time.monotonic()-start);assert left>0
                with (folder/f'n{n}.log').open('w') as f:
                    subprocess.run([sys.executable,__file__,'--worker',str(j),'--n',str(n)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=min(120,left))
            lo,hi=[read(folder/f'n{n}.json') for n in [400,800]]
            assert physical_gate(lo) and physical_gate(hi)
            old=read(ROOT/source);m=hi['mol_per_feed_carbon'];om=old['mol_per_feed_carbon'];lm=lo['mol_per_feed_carbon']
            replay=max(abs(m.get(k,0)-om.get(k,0)) for k in set(m)|set(om));assert replay<1e-8
            phase=max(abs(m.get(k,0)-lm.get(k,0)) for k in set(m)|set(lm));assert phase<1e-4
            sl,sh=[summarize(folder,n) for n in [400,800]]
            for f in sh['scenarios']:
                for k in ['input_W','cooling_W']:
                    assert abs(sl['scenarios'][f][k]-sh['scenarios'][f][k])/max(abs(sh['scenarios'][f][k]),1)<.005
            e=read(folder/'n800-energy.json');assert abs(e['energy_balance_residual_J'])<1e-6
            row=dict(index=j,source=source,replay_species_error=replay,phase_error=phase,**sh)
            save(folder/'summary.json',row);done.append(row)
            save(OUT/'status.json',dict(status='running',completed=done,wall_s=time.monotonic()-start))
        state='completed'
    except Exception as e: reason=f'{type(e).__name__}: {e}'
    finally:
        elapsed=time.monotonic()-start;save(OUT/'status.json',dict(status=state,reason=reason,completed=done,wall_s=elapsed))
        ledger['spent_s']+=elapsed;ledger['active']=None;ledger['batches'].append(dict(stage=OUT.name,status=state,wall_s=elapsed));save(C/'budget.json',ledger)
    print(json.dumps(dict(status=state,reason=reason,n=len(done),wall_s=elapsed)))
    if state!='completed':raise SystemExit(1)
if __name__=='__main__':main()
