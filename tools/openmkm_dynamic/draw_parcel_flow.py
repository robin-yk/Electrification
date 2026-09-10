"""Nature five-inch panels for the fixed-volume flow pilot."""
import json,importlib.util
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
common=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-hold/joule-heating-2d-model/figures/plates-5in/scripts/common.py')
spec=importlib.util.spec_from_file_location('style',common);style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
out=Path(__file__).resolve().parents[2]/'docs/research/parcel-flow-screen-2026-09-10'
d=json.loads((out/'result.json').read_text());rows=d['rows'];x=[r['flow_sccm'] for r in rows]
fig=plt.figure(figsize=(10,5));dimensions=[]
for i,(key,label) in enumerate([('Y_C2H2_pct','C$_2$H$_2$ carbon yield (%)'),('C2H2_mmol_kJ','C$_2$H$_2$ per input heat (mmol kJ$^{-1}$)')]):
    ax=fig.add_axes([(i*5+.9)/10,.8/5,3.85/10,3.85/5]);ax.set_box_aspect(1)
    ax.plot(x,[r[key] for r in rows],'-o',color='#237e88',lw=2.5,ms=10,mew=0)
    ax.set_xscale('log');ax.set_xlim(10,10**__import__('math').ceil(__import__('math').log10(max(x))))
    ax.set_xlabel('Total feed rate (sccm)');ax.set_ylabel(label)
    ax.set_ylim(0,max(r[key] for r in rows)*1.22)
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.text(.03,.95,'ab'[i],transform=ax.transAxes,fontsize=18,fontweight='bold',va='top')
    if i==1:
        peak=max(rows,key=lambda r:r[key])
        ax.text(peak['flow_sccm'],peak[key]*1.10,f"{peak['flow_sccm']} sccm",ha='center',fontsize=11)
    fig.canvas.draw();b=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted());dimensions.append([b.width,b.height]);assert abs(b.width/b.height-1)<.01
problems=style.figcheck(fig);assert not problems,problems
fig.savefig(out/'flow.png',dpi=600);fig.savefig(out/'flow.svg')
from PIL import Image
with Image.open(out/'flow.png') as im: assert im.size==(6000,3000)
(out/'figure-check.json').write_text(json.dumps(dict(panel_inches=[5,5],canvas_inches=[10,5],axes_inches=dimensions,figcheck=problems,png_pixels=[6000,3000],dpi=600),indent=2)+'\n')
