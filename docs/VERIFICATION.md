# Numerical verification of the 2D solver

This document verifies that the 2D finite-volume solver solves its
discretized equations correctly, separately from the *physical* validation
against published reactors (the cross-check panels in the Joule tool). Code
verification asks a narrower question: given the model equations, does the discrete solution
converge to the exact one at the expected rate?

Everything below is reproducible:

```bash
npm run verify:joule   # ~20 min (the finest physical-case grid dominates)
npm test               # includes fast guard tests on the coarse grid pairs
```

The only solver change made for verification is a test-only hook,
`cfg.verificationSource(r, z)`, which replaces the Joule source term with a
prescribed volumetric source for manufactured-solution runs. The pages never
set it.

## Methods

Four standard techniques are used:

1. **Discrete exactness**: a uniform volumetric source with constant
   conductivity has an exactly parabolic radial temperature profile, and a
   conservative two-point-flux FV scheme reproduces quadratics exactly at cell
   centers. Any mismatch is therefore *physics left in the setup* (finite-rod
   axial leakage), not discretization error, and must vanish as the element is
   made longer.
2. **Analytic multi-layer benchmark**: mid-plane temperature drops across the
   element / wall / surrounding-air layers versus the ln-resistance solution
   of an infinite cylinder.
3. **Manufactured solution (MMS)**: a smooth exact solution
   T\*(r,z) = T_a + A·(1−(r/R_d)²)²·(1−(2z/H_d)²)² is imposed by injecting the
   analytically derived source q = −k∇²T\* on a uniform-conductivity domain
   (element k = wall k = gap k = outside-air k) with radiation and convection
   off. The quartic bump vanishes with zero slope on every outer boundary, so
   the solver's ambient boundary handling is exactly consistent with T\*. L2
   and L∞ errors against T\* measure the observed convergence order.
4. **Grid sensitivity of the shipped default cases**: the full nonlinear
   models (radiation, He purge flow, temperature-dependent properties) on a
   doubling grid sequence.

## Joule solver (`apps/joule/solver.js`, `solveThermal2D`)

### 1. Radial parabola: discrete exactness

Constant-k SiC, uniform Joule source, gap 0. The analytic center-to-surface
rise is q·R²/(4k); the worst relative mismatch of the mid-plane radial profile
against the exact parabola:

| case | analytic center→surface rise | worst relative mismatch |
| --- | --- | --- |
| L/D = 20 | 10.54 K | 7.4e-3 |
| L/D = 40 | 5.86 K | 4.3e-4 |
| L/D = 80 | 1.46 K | 3.0e-5 |

The mismatch collapses by more than an order of magnitude per doubling of L/D. It is the physical axial
curvature of a finite rod, not discretization error. At L/D = 80 the discrete
radial operator reproduces the exact solution to 3.0e-5.

### 2. Multi-layer annulus vs ln-resistance theory

Radiation and convection off, 2 W fixed power, layers element (k = 120) /
quartz wall (k = 1.4) / air (k = 0.026), drops measured at the mid-plane
against the piecewise analytic solution:

| L/D | worst layer error |
| --- | --- |
| 20 | 17.5% |
| 50 | 5.2% |
| 100 | 1.9% |

The error is a uniform flux deficit across all layers (axial leakage carrying
part of the power to the ends), shrinking toward zero as the cylinder
approaches the infinite-length limit; the multi-region conduction assembly
(material interfaces, harmonic series resistances, cylindrical metrics) is
consistent with theory.

### 3. Manufactured solution: observed order

| grid | L2 error (K) | L∞ error (K) | order (L2) | order (L∞) |
| --- | --- | --- | --- | --- |
| 30×60 | 1.582e+0 | 4.817e+0 | — | — |
| 60×120 | 3.826e-1 | 1.408e+0 | 2.05 | 1.77 |
| 120×240 | 9.156e-2 | 3.769e-1 | 2.06 | 1.90 |

**Observed order 2.05 in L2, 1.77 rising to 1.90 in L∞**. The discretization
(including the non-uniform radial mesh, the cylindrical metrics, and the
ambient boundary treatment) is second-order accurate in the mean, as designed.
The L∞ order is the worst single cell rather than the field, and it approaches
2 from below as the graded outer band is refined; the two published orders
should be quoted separately rather than as one number.

### 4. Default SiC case: grid sensitivity

