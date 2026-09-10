"""Bounded reconstruction of candidate A with a fixed archived temperature history."""
import os
os.environ.update(TZ='UTC0', LC_ALL='C', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import json, hashlib, time, sys, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/research/rph-candidate-flow-pilot-2026-09-10'
if '--attempt02' in sys.argv:
    OUT=ROOT/'docs/research/rph-candidate-flow-pilot-2026-09-10-attempt02'
MECH=ROOT/'tools/cantera/mechanisms/aramco20.yaml'
def update_slope(reactor, network, slope):
    """Retain the integrator history while the prescribed slope is unchanged."""
    if reactor.slope != slope:
        reactor.slope=slope
        network.reinitialize()
def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def calculate():
    import numpy as np
    import cantera as ct
    from element_drive import cfp_heat_capacity
    class Prescribed(ct.ExtensibleIdealGasMoleReactor):
        slope=0.
        def after_eval(self,t,lhs,rhs):
            j=self.component_index('temperature');lhs[j]=1.;rhs[j]=self.slope
    # Reconstruct the historical implementation for Cantera 3.1; test before flow expansion.
    gas=ct.Solution(str(MECH),transport_model=None)
    gas.TPX=300,101325,{'N2':1}
    test=Prescribed(gas,energy='off',volume=1e-8);test.slope=100
    net=ct.ReactorNet([test]);net.advance(.1)
    assert abs(test.T-310)<1e-6
    save('analytic.json',dict(passed=True,T_K=test.T,engine=ct.__version__))
    atlas=json.loads((ROOT/'docs/research/all-energy-atlas-2026-09-10/case-table.json').read_text())
    case=next(c for c in atlas if c['id']=='RPH-d9641af44c')
    source=Path(case['source']);ref=json.loads(source.read_text());settings=ref['inputs']
    save('manifest.json',dict(source=str(source),source_sha256=digest(source),script_sha256=digest(Path(__file__)),mechanism_sha256=digest(MECH),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),engine=ct.__version__,jobs=['A50-n4','A50-n8','A100-n4','A100-n8']))
    results={}
    for flow in ([50] if '--attempt02' in sys.argv else [50,100]):
        for n in [4,8]:
            name=f'A{flow}-n{n}';started=time.monotonic()
            save('progress.json',dict(active=name,completed=list(results)))
            parts=settings['segments'];period=settings['period_s'];vol=settings['volume_m3'];feed=settings['feed']
            gas.TPX=298.15,101325,feed
            mw=gas.molecular_weights.copy();yin=gas.Y.copy()
            atoms=np.array([[gas.n_atoms(k,e) for k in range(gas.n_species)] for e in ['C','H','O']])
            hin=gas.enthalpy_mass;h298=gas.partial_molar_enthalpies.copy()
            finmol=flow*1e-6/60*settings['standard_P_Pa']/(8.314462618*settings['standard_T_K'])
            mdot=finmol*gas.mean_molecular_weight/1000
            inlet=ct.Reservoir(gas);exhaust=ct.Reservoir(gas)
            gas.TPX=parts[0][1],101325,feed
            r=Prescribed(gas,energy='off',volume=vol)
            mfc=ct.MassFlowController(inlet,r,mdot=mdot)
            pc=ct.PressureController(r,exhaust,primary=mfc,K=settings['pressure_controller_K'])
            net=ct.ReactorNet([r]);net.rtol=1e-11;net.atol=1e-15*vol
            net.preconditioner=ct.AdaptivePreconditioner()
            net.derivative_settings={'skip-third-bodies':True,'skip-falloff':True}
            last=None;stable=0;t=0.;history=[]
            for cycle in range(1,9):
                inv0=r.mass*r.thermo.Y/mw;mass0=r.mass;integ=np.zeros(gas.n_species);mout=0.;steps=[];maxp=0.;maxt=0.
                for duration,ta,tb in parts:
                    update_slope(r,net,(tb-ta)/duration);start=t
                    for j in range(1,n+1):
                        before=r.mass*r.thermo.int_energy_mass;T0=r.T
                        f0=pc.mass_flow_rate*r.thermo.Y/mw;md0=pc.mass_flow_rate;hf0=md0*r.thermo.enthalpy_mass
                        target=start+duration*j/n;net.advance(target);dt=target-t;t=target
                        f1=pc.mass_flow_rate*r.thermo.Y/mw;md1=pc.mass_flow_rate
                        integ+=(f0+f1)*dt/2;mout+=(md0+md1)*dt/2
                        q=r.mass*r.thermo.int_energy_mass-before+((hf0+md1*r.thermo.enthalpy_mass)/2-mdot*hin)*dt
                        mid=(T0+r.T)/2;store=28.8e-6*cfp_heat_capacity(mid-273.15)*(r.T-T0)
                        rad=.57*5.670374419e-8*.000608*(mid**4-298.15**4)*dt
                        steps.append([dt,q,store,rad]);maxp=max(maxp,abs(r.thermo.P/101325-1));maxt=max(maxt,abs(r.T-(ta+(tb-ta)*j/n)))
                inv=r.mass*r.thermo.Y/mw;ein=atoms@(mdot*yin/mw)*period
                err=(atoms@(mdot*yin/mw*period-integ-(inv-inv0)))/ein
                masserr=(mdot*period-mout-(r.mass-mass0))/(mdot*period)
                ratios=integ/(finmol/1000*period)
                change=1 if last is None else float(max(abs(ratios-last)))
                stable=stable+1 if change<1e-7 else 0;last=ratios.copy()
                history.append(dict(cycle=cycle,element_residual=max(abs(err)),mass_residual=masserr,change=change,max_pressure_error=maxp,max_temperature_error_K=maxt))
                save(name+'-diagnostic.json',dict(history=history,wall_s=time.monotonic()-started))
                assert maxp<1e-4 and maxt<1e-4
                assert max(abs(err))<1e-3 and abs(masserr)<1e-3
                if cycle>=3 and stable>=2:break
            assert stable>=2 and max(abs(err))<1e-4 and abs(masserr)<1e-4
            qrx=float(np.dot(integ,h298)/period-mdot*hin)
            scenarios=[]
            for factor in [1.,.1]:
                positive=sum(max(0,q+s+factor*rad) for dt,q,s,rad in steps)/period
                cooling=sum(max(0,-q-s-factor*rad) for dt,q,s,rad in steps)/period
                scenarios.append(dict(radiation_remaining=factor,input_W=positive,cooling_W=cooling,eta_rxn_pct=100*qrx/positive))
            result=dict(id=name,inputs=dict(settings,flow_sccm=flow,samples_per_segment=n),mol_per_feed_carbon=dict(zip(gas.species_names,map(float,ratios))),Y_C2H2_pct=200*float(ratios[gas.species_index('C2H2')]),CO_C2H2=float(ratios[gas.species_index('CO')]/ratios[gas.species_index('C2H2')]),Q_rxn_W=qrx,scenarios=scenarios,phase_energy_steps=steps,history=history,wall_s=time.monotonic()-started)
            save(name+'.json',result);results[name]=result
        lo=results[f'A{flow}-n4'];hi=results[f'A{flow}-n8']
        diff=max(abs(lo['mol_per_feed_carbon'][k]-v) for k,v in hi['mol_per_feed_carbon'].items())
        ediff=max(abs(a['input_W']/b['input_W']-1) for a,b in zip(lo['scenarios'],hi['scenarios']))
        reference_error=None
        if flow==50:reference_error=max(abs(hi['mol_per_feed_carbon'].get(k,0)-v) for k,v in ref['mol_per_feed_carbon'].items())
        passed=diff<1e-4 and ediff<.01 and (reference_error is None or reference_error<1e-4)
        save(f'A{flow}-gate.json',dict(passed=passed,max_species_refinement_error=diff,relative_energy_error=ediff,archived_reference_error=reference_error))
        assert passed,'Paired or archived reproduction gate failed; stop queued jobs'
    save('summary.json',[{k:v for k,v in r.items() if k in ['id','Y_C2H2_pct','CO_C2H2','Q_rxn_W','scenarios','wall_s']} for r in results.values()])

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    if '--worker' in sys.argv:calculate()
    else:
        assert not (OUT/'status.json').exists(),'Preserve previous attempt; do not overwrite'
        start=time.monotonic()
        with (OUT/'execution.log').open('w') as f:
            try:
                p=subprocess.run([sys.executable,'-u',__file__,'--worker']+(['--attempt02'] if '--attempt02' in sys.argv else []),stdout=f,stderr=subprocess.STDOUT,timeout=300)
                status='completed' if p.returncode==0 else 'failed'
            except subprocess.TimeoutExpired:status='timeout'
        save('status.json',dict(status=status,wall_s=time.monotonic()-start,cap_s=300))
        print((OUT/'status.json').read_text())
