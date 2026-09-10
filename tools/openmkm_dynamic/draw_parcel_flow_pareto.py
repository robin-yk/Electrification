"""Yield versus reaction-heat fraction with standard-flow GHSV labels."""
import json,importlib.util
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from PIL import Image
common=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-hold/joule-heating-2d-model/figures/plates-5in/scripts/common.py')
spec=importlib.util.spec_from_file_location('style',common);style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
out=Path(__file__).resolve().parents[2]/'docs/research/parcel-flow-screen-2026-09-10'
d=json.loads((out/'result.json').read_text());rows=d['rows'];volume=d['volume_cm3']
fig=plt.figure(figsize=(5,5.9))
# The lower five-inch square is the chart panel; the top strip holds notes.
ax=fig.add_axes([.87/5,.8/5.9,3.85/5,3.85/5.9]);ax.set_box_aspect(1)
ax.plot([r['Y_C2H2_pct'] for r in rows],[r['eta_rxn_pct'] for r in rows],'-o',color='#237e88',lw=2.5,ms=10,mew=0)
offsets=[(-8,-20),(8,7),(8,7),(0,12),(-7,12),(8,-15)]
ghsv=[]
for r,(dx,dy) in zip(rows,offsets):
    value=r['flow_sccm']*60/volume
    ghsv.append(dict(flow_sccm=r['flow_sccm'],GHSV_h_inverse=value))
    ax.annotate(f'{value/1000:.1f}',(r['Y_C2H2_pct'],r['eta_rxn_pct']),xytext=(dx,dy),textcoords='offset points',ha='center' if dx<=0 else 'left',fontsize=11)
ax.set(xlabel='C$_2$H$_2$ carbon yield (%)',ylabel='Reaction heat / input heat (%)',xlim=(0,100),ylim=(0,12))
ax.xaxis.set_minor_locator(AutoMinorLocator(2));ax.yaxis.set_minor_locator(AutoMinorLocator(2))
notes=[
    '1500 °C | CH$_4$ 10% / He | 1 atm',
    f'Gas volume: {volume:.3f} cm$^3$ | Radiation reduced by 90%',
    'Point labels: GHSV (10$^3$ h$^{-1}$)',
    'Standard flow: 0 °C, 1 atm | Inlet heat reference: 25 °C']
for y,label in zip([5.68,5.46,5.24,5.02],notes):
    fig.text(.1/5,y/5.9,label,fontsize=10,va='center')
fig.canvas.draw();b=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
assert abs(b.width/b.height-1)<.01
problems=style.figcheck(fig);assert not problems,problems
renderer=fig.canvas.get_renderer()
for t in fig.texts:
    bb=t.get_window_extent(renderer)
    assert bb.x0>=0 and bb.y0>=0 and bb.x1<=fig.bbox.x1 and bb.y1<=fig.bbox.y1,t.get_text()
fig.savefig(out/'flow-pareto-ghsv.png',dpi=600);fig.savefig(out/'flow-pareto-ghsv.svg')
with Image.open(out/'flow-pareto-ghsv.png') as im: assert im.size==(3000,3540)
(out/'flow-pareto-ghsv-check.json').write_text(json.dumps(dict(GHSV=ghsv,definition='standard inlet volumetric flow / fixed gas reaction volume',panel_inches=[5,5],note_strip_inches=.9,canvas_inches=[5,5.9],axes_inches=[b.width,b.height],figcheck=problems,png_pixels=[3000,3540],dpi=600),indent=2)+'\n')
