"""Small, bounded CH4/He temperature screen using the verified parcel worker."""
import json
import os
from pathlib import Path
import sys
from cantera_quickstart import ROOT, WORKER, MECH, digest, supervise

out=ROOT/'docs/research/parcel-temperature-screen-2026-09-10/results'
if out.exists():
    raise SystemExit('Results already exist. Inspect them before planning another attempt.')
out.mkdir(parents=True)
env=dict(os.environ,TZ='UTC0',LC_ALL='C',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
command=[sys.executable,'-u',str(WORKER),'--output',str(out),
         '--temperatures-c','1800','1200','1300','1400','1500','1600','1700',
         '--times-s','.001','.005','.02','.04','--refine-temperatures-c','1800']
(out/'launch.json').write_text(json.dumps(dict(command=command,worker_sha256=digest(WORKER),
    launcher_sha256=digest(Path(__file__)),mechanism_sha256=digest(MECH),timeout_s=300),indent=2)+'\n')
with (out/'execution.log').open('w') as log:
    status=supervise(command,env,log,300)
(out/'supervisor.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status))
if status['exit_code']:
    raise SystemExit(status['exit_code'])
brief=json.loads((out/'brief.json').read_text())
lines=['# CH4/He isothermal parcel screen','',
    'CH4 10 mol%, He 90 mol%; 1 atm; uniform prescribed gas temperature. Closed constant-pressure parcel; elapsed reaction time is reported below. No flow-through CSTR or heater model is used.',
    '', 'All cases passed carbon and mass checks. The 1800 C trajectory alone received paired refinement. Remaining temperatures are screening results.', '',
    '| Gas T (C) | Time (ms) | CH4 conversion (%) | C2H2 carbon yield (%) | C2H2 selectivity (%) | C6 carbon yield (%) |',
    '|---|---|---|---|---|---|']
for r in sorted(brief['rows'],key=lambda r:(r['T_C'],r['time_s'])):
    lines.append('| '+' | '.join(f'{v:.3f}' for v in [r['T_C'],r['time_s']*1000,r['X_CH4_pct'],r['Y_C2H2_carbon_pct'],r['S_C2H2_carbon_pct'],r['C6_carbon_yield_pct']])+' |')
(out.parent/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(brief))