The app's default inputs (1.18 cm³ SiC, L/D 1.5, quartz enclosure, He purge,
radiation on, 20 A current-limited drive):

| grid | avg T (°C) | max T (°C) | energy closure | linear residual |
| --- | --- | --- | --- | --- |
| 30×60 (default) | 644.21 | 646.10 | 5.2e-8 | 7.4e-12 |
| 60×120 | 643.20 | 645.09 | 5.2e-8 | 7.9e-12 |
| 120×240 | 642.86 | 644.77 | 5.3e-8 | 7.2e-12 |
| 240×480 | 642.76 | 644.67 | 5.2e-8 | 6.2e-12 |

Regenerated 2026-09-06 with helium k(T) in the gap
(`node docs/figures/make-verification-data.mjs --levels 4`, which records
these rows in `verification-data.json`). The default case is 200 K cooler
than it was with the constant 0.03 W/m·K gap (846.75 °C on the same grid),
because the gas now carries heat to the wall.

Richardson on the first three grids gives an observed order of **1.62** for
average temperature (1.62 for peak), an extrapolated 642.71 °C, and a
finest-grid relative error of 2.5e-4. Repeating it on grids 2–4 gives 1.71 and
642.72 °C: the two overlapping triplets agree on the extrapolated value to
0.01 K and on the order to 0.1, which is the check that the sequence is
genuinely in the asymptotic range rather than accidentally well-behaved on
one triplet. With air in the gap the same study read 1.45 and 1.46.

The order sits between first and second because the case mixes both. Conduction
and surface radiation are second-order (studies 1–3); the He purge enthalpy
balance is first-order upwind. A mixture converging between 1.6 and 1.7 is the
expected result, not a defect.

**Sensitivity bound: the default 30×60 grid differs from the 240×480 grid by
1.45 K in average temperature and 1.44 K in peak, i.e. 0.23% of the ~624 K
temperature rise.**

#### Why this section used to report a negative order

Until the purge advection was corrected, this study reported an observed order
of **−0.588**: the answer moved further on each refinement instead of settling
(837.40 → 833.68 → 827.12 °C on the three grids, and the advected purge power
collapsing 0.75 → 0.63 → 0.50 W). A complexity ladder on the same grid sequence
localized it to a single term:

| configuration | observed order |
| --- | --- |
| pure conduction; no gap, no purge, no radiation | +1.22 |
| radiation on; no gap, no purge | +1.16 |
| gap present, purge **off**, no radiation | +1.33 |
| gap present, purge **on**, no radiation | −0.32 |
| full default | −0.588 |

Conduction, radiation and the gap geometry all converged. Only the purge did
not, and it is the sole difference between the third and fourth rows.

The advection had given every flow cell an inflow equal to the area-weighted
mean of the whole upstream row. That homogenizes the stream radially once per
cell, so the mixing length is the mesh spacing and the mixing rate per unit
length diverges under refinement; it is not a discretization of anything. The
artifact did not stay in the gas, because the purge cells are also conduction
cells: it landed in the element-to-wall gap resistance, whose temperature drop
moved 906 → 803 → 672 K across the three grids while the heat through it barely
changed. That is what carried the element temperature down and inverted the
order. The advected power itself was never the mechanism, changing by only
0.26 W against a 57 K/W case sensitivity, worth 15 K of the observed 264 K.

Where the flow cross-section is unchanged from row to row, each cell now draws
its inflow from the cell directly upstream of it; the area-weighted mean is kept
for exactly the rows where the stream contracts or expands at the ends of the
element annulus. Both branches conserve enthalpy. `cfg.purge` was added at the
same time so the stream can be switched off without deleting the gap, which is
what makes the ladder above separable at all.

## When the 0D screening model can be trusted (`tools/verification/zerod-*.mjs`)

A model-reduction study, not verification and not validation: it measures when
the lumped 0D temperature agrees with the resolved field, so it inherits the 2D
solver's credibility and has to establish an anchor before it sweeps. Run with
`npm run verify:zerod-limit` and `npm run verify:zerod-sweep`.

### The gap is two quantities, not one

Driving Bi_R to 2.3e-6 by scaling conductivity 1000x leaves the element
isothermal — spread 0.05 K — while the 2D mean still sat **28.72 K above** the
0D steady temperature. An offset that outlives the isothermal limit is not a
lumping error, so the difference between the models separates:

