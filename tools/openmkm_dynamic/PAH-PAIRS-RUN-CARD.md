# Paired PAH comparison at four archived conditions

Purpose: every archived map here uses AramcoMech 2.0, which stops at C8 and
carries benzene as its largest ring. The maps therefore report the carbon that
reaches C2H2, C4H2 and C6H6 and then stop, and they cannot say how much of it
would keep going. This batch runs four of those exact conditions under a
mechanism that has the channel and reports the two questions separately: how far
the C0 to C4 layer moves when the mechanism changes, and how much carbon leaves
the C6 pool for naphthalene and larger.

This is a four-condition sample. It is not an optimization, not a soot yield,
and not an experimental validation of either mechanism. User requested execution
on 2026-09-07.

## Inputs

Closure, solver, feed strings, pressure and convergence settings are the ones
the archived constant-temperature maps used, unchanged: constant pressure,
prescribed constant gas temperature, inlet and outlet mass flow equal, residence
time an input. The generator asserts the archived `solver_sha256` and the
archived `mechanism_sha256` for Aramco before it runs, so a change in either
stops the batch instead of producing a comparison against a moved reference.

Mechanism under test, selected with `--mechanism`. GRI-Mech 3.0, 53 species and
325 reactions, has no species above C3 and its only C3 species are C3H7 and
C3H8, so it has no propargyl route and no path to a ring; it is included to
measure what a mechanism ceiling does to these four conditions, and it is a
natural-gas combustion mechanism with no validation for oxygen-free pyrolysis
above about 1200 C. The mechanism that answers the ring question is
CRECK 2003 high temperature with soot and NOx,
`tools/cantera/mechanisms/creck2003-ht-soot-nox.yaml`, 497 species and 24501
reactions, sparse Jacobian with the adaptive preconditioner. It carries
naphthalene, acenaphthylene, anthracene or phenanthrene, pyrene, and lumped
soot-precursor particles named BIN. The feed carries no nitrogen, so the NOx
sub-mechanism is inert here and is kept only because that is how the mechanism
is distributed.

Conditions, all four already in the archived maps:

| Feed | T | tau | why |
|---|---|---|---|
| CH4/CO2 | 1750 C | 1 ms | the acetylene maximum of the CH4/CO2 map |
| CH4/CO2 | 1200 C | 1 s | the benzene-rich moderate-severity corner |
| CH4/H2O | 1800 C | 1 ms | the acetylene maximum of the CH4/H2O map |
| CH4/H2O | 1200 C | 1 s | the same corner on the steam feed |

The Aramco side of every pair is read from the archive. Nothing archived is
recomputed and nothing archived is rewritten.

## Execution

`run_pah_pairs.py`, one subprocess per case, seven executions: a cold control,
four map conditions, and two sampling gates. Measured cost of one CRECK case at
1750 C and 1 ms: 34 s, against 8.5 s for the archived Aramco case at the same
condition. Seven executions are estimated at 300 to 500 s. Hard limits: 1200 s
for the batch and 300 s per case. No automatic retry. On failure the run stops,
preserves completed outputs, and writes the reason into `status.json`.

## Acceptance gates

1. Cold control at 26.85 C returns zero methane conversion to 1e-8.
2. Sampling: one condition per feed also runs at 40 phase points instead of 20.
   The C7+ carbon fraction, the BIN carbon fraction and each named ring must
   agree with the 20-point case to 1e-5 in carbon fraction.
3. Per case, enforced by the solver and its caller: periodic-state boundary
   residual below the cycle tolerance, carbon group partition closed to
   1e-12 of carbon out, outflow mass partition residual below 1e-6, and C, H
   and O element residuals below 5e-3.

These are numerical screening bounds. They do not bound mechanism error, and
they say nothing about which of the two mechanisms is closer to a real reactor.

## Outputs

One directory per mechanism, `docs/research/pah-pairs-2026-09-07/` for CRECK and
`docs/research/pah-pairs-gri-2026-09-07/` for GRI: per-case raw result, parameters, metrics
and log; `manifest.json` with the commit, script, solver and both mechanism
hashes and the reference archive paths; `gates.json`; `status.json`;
`summary.json` pairing each CRECK case with its archived Aramco row; a
`REPORT.md`; and `checksums.json`.

Carbon is reported as a fraction of carbon out, partitioned C0 through C6 and
C7+, with the named rings pulled out of C7+ and the rest reported as a
remainder, so the partition closes. Carbon yields are per total inlet carbon,
which is all methane on the steam feed and half CO2 on the CO2 feed, so the two
feeds are one scale only after the CO2 figures are doubled.

A changed mechanism is a new model. Nothing in this batch transfers an optimum,
a ranking or a validation status from Aramco to CRECK or back. The BIN species
are lumped soot precursors from a gas-phase mechanism with no particle dynamics,
so the BIN carbon fraction is a mechanism output and not a predicted soot yield.

## Cache and invalidation

Nothing is reused, overwritten or invalidated. Every archived map, its report
and every published plate are untouched. The only edited file outside this batch
is `run_aramco_cjh_baseline.py`, which gains a mechanism table so a third
mechanism can be named; the archived manifests record the solver and mechanism
hashes and not this script's hash, and both are asserted unchanged.

Generator: `python tools/openmkm_dynamic/run_pah_pairs.py --mechanism creck|gri
--output-dir <dir>`. Report: `python tools/openmkm_dynamic/summarize_pah_pairs.py
--archive <dir>`, which reads the mechanism from the batch manifest.
