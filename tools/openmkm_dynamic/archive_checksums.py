"""Generate or verify SHA256 inventory without altering raw artifacts."""
import argparse
import hashlib
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("directory", type=Path)
ap.add_argument("--verify", action="store_true")
a = ap.parse_args()
target = a.directory / "checksums.json"
actual = {str(p.relative_to(a.directory)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(a.directory.rglob("*")) if p.is_file() and p != target}
if a.verify:
    assert actual == json.loads(target.read_text()), "archive inventory mismatch"
else:
    target.write_text(json.dumps(actual, indent=2) + "\n")
print(f"{'Verified' if a.verify else 'Recorded'} {len(actual)} file checksums")
