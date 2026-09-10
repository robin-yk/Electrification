"""Build the accepted flow-pilot comparison from saved higher-resolution results."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/research'
rows=[]
sources=[('rph-candidate-flow-pilot-2026-09-10-attempt02',50),('rph-candidate-flow-pilot-2026-09-10-flow100',100)]
if '--flow200' in sys.argv:
    sources.append(('rph-candidate-flow-pilot-2026-09-10-flow200',200))
for folder,flow in sources:
    assert json.loads((D/folder/f'A{flow}-gate.json').read_text())['passed']
    r=json.loads((D/folder/f'A{flow}-n8.json').read_text())
    for s in r['scenarios']:
        rows.append(dict(mode='RPH',flow_sccm=flow,Y=r['Y_C2H2_pct'],ratio=r['CO_C2H2'],qrx=r['Q_rxn_W'],**s))
c=next(c for c in json.loads((D/'all-energy-atlas-2026-09-10/case-table.json').read_text()) if c['id']=='ch4-0.65-Q400')
for factor in [1.,.1]:
    p=c['Q_gas_net_W']+factor*c['radiation_unscaled_W']
    rows.append(dict(mode='CJH',flow_sccm=c['flow_sccm'],Y=c['Y_C2H2_pct'],ratio=c['CO_C2H2'],qrx=c['Q_rxn_W'],radiation_remaining=factor,input_W=p,cooling_W=0.,eta_rxn_pct=100*c['Q_rxn_W']/p))
out=D/sources[-1][0]
(out/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# RPH flow pilot: accepted comparison','',
'Paired RPH resolutions passed the declared gates at each listed flow. The 50 sccm condition also reproduced the archived species results. See the gate files for errors and the status files for elapsed times.','',
'RPH uses the same archived gas-temperature waveform and composition at each flow. The CJH row is the existing compromise at a different composition and flow, not a matched-control pair. All rows use the same fixed gas volume. Carbon yield is normalized by total inlet carbon; CO/C2H2 is molar.','',
'| Mode | Flow (sccm) | Radiation remaining | C2H2 yield (%) | CO/C2H2 | Reaction heat (W) | Positive input (W) | Reaction heat / input (%) | Additional cooling (W) |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
    lines.append(f"| {r['mode']} | {r['flow_sccm']} | {r['radiation_remaining']:.1f} | {r['Y']:.3f} | {r['ratio']:.3f} | {r['qrx']:.3f} | {r['input_W']:.3f} | {r['eta_rxn_pct']:.3f} | {r['cooling_W']:.3f} |")
lines+=['','Read the yield, product ratio and reaction-heat fraction together when selecting a flow. The CJH row provides the existing design comparator.','',
'The radiation-reduction rows retain the imposed waveform. Additional cooling is listed separately and is not converted into cooling-system electricity. These rows are conditional thermal postprocessing, not a passive-insulation simulation.','',
'The redundant CVODES resets were removed before these runs. Paired resolutions completed with unchanged tolerances and sparse preconditioning. The atlas and manuscript remain unchanged.','',
'Regenerate with `python tools/openmkm_dynamic/report_rph_flow_pilot.py'+(' --flow200' if '--flow200' in sys.argv else '')+'`.']
(out/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
