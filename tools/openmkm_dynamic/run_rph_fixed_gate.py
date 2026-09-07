"""First gate only: prescribed-temperature derivative and archived CJH limit."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
import cantera as ct
import run_cjh_feed_ratio_01 as base

class PrescribedTemperatureReactor(ct.ExtensibleIdealGasMoleReactor):
    temperature_slope = 0.0

    def after_eval(self, t, lhs, rhs):
        i = self.component_index("temperature")
        lhs[i] = 1.0
        rhs[i] = self.temperature_slope

def analytic(out):
    gas = ct.Solution("gri30.yaml")
    gas.TPX = 300, 101325, "N2:1"
    r = PrescribedTemperatureReactor(gas, energy="off", volume=base.volume_reference(), clone=True)
    r.temperature_slope = 100.0
    net = ct.ReactorNet([r])
    net.rtol = 1e-10
    net.atol = 1e-24
    mass, volume = r.mass, r.volume
    net.advance(0.1)
    assert abs(r.T-310) < 1e-6
    assert abs(r.mass/mass-1) < 1e-10
    assert abs(r.volume/volume-1) < 1e-12
    assert abs(r.phase.P/(101325*310/300)-1) < 1e-8
    base.write(out/"analytic.json",dict(T_K=r.T,pressure_Pa=r.phase.P,passed=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--worker",choices=["analytic","anchor"])
    a=ap.parse_args(); out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    if a.worker == "analytic": analytic(out);return
    if a.worker == "anchor":
        base.worker(out,"anchor",.5,tight=2,reactor_type=PrescribedTemperatureReactor)
        return
    ledger=base.read(base.ROOT/"docs/research/c2co-campaign-2026-09-07/budget.json")
    assert ledger["spent_s"]+ledger["reserved_s"]<=ledger["total_budget_s"]
    assert any(b["id"]=="rph-fixed-gate-01" and b["reserved_s"]==180 for b in ledger["batches"])
    base.write(out/"manifest.json",dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        hashes={str(p.relative_to(base.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(base.__file__),base.MECH]},
        cap_s=180,claim="Analytic closed inert ramp and reacting constant-temperature limit only; no pulse optimization."))
    start=time.monotonic(); done=[];active=None
    try:
        for active in ["analytic","anchor"]:
            with (out/(active+".log")).open("w") as f:
                subprocess.run([sys.executable,__file__,"--output-dir",str(out),"--worker",active],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=max(1,180-(time.monotonic()-start)))
            done.append(active)
        ref=base.read(base.ROOT/"docs/research/cjh-feed-ratio-02-2026-09-07/data/anchor.json")
        err=base.compare(ref["mol_per_feed_carbon"],base.read(out/"anchor.json")["mol_per_feed_carbon"])
        base.write(out/"gates.json",dict(analytic=True,archived_max_abs_error=err))
        base.write(out/"status.json",dict(status="completed",completed=done,wall_s=time.monotonic()-start))
    except Exception as e:
        base.write(out/"status.json",dict(status="stopped",active=active,completed=done,reason=str(e),wall_s=time.monotonic()-start));raise
if __name__=="__main__":main()
