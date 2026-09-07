"""Report the approved extension without altering the frozen 39-pair study."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from plot_matched_xs import coordinates

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/research/rph-xs-extension-01-2026-09-07'

def main():
    status=json.loads((DEST/'data/status.json').read_text())
    assert status['status']=='completed'
    new=[json.loads(f.read_text()) for f in sorted((DEST/'data').glob('*-matched.json'))]
    assert len(new)==4 and len({r['id'] for r in new})==4
    old=json.loads((ROOT/'docs/research/cjh-rph-matched-39-2026-09-07/report.json').read_text())['rows']
    rows=old+new
    assert len({r['id'] for r in rows})==43
    assert all(abs(r['match_error'])<r['match_tolerance'] for r in rows)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
        'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15,'font.size':12,
        'axes.linewidth':1.2,'xtick.direction':'in','ytick.direction':'in','xtick.top':True,
        'ytick.right':True,'legend.frameon':False,'svg.fonttype':'none','mathtext.default':'regular'})
    fig,axes=plt.subplots(1,2,figsize=(10,6.1))
    fig.subplots_adjust(left=.085,right=.96,bottom=.12,top=.82,wspace=.29)
    groups=[sorted([r for r in rows if r['flow_sccm']==50 and r['peak_C']==1800],key=lambda r:r['hold_s']),
        sorted([r for r in rows if r['peak_C']==1800 and r['hold_s']==.5],key=lambda r:r['flow_sccm'])]
    for ax,group,label in zip(axes,groups,['a  |  50 sccm; variable hot hold','b  |  0.50 s hot hold; variable flow']):
        for mode,marker,color in [('CJH','s','#444444'),('RPH','o','#70257d')]:
            ax.plot(*coordinates(group,mode),color=color,marker=marker,ms=6,mew=0,lw=1.8,label=mode)
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.04),ncol=2,fontsize=13)
        ax.text(.04,.95,label,transform=ax.transAxes,va='top',fontsize=10.5)
        ax.set(xlabel=r'CH$_4$ conversion (%)',ylabel=r'C$_2$H$_2$ selectivity (%)',xlim=(0,100),ylim=(0,65))
        ax.set_box_aspect(1);ax.xaxis.set_minor_locator(AutoMinorLocator(2));ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(which='major',length=6,width=1.2);ax.tick_params(which='minor',length=3,width=.9)
        added=[r for r in group if r in new]
        for r in added:
            x,y=coordinates([r],'RPH')
            ax.plot(x,y,marker='o',ms=10,mfc='none',mec='#70257d',mew=1.1,ls='none')
    fig.canvas.draw();checks=[]
    for ax in axes:
        bb=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        assert abs(bb.width/bb.height-1)<.01
        checks.append({'width_in':bb.width,'height_in':bb.height})
    renderer=fig.canvas.get_renderer()
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text():continue
        bb=t.get_window_extent(renderer)
        if bb.width and bb.height:assert bb.x0>=-1 and bb.y0>=-1 and bb.x1<=fig.bbox.width+1 and bb.y1<=fig.bbox.height+1,t.get_text()
    for ext in ['svg','png']:fig.savefig(DEST/f'conversion-selectivity-extension.{ext}',dpi=600,facecolor='white')
    table=[]
    anchor=next(r for r in old if r['id']=='Q50-T1800-h0.5')
    for r in [anchor]+new:
        table.append(dict(id=r['id'],flow_sccm=r['flow_sccm'],hold_s=r['hold_s'],X_pct=100*r['target_X'],
            CJH_T_C=r['CJH_T_C'],CJH_S_pct=coordinates([r],'CJH')[1][0],RPH_S_pct=coordinates([r],'RPH')[1][0],
            RPH_C2H2_Y_pct=r['RPH_yield_pct']['C2H2'],RPH_C6_Y_pct=r['RPH_yield_pct']['C6_total']))
    result={'completed_pairs':4,'wall_s':status['wall_s'],'rows':table,'raw_pairs':new,'figure_checks':checks}
    (DEST/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Higher-conversion pulse extension','',
        'Four new RPH points and their individually matched CJH states passed all configured checks. The original 39-pair report is unchanged.',
        '', '![Conversion and selectivity](conversion-selectivity-extension.svg)','',
        '| Flow sccm | Hot hold s | CH4 X % | Matched CJH C | CJH C2H2 S % | RPH C2H2 S % | RPH C2H2 Y C% | RPH total C6 Y C% |',
        '|---|---|---|---|---|---|---|---|']
    for r in table:lines.append('| '+' | '.join(f'{r[k]:.7g}' for k in ['flow_sccm','hold_s','X_pct','CJH_T_C','CJH_S_pct','RPH_S_pct','RPH_C2H2_Y_pct','RPH_C6_Y_pct'])+' |')
    lines+=['','The 50 sccm/0.50 s row is the existing anchor. Circles with outer rings mark new RPH points. Panel (a) varies hot hold at 50 sccm; panel (b) varies flow at 0.50 s hot hold. All RPH peaks are 1800 C, floor 450 C, period 1 s, rise 0.025 s and fall 0.10 s. Lines guide the eye. CJH temperature alone is adjusted per pair; feed, standard flow, volume and pressure remain identical within each pair.',
        '', 'S = 100 × 2 n(C2H2,out) / [n(CH4,in) − n(CH4,out)]. RPH uses cycle-integrated amounts and CJH steady flows. CO2 is also a carbon source, so this is methane-consumption-normalized selectivity without carbon-source attribution. Y uses total inlet CH4+CO2 carbon. Gas-phase C6 is not soot. No equal-power or physically validated reactor-volume claim.',
        '',f'Calculation time including controls and root searches: {status["wall_s"]:.3f} s. Regenerate with `python tools/openmkm_dynamic/report_rph_xs_extension.py`.']
    (DEST/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result['rows'],indent=2))

if __name__=='__main__':main()
