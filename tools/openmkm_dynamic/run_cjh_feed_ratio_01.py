"""Fixed-volume, fixed-feed, pressure-regulated isothermal CSTR pilot."""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BATCH="cjh-feed-ratio-02"
MECH=ROOT/"tools/cantera/mechanisms/aramco20.yaml"
REF=ROOT/"docs/research/cjh-refine-04-2026-09-07/data/T1750-tau0.001-metrics.json"
def read(p): return json.loads(Path(p).read_text())
def write(p,x): Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+"\n")
def settings(x,volume):
    assert 0<x<1 and volume>0
    return dict(T_K=2023.15,P_Pa=101325.,flow_sccm=50.,standard_T_K=273.15,
                standard_P_Pa=101325.,volume_m3=volume,feed=dict(CH4=x,CO2=1-x))
def volume_reference():
    r=read(REF)
    beta=sum(r["mol_per_feed_carbon"].values())
    return .001*50/60*(2023.15/273.15)*beta*1e-6
def compare(ref,actual):
    keys=set(ref)|set(actual)
    err=max(abs(ref.get(k,0)-actual.get(k,0)) for k in keys)
    assert err<1e-5, f"reference mismatch {err}"
    return err
def worker(out,name,x,tight=False,cold=False,reactor_type=None,temperature_K=None,flow_sccm=50.,pressure_K=1e-8):
    print("stage: importing cantera",flush=True)
    import cantera as ct
    import numpy as np
    started=time.monotonic()
    p=settings(x,volume_reference())
    if temperature_K is not None:p['T_K']=float(temperature_K)
    p['flow_sccm']=float(flow_sccm)
    assert p['T_K']>0 and p['flow_sccm']>0 and pressure_K>0
    if cold: p["T_K"]=300.
    print("stage: loading mechanism",flush=True)
    gas=ct.Solution("gri30.yaml" if cold else str(MECH))
    print("stage: mechanism loaded",time.monotonic()-started,flush=True)
    gas.TPX=p["T_K"],p["P_Pa"],p["feed"]
    feedY=gas.Y.copy(); mw=gas.molecular_weights.copy()
    atoms=np.array([[gas.n_atoms(k,e) for k in range(gas.n_species)] for e in ("C","H","O")])
    flow_mol_s=p['flow_sccm']/22414/60
    mdot=flow_mol_s*gas.mean_molecular_weight/1000
    inlet=ct.Reservoir(gas,clone=True); exhaust=ct.Reservoir(gas,clone=True)
    reactor_type=reactor_type or ct.IdealGasMoleReactor
    r=reactor_type(gas,energy="off",volume=p["volume_m3"],clone=True)
    mfc=ct.MassFlowController(inlet,r,mdot=mdot)
    pc=ct.PressureController(r,exhaust,primary=mfc,K=pressure_K)
    net=ct.ReactorNet([r]); net.rtol=1e-11 if tight in (1,3) else 1e-9
    net.atol=1e-19 if tight==1 else 1e-15
    if tight==2: net.atol=1e-15*p["volume_m3"]
    if tight==3: net.atol=1e-17*p["volume_m3"]
    net.preconditioner=ct.AdaptivePreconditioner()
    net.derivative_settings={"skip-third-bodies":True,"skip-falloff":True}
    last=None; stable=0; hist=[]
    # Physical comparison times are identical between normal/tight integrations.
    for block in range(1,101):
        net.advance(block*.005)
        if block==1 or block%20==0: print("stage: integration",block,time.monotonic()-started,flush=True)
        y=r.phase.Y.copy()
        state=np.r_[y,r.mass]
        residual=1. if last is None else float(max(np.max(abs(y-last[:-1])),abs(r.mass/last[-1]-1)))
        last=state
        stable=stable+1 if residual<1e-8 else 0
        hist.append(dict(time_s=net.time,residual=residual,P_Pa=r.phase.P,mass_kg=r.mass,
                         Y_CH4=float(y[gas.species_index("CH4")]),
                         Y_C2H2=float(y[gas.species_index("C2H2")]),
                         flow_ratio=pc.mass_flow_rate/mdot))
        if block>=20 and stable>=5: break
    write(out/(name+"-diagnostic.json"),dict(inputs=p,rtol=net.rtol,atol=net.atol,
        stable=stable,history=hist,moles_kmol=r.mass/r.phase.mean_molecular_weight,
        solver_stats=net.solver_stats,wall_s=time.monotonic()-started))
    assert stable>=5,"stationarity failed"
    assert abs(r.phase.P/p["P_Pa"]-1)<1e-4,"pressure drift"
    assert abs(r.volume/p["volume_m3"]-1)<1e-12,"volume drift"
    inlet_C=mdot*float(np.dot(atoms[0],feedY/mw))
    molratio=(pc.mass_flow_rate*y/mw)/inlet_C
    ratios={k:float(v) for k,v in zip(gas.species_names,molratio) if v>0}
    fin=mdot*(atoms@(feedY/mw)); fout=pc.mass_flow_rate*(atoms@(y/mw))
    errors=(fout-fin)/fin
    assert np.max(abs(errors))<1e-5, f"element flow residual {errors}"
    assert abs(pc.mass_flow_rate/mdot-1)<1e-6,"mass flow mismatch"
    if cold: assert max(abs(y-feedY))<1e-8,"cold analytic failed"
    cy={k:float(gas.n_atoms(k,"C")*v) for k,v in ratios.items()}
    rates={k:float(v*flow_mol_s*3600*gas.molecular_weights[gas.species_index(k)]) for k,v in ratios.items()}
    # g/mol numerical molecular weights, flow_mol_s is mol/s.
    result=dict(name=name,inputs=p,mechanism=gas.source,engine=ct.__version__,
      rtol=net.rtol,atol=net.atol,pressure_controller_K=pressure_K,
      mass_flow_kg_s=mdot,outlet_mass_flow_kg_s=pc.mass_flow_rate,
      mass_residence_time_s=r.mass/mdot,pressure_Pa=r.phase.P,volume_m3=r.volume,
      mol_per_feed_carbon=ratios,carbon_yields=cy,product_g_h=rates,
      product_g_per_g_CFP_h={k:v/.0288 for k,v in rates.items()},
      CH4_conversion=1-ratios.get("CH4",0)/x,
      CO2_conversion=1-ratios.get("CO2",0)/(1-x),
      elemental_flow_residuals=dict(zip(("C","H","O"),map(float,errors))),
      history=hist,wall_s=time.monotonic()-started)
    write(out/(name+".json"),result)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--refine",action="store_true")
    ap.add_argument("--worker",nargs=4);a=ap.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.worker:
        name,x,tight,cold=a.worker;worker(out,name,float(x),int(tight),bool(int(cold)));return
    ledger=read(ROOT/"docs/research/c2co-campaign-2026-09-07/budget.json")
    assert ledger["spent_s"]+ledger["reserved_s"]<=3600
    batch,cap=("cjh-feed-ratio-03",180) if a.refine else (BATCH,540)
    assert any(b["id"]==batch and b["reserved_s"]==cap for b in ledger["batches"])
    jobs=[("cold",.5,2,1),("anchor",.5,2,0),("anchor-tight",.5,3,0),
          ("ratio-1-4",.2,2,0),("ratio-1-2",1/3,2,0),
          ("ratio-2-1",2/3,2,0),("ratio-4-1",.8,2,0)]
    if a.refine:
        prior=ROOT/"docs/research/cjh-feed-ratio-02-2026-09-07/data"
        assert read(prior/"status.json")["status"]=="completed"
        assert len(read(prior/"gates.json"))==2
        assert hashlib.sha256(MECH.read_bytes()).hexdigest()==read(prior/"manifest.json")["mechanism_sha256"]
        jobs=[("ch4-40",.4,2,0),("ch4-60",.6,2,0)]
    write(out/"manifest.json",dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
       script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       mechanism_sha256=hashlib.sha256(MECH.read_bytes()).hexdigest(),jobs=jobs,
       reference=str(REF.relative_to(ROOT)),budget_s=cap,worker_limit_s=100,
       note="New fixed-volume, constant feed model; pressure controller enforces near-1-atm. No device heating model."))
    started=time.monotonic();done=[];gates=[];active=None
    try:
        for name,x,tight,cold in jobs:
            active=name
            write(out/"status.json",dict(status="running",completed=done,active=name))
            left=cap-(time.monotonic()-started)
            assert left>5,"batch exhausted"
            with (out/(name+".log")).open("w") as log:
                subprocess.run([sys.executable,__file__,"--output-dir",str(out),"--worker",
                    name,str(x),str(tight),str(cold)],check=True,timeout=min(100,left),stdout=log,stderr=subprocess.STDOUT)
            r=read(out/(name+".json"))
            if name=="anchor":
                gates.append(dict(name="archived chemistry",max_abs=compare(read(REF)["mol_per_feed_carbon"],r["mol_per_feed_carbon"])))
            if name=="anchor-tight":
                gates.append(dict(name="integrator refinement",max_abs=compare(read(out/"anchor.json")["mol_per_feed_carbon"],r["mol_per_feed_carbon"])))
            done.append(name);write(out/"gates.json",gates)
        write(out/"status.json",dict(status="completed",completed=done,wall_s=time.monotonic()-started))
    except Exception as e:
        write(out/"status.json",dict(status="stopped",completed=done,active=active,reason=str(e),wall_s=time.monotonic()-started))
        raise
if __name__=="__main__":main()
