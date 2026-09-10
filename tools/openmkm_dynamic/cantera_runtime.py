"""Mandatory lightweight environment gate, before importing Cantera."""
import importlib.metadata
import json
import locale
import os
import sys
import time

REQUIRED = {"TZ": "UTC0", "LC_ALL": "C", "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}

def prepare_runtime():
    try:
        version = importlib.metadata.version("cantera")
    except importlib.metadata.PackageNotFoundError:
        raise SystemExit("Cantera is missing. Use the verified Cantera 3.2.0 environment.")
    if version != "3.2.0":
        raise SystemExit(f"Cantera 3.2.0 required; found {version} in {sys.executable}. No calculation started.")
    os.environ.update(REQUIRED)
    if hasattr(time, "tzset"):
        time.tzset()
    locale.setlocale(locale.LC_ALL, "C")
    return {"cantera": version, "python": sys.executable, "environment": dict(REQUIRED)}

if __name__ == "__main__":
    print(json.dumps(prepare_runtime()))
