"""Bounded, cached entry point for the verified CH4/He parcel example."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / 'tools/openmkm_dynamic/porsin_scoping.py'
MECH = ROOT / 'tools/cantera/mechanisms/aramco20.yaml'
REFERENCE = ROOT / 'docs/research/porsin-scoping-2026-09-10/retry-600s/tight.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def supervise(command, env, log, timeout):
    started = time.monotonic()
    p = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        code = p.wait(timeout=timeout)
        outcome = 'completed' if code == 0 else 'failed'
    except subprocess.TimeoutExpired:
        p.kill()
        code = p.wait()
        outcome = 'timeout'
    return dict(outcome=outcome, exit_code=code, wall_s=time.monotonic()-started)

def main():
    from cantera_runtime import prepare_runtime
    prepare_runtime()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-env', action='store_true')
    parser.add_argument('--temperatures-c', type=int, nargs='+', default=[1900, 1800])
    parser.add_argument('--timeout-s', type=int, default=600)
    args = parser.parse_args()
    if not 1 <= args.timeout_s <= 600:
        parser.error('Use a 1 to 600 second cap.')
    if len(args.temperatures_c)>2 or len(set(args.temperatures_c))!=len(args.temperatures_c):
        parser.error('This quickstart accepts at most two distinct temperatures, not a sweep.')
    try:
        version = importlib.metadata.version('cantera')
    except importlib.metadata.PackageNotFoundError:
        raise SystemExit('Cantera is absent from this interpreter. See the wiki quickstart installation section.')
    env = dict(os.environ, TZ='UTC0', LC_ALL='C', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    identity = dict(python=sys.version, executable=sys.executable, cantera=version,
                    temperatures_C=args.temperatures_c, mechanism_sha256=digest(MECH),
                    worker_sha256=digest(WORKER), launcher_sha256=digest(Path(__file__)),
                    reference_sha256=digest(REFERENCE),
                    env={k:env[k] for k in ('TZ','LC_ALL','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')})
    if args.check_env:
        print(json.dumps(identity, indent=2)); return
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    base = ROOT / 'docs/research/cantera-quickstart-2026-09-10' / key
    base.mkdir(parents=True, exist_ok=True)
    for candidate in sorted(base.glob('attempt-*')):
        seal = candidate / 'cache.json'
        if seal.exists():
            saved = json.loads(seal.read_text())
            if saved['identity']==identity and all((candidate/n).is_file() and digest(candidate/n)==h for n,h in saved['outputs'].items()):
                print(json.dumps(dict(cache_hit=True, output=str(candidate), brief=json.loads((candidate/'brief.json').read_text())))); return
    attempt = 1
    while (base/f'attempt-{attempt:03d}').exists(): attempt += 1
    out = base/f'attempt-{attempt:03d}'
    out.mkdir()
    (out/'launch.json').write_text(json.dumps(identity,indent=2)+'\n')
    with (out/'execution.log').open('w') as log:
        record = supervise([sys.executable,'-u',str(WORKER),'--output',str(out),
                             '--temperatures-c',*[str(t) for t in args.temperatures_c]], env, log, args.timeout_s)
    (out/'supervisor.json').write_text(json.dumps(record,indent=2)+'\n')
    if record['outcome']!='completed':
        print(json.dumps(dict(output=str(out),**record)))
        raise SystemExit(1)
    brief=json.loads((out/'brief.json').read_text())
    if brief['numerical_gate']!='passed': raise SystemExit('Missing numerical acceptance')
    outputs={p.name:digest(p) for p in out.iterdir() if p.is_file()}
    (out/'cache.json').write_text(json.dumps(dict(identity=identity,outputs=outputs),indent=2)+'\n')
    print(json.dumps(dict(cache_hit=False,output=str(out),brief=brief,**record)))

if __name__=='__main__':
    main()
