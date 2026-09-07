"""Two-run diagnostic only; no downstream feed ratios."""
import json, subprocess, sys, time
from pathlib import Path
from run_cjh_feed_ratio_01 import ROOT,write,read,compare,REF
out=ROOT/'out/cjh-small-volume-diagnostic';out.mkdir(parents=True,exist_ok=True)
ledger=read(ROOT/'docs/research/c2co-campaign-2026-09-07/budget.json')
assert ledger['spent_s']+ledger['reserved_s']<=3600
assert any(b['id']=='cjh-small-volume-diagnostic' and b['reserved_s']==140 for b in ledger['batches'])
start=time.monotonic();results=[]
try:
    for name,mode in [('nominal',0),('volume-scaled-atol',2)]:
        with (out/(name+'.log')).open('w') as log:
            r=subprocess.run([sys.executable,str(ROOT/'tools/openmkm_dynamic/run_cjh_feed_ratio_01.py'),
                '--output-dir',str(out),'--worker',name,'0.5',str(mode),'0'],
                stdout=log,stderr=subprocess.STDOUT,timeout=min(60,140-(time.monotonic()-start)))
        results.append(dict(name=name,returncode=r.returncode))
        if r.returncode==0:
            results[-1]['archive_max_abs']=compare(read(REF)['mol_per_feed_carbon'],read(out/(name+'.json'))['mol_per_feed_carbon'])
finally:
    write(out/'status.json',dict(results=results,wall_s=time.monotonic()-start,
       purpose='Diagnose absolute mole tolerances at small volume; not a feed-ratio batch',
       commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