| component | definition | scales with Bi_R |
| --- | --- | --- |
| offset | `T_avg(2D) − T_ss(0D)` | no |
| spread | `T_max(2D) − T_avg(2D)` | yes |

Interrogating both loss models at the *same* temperature divides out the
operating point and names the channel. At the isothermal limit the 0D network
claims 554.28 W where the resolved field carries 532.23 W (4.14%):

| path | 0D | 2D |
| --- | --- | --- |
| side | 505.03 W | — |
| end | 47.90 W | — |
| static total | 552.93 W | 532.12 W |
| He advective | 1.352 W | 0.114 W |

94% of the discrepancy is the static path. Splitting the 2D boundary terms by
channel — the instrumentation this study added — located it precisely, and it was
not the end path at all:

| path | 0D | 2D |
| --- | --- | --- |
| wall radiation + outer radial + axial | 505.03 W (`side`) | 484.49 W |
| element end radiation | 47.90 W (`end`) | 47.63 W |

The end paths agree to 0.3 W. All 20.5 W sits on the side, and the cause is that
the 0D network charged `2 pi r_out * domainHeight` of radiating area to the
near-element wall temperature. The wall is not isothermal over the domain: it is
heated across the element's length and cools away from it, so the overhang was
being counted as hot radiating area.

**Fixed** by treating the overhang as a radiating fin, contributing
`tanh(m*margin)/m` of effective length per side with `m = sqrt(hP/kA)` evaluated
at the current wall temperature inside the existing bisection. The isothermal
limit then reads:

| | before | after |
| --- | --- | --- |
| offset at Bi_R = 2e-6 | +28.72 K | **−8.90 K** |
| loss agreement | +4.14% | **−1.23%** |

The correction slightly overshoots, leaving the 0D 1.2% *under* the resolved
field. Two residuals remain and are named rather than tuned away: the side path
is now 8.1 W low, and the He advective terms still differ twelvefold (1.352 W
against 0.114 W) because the 0D carries downstream cooling on the element end
area alone, where the resolved exit region loses heat radially over the full
annulus.

It was derived purely from 0D-versus-2D consistency, with no reference to
measurement — and it moved the 0D **toward** the experiment, which is
independent support for it:

| case | 0D before | 0D after | measured |
| --- | --- | --- | --- |
| Wismann | 761.9 °C (−4.8%) | **787.4 °C (−1.6%)** | 800 °C |
| Zheng | 736.0 °C | 757.3 °C | not tabulated |
| Kwak | 1270.7 °C | 1276.5 °C | 1094 °C |

**Consequence for the earlier cross-check claim.** The 0D-to-2D gap on Wismann
was 49.8 K and became 24.3 K (29.2 K on the 2026-09-06 gas model, below). Roughly half of what had been reported as the 2D
resolving something the lumped model could not was this network's own
over-prediction of wall radiating area.

### The gap gas, 2026-09-06: the agreement above was air's

Everything in this section up to here was measured with the gap conducting
at a constant 0.03 W/m·K, which is air near room temperature, in a gap the
page labels as helium. `cfg.gapGas` now selects the gas and the
conductivity follows k(T) = k₃₀₀·(T/300)^n at the local film temperature
(helium 0.152 W/m·K at 300 K, 0.36 at 1000 K; `GAP_GASES` in
`solver.js`). The shipped default is helium. Rerunning the isothermal limit
(`npm run verify:zerod-limit`) with helium:

| | air, constant 0.03 | helium, k(T) |
| --- | --- | --- |
| offset at Bi_R = 3.7e-6 | −8.3 K | **+83.6 K** |
| 0D loss at the 2D mean temperature | 526.1 W | 600.9 W |
| 2D loss at the same temperature | 532.2 W | 532.2 W |
| loss agreement | −1.2% | **+12.9%** |

The resolved loss did not move: helium conducts 15 W more through the gap
in 2D and the wall re-radiates it, so the 2D total stays at 532 W and the
2D mean temperature falls by 164 K. The 0D network moved by 75 W. Channel
by channel, both at the 2D mean:

| path | 0D | 2D |
| --- | --- | --- |
| side (gap, wall, outside) | 562.30 W | 497.1 W (wall radiation 449.7 + outer radial 40.8 + axial 6.6) |
| element end | 38.19 W | 35.02 W |
| He advective | 0.42 W | 0.12 W |

