"""Verify actual outlet ratios at deterministic interpolated feed proposals."""
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/research/rph-yield-grid-2026-09-07/feed-target-01'
def read(p):return json.loads(p.read_text())
def main():
    s=read(D/'status.json');m=read(D/'manifest.json')
    for p,h in m['hashes'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    rows=[]
    for idx in s['completed']:
        hi=read(D/str(idx)/'n800.json');lo=read(D/str(idx)/'n400.json')
        a=hi['mol_per_feed_carbon'];b=lo['mol_per_feed_carbon']
        err=max(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b));assert err<1e-4
        target=m['targets'][idx];ratio=a['CO']/a['C2H2'];delta=ratio/target-1
        assert abs(hi['inputs']['feed']['CH4']-m['fractions'][idx])<1e-12
        rows.append(dict(target=target,feed_CH4_pct=100*m['fractions'][idx],ratio=ratio,
            relative_error_pct=100*delta,within_2pct=abs(delta)<=.02,within_5pct=abs(delta)<=.05,
            within_10pct=abs(delta)<=.1,C2H2_Y_pct=200*a['C2H2'],CO_Y_pct=100*a['CO'],
            C2H2_g_gCFP_h=hi['product_g_per_g_CFP_h']['C2H2'],phase_error=err,
            final_cycle=hi['history'][-1],source=str((D/str(idx)/'n800.json').relative_to(ROOT))))
    report=dict(status=s,rows=rows,scope='Fixed-waveform composition-only baseline; not yield optimization.')
    (D/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Directly verified feed-ratio proposals','',
        '1800 C peak, 450 C floor, 0.80 s hold, 1 s period, 0.025/0.10 s rise/fall, 50 sccm, 1 atm, 0.009228077898 cm3. Undiluted CH4/CO2. Total inlet carbon yield basis; 0.0288 g CFP productivity basis. Ratios use cycle-integrated outlet amounts.', '',
        '| Target C2H2:CO | CH4 feed (%) | Actual CO/C2H2 | Relative error (%) | C2H2 carbon yield (%) | CO carbon yield (%) | Within 2% |',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in rows:lines.append(f"| 1:{r['target']:g} | {r['feed_CH4_pct']:.5f} | {r['ratio']:.5f} | {r['relative_error_pct']:.3f} | {r['C2H2_Y_pct']:.5f} | {r['CO_Y_pct']:.5f} | {r['within_2pct']} |")
    lines+=['',f"Calculation time: {s['wall_s']:.3f} s. Status: {s['status']}.", '',
        'Accepted ratio matches are fixed-waveform baseline observations, not exact roots or constrained yield optima. Tolerance bands are design assumptions. No Bayesian selection was used.', '',
        'Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_feed_targets.py`.']
    (D/'REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
