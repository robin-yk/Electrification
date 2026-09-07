"""Plot matched conversion/selectivity from archived paired integrations."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'docs/research/cjh-rph-matched-39-2026-09-07'

def coordinates(rows, mode):
    # Yield is percent of total inlet carbon; methane is half of inlet carbon.
    x = [r['CJH_X'] if mode == 'CJH' else r['target_X'] for r in rows]
    return [100*v for v in x], [r[mode+'_yield_pct']['C2H2']/(0.5*v) for r,v in zip(rows,x)]

def main():
    data = json.loads((DEST/'report.json').read_text())
    rows = data['rows']
    assert data['completed'] == 39 and len(rows) == 39
    assert all(r['inputs']['feed'] == {'CH4':0.5,'CO2':0.5} for r in rows)
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
        'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15,'font.size':12,
        'axes.linewidth':1.2,'xtick.direction':'in','ytick.direction':'in',
        'xtick.top':True,'ytick.right':True,'legend.frameon':False,
        'svg.fonttype':'none','mathtext.default':'regular'})
    fig, axes = plt.subplots(1,2,figsize=(10,6.1))
    fig.subplots_adjust(left=.085,right=.985,bottom=.12,top=.82,wspace=.29)
    ax=axes[0]
    base=sorted([r for r in rows if r['flow_sccm']==50],key=lambda r:r['target_X'])
    ax.plot(*coordinates(base,'CJH'),color='#444444',marker='s',ms=4,mew=0,lw=1.6,label='CJH')
    for peak,color in zip([1200,1400,1600,1800],['#9c9e21','#35a88a','#31688e','#70257d']):
        group=sorted([r for r in base if r['peak_C']==peak],key=lambda r:r['hold_s'])
        ax.plot(*coordinates(group,'RPH'),color=color,marker='o',ms=6,mew=0,lw=1.8,label=f'RPH {peak} °C')
    ax.legend(loc='lower left',bbox_to_anchor=(-.05,1.04),ncol=2,fontsize=11,columnspacing=1,handlelength=1.8)
    ax.text(.04,.94,'a  |  50 sccm',transform=ax.transAxes,va='top')
    ax=axes[1]
    for hold,color in [(.1,'#31688e'),(.5,'#c0392b')]:
        group=sorted([r for r in rows if r['peak_C']==1800 and r['hold_s']==hold],key=lambda r:r['flow_sccm'])
        for mode,marker,ls in [('CJH','s','--'),('RPH','o','-')]:
            ax.plot(*coordinates(group,mode),color=color,marker=marker,ms=6,mew=0,lw=1.8,ls=ls,label=f'{mode}, {hold:.1f} s')
    ax.legend(loc='lower left',bbox_to_anchor=(-.05,1.04),ncol=2,fontsize=11,columnspacing=1,handlelength=1.8)
    ax.text(.04,.94,'b  |  RPH peak 1800 °C',transform=ax.transAxes,va='top')
    for ax in axes:
        ax.set(xlabel=r'CH$_4$ conversion (%)',ylabel=r'C$_2$H$_2$ selectivity (%)',xlim=(0,50),ylim=(0,65))
        ax.set_box_aspect(1)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2));ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(which='major',length=6,width=1.2)
        ax.tick_params(which='minor',length=3,width=.9)
    fig.canvas.draw()
    checks=[]
    for ax in axes:
        bb=ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        assert abs(bb.width/bb.height-1)<.01
        checks.append({'width_in':bb.width,'height_in':bb.height,'ratio':bb.width/bb.height})
    renderer=fig.canvas.get_renderer()
    for text in fig.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text(): continue
        bb=text.get_window_extent(renderer)
        if bb.width and bb.height:
            assert bb.x0>=-1 and bb.y0>=-1 and bb.x1<=fig.bbox.width+1 and bb.y1<=fig.bbox.height+1, text.get_text()
    for ext in ['svg','png']:
        fig.savefig(DEST/f'conversion-selectivity.{ext}',dpi=600,facecolor='white')
    derived=[]
    for r in rows:
        derived.append({'id':r['id'],'flow_sccm':r['flow_sccm'],'RPH_peak_C':r['peak_C'],'hold_s':r['hold_s'],
            'CJH_X_pct':100*r['CJH_X'],'RPH_X_pct':100*r['target_X'],
            'CJH_S_C2H2_pct':coordinates([r],'CJH')[1][0],
            'RPH_S_C2H2_pct':coordinates([r],'RPH')[1][0],
            'low_conversion_warning':r['low_conversion_warning']})
    (DEST/'conversion-selectivity.json').write_text(json.dumps({'panels':checks,'rows':derived},indent=2)+'\n')
    (DEST/'conversion-selectivity-caption.md').write_text('''# Conversion versus acetylene selectivity

![Matched conversion/selectivity](conversion-selectivity.svg)

Selectivity is 100 × 2 n(C2H2,out) / [n(CH4,in) − n(CH4,out)]. For RPH, amounts are integrated over the converged cycle; CJH uses steady flows. With equimolar CH4/CO2 feed, this equals the total-feed-carbon yield in percent divided by (0.5 × methane conversion as a fraction). This methane-consumption normalization does not establish the carbon provenance of C2H2 in a two-carbon-source feed.

(a) Fixed 50 sccm: CJH temperatures are matched individually to each RPH conversion. RPH curves vary hot hold from 0.025 to 0.50 s at each indicated peak temperature. (b) RPH peak 1800 °C: each curve varies flow from 50 to 1600 sccm at the indicated RPH hot hold; CJH dashed curves contain the corresponding individually matched steady states. The 0.50 s series includes 1215.743353 sccm. Lines guide the eye; no new integration or fitted selectivity curve is introduced. All 39 pairs are included in panel (a) or (b); their overlap is intentional.

Both panels retain the fixed gas volume, equimolar undiluted feed and 1 atm pressure. RPH floor 450 °C, period 1 s, rise 0.025 s and fall 0.10 s. The three flagged low-conversion points remain in the figure but are not evidence of a resolved trace-selectivity advantage. This is a prescribed gas-temperature comparison, not an equal-power comparison. Full paired values and warnings are in conversion-selectivity.json.

Regenerate with `python tools/openmkm_dynamic/plot_matched_xs.py` after regenerating the matched report.
''')
    print(json.dumps({'completed':len(rows),'panels':checks}))

if __name__=='__main__':main()
