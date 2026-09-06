---
name: fig-style-5in
description: Publication figure style, Nature-type square 5 in panel. Use for every matplotlib figure made for a manuscript or SI in this repository. Invoke with "fig style 5in" or whenever a figure is requested for publication.
---

# Figure style: Nature-type square panel (5 in)

Lookup material for publication figures. Non-normative. First used for the
titania dielectric-redox manuscript (Figure S17, TEA panels, 2026-09-01).

Two layers. The design identity in sections 1 to 4 (font, box, ticks, sizes,
colors, legend, margins, export) holds for every figure. Chart form is
per-figure judgment: axis scale (linear or log), points, lines, or bars, axis
ranges, tick placement, and annotation position follow the data span and the
comparison the figure makes, within field conventions.

Apply the rcParams with one line:

    import sys; sys.path.insert(0, ".claude/skills/fig-style-5in")
    import figstyle; figstyle.apply()          # rcParams from section 4
    fig, ax = figstyle.panel()                 # 5 x 5 in, minor ticks on
    figstyle.save(fig, "docs/figures/name")    # name.svg + name.png at 600 dpi

Environment note: the remote container has no Arial. `figstyle.py` lists
Liberation Sans after Helvetica; it is metric-compatible with Arial, so
layout is identical, and the SVG keeps Arial first in its font-family so
the text renders in Arial once opened on a machine that has it. Check the
PNG for glyph coverage (primes, degree sign) before delivery.

## 1. Common rules

- White background, Arial (fallback Helvetica, DejaVu Sans).
- Full rectangular box: all four spines visible.
- Ticks inward on all four sides; tick labels only on bottom and left.
- No grid. No title inside the panel unless required.
- Frameless legend.
- Markers without edge line (mew=0).
- Compact margins: tight_layout(pad=0.4 to 0.5).
- Export both SVG (svg.fonttype='none', text stays editable) and PNG at 600 dpi.
- Superscripts through mathtext with mathtext.default='regular', for example
  kg$^{-1}$. Do not use Unicode superscript minus (missing in Arial).
- Primed symbols (ε′, ε″) as plain Unicode text, not mathtext $\epsilon'$:
  the mathtext prime renders small and detached from the letter. Arial
  carries U+2032 and U+2033. Unicode subscript digits are missing in Arial,
  so chemical formulas stay in mathtext (Ti$_2$O$_3$).
- Escape a literal dollar sign as \$ in any label.
- Units in axis labels as (US\$ kg$^{-1}$), (°C), (μmol$_O$ g$^{-1}$).
- Log axes keep the conventional 10^n decade labels (matplotlib default).
  Set the axis limits at decade boundaries so at least two decade labels
  appear per axis; a log axis showing a single major label means the limits
  need widening, not the formatter replacing with scalar ticks.

## 2. Sizes (5in, the only preset)

| Item | Value |
|---|---|
| figsize | 5 x 5 in per panel |
| axis label | 18 pt |
| tick label | 15 pt |
| legend | 14 pt |
| annotation | 11 pt |
| axis linewidth | 1.2 pt |
| major / minor tick length | 6 / 3 pt |
| major / minor tick width | 1.2 / 0.9 pt |
| curve linewidth | 2.5 pt |
| marker size | 10 pt |
| reference dashed line | 1.8 pt |

Minor ticks: AutoMinorLocator(2) on both axes. Omit minor ticks when
matching an existing figure that has none.

## 3. Colors

- Ordered series (efficiency, temperature, power):
  plt.cm.viridis(np.linspace(0.85, 0.1, n)), light to dark with increasing value.
- Two-mode comparison: CH = #444444 square, MW = #c0392b circle.
- Reference line: black dashed; secondary reference: #888888 dotted.

## 4. matplotlib rcParams

    rcParams.update({
     'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
     'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15,'legend.fontsize':14,'font.size':14,
     'axes.linewidth':1.2,'xtick.direction':'in','ytick.direction':'in','xtick.top':True,'ytick.right':True,
     'xtick.major.size':6,'ytick.major.size':6,'xtick.minor.size':3,'ytick.minor.size':3,
     'xtick.major.width':1.2,'ytick.major.width':1.2,'xtick.minor.width':0.9,'ytick.minor.width':0.9,
     'legend.frameon':False,'savefig.facecolor':'white','figure.facecolor':'white',
     'svg.fonttype':'none','mathtext.default':'regular'})

## 5. Request template

    fig style 5in. SVG + 600 dpi PNG.
    Data:
    x = [...]
    y = { label: [...], ... }
    reference line: y = ..., label "..."
    markers/annotations: ...

## 6. Delivery

Save to the manuscript figure folder, view the PNG before delivery, then send
with SendUserFile.

Finish pass: inspect the rendered PNG and repair every fixable defect before
delivery, without asking. This covers a log axis left with a single decade
label (widen the limits to decade boundaries), detached primes, label
collisions, text overlapping a curve or marker, clipped text, and annotation
drift off its target. Re-render and re-inspect until clean. Deliver only the
clean version; do not deliver a flawed figure with the flaw listed as a
caveat.
