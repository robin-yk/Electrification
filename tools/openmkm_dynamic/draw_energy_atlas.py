"""Five-inch energy-atlas panels with CO/acetylene ratio as color."""
import json,importlib.util,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,Normalize
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator
from PIL import Image
common=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-hold/joule-heating-2d-model/figures/plates-5in/scripts/common.py')
spec=importlib.util.spec_from_file_location('style',common);style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
out=Path(__file__).resolve().parents[2]/'docs/research/all-energy-atlas-2026-09-10'
rows=json.loads((out/'plot-data.json').read_text())
cases=json.loads((out/'case-table.json').read_text())
def fmt(v):
    return '—' if v is None else f'{v:.5g}' if isinstance(v,(int,float)) else str(v)
table=['# Plotted condition register','', 'Yield uses total inlet carbon. Heat fractions use the 298.15 K reaction-enthalpy reference. Exact sources and waveform segments are retained in case-table.json.','', '| ID | Mode | Feed family | Tmax (°C) | Flow (sccm) | Gas volume (cm³) | GHSV (h⁻¹) | C2H2 yield (%) | CO/C2H2 | Gas-only heat fraction (%) | Full-radiation fraction (%) | 90%-lower-radiation fraction (%) |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for c in cases:
    eta={r['scenario']:r['eta_rxn_pct'] for r in rows if r['id']==c['id']}
    values=[c.get(k) for k in ['id','mode','family','Tmax_C','flow_sccm','volume_cm3','GHSV_h_inverse','Y_C2H2_pct','CO_C2H2']]+[eta.get(s) for s in ['Gas only','Full radiation','90% lower radiation']]
    table.append('| '+' | '.join(map(fmt,values))+' |')
(out/'case-table.md').write_text('\n'.join(table)+'\n')
cmap=ListedColormap(plt.cm.viridis(np.linspace(.85,.1,256)))
norm=Normalize(vmin=0,vmax=5)
scenarios=['Gas only','Full radiation','90% lower radiation']
fig=plt.figure(figsize=(16.6,10.8));panels=[]
for row,family in enumerate(['CH4/CO2','CH4/He']):
    familydata=[r for r in rows if r['family']==family]
    ymax=max(5,math.ceil(max(r['eta_rxn_pct'] for r in familydata)/5)*5)
    ymin=min(0,math.floor(min(r['eta_rxn_pct'] for r in familydata)))
    for col,scenario in enumerate(scenarios):
        ax=fig.add_axes([(5*col+.9)/16.6,(5*(1-row)+.8)/10.8,3.8/16.6,3.8/10.8]);ax.set_box_aspect(1)
        data=[r for r in familydata if r['scenario']==scenario]
        for mode,marker in [('CJH','o'),('RPH','^')]:
            subset=[r for r in data if r['mode']==mode]
            known=[r for r in subset if r.get('CO_C2H2') is not None and r['CO_C2H2']>=0]
            unknown=[r for r in subset if r not in known]
            if known:ax.scatter([r['Y_C2H2_pct'] for r in known],[r['eta_rxn_pct'] for r in known],c=[r['CO_C2H2'] for r in known],cmap=cmap,norm=norm,s=100,marker=marker,edgecolors='none',zorder=3 if mode=='RPH' else 2,alpha=.8)
            if unknown:ax.scatter([r['Y_C2H2_pct'] for r in unknown],[r['eta_rxn_pct'] for r in unknown],color='#888888',s=100,marker=marker,edgecolors='none')
        ax.set(xlim=(0,100),ylim=(ymin,ymax*1.16),xlabel='C$_2$H$_2$ carbon yield (%)',ylabel='Reaction heat / input heat (%)')
        ax.xaxis.set_minor_locator(AutoMinorLocator(2));ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.text(.03,.97,'abcdef'[3*row+col],transform=ax.transAxes,va='top',fontweight='bold',fontsize=18)
        label=('CH$_4$/CO$_2$' if row==0 else 'CH$_4$/He')+' | '+scenario
        ax.text(.13,.97,label,transform=ax.transAxes,fontsize=11,va='top')
        counts={m:sum(r['mode']==m for r in data) for m in ['CJH','RPH']}
        ax.text(.97,.87,f"{counts['CJH']} CJH | {counts['RPH']} RPH",transform=ax.transAxes,ha='right',fontsize=11)
        fig.canvas.draw();b=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted());assert abs(b.width/b.height-1)<.01
        panels.append(dict(family=family,scenario=scenario,counts=counts,axes_inches=[b.width,b.height]))
cax=fig.add_axes([15.22/16.6,1.8/10.8,.18/16.6,6.5/10.8])
bar=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,extend='max',ticks=[0,1,2,3,4,5])
bar.set_label('CO/C$_2$H$_2$ molar ratio')
fig.text(.2/16.6,10.55/10.8,'298 K reaction-enthalpy reference | Fixed prescribed temperature histories | No heat recovery',fontsize=12)
fig.text(.2/16.6,10.27/10.8,'Full/reduced radiation: 0.57 emissivity, 6.08 cm$^2$ area, 25 °C surroundings | Gas-only panels exclude CFP storage',fontsize=11)
fig.legend(handles=[Line2D([],[],color='#444444',marker='o',linestyle='none',ms=10,mew=0,label='CJH'),Line2D([],[],color='#444444',marker='^',linestyle='none',ms=10,mew=0,label='RPH')],loc='upper right',bbox_to_anchor=(.96,.995),ncol=2,frameon=False)
problems=style.figcheck(fig);assert not problems,problems
fig.savefig(out/'atlas.png',dpi=600);fig.savefig(out/'atlas.svg')
with Image.open(out/'atlas.png') as im: pixels=im.size
assert pixels==(9960,6480),pixels
(out/'figure-check.json').write_text(json.dumps(dict(panel_allocation_inches=[5,5],canvas_inches=[16.6,10.8],panels=panels,png_pixels=pixels,dpi=600,figcheck=problems,color_scale='linear 0 to 5; ratios above 5 share the extended upper color; exact values retained'),indent=2)+'\n')
