"""Gas-only enthalpy accounting for saved CH4/He parcel compositions."""
import os
for k,v in {'TZ':'UTC0','LC_ALL':'C','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}.items(): os.environ[k]=v
import json
import hashlib
from pathlib import Path
import time
import numpy as np
import cantera as ct
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'docs/research/parcel-temperature-screen-2026-09-10/results'
OUT=SRC.parent/'energy-pareto'
OUT.mkdir(exist_ok=True)
started=time.monotonic()
mech=ROOT/'tools/cantera/mechanisms/aramco20.yaml'
gas=ct.Solution(str(mech))
gas.TPX=298.15,101325,{'CH4':1,'HE':9}
# Basis: one mol CH4 plus nine mol He. Molecular weights in g/mol.
mass_g=10*gas.mean_molecular_weight
n_in=10*gas.X.copy()
h_in=gas.partial_molar_enthalpies/1000
H_in=float(n_in@h_in)
sources={}
rows=[]
for T in range(1200,1801,100):
    source=SRC/f'T{T}-{"tight" if T==1800 else "standard"}.json'
    sources[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
    for r in json.loads(source.read_text())['rows']:
        gas.TPX=298.15,101325,r['mole_fractions']
        n_out=gas.X*(mass_g/gas.mean_molecular_weight)
        H_out_ref=float(n_out@(gas.partial_molar_enthalpies/1000))
        qrx=H_out_ref-H_in
        gas.TP=T+273.15,101325
        H_out_hot=float(n_out@(gas.partial_molar_enthalpies/1000))
        qsens=H_out_hot-H_out_ref
        qtotal=H_out_hot-H_in
        assert abs(qtotal-qrx-qsens)<1e-6 and qtotal>0
        # Independent heat path: heat the feed, then react isothermally.
        qpreheat=float(n_in@(gas.partial_molar_enthalpies/1000))-H_in
        qreaction_hot=float((n_out-n_in)@(gas.partial_molar_enthalpies/1000))
        assert abs(qtotal-qpreheat-qreaction_hot)<1e-6
        for element in gas.element_names:
            a=np.array([gas.n_atoms(s,element) for s in gas.species_names])
            assert abs(float((n_out-n_in)@a))<1e-6
        he=gas.species_index('HE')
        qhe=float(n_out[he]*(gas.partial_molar_enthalpies[he]/1000-h_in[he]))
        rows.append(dict(T_C=T,time_ms=r['time_s']*1000,Y_C2H2_pct=r['Y_C2H2_carbon_pct'],
            X_CH4_pct=r['X_CH4_pct'],Q_rxn_kJ_per_mol_CH4=qrx/1000,
            Q_sensible_kJ_per_mol_CH4=qsens/1000,Q_He_kJ_per_mol_CH4=qhe/1000,
            Q_gas_kJ_per_mol_CH4=qtotal/1000,eta_rxn_pct=100*qrx/qtotal,
            C2H2_mmol_per_kJ=n_out[gas.species_index('C2H2')]*1e6/qtotal,
            preheat_kJ_per_mol_CH4=qpreheat/1000,isothermal_reaction_kJ_per_mol_CH4=qreaction_hot/1000))
for r in rows:
    r['pareto']=not any(s['Y_C2H2_pct']>=r['Y_C2H2_pct'] and s['eta_rxn_pct']>=r['eta_rxn_pct'] and
        (s['Y_C2H2_pct']>r['Y_C2H2_pct'] or s['eta_rxn_pct']>r['eta_rxn_pct']) for s in rows)
front=sorted([r for r in rows if r['pareto']],key=lambda r:r['Y_C2H2_pct'])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(7,5.1))
markers={1:'o',5:'s',20:'^',40:'D'}
for t,m in markers.items():
    data=[r for r in rows if r['time_ms']==t]
    sc=ax.scatter([r['Y_C2H2_pct'] for r in data],[r['eta_rxn_pct'] for r in data],c=[r['T_C'] for r in data],
        cmap='viridis',vmin=1200,vmax=1800,s=66,marker=m,edgecolor='white',linewidth=.7,label=f'{t} ms',zorder=3)
ax.plot([r['Y_C2H2_pct'] for r in front],[r['eta_rxn_pct'] for r in front],color='#333333',lw=1,zorder=2)
for i,r in enumerate(front):
    ax.annotate(f"{r['T_C']} °C, {r['time_ms']:g} ms",(r['Y_C2H2_pct'],r['eta_rxn_pct']),
        xytext=(-105,15+18*i),textcoords='offset points',fontsize=9,arrowprops={'arrowstyle':'-','color':'.45','lw':.6})
ax.set(xlabel='Acetylene carbon yield (%)',ylabel='Reaction heat / total gas heat (%)',xlim=(-2,100),ylim=(-1,50))
ax.legend(title='Reaction time',frameon=False,loc='upper left')
fig.colorbar(sc,ax=ax,label='Gas temperature (°C)',pad=.03)
ax.set_title('CH₄ 10% / He | 1 atm | inlet reference 25 °C',fontsize=11,pad=12)
fig.tight_layout()
fig.savefig(OUT/'pareto.png',dpi=200)
fig.savefig(OUT/'pareto.svg')
(OUT/'data.json').write_text(json.dumps(dict(rows=rows,pareto=front,source_sha256=sources,
    mechanism_sha256=hashlib.sha256(mech.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    cantera=ct.__version__,wall_s=time.monotonic()-started),indent=2)+'\n')
lines=['# Gas-only energy Pareto for CH4/He','',
    'Basis: one mol CH4 plus nine mol He at 298.15 K and 1 atm. Outlet compositions are reused from the isothermal parcel screen. No new reaction integration is performed.',
    '', 'Q_rxn = H_out(298.15 K) - H_in(298.15 K); Q_sensible = H_out(T) - H_out(298.15 K); Q_gas = Q_rxn + Q_sensible. The reaction fraction uses net reaction enthalpy referenced to 298.15 K. It includes all gaseous products. Heater heat storage, radiation, other device losses, and heat recovery are excluded.',
    '', 'Total heat also equals feed preheating plus isothermal reaction enthalpy at the reaction temperature. Both paths and elemental balances were checked. A point is Pareto-efficient if no sampled point has both greater or equal acetylene yield and greater or equal reaction-heat fraction, with one strict improvement. Only 1800 C samples have individual paired refinement.',
    '', '![Energy Pareto](pareto.png)','',
    '| T (C) | Time (ms) | C2H2 yield (%) | Reaction heat fraction (%) | Gas heat (kJ/mol CH4) | C2H2 (mmol/kJ) | Pareto |',
    '|---|---|---|---|---|---|---|']
for r in rows:
    lines.append(f"| {r['T_C']} | {r['time_ms']:g} | {r['Y_C2H2_pct']:.3f} | {r['eta_rxn_pct']:.3f} | {r['Q_gas_kJ_per_mol_CH4']:.3f} | {r['C2H2_mmol_per_kJ']:.3f} | {r['pareto']} |")
lines+=['','Reproduce: `/Users/robin_yeonsu/cantera-env/bin/python tools/openmkm_dynamic/parcel_energy_pareto.py` from the repository root.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(pareto=front,best_mmol_per_kJ=max(rows,key=lambda r:r['C2H2_mmol_per_kJ']),wall_s=time.monotonic()-started)))
