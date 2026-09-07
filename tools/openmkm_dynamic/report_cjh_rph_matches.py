"""Collect only verified matched-conversion pairs, on one carbon basis."""
from pathlib import Path
from run_cjh_feed_ratio_01 import ROOT,read,write

def main():
    rows=[]
    for d in sorted((ROOT/'docs/research').glob('cjh-rph-match-*-2026-09-07/data')):
        for f in sorted(d.glob('*-matched.json')):
            r=read(f);assert abs(r['match_error'])<r['match_tolerance']
            r['matched_source']=str(f.relative_to(ROOT));rows.append(r)
    assert len({r['id'] for r in rows})==len(rows)
    rows.sort(key=lambda r:(r['flow_sccm'],r['peak_C'],r['hold_s']))
    dest=ROOT/'docs/research/cjh-rph-matched-39-2026-09-07';dest.mkdir(parents=True,exist_ok=True)
    write(dest/'report.json',dict(completed=len(rows),planned=39,rows=rows))
    lines=['# CJH versus RPH at matched methane conversion','',f'Completed verified matches: {len(rows)}/39.',
        '', 'For each pair, feed composition, standard flow, gas volume and pressure are identical. Only steady CJH gas temperature is varied. Carbon yields use total inlet carbon. RPH floor is 450 C and period is 1 s. C6 total includes every gas-phase species with six carbon atoms; it is not a soot prediction.',
        '', '| Flow sccm | RPH peak C | Hot hold s | CH4 X % | Matched CJH C | C2H2 CJH C% | C2H2 RPH C% | C6H6 CJH C% | C6H6 RPH C% | Total C6 CJH C% | Total C6 RPH C% | Low-X warning |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        c,p=r['CJH_yield_pct'],r['RPH_yield_pct']
        vals=[r['flow_sccm'],r['peak_C'],r['hold_s'],100*r['target_X'],r['CJH_T_C'],c['C2H2'],p['C2H2'],c['C6H6'],p['C6H6'],c['C6_total'],p['C6_total']]
        lines.append('| '+' | '.join(f'{v:.7g}' for v in vals)+' | '+str(r['low_conversion_warning'])+' |')
    lines+=['','Low-X warning means the RPH 400/800 phase-conversion difference exceeds one tenth of target conversion. Those trace-conversion comparisons require caution even when the CJH root is tightly matched. No blanket RPH selectivity advantage is assumed. CO, other C2 species, strict match errors and provenance are retained in report.json.']
    (dest/'REPORT.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))

if __name__=='__main__':main()
