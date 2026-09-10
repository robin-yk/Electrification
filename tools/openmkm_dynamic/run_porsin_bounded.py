"""Supervise the Porsin retry with a native-call-safe wall timeout."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/research/porsin-scoping-2026-09-10/retry-600s'
OUT.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
with (OUT / 'execution.log').open('w') as log:
    process = subprocess.Popen(
        [sys.executable, '-u', str(ROOT / 'tools/openmkm_dynamic/porsin_scoping.py')],
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
