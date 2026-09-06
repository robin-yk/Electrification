# The C2 pulse question, asked of the mechanism

## Why this document exists

`PREMISE-ARAMCO.md` ends with the reactor picture open: no model in this
repository reproduces the paper's absolute conversions, and `RUNCARD-BL.md`
records that the two candidate pictures bracket the data with a gap that
only flow information could close. That is a statement about the device.
The pulse question is a statement about the chemistry, and it can be asked
without settling the device: on a prescribed temperature history, does a
pulse protect the C2 intermediate against the C3+ sink better than a
steady element that reaches the same conversion? Every number below is a
uniform-temperature CSTR on the S1f-calibrated element trajectory, and is
quoted as the mechanism's ranking of drives, not as the device's output.

## Closure correction, 2026-09-05, and the rerun of 2026-09-06

The march used before 2026-09-06 swapped methane for products at each
temperature step (`run_cstr_case.step_temperature`; the README's
Formulation list says what it did and how it was found). On 2026-09-06
the author approved a rerun of every case in the three round tables below
on the corrected march, with `--min-cycles 4` so the cycle map stops once
the boundary residual is below 1e-7 (all thirteen cases converged at
cycle 4, the 0.2 s period at cycle 8). The round tables and the run card
now carry the corrected numbers; reproduce them with

    python3 tools/openmkm_dynamic/run_pulse_c2.py compare

The matched-comparison table in the next section is on the CH4/CO2 feed
(`data/s9/conditions-siop`) and was not part of the approved rerun. Its
pulse columns still overstate conversion by about a fifth and acetylene
by about a quarter; the corrected tau 0.2 s conversion is 16.5 percent
(README, Formulation), the rest of that table is `미확인` until those
three cases are rerun. The flux section was rerun on 2026-09-05 and is
correct.

What the rerun changed: every pulse conversion fell by about a fifth
(anchor 22.0 to 17.3 percent) and pulse benzene rose by two to five
points, so each pulse-to-steady benzene ratio moved up (anchor 0.36 to
0.41 on the dense steady grid below). No ranking reversed. The three claims, restated on corrected
numbers, are at the end of each round below.

## Matched comparison: the fair test

