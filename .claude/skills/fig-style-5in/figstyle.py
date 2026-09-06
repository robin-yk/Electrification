"""Nature-type square 5 in panel style. See SKILL.md in this directory.

    import figstyle; figstyle.apply()
    fig, ax = figstyle.panel()
    figstyle.save(fig, "docs/figures/name")   # writes name.svg and name.png
"""
import numpy as np

RC = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'Liberation Sans', 'DejaVu Sans'],
    'axes.labelsize': 18, 'xtick.labelsize': 15, 'ytick.labelsize': 15,
    'legend.fontsize': 14, 'font.size': 14,
    'axes.linewidth': 1.2,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.top': True, 'ytick.right': True,
    'xtick.major.size': 6, 'ytick.major.size': 6,
    'xtick.minor.size': 3, 'ytick.minor.size': 3,
    'xtick.major.width': 1.2, 'ytick.major.width': 1.2,
    'xtick.minor.width': 0.9, 'ytick.minor.width': 0.9,
    'legend.frameon': False,
    'savefig.facecolor': 'white', 'figure.facecolor': 'white',
    'svg.fonttype': 'none', 'mathtext.default': 'regular',
}
LINE_W = 2.5
MARKER = 10
REF_W = 1.8
ANNOT_PT = 11
CH_COLOR, MW_COLOR = '#444444', '#c0392b'
REF2_COLOR = '#888888'


def apply():
    import matplotlib
    matplotlib.rcParams.update(RC)


def ordered_colors(n):
    """Light to dark viridis for an ordered series."""
    import matplotlib.pyplot as plt
    return plt.cm.viridis(np.linspace(0.85, 0.1, n))


def panel(minor=True):
    import matplotlib.pyplot as plt
    from matplotlib.ticker import AutoMinorLocator
    fig, ax = plt.subplots(figsize=(5, 5))
    if minor:
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    return fig, ax


def save(fig, stem, pad=0.4):
    fig.tight_layout(pad=pad)
    fig.savefig(f"{stem}.svg")
    fig.savefig(f"{stem}.png", dpi=600)
    return f"{stem}.svg", f"{stem}.png"
