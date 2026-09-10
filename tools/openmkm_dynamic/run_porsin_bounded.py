"""Supervise the Porsin retry with a native-call-safe wall timeout."""
import json
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--temperature-c', type=int, default=1900)
args = parser.parse_args()
folder = 'retry-600s' if args.temperature_c == 1900 else f'T{args.temperature_c}-600s'
OUT = ROOT / 'docs/research/porsin-scoping-2026-09-10' / folder
if (OUT / 'supervisor.json').exists():
    raise SystemExit('Existing run preserved. Inspect its results before retrying.')
OUT.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
with (OUT / 'execution.log').open('w') as log:
    process = subprocess.Popen(
        [sys.executable, '-u', str(ROOT / 'tools/openmkm_dynamic/porsin_scoping.py'),
         '--temperature-c', str(args.temperature_c)],
        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    try:
        code = process.wait(timeout=600)
        outcome = 'completed' if code == 0 else 'failed'
    except subprocess.TimeoutExpired:
        process.kill()
        code = process.wait()
        outcome = 'timeout'
record = dict(outcome=outcome, exit_code=code, wall_s=time.monotonic()-started,
              cap_s=600)
(OUT / 'supervisor.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record), flush=True)
sys.exit(0 if outcome == 'completed' else 1)
