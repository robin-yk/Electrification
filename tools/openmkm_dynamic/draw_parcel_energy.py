"""Plot saved gas-only parcel energy results with matplotlib."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parents[2]/'docs/research/parcel-temperature-screen-2026-09-10/energy-pareto'
data=json.loads((out/'data.json').read_text())
rows,front=data['rows'],data['pareto']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(7,5.1))
for t,m in {1:'o',5:'s',20:'^',40:'D'}.items():
    subset=[r for r in rows if r['time_ms']==t]
    sc=ax.scatter([r['Y_C2H2_pct'] for r in subset],[r['eta_rxn_pct'] for r in subset],c=[r['T_C'] for r in subset],cmap='viridis',vmin=1200,vmax=1800,s=66,marker=m,edgecolor='white',linewidth=.7,label=f'{t} ms',zorder=3)
ax.plot([r['Y_C2H2_pct'] for r in front],[r['eta_rxn_pct'] for r in front],color='#333333',lw=1,zorder=2)
for i,r in enumerate(front):
    ax.annotate(f"{r['T_C']} °C, {r['time_ms']:g} ms",(r['Y_C2H2_pct'],r['eta_rxn_pct']),xytext=(-110,18+18*i),textcoords='offset points',fontsize=9,arrowprops={'arrowstyle':'-','color':'.45','lw':.6})
ax.set(xlabel='Acetylene carbon yield (%)',ylabel='Reaction heat / total gas heat (%)',xlim=(-2,100),ylim=(-1,max(r['eta_rxn_pct'] for r in rows)+15))
ax.legend(title='Reaction time',frameon=False,loc='upper left')
fig.colorbar(sc,ax=ax,label='Gas temperature (°C)',pad=.03)
ax.set_title('CH₄ 10% / He | 1 atm | inlet reference 25 °C',fontsize=11,pad=12)
fig.tight_layout()
fig.savefig(out/'pareto.png',dpi=200)
fig.savefig(out/'pareto.svg')
