"""Re-score accepted raw observations without reaction integration or GP fitting."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / 'docs/research/rph-yield-grid-2026-09-07'
OUT = C / 'ratio-scenarios-01'

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inventories = [(C/'observations.json', 'points'),
                   (C/'hot-boundary-02/report.json', 'rows'),
                   (C/'bo-03/observations-for-next-fit.json', 'rows')]
    rows = {}
    for file, key in inventories:
        for item in read(file)[key]:
            source = ROOT / item['source']
            assert sha(source) == item['sha256'], source
            raw = read(source)
            i = raw['inputs']
            assert i['feed'] == {'CH4': .5, 'CO2': .5}
            amounts = raw['mol_per_feed_carbon']
            a, co = amounts.get('C2H2', 0), amounts.get('CO', 0)
            assert a > 0 and co >= 0
            row = dict(source=item['source'], sha256=sha(source), inputs=i,
                       C2H2_Y_pct=200*a, CO_Y_pct=100*co,
                       CO_per_C2H2=co/a,
                       C2H2_g_gCFP_h=raw['product_g_per_g_CFP_h'].get('C2H2', 0),
                       CO_g_gCFP_h=raw['product_g_per_g_CFP_h'].get('CO', 0),
                       peak_C=max(s[2] for s in i['segments'])-273.15,
                       hold_s=i['segments'][1][0], flow_sccm=i['flow_sccm'])
            rows[item['source']] = row
    values = list(rows.values())
    # Prefer the latest accepted record for identical physical inputs.
    unique = {}
    for row in values:
        key = json.dumps(row['inputs'], sort_keys=True)
        unique[key] = row
    values = list(unique.values())
    scenarios = []
    for tolerance in [.02, .05, .10]:
        for target in [1, 1.5, 1.75]:
            feasible = [r for r in values if abs(r['CO_per_C2H2']/target-1) <= tolerance]
            scenarios.append(dict(target_CO_per_C2H2=target, relative_tolerance=tolerance,
                count=len(feasible), best=max(feasible, key=lambda r:r['C2H2_Y_pct']) if feasible else None,
                nearest=min(values,key=lambda r:abs(r['CO_per_C2H2']/target-1))))
    best = max(values,key=lambda r:r['C2H2_Y_pct'])
    report = dict(scope='Accepted equimolar fixed-volume RPH inventory, not all historical reactor models.',
        operation='Postprocessing only; no constrained BO performed.',
        ratio_definition='Cycle-integrated N_CO/N_C2H2 = 2 Y_CO/Y_C2H2.',
        tolerance_status='Design scenarios; tolerances are not literature optima.',
        inventory_hashes={str(p.relative_to(ROOT)):sha(p) for p,_ in inventories},
        accepted_sources=len(rows), unique_conditions=len(values), incumbent=best,
        scenarios=scenarios, rows=values)
    OUT.mkdir(exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Acetylene and CO ratio scenarios from existing RPH data','',
        f'{len(values)} unique accepted equimolar conditions. No new reaction integration or constrained optimization.', '',
        'Reproduce: `python3 tools/openmkm_dynamic/summarize_rph_ratio_scenarios.py`.', '',
        'Ratio is cycle-integrated CO/C2H2 mol/mol. Carbon yields use total inlet carbon. Relative tolerance is a design choice, not a reported literature optimum.', '',
        '| Target C2H2:CO | Tolerance | Accepted matches | Best sampled C2H2 carbon yield (%) | Actual CO/C2H2 | Peak (C) | Hold (s) | Flow (sccm) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for s in scenarios:
        b=s['best']
        tail=(f"{b['C2H2_Y_pct']:.5f} | {b['CO_per_C2H2']:.5f} | {b['peak_C']:.2f} | {b['hold_s']:.4f} | {b['flow_sccm']:.3f}" if b else 'none | n/a | n/a | n/a | n/a')
        lines.append(f"| 1:{s['target_CO_per_C2H2']:g} | {100*s['relative_tolerance']:g}% | {s['count']} | {tail} |")
    lines += ['',f"Unconstrained incumbent: {best['C2H2_Y_pct']:.5f}% C2H2 carbon yield; CO/C2H2 = {best['CO_per_C2H2']:.5f} mol/mol.", '',
        'A missing match means this inventory does not cover the ratio band, not that the band is chemically inaccessible. Best sampled matches are not constrained optima. Feed composition is fixed at CH4:CO2 = 1:1 in these data. Raw-file hashes, inputs, productivity, and nearest points for empty bands are retained in report.json.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