The side path carries 65 of the 69 W. The 0D wall temperature it solves
for, 1319 °C, now sits at the 2D outer-wall mid-plane value, 1313 °C, and
at that temperature the fin network above radiates 13 percent more than
the resolved wall does. With air the same network sat 66 K below the 2D
mid-plane wall (1248 against 1314 °C) and came out 8 W low, so the −1.2
percent agreement recorded above was two errors cancelling: a gap that
barely conducted, and a radiating-area model that overshoots once the wall
is as hot as it should be. **The 0D network under-predicts the element
temperature by 84 K at the isothermal limit with helium in the gap**, and
that offset is the number to quote beside any 0D screening result until
the fin network is re-derived against the resolved wall profile. It is not
fixed here.

The cross-check column moved with it. Wismann's tube and Zheng's foam were
never helium-purged, so those two cases now carry air at k(T) (0.026 W/m·K
at 300 K, 0.068 at 1000 K) rather than the constant 0.03; Kwak's strip sat
in helium in its 17 mm quartz tube and takes the helium model:

| case | 0D, constant 0.03 | 0D now | 2D avg now | measured |
| --- | --- | --- | --- | --- |
| Wismann | 787.4 °C | 724.5 °C | 753.7 °C | 800 °C |
| Zheng | 757.3 °C | 727.5 °C | 749.0 °C | not tabulated |
| Kwak | 1276.5 °C | 1172.8 °C | 1200.1 °C | 1086 °C from the T–P fit at 117.6 W |

Kwak moved toward its measurement by 104 K on the strength of the gas
alone; Wismann moved away by 63 K, because air at 700 °C conducts 0.06
W/m·K rather than 0.03 and the page enclosure was never that reactor's. The
Mittal et al. (2025) strip that exposed the problem, 38 × 8 × 0.21 mm at
the paper's effective 29.1 V and 303 W, reads 1783 °C in 0D and 1785 °C in
2D with the constant 0.03, and 1543 °C (0D) and 1616 °C (2D) with helium,
against the paper's CFD range of 1517 to 1532 °C. The gas closed 170 of the
260 K gap in the resolved model; the remaining 85 to 100 K is `미확인`
(the paper's tube diameter and the strip's emissivity are not stated in
the inputs used here). Reproduce with `tests/joule-gap-gas.test.js` and
`node tools/verification/crosscheck.mjs`.

### Control: the closed form is reproduced exactly

For a cylinder of radius R with uniform volumetric generation — which is what the
solver applies, since `qVol = pBulk / envelopeVolume` carries no local ρ(T)
coupling — the hand derivation gives

    centre-to-surface / surface-to-ambient  =  h R / (2k)  =  Bi_R / 2

Scanning k over 32× returns a measured ratio that is a **constant 0.93333** of
that. The constancy is the tell: cell-centred unknowns are sampled h/2 inside
each boundary, which shortens the drop by exactly `1 − 1/N`, and N = 15 here.

| test | raw | corrected for `1 − 1/N` |
| --- | --- | --- |
| parabola, `(centre−surface) / (qR²/4k)` | 0.93260 | **0.99921** |
| ratio, through-origin slope on Bi_R/2 | 0.93333 | **0.99999** |

The apparent 7% deficit is where the unknowns sit, not solver error.

### The sweep

Bi_R is scanned one factor at a time — k, emissivity and drive current
separately — with Bi_R computed from the 2D solve's own side loss and surface
temperature so both sides of the ratio refer to the same operating point.

| stage | what varies | slope on Bi_R/2 | R² | n | Bi_R range |
| --- | --- | --- | --- | --- | --- |
| 3a | k, ε, current (SiC, L/D 30) | 0.9374 | 1.0000 | 48 | 2.9e-4 … 5.8e-2 |
| 3b | 4 materials, power-matched | 0.9374 | 1.0000 | 12 | 2.6e-3 … 3.5e-2 |

Both land on the same 0.937 the control explained, across a 200× range of Bi_R
and materials whose conductivity spans 11 to 174 W/m·K. **Corrected for
sampling, `spread / rise = Bi_R / 2` holds exactly and is material-free.**

### Aspect ratio is a second group

The hypothesis that Bi_R alone predicts is **rejected**. Holding Bi_R by
construction and sweeping L/D:

