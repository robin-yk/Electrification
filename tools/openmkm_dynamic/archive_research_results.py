"""Copy research outputs byte-for-byte and generate a verifiable inventory."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--destination", type=Path, required=True)
    args = ap.parse_args()
    dst = args.destination
    dst.mkdir(parents=True, exist_ok=True)
    names = ["gri-aramco-three-rph-pairs-2026-09-06.md",
             "low-cost-research-operations-2026-09-06.md"]
    for folder in ("three-rph-pairs-2026-09-06", "early-stop-validation-2026-09-06"):
        names += [str(p.relative_to(args.source)) for p in sorted((args.source / "data" / folder).rglob("*")) if p.is_file()]
    checksums = {}
    for name in names:
        src, target = args.source / name, dst / name
        raw = src.read_bytes()
        if target.exists() and target.read_bytes() != raw:
            raise RuntimeError("refuse to overwrite differing archive: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        checksums[name] = hashlib.sha256(raw).hexdigest()
        assert hashlib.sha256(target.read_bytes()).hexdigest() == checksums[name]
    rows = []
    for case in (6300012, 6000015, 8300048):
        for mech in ("gri", "aramco"):
            for grid in ("base", "refined"):
                name = f"data/three-rph-pairs-2026-09-06/{case}-{mech}-{grid}.json"
                row = dict(case=case, mechanism=mech, grid=grid, file=name)
                if (dst / name).exists():
                    r = json.loads((dst / name).read_text())
                    row.update(status="completed", converged=r["cycle_summary"]["converged"],
                               substeps=r["inputs"]["substeps_per_cycle"], sha256=checksums[name])
                else:
                    row.update(status="missing", reason="resume run timed out before result was written")
                rows.append(row)
    (dst / "checksums.json").write_text(json.dumps(checksums, indent=2) + "\n")
    (dst / "completion.json").write_text(json.dumps(dict(
        completed=sum(r["status"] == "completed" for r in rows), expected=len(rows), cases=rows,
        source_runs=[34075748186, 34077150687], early_stop_validation_run=34078455559), indent=2) + "\n")
    print(json.dumps(dict(archived_files=len(checksums), completed=sum(r["status"] == "completed" for r in rows))))


if __name__ == "__main__":
    main()
