"""Read artifacts and emit a bounded machine summary. No LLM/API calls."""
import argparse
import hashlib
import json
from pathlib import Path


def cache_key(inputs, mechanism_sha, solver_sha, tolerances):
    """Callers must include sampled waveform and closure in inputs, without rounding."""
    payload = dict(inputs=inputs, mechanism_sha=mechanism_sha,
                   solver_sha=solver_sha, tolerances=tolerances)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def digest(directory):
    directory = Path(directory)
    status = json.loads((directory / "status.json").read_text()) if (directory / "status.json").exists() else {"status": "partial"}
    rows = []
    for path in sorted(directory.glob("*-refined.json")):
        r = json.loads(path.read_text())
        a, s = r["carbon_audit"], r["cycle_summary"]
        carbon_in = a["carbon_in_kmol"]
        rows.append({"file": path.name, "converged": s["converged"],
                     "CH4_conversion": s["mean_ch4_conversion"],
                     "C2H2_carbon_yield": 2 * a["species_out_kmol"].get("C2H2", 0) / carbon_in,
                     "C6_carbon_yield": a["groups"]["C6"]["carbon_kmol"] / carbon_in,
                     "max_element_residual": max(abs(v["residual_fraction_of_in"]) for v in a["elements"].values())})
    return {"status": status, "refined_results": rows, "source_directory": str(directory)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("directory", type=Path)
    args = ap.parse_args()
    result = digest(args.directory)
    text = json.dumps(result, separators=(",", ":"))
    if len(text) > 6000:
        text = json.dumps({"status": result["status"], "refined_count": len(result["refined_results"]),
                           "source_directory": str(args.directory), "detail": "request one case explicitly"})
    print(text)