Selectivity to an intermediate falls with conversion in any series network,
so a pulse compared with a steady point at a different conversion reads
partly as a slide along that curve. `pulse_vs_steady.py` therefore finds,
for each pulsed case, the steady temperature at the same feed and residence
time that reaches the same methane conversion, and prints both slates.

    python3 tools/openmkm_dynamic/pulse_vs_steady.py \
        --steady tools/openmkm_dynamic/data/lump/steady-cstr-ch4co2.json \
        tools/openmkm_dynamic/data/s9/conditions-siop/*.json

On the CH4/CO2 feed with the SI operating point (peak 1800 C, 1 Hz, 5
percent duty), AramcoMech 2.0:

| tau, s | X, % | steady needs, C | S_C6H6 steady / pulse, % | S_C2H2 steady / pulse, % |
|---|---|---|---|---|
| 0.05 | 8.5 | 1230 | 29.6 / 25.4 | 18.7 / 56.4 |
| 0.2 | 20.3 | 1203 | 55.3 / 17.0 | 18.8 / 70.6 |
| 1.0 | 61.2 | 1227 | 72.5 / 2.4 | 20.8 / 89.5 |

The pulse protects C2 by three to thirty times at matched conversion and
moves the C2 from ethylene to acetylene. The steady element reaches the
same conversion at about 1200 C, held for the whole residence time, which
is the temperature at which benzene forms and survives. The pulse also
forms benzene, on the way through 1200 to 1400 C, and then takes it apart
at the peak; the flux section below has the numbers. An earlier draft of
this paragraph said the pulse was too cold for most of the cycle to make
benzene, which the flux diagram showed to be wrong.

## The lumped series model, and why it is a screen

`lump_fit.py` fits the page's A -> B -> C model (`apps/rphcjh/solver.js`)
to constant-temperature batches of the methane feed: C1 methane, C2 every
two-carbon species, C3+ everything heavier. Above 1300 C the first-order
picture holds to about ten percent in the C2 trajectory; below it the
sink is not first order and the fit is poor, so the Arrhenius lines use
1300 C and above. The result is Ea1 368 and Ea2 362 kJ/mol
(`data/lump/aramco-ch4-he.json`). With equal activation energies k2/k1
does not move with temperature and a linear series model predicts no
selectivity gain from any temperature program. `series_pulse.py`, the
page's exact periodic solver ported and checked against it to 1e-9
(`test_series_pulse.py`), confirms it over 528 element trajectories: gain
0.99 to 1.00 at every residence time (`data/lump/series-pulse-front.json`).

    python3 tools/openmkm_dynamic/lump_fit.py \
        --mechanism tools/cantera/mechanisms/aramco20.yaml --fit-above-c 1300 \
        --output tools/openmkm_dynamic/data/lump/aramco-ch4-he.json
    python3 tools/openmkm_dynamic/series_pulse.py \
        --lump tools/openmkm_dynamic/data/lump/aramco-ch4-he.json \
        --output tools/openmkm_dynamic/data/lump/series-pulse-front.json

The mechanism and the lump disagree because the benzene the steady element
makes forms at 1200 C over tenths of a second, exactly where the lump fits
worst and outside the range its constants come from. The lump is kept as a
screen and the ranking is taken from the mechanism.

## Which pulse protects C2 best

`run_pulse_c2.py` (`RUNCARD-C2.md`) moves one knob at a time from the SI
anchor on the methane feed at tau 0.2 s: peak down to 60 V, period down to
0.2 s, duty up to 20 percent. Each case is compared with the steady
element at its own conversion.

    python3 tools/openmkm_dynamic/run_pulse_c2.py run
    python3 tools/openmkm_dynamic/run_pulse_c2.py compare

Round 1, methane feed, tau 0.2 s, benzene at matched conversion:

| drive | peak, C | X, % | S_C6H6 pulse / steady, % | S_C2H2 pulse / steady, % | element W |
|---|---|---|---|---|---|
| anchor, 78 V, 1 s, 5 % | 1800 | 17.3 | 21.3 / 52.6 | 63.0 / 19.0 | 91 |
| 60 V, 1 s, 5 % | 1233 | 0.20 | 1.2 / 1.0 | 8.5 / 0.8 | 50 |
| 78 V, 0.2 s, 5 % | 1131 | 0.10 | 0.0 / 0.4 | 1.2 / 0.4 | 87 |
| 78 V, 1 s, 20 % | 3063 | 34.5 | 13.2 / 61.6 | 66.5 / 22.3 | 510 |

The element answered before the chemistry did. Dropping the voltage or
shortening the period leaves the peak below 1250 C, where nothing converts
in 0.2 s; raising the duty to 20 percent drives the peak past 3000 C,
which no carbon paper survives, so that row is outside the element's
domain. Between those, the anchor's advantage stands: 21.3 against 52.6
percent benzene at the same 17.3 percent conversion, a ratio of 0.41.

Round 2, smaller steps:

| drive | peak, C | X, % | S_C6H6 pulse / steady, % | S_C2H2 pulse / steady, % | element W |
|---|---|---|---|---|---|
| 70 V, 1 s, 5 % | 1534 | 13.0 | 28.4 / 47.3 | 56.8 / 18.2 | 71 |
| 78 V, 2 s, 5 % | 2595 | 9.7 | 15.5 / 42.0 | 67.5 / 17.5 | 101 |
| 78 V, 1 s, 10 % | 2707 | 26.8 | 15.0 / 59.5 | 67.6 / 20.5 | 213 |
| 70 V, 1 s, 10 % | 2340 | 24.8 | 16.1 / 58.4 | 67.3 / 20.2 | 160 |

Only the 70 V row stays inside the element's domain, and it is worse than
the anchor: benzene at 0.60 of the steady value against the anchor's 0.41.
Every row that overshoots the peak protects more (0.21 to 0.37), so the
trend is one line: the higher the peak, the less benzene at matched
conversion, and the element's material ceiling is the constraint that
binds. Doubling the period or the duty at fixed voltage moves the peak by
800 to 900 C, which is why single-knob steps keep leaving the window. The
right comparison is at fixed peak: for each period and duty, the voltage
that reaches 1800 C, and then the waveform shape is the only thing that
differs. That is round 3.

Round 3, peak held at 1800 C, voltage solved per shape
(`calibrate_element_si.operating_point`), anchor repeated for reference:

| drive | T_min / T_mean, C | X, % | S_C6H6 pulse / steady, % | S_C2H2 pulse / steady, % | element W |
|---|---|---|---|---|---|
| 78 V, 1 s, 5 % (anchor) | 502 / 887 | 17.3 | 21.3 / 52.6 | 63.0 / 19.0 | 91 |
| 57.7 V, 1 s, 10 % | 523 / 924 | 19.1 | 20.3 / 54.3 | 63.9 / 19.3 | 100 |
| 44.8 V, 1 s, 20 % | 570 / 1006 | 23.6 | 18.4 / 57.7 | 65.6 / 20.0 | 123 |
| 97.1 V, 0.5 s, 5 % | 780 / 1128 | 37.6 | 21.1 / 62.1 | 63.2 / 23.0 | 144 |
| 61.4 V, 2 s, 5 % | 235 / 635 | 7.1 | 20.6 / 36.4 | 63.7 / 16.9 | 55 |
| 122.5 V, 0.2 s, 5 % | 1135 / 1401 | 74.0 | 15.9 / 37.0 | 68.3 / 51.3 | 238 |

The pulse column barely moves: benzene 18.4 to 21.3 percent and acetylene
63 to 66 percent across a shape family whose conversion spans 7.1 to 37.6
percent and whose mean temperature spans 635 to 1128 C. The peak sets the
product split; the shape sets only how much methane passes through the
hot part of the cycle. Everything that changes in the ratio column (0.32
to 0.57) comes from the steady comparator, which needs a different
temperature to reach each conversion and makes a different amount of
benzene there. So the waveform is a conversion knob, not a selectivity
knob, and the one selectivity knob the element has, the peak, is pinned
by its material ceiling. The 0.5 s case needs 97 V against the SI's 75 V
supply; it is a model point, not an operable one. The 0.2 s row is more
so: 122 V, and a floor of 1135 C that never lets the vessel cool, so the
mechanism sees a near-steady 1400 C and converts 74 percent. It is the
one shape whose selectivity moves (benzene 15.9 percent), and it moves
because the floor, not the peak, has changed. It was produced by the
voltage solver when the 0.2 s period case was requested at "si-op"
(commit 0ecc311) and is kept as the end of the family.

## The steady comparator on a dense grid, 2026-09-06

Every steady number above is read off `data/premise/cjh-inversion/cjh-cstr.json`
by interpolation in conversion. Until 2026-09-06 that file held five
temperatures at tau 0.2 s (1000, 1150, 1230, 1400, 1470 C), so every
matched point between 5 and 29 percent conversion sat on one straight
line between 1150 and 1230 C, and every point between 29 and 83 percent
on another. The steady benzene curve is concave there, so the straight
line understated it: at the anchor's 17.3 percent the old interpolation
gave 46.2 percent, the dense grid gives 52.6. Eight temperatures were
added to both the CSTR and the plug-flow files (1160, 1175, 1190, 1205,
1220, 1260, 1300, 1350 C) with

    python3 tools/openmkm_dynamic/premise_probe.py sweep \
        --mechanism tools/cantera/mechanisms/aramco20.yaml \
        --kind cstr --feed ch4 --tau 0.2 \
        --temperature 1160 1175 1190 1205 1220 1260 1300 1350

and the same with `--kind pfr`. The tables above were regenerated from
`run_pulse_c2.py compare` afterwards. Every steady benzene value rose by
one to eleven points and every ratio fell; no ranking changed. The pulse
column did not move, because the pulse cases were not touched.

The same dense grid answers a question the CSTR comparison cannot: is
the pulse doing anything a plug-flow reactor would not? A pulse at 5
percent duty exposes each parcel to the peak for a short, sharp interval,
which is closer to plug flow than to a stirred tank. Reading the
plug-flow file at each pulse conversion:

| X, % | S_C6H6 pulse / PFR / CSTR, % | S_C2H2 pulse / PFR / CSTR, % |
|---|---|---|
| 7.1 | 20.6 / 18.3 / 36.4 | 63.7 / 19.2 / 16.9 |
| 13.0 | 28.4 / 29.0 / 47.3 | 56.8 / 22.5 / 18.2 |
| 17.3 (anchor) | 21.3 / 35.0 / 52.6 | 63.0 / 24.1 / 19.0 |
| 23.6 | 18.4 / 42.1 / 57.7 | 65.6 / 25.9 / 20.0 |
| 37.6 | 21.1 / 52.7 / 62.1 | 63.2 / 28.3 / 23.0 |

Below about 13 percent conversion the plug-flow reactor makes as little
benzene as the pulse or less, so the benzene claim, stated against a
stirred tank, is partly a residence-time-distribution effect there. Above
that the pulse holds benzene flat near 20 percent while both steady
reactors climb past 40. The acetylene column is the one that separates
the pulse from both steady reactors at every conversion: 57 to 66 percent
against 17 to 28. That is the claim the data supports without a caveat
about which steady reactor it is compared with. To reproduce the table,
read `x_ch4`, `s_c6h6` and `s_c2h2` at tau 0.2 s from both files and
interpolate linearly in `x_ch4` at each pulse conversion.

## Where the carbon goes: the flux diagram

`pathway_flux.py` charges every reaction's rate to species-to-species carbon
edges and integrates them over one cycle of the anchor case and over unit
time for the steady CSTR at the same conversion; `draw_pathway.py` draws
both as `docs/figures/pathway-anchor.svg`. Numbers below are percent of the
carbon fed and come from `data/c2pulse/pathway-anchor.json`; the steady
element is matched to the conversion the corrected march gives, 17.4
percent, at 1197 C.

The route to benzene is the same in both: acetylene and methyl make C3
(propargyl, C3H3), and C3 pairs into the ring. What differs is what happens
to the ring afterwards.

| carbon flow | steady 1197 C | pulse, peak 1800 C |
|---|---|---|
| into benzene (C3 and C6 to C6H6) | 9.5 | 15.1 |
| out of benzene (to C4H2, C2H2, other C6) | 0.3 | 11.5 |
| benzene leaving the reactor | 9.2 | 3.6 |
| C4H2 back to C2H2 | 0.1 | 7.3 |
| acetylene leaving the reactor | 3.3 | 10.7 |

The pulse makes more benzene than the steady element, not less: 15.1
against 9.5 percent of the fed carbon enters the ring, most of it on the
way up and down through 1200 to 1400 C. At the 1800 C peak the ring cracks,
6.4 to diacetylene and 3.4 straight back to acetylene, and the diacetylene
cracks too, 7.3 back to acetylene. So the low benzene of the pulse is not
the ring failing to form, it is the ring being taken apart at the peak and
the fragments frozen as acetylene in the quench. This is why the peak, and
nothing about the shape, sets the split (round 3), and it is also why the
polyyne route matters: the carbon that leaves as C4H2 and C6H2 in the model
is the carbon that would deposit in the device.

### The same diagram for the CH4/CO2 feed

`docs/figures/pathway-ch4co2-tau0.2.svg` repeats the analysis for the feed the
device actually runs, 5 % CH4, 5 % CO2 in helium at tau 0.2 s
(`data/c2pulse/pathway-ch4co2-tau0.2.json`; pulse 16.5 % conversion on the
corrected march, steady matched at 1192 C). Numbers are percent of the
carbon fed as methane. CO2 and CO are separate boxes: the CO2 box is fed
another 100 and shows what is left of it, the CO box shows what arrived.

| carbon flow | steady 1192 C | pulse, peak 1800 C |
|---|---|---|
| into benzene | 8.7 | 8.7 |
| out of benzene | 0.3 | 7.2 |
| benzene leaving the reactor | 8.5 | 1.5 |
| C4H2 back to C2H2 | 0.1 | 5.2 |
| acetylene leaving the reactor | 3.0 | 4.7 |
| CO2 to CO | 2.2 | 13.6 |
| methane carbon to CO | 0.1 | 8.6 |
| CO leaving the reactor | 2.3 | 22.0 |

The ring picture is the one above: benzene forms both ways and the pulse
cracks it at the peak. CO2 changes one thing, and only in the pulse. Steady
at 1192 C the CO2 is nearly a spectator: 2.2 percent of it goes to CO by
the reverse water-gas shift and no methane carbon follows. At the 1800 C
peak the CO2 both reduces, 13.6 of its own carbon to CO, and oxidises the
intermediates, 4.9 from acetylene, 1.9 from methyl, 1.7 from C3, so 8.6
percent of the methane carbon leaves as CO. That is the largest single
sink of methane carbon in the pulse, larger than benzene and acetylene
together, and it is where the pulse's hydrocarbon selectivity goes on this
feed. The CO the device would measure is 22 percent of the methane carbon
fed, of which 13.6 came from CO2 and 8.6 from methane.

## Standing caveats

- Uniform-temperature CSTR at the element temperature. The device is not
  that (`PREMISE-ARAMCO.md`); these are rankings of drives on a prescribed
  history.
- The element trajectory is one-way coupled; at 5 percent hydrocarbon the
  reaction load is small against the element power.
- No condensed phase. C3+ here is gas-phase hydrocarbon carbon; the
  experimental carbon balance declines where solid carbon forms.
- Figure 2 numbers quoted anywhere are read by eye, one unit each axis.
