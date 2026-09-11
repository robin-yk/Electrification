"""Two projections of the same four-objective nondominated records."""
import json, sys, importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'docs/research/four-objective-pareto-2026-09-10'
common=Path('/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-hold/joule-heating-2d-model/figures/plates-5in/scripts/common.py')
spec=importlib.util.spec_from_file_location('common',common);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.cm import ScalarMappable
rows=json.loads((O/'eligible-records.json').read_text());fronts=json.loads((O/'pareto.json').read_text())
checks=[]
for target in [1.,1.5,1.75]:
    pool='CH4/CO2 | CSTR | 90% lower radiation'
    s=next(s for s in fronts if s['pool']==pool and s['target_CO_C2H2']==target)
    bg=[r for r in rows if r['pool']==pool]; fg=s['pareto']
    fig=plt.figure(figsize=(10.8,6.0))
    axes=[fig.add_axes([.08,.23,.365,.657]),fig.add_axes([.565,.23,.365,.657])]
    norm=Normalize(0,.5,clip=True);cmap='viridis_r'
    for index,(ax,xkey,xlabel) in enumerate(zip(axes,['Y_C2H2_pct','cooling_W'],['C$_2$H$_2$ carbon yield (%)','Additional cooling duty (W)'])):
        ax.set_box_aspect(1)
        for mode,marker in [('CJH','o'),('RPH','^')]:
            b=[r for r in bg if r['mode']==mode]; f=[r for r in fg if r['mode']==mode]
            ax.scatter([r[xkey] for r in b],[r['C2H2_mmol_kJ'] for r in b],s=25,c='#d5d5d5',marker=marker,edgecolors='none',alpha=.65,zorder=1)
            ax.scatter([r[xkey] for r in f],[r['C2H2_mmol_kJ'] for r in f],s=100,c=[abs(r['CO_C2H2']-target) for r in f],norm=norm,cmap=cmap,marker=marker,edgecolors='none',zorder=3)
        ax.set_xlabel(xlabel);ax.set_ylabel('C$_2$H$_2$ production (mmol kJ$^{-1}$)')
        ax.set_ylim(-.015,.415);ax.set_yticks([0,.1,.2,.3,.4])
        ax.set_xlim((-2,52) if index==0 else (-3,65))
        c.minor(ax);c.letter(ax,'ab'[index],x=-.08,y=1.065)
    handles=[Line2D([],[],marker='o',color='none',markerfacecolor='#444',markeredgewidth=0,markersize=10,label='CJH'),Line2D([],[],marker='^',color='none',markerfacecolor='#444',markeredgewidth=0,markersize=10,label='RPH'),Line2D([],[],marker='o',color='none',markerfacecolor='#d5d5d5',markeredgewidth=0,markersize=7,label='All evaluated points')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.99),ncol=3)
    cbax=fig.add_axes([.32,.1,.4,.024]);cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cbax,orientation='horizontal',extend='max')
    cb.set_ticks([0,.25,.5]);cb.ax.tick_params(labelsize=11);cb.set_label('Absolute CO/C$_2$H$_2$ ratio error',fontsize=13)
    fig.canvas.draw();problems=c.figcheck(fig);assert not problems,problems
    sizes=[]
    for ax in axes:
        b=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted());assert abs(b.width/b.height-1)<.01
        sizes.append(dict(width_in=b.width,height_in=b.height,aspect=b.width/b.height))
    name=f'pareto-target-{target:g}'
    fig.savefig(O/(name+'.png'),dpi=600);fig.savefig(O/(name+'.svg'))
    checks.append(dict(name=name,canvas_in=[10.8,6],panel_allocation_in=[5,5],axes=sizes,figcheck=problems,pixels=[6480,3600],nondominated=len(fg)))
    plt.close(fig)
(O/'figure-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(O/'FIGURES.md').write_text('# Four-objective Pareto projections\n\n'+ '\n\n'.join(f'## Target CO/C2H2 = {t:g}\n\n![Pareto](pareto-target-{t:g}.png)' for t in [1,1.5,1.75])+ '\n\nBoth panels show the same four-objective Pareto set. Panel a projects yield against energy-specific production; panel b projects additional cooling against energy-specific production. Color gives absolute molar-ratio mismatch, with values above 0.5 at the darkest endpoint. Circles denote CJH and triangles RPH. Gray points show eligible archived records. A colored point can appear inferior in either two-dimensional projection while remaining nondominated in four dimensions. Coincident points overlap.\n\nCH4/CO2 CSTR archive; 90% lower radiation, imposed temperature histories retained. Cooling-system electricity is excluded. Operating conditions vary between records. Target ratio is an objective, not an enforced tolerance constraint. Each panel receives a 5-inch-square allocation plus shared legend and colorbar space. No new reaction evaluations.\n\nReproduce with `/usr/bin/python3 tools/openmkm_dynamic/draw_four_objective_pareto.py`.\n')
print(json.dumps(checks))
