"""Plot saved gas-only parcel energy results with matplotlib."""
import json
import importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.ticker import AutoMinorLocator
common=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-hold/joule-heating-2d-model/figures/plates-5in/scripts/common.py')
spec=importlib.util.spec_from_file_location('figure_common',common)
style=importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)
out=Path(__file__).resolve().parents[2]/'docs/research/parcel-temperature-screen-2026-09-10/energy-pareto'
data=json.loads((out/'data.json').read_text())
rows,front=data['rows'],data['pareto']
plt.rcParams.update({'axes.spines.top':True,'axes.spines.right':True})
# Five-inch square panel plus a separate 1.3-inch colorbar allocation.
fig=plt.figure(figsize=(6.3,5))
ax=fig.add_axes([.87/6.3,.78/5,3.85/6.3,3.85/5])
ax.set_box_aspect(1)
cax=fig.add_axes([5.04/6.3,.78/5,.18/6.3,3.85/5])
cmap=ListedColormap(plt.cm.viridis(np.linspace(.85,.1,256)))
for t,m in {1:'o',5:'s',20:'^',40:'D'}.items():
    subset=[r for r in rows if r['time_ms']==t]
    sc=ax.scatter([r['Y_C2H2_pct'] for r in subset],[r['eta_rxn_pct'] for r in subset],c=[r['T_C'] for r in subset],cmap=cmap,vmin=1200,vmax=1800,s=100,marker=m,edgecolors='none',linewidths=0,label=f'{t} ms',zorder=3)
ax.plot([r['Y_C2H2_pct'] for r in front],[r['eta_rxn_pct'] for r in front],color='#333333',lw=2.5,zorder=2)
for i,r in enumerate(front):
    y=36+5*i
    ax.text(45,y,f"{r['T_C']} °C, {r['time_ms']:g} ms",fontsize=11)
    ax.annotate('',(r['Y_C2H2_pct'],r['eta_rxn_pct']),xytext=(77,y-.5),arrowprops={'arrowstyle':'-','color':'.45','lw':.9})
ax.set(xlabel='C$_2$H$_2$ carbon yield (%)',ylabel='Reaction heat / gas heat (%)',xlim=(-2,100),ylim=(-1,46))
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
ax.legend(frameon=False,loc='upper left',handletextpad=.3,labelspacing=.4)
fig.colorbar(sc,cax=cax,label='Gas temperature (°C)',ticks=[1200,1400,1600,1800])
fig.canvas.draw()
b=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
checks=style.figcheck(fig)
assert abs(b.width/b.height-1)<.01,(b.width,b.height)
assert np.allclose(fig.get_size_inches(),[6.3,5])
assert not checks,checks
fig.savefig(out/'pareto.png',dpi=600)
fig.savefig(out/'pareto.svg')
from PIL import Image
with Image.open(out/'pareto.png') as im:
    assert im.size==(3780,3000),im.size
(out/'figure-check.json').write_text(json.dumps(dict(panel_allocation_inches=[5,5],colorbar_extra_width_inches=1.3,canvas_inches=[6.3,5],axes_inches=[b.width,b.height],axes_aspect=b.width/b.height,png_pixels=[3780,3000],dpi=600,figcheck=checks),indent=2)+'\n')
