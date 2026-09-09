"""Resume only missing conditions with unchanged, verified solver sources."""
import sys,time,json,hashlib,subprocess
from pathlib import Path
import cjh_energy_pilot as solver
OUT=solver.ROOT/'docs/research/cjh-energy-six-2026-09-09'
JOBS=[(.65,400),(.8,100),(.8,200),(.8,400)]
def save(n,d):(OUT/(n+'.json')).write_text(json.dumps(d,indent=2)+'\n')
def validate():
    m=json.loads((OUT/'manifest.json').read_text())
    for path,digest in m['files'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
    for gate in ['anchor-gate','paired-gate']:
        assert json.loads((OUT/(gate+'.json')).read_text())['passed']
def worker():
    validate();solver.OUT=OUT
    for x,q in JOBS:
        name=f'ch4-{x:.2f}-Q{q}'
        assert not (OUT/(name+'.json')).exists(),'unexpected existing result'
        solver.run(name,T_C=1800,flow=q,ch4=x)
if __name__=='__main__':
    if '--worker' in sys.argv:worker()
    else:
        validate()
        save('resume-manifest',dict(jobs=JOBS,budget_s=300,
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             prior_manifest_sha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest(),
             commit=subprocess.check_output(['git','-C',str(solver.ROOT),'rev-parse','HEAD'],text=True).strip(),
             role='user-authorized completion of four missing fixed-pilot conditions; no BO acquisition'))
        t=time.monotonic()
        with (OUT/'resume.log').open('w') as log:
            try:code=subprocess.run([sys.executable,'-u',__file__,'--worker'],stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
            except subprocess.TimeoutExpired:code=124
        save('resume-status',dict(exit_code=code,wall_s=time.monotonic()-t,
             completed=[f'ch4-{x:.2f}-Q{q}' for x,q in JOBS if (OUT/f'ch4-{x:.2f}-Q{q}.json').exists()]))
        print((OUT/'resume-status.json').read_text())
