"""Bounded periodic fixed-volume, fixed-feed gas-temperature verification."""
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
import cantera as ct
import run_cjh_feed_ratio_01 as base
from run_rph_fixed_gate import PrescribedTemperatureReactor
PRESSURE_K = 1e-7

def segments(period):
    assert period>0
    return [(period*f,a,b) for f,a,b in [(0.025,873.15,2073.15),(.05,2073.15,2073.15),(.1,2073.15,873.15),(.825,873.15,873.15)]]

def worker(out,name,n,period=1.,inert=False,waveform=None):
    started=time.monotonic()
    parts=segments(period) if waveform is None else waveform
    assert all(d>0 and a>0 and b>0 for d,a,b in parts)
    assert abs(sum(d for d,_,_ in parts)-period)<1e-12
    assert all(abs(a[2]-b[1])<1e-10 for a,b in zip(parts,parts[1:]+parts[:1]))
    gas=ct.Solution("gri30.yaml" if inert else str(base.MECH))
    feed={"N2":1} if inert else {"CH4":.5,"CO2":.5}
    gas.TPX=parts[0][1],101325,feed
    mw=gas.molecular_weights.copy(); yin=gas.Y.copy()
    elements=["N"] if inert else ["C","H","O"]
    atoms=np.array([[gas.n_atoms(k,e) for k in range(gas.n_species)] for e in elements])
    flow_mol_s=50/22414/60
    mdot=flow_mol_s*gas.mean_molecular_weight/1000
    vol=base.volume_reference()
    inlet=ct.Reservoir(gas,clone=True);exhaust=ct.Reservoir(gas,clone=True)
    r=PrescribedTemperatureReactor(gas,energy="off",volume=vol,clone=True)
    mfc=ct.MassFlowController(inlet,r,mdot=mdot)
    pc=ct.PressureController(r,exhaust,primary=mfc,K=PRESSURE_K)
    net=ct.ReactorNet([r]);net.rtol=1e-9;net.atol=1e-15*vol
    net.preconditioner=ct.AdaptivePreconditioner()
    net.derivative_settings={"skip-third-bodies":True,"skip-falloff":True}
    fin=mdot*yin/mw
    last=None;stable=0;history=[];last_end=None
    t=0.
    for cycle in range(1,9):
        inventory0=r.mass*r.phase.Y/mw
        integral=np.zeros(gas.n_species);massout=0.;maxp=0.;maxt=0.;samples=[]
        for duration,ta,tb in parts:
            r.temperature_slope=(tb-ta)/duration
            net.reinitialize()
            start=t
            # Sample each linear segment separately so corners are explicit.
            prevflow=pc.mass_flow_rate*r.phase.Y/mw
            prevmass=pc.mass_flow_rate
            for j in range(1,n+1):
                target=start+duration*j/n
                net.advance(target)
                dt=target-t;t=target
                flow=pc.mass_flow_rate*r.phase.Y/mw
                integral+=(prevflow+flow)*(.5*dt)
                massout+=(prevmass+pc.mass_flow_rate)*(.5*dt)
                prevflow=flow;prevmass=pc.mass_flow_rate
                maxp=max(maxp,abs(r.phase.P/101325-1))
                maxt=max(maxt,abs(r.T-(ta+(tb-ta)*j/n)))
                if j==n or j%max(1,n//20)==0:
                    samples.append(dict(time_s=t,T_K=r.T,P_Pa=r.phase.P,mass_kg=r.mass,mdot_out_kg_s=pc.mass_flow_rate))
        inv=r.mass*r.phase.Y/mw
        elem_in=atoms@fin*period
        residual=(atoms@(fin*period-integral-(inv-inventory0)))/elem_in
        massres=(mdot*period-massout-(r.mass-float(np.dot(inventory0,mw))))/(mdot*period)
        norm=flow_mol_s/1000*period
        ratios=integral/norm
        change=None if last is None else float(np.max(abs(ratios-last)))
        statechange=None if last_end is None else float(max(np.max(abs(r.phase.Y-last_end[0])),abs(r.mass/last_end[1]-1)))
        stable=stable+1 if change is not None and change<1e-7 and statechange<1e-7 else 0
        last=ratios.copy();last_end=(r.phase.Y.copy(),r.mass)
        history.append(dict(cycle=cycle,max_species_cycle_change=change,state_change=statechange,
            elemental_residuals=dict(zip(elements,map(float,residual))),mass_residual=float(massres),
            max_pressure_relative_error=maxp,max_temperature_error_K=maxt))
        base.write(out/(name+"-diagnostic.json"),dict(history=history,last_cycle_samples=samples,wall_s=time.monotonic()-started))
        print(name,cycle,history[-1],flush=True)
        assert maxt<1e-4,"temperature waveform drift"
        assert maxp<1e-4,"pressure control failed"
        assert max(abs(residual))<1e-3 and abs(massres)<1e-3,"cycle integral balance failed"
        assert abs(r.volume/vol-1)<1e-12
        if cycle>=3 and stable>=2:break
    assert stable>=2,"periodic convergence failed"
    if inert:assert np.max(abs(r.phase.Y-yin))<1e-10
    ratiosdict={k:float(v) for k,v in zip(gas.species_names,ratios) if v>0}
    rates={k:float(v*flow_mol_s*3600*m) for k,v,m in zip(gas.species_names,ratios,mw) if v>0}
    base.write(out/(name+".json"),dict(name=name,engine=ct.__version__,
        inputs=dict(feed=feed,flow_sccm=50,standard_T_K=273.15,standard_P_Pa=101325,volume_m3=vol,
          pressure_target_Pa=101325,pressure_controller_K=PRESSURE_K,period_s=period,segments=parts,samples_per_segment=n),
        basis="mol product per mol inlet total carbon for CH4/CO2; mol per mol inlet for inert control",
        mol_per_feed_carbon=ratiosdict,carbon_yields={k:float(gas.n_atoms(k,"C")*v) for k,v in ratiosdict.items()},
        product_g_h=rates,product_g_per_g_CFP_h={k:v/.0288 for k,v in rates.items()},
        cycles=cycle,history=history,wall_s=time.monotonic()-started))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--period-study",action="store_true")
    ap.add_argument("--worker",choices=["inert","baseline","refined","half","half-refined","double","double-refined"]);a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.worker:
        period=.5 if a.worker.startswith("half") else 2. if a.worker.startswith("double") else 1.
        worker(out,a.worker,800 if "refined" in a.worker else 400,period=period,inert=a.worker=="inert");return
    ledger=base.read(base.ROOT/"docs/research/c2co-campaign-2026-09-07/budget.json")
    assert ledger["spent_s"]+ledger["reserved_s"]<=ledger["total_budget_s"]
    batch,cap=("rph-fixed-period-01",240) if a.period_study else ("rph-fixed-pulse-02",540)
    assert any(b["id"]==batch and b["reserved_s"]==cap for b in ledger["batches"])
    if a.period_study:
        assert base.read(base.ROOT/"docs/research/rph-fixed-pulse-02-2026-09-07/data/status.json")["status"]=="completed"
    assert base.read(base.ROOT/"docs/research/rph-fixed-gate-01-2026-09-07/data/status.json")["status"]=="completed"
    paths=[Path(__file__),Path(base.__file__),Path(__file__).with_name("run_rph_fixed_gate.py"),base.MECH]
    base.write(out/"manifest.json",dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},cap_s=cap))
    started=time.monotonic();done=[];active=None
    try:
        jobs=["half","half-refined","double","double-refined"] if a.period_study else ["inert","baseline","refined"]
        for active in jobs:
            with (out/(active+".log")).open("w") as f:
                subprocess.run([sys.executable,__file__,"--output-dir",str(out),"--worker",active],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=max(1,min(100,cap-(time.monotonic()-started))))
            done.append(active)
            if "refined" in active:
                first=active.replace("-refined","") if "-refined" in active else "baseline"
                r1=base.read(out/(first+".json"))["mol_per_feed_carbon"];r2=base.read(out/(active+".json"))["mol_per_feed_carbon"]
                err=max(abs(r1.get(k,0)-r2.get(k,0)) for k in set(r1)|set(r2))
                assert err<1e-4,f"phase integration refinement failed: {err}"
                base.write(out/(first+"-gates.json"),dict(max_species_refinement_error=err,threshold=1e-4))
        base.write(out/"status.json",dict(status="completed",completed=done,wall_s=time.monotonic()-started))
    except Exception as e:
        base.write(out/"status.json",dict(status="stopped",active=active,completed=done,reason=str(e),wall_s=time.monotonic()-started));raise
if __name__=="__main__":main()
