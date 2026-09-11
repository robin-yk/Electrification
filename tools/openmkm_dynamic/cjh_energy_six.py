"""Six requested feed-flow points after archived-anchor and paired checks."""
import json,time,hashlib,subprocess,sys
from pathlib import Path
import cjh_energy_pilot as solver
OUT=solver.ROOT/'docs/research/cjh-energy-six-2026-09-09'
OUT.mkdir(exist_ok=True)
def save(n,d):(OUT/(n+'.json')).write_text(json.dumps(d,indent=2)+'\n')
def worker():
    prior=solver.OUT
    assert json.loads((prior/'status.json').read_text())['status']=='passed'
    solver.OUT=OUT
    check=solver.run('anchor',tight=True)
    ref=json.loads((prior/'tight.json').read_text())
    error=max(abs(check['mol_per_feed_carbon'][k]-ref['mol_per_feed_carbon'][k]) for k in check['mol_per_feed_carbon'])
    assert error<1e-5
    save('anchor-gate',dict(passed=True,error=error))
    for x in [.65,.8]:
        for q in [100,200,400]:
            name=f'ch4-{x:.2f}-Q{q}'
            a=solver.run(name,T_C=1800,flow=q,ch4=x)
            if x==.65 and q==100:
                b=solver.run(name+'-tight',tight=True,T_C=1800,flow=q,ch4=x)
                error=max(abs(a['mol_per_feed_carbon'][k]-b['mol_per_feed_carbon'][k]) for k in a['mol_per_feed_carbon'])
                assert error<1e-5
                save('paired-gate',dict(passed=True,error=error))
if __name__=='__main__':
    if '--worker' in sys.argv:worker()
    else:
        save('manifest',dict(inputs=dict(T_C=1800,CH4=[.65,.8],flow_sccm=[100,200,400],radiation_remaining=.1),
             files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(solver.__file__),solver.MECH]},
             commit=subprocess.check_output(['git','-C',str(solver.ROOT),'rev-parse','HEAD'],text=True).strip(),
             budget_s=300,role='six-point pilot; no BO acquisition'))
        start=time.monotonic()
        with (OUT/'execution.log').open('w') as log:
            try:
                r=subprocess.run([sys.executable,'-u',__file__,'--worker'],stdout=log,stderr=subprocess.STDOUT,timeout=300)
                code=r.returncode
            except subprocess.TimeoutExpired:code=124
        save('status',dict(exit_code=code,wall_s=time.monotonic()-start,status='completed' if code==0 else 'stopped; no follow-on cases'))
        print(json.dumps(json.loads((OUT/'status.json').read_text())))