| L/D | 1.5 | 4 | 10 | 30 | 60 |
| --- | --- | --- | --- | --- | --- |
| f(L/D), air 0.03 in the gap (2026-08) | 0.649 | 0.799 | 0.939 | 1.000 | 0.9995 |
| f(L/D), helium k(T) in the gap (2026-09-06) | 0.454 | 0.751 | 0.932 | 1.000 | 0.9999 |

f rises monotonically and saturates near L/D ≈ 20, a factor of 1.54 across the
range with air in the gap and 2.2 with helium: a conducting gas lets a short
element shed even more of its heat axially, so the correction the lumped model
needs at L/D 1.5 is larger, not smaller, on the shipped default gas. Short elements shed heat axially, which relieves the radial gradient the
lumped model cannot see. So the law carries a correction:

    spread / rise  =  (Bi_R / 2) · f(L/D)

Because f ≤ 1 everywhere swept, **Bi_R/2 remains a conservative upper bound**,
which is the form worth applying:

    Bi_R  ≤  2 ΔT_allowed / (T_avg − T_ambient)

At a 2000 K rise, holding the unseen spread under 25 K needs Bi_R < 0.025. The
textbook Bi < 0.1 rule — derived for transient cooling of an initially uniform
body, not for steady internal generation — admits 5% of the rise, i.e. 100 K at
that same operating point, and is **four times too permissive here**.

### What this does not license

The sweep figures quoted here predate the fin correction: with the old network
the offset was frequently *larger* than the spread (39.9 K against 5.2 K at
Bi_R = 3.9e-4) and changed sign at low emissivity with a high drive. The
correction cuts the isothermal-limit offset by 3.2x, so the offset is no longer
the dominant term in most of the sweep — but it does not reach zero, and it still
does not scale with Bi_R. **A Biot criterion remains necessary and not
sufficient**, and must be quoted with the residual offset. The fin fix touched
only the 0D network, so it left every 2D quantity alone. The gap-gas model of
2026-09-06 did not: it is a 2D change, and on rerunning the sweep with helium
the slopes held (0.9374 in 3a and 3b, R² 1.000, n 48 and 12) while f(L/D) at
short aspect ratio fell, as tabulated above. The offsets in the sweep rows
are now 33 to 200 K, all positive, consistent with the isothermal-limit
finding recorded in the gap gas section.

Two reporting defects were found and fixed inside this study, both of the same
shape — a summary statistic agreeing with the hypothesis while the rows
underneath disagreed. A single fit through every aspect ratio averaged the f
trend away and printed a pass; and `MATERIALS.find(m => m.name === "Kanthal
A-1")` missed an entry reading `"Kanthal A-1 (FeCrAl)"` and dropped a material in
silence, the fit returning n = 9 instead of 12 with nothing said. Both stages now
print every point and name every drop.

## Continuous guards

`tests/verification.test.js` (run by `npm test` and CI) keeps the headline
results true as the solvers evolve, using the cheap grid levels only:

- Joule parabola mismatch < 2e-3 at L/D = 40 and collapsing ≥4× by L/D = 80;
- Joule annulus worst-layer error < 8% at L/D = 50, < 3% at L/D = 100;
- Joule MMS observed order > 1.7 (L2) / > 1.6 (L∞) on the 30×60→60×120 pair.

Studies 1 to 3 were regenerated on 2026-08-25 against the then-current
`build2DMesh`, and again on 2026-09-06 (`npm run verify:joule`) after the
gap-gas model landed. Commit `319e5a2` changed how the mesh states its outer
domain reach, which moves every study that compares against an
infinite-length or unbounded analytic solution: the parabola mismatch at
L/D = 20 went 5.8e-3 to 6.4e-3 and then 7.4e-3, the annulus worst-layer
error at L/D = 100 went 0.8% to 1.95% and then 1.9%, and the
manufactured-solution orders went 2.00/2.01 to 2.05/2.06 in L2 and 1.96/1.98
to 1.77/1.90 in L∞, where they stay: the manufactured solution pins the gas
to a constant, so the gap-gas model does not touch it. The conclusions are
unchanged; the numbers are not. Every other study in this document (4, the
0D-trust section, the transient and electrical guards) was rerun the same
day; the transient orders (0.973, 0.986) and every electrical identity are
unchanged because their cases carry constant gap conductivities.
