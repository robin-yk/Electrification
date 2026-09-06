# Run card: the C2 pulse study on AramcoMech 2.0

Required by `CLAUDE.md`: four sawtooth cases at about 45 minutes each is
three CPU-hours. Generator `run_pulse_c2.py`, committed before the run.

## Purpose

Which drive protects C2 best, on the full mechanism, at matched feed,
residence time and conversion. One anchor (the SI operating point: the
voltage at which the calibrated element peaks at 1800 C, 1 Hz, 5 percent
duty) and three single-knob moves: peak down (60 V), cycle shorter (0.2 s),
hot fraction longer (20 percent duty). Feed is the paper's methane feed, 5
percent CH4 in helium, 1 bar; residence time 0.2 s.

## Claim boundary

Passing licenses: in a uniform-temperature CSTR on the calibrated element
trajectory, this mechanism ranks these four drives in the stated order for
C2 protection at their own conversions. Nothing about the device's absolute
conversion (the reactor picture is open, `RUNCARD-BL.md`), nothing about
other residence times or feeds.

## Inputs

| | value | source |
|---|---|---|
| mechanism | AramcoMech 2.0 | `tools/cantera/mechanisms/aramco20.yaml` |
| element | S1f calibration: loss scale, clamp conduction, heat-capacity scale | `calibrate_element_si.py` |
| drives | see `run_pulse_c2.py plan` | anchor from the SI; moves chosen by hand |
| feed, pressure, tau | CH4 0.05 He 0.95, 1 bar, 0.2 s | SI flow control; tau as in `RUNCARD-S9.md` |
| steady comparison | `data/premise/cjh-inversion/cjh-cstr.json`, tau 0.2 s, 1000 to 1470 C | `premise_probe.py sweep` |

## Acceptance gates

1. Each case converges to a periodic state and closes carbon (schema 2 audit).
2. Its conversion lies inside the steady sweep's range at tau 0.2 s, so the
   matched steady point exists by interpolation and not extrapolation.
3. Output: the four product slates beside their matched steady slates
   (`run_pulse_c2.py compare`). The ranking on benzene at matched conversion
   is the result, whichever way it comes out.

## Round 1 result, and round 2

Round 1 (45 wall minutes, four cores): the anchor converts 22.0 percent
with 18.8 percent benzene against 52.0 for the steady element at 1207 C.
The three moves left the chemistry's window: 60 V peaks at 1233 C and
converts 0.29 percent, a 0.2 s period peaks at 1131 C and converts 0.13,
and 20 percent duty peaks at 3063 C, which no carbon paper survives, so
its 38.7 percent conversion and 13.1 percent benzene are outside the
element's domain and are reported, not used. The knob steps were too
coarse for an element whose peak is set by the energy per pulse against a
T^4 loss. Round 2 steps inside the window: 70 V at 5 percent duty, 2 s
period at the SI voltage, 10 percent duty at 78 and at 70 V. Same gates,
same cost.

## Round 2 result, and round 3

Round 2: 70 V at 5 percent peaks at 1534 C and protects less than the
anchor (benzene 0.51 of the matched steady value against 0.36); the three
cases that overshoot the peak (2340 to 2707 C) protect more (0.25 to
0.41). One trend, higher peak less benzene, with the element's ceiling as
the binding constraint. Round 3 therefore holds the peak at 1800 C and
varies only the waveform shape: `operating_point` solves the voltage for
each period and duty. Cases: 1 s at 10 and 20 percent duty, 0.5 s and 2 s
at 5 percent. Their solved voltages are 57.7, 44.8, 97.1 and 61.4 V
(`calibrate_element_si.operating_point`); the 0.5 s case exceeds the SI's
75 V supply and is kept because the element, not the supply, is the model
under test. The element's floor and mean differ widely across these:
mean temperature 635 to 1128 C at the same peak.

## Round 3 result

All four cases converged (cycle boundary residual below 1e-12) with carbon
closed to round-off. At a fixed 1800 C peak the pulse selectivity is flat:
benzene 16.5 to 18.8 percent, acetylene 66 to 68 percent, while conversion
runs from 8.5 percent (2 s, 5 percent duty) to 47.2 percent (0.5 s, 5
percent). The pulse-over-steady benzene ratio (0.27 to 0.52) tracks the
steady comparator, not the pulse. Conclusion for the claim boundary: the
peak fixes the product split, the shape fixes throughput. No round 4 on
shape is warranted; the next question, if any, is the peak itself, which
the element cannot raise. Numbers: `run_pulse_c2.py compare`.

## Cost

4 cases per round, about 45 min each measured on the si-op sawtooth
locally, four in parallel on four cores: about one wall hour per round.
Cache: a finished case file is not recomputed.

Rerun of 2026-09-06: the generator now passes `--min-cycles 4`. The
original runs marched 20 cycles each because that is `run_cstr_case.py`'s
floor, while their convergence histories show the boundary residual under
the 1e-7 tolerance by cycle 2 or 3 (cycle 9 for the 0.2 s period). At tau
0.2 s and a 1 s period the vessel turns over five times a cycle, so there is
no cycle-to-cycle memory to wait for. Expected cost of the twelve-case rerun:
about 10 min per case, four in parallel, under one wall hour.

## What this invalidates

Nothing. Writes only to `data/c2pulse/`.

## Invalidated by, 2026-09-05

The closure fix in `run_cstr_case.step_temperature` (README, Formulation).
All twelve case files here were marched before it and overstated
conversion by about a fifth. The three round sections above are the
record of what was run on the old march; the corrected numbers are in the
next section and in `docs/C2-PULSE.md`.

## Rerun result, 2026-09-06

Author approved the rerun of all twelve cases on the corrected march on
2026-09-06. Run as `run_pulse_c2.py run --force --jobs 4` with
`--min-cycles 4`; the four round-2 fixed-voltage cases were rerun by hand
at the literal SI voltage 78.11344859393759 V because "si-op" in the
generator now re-solves the voltage per shape (see the comment above
`CASES`). One of those si-op runs, 0.2 s at 5 percent duty, solved to
122.5 V and is kept as `peak1800-0.2s-d0.05`, the thirteenth case. All
thirteen converged, twelve at cycle 4 and the 0.2 s period at cycle 8;
wall time 3 to 10 minutes per case against the 45 minutes of the
20-cycle originals.

Corrected numbers, pulse benzene / matched steady benzene in percent,
from `run_pulse_c2.py compare`:

| case | peak, C | X, % | old X, % | S_C6H6 p / s | ratio (old) |
|---|---|---|---|---|---|
| anchor 78 V, 1 s, 5 % | 1800 | 17.3 | 22.0 | 21.3 / 52.6 | 0.41 (0.36) |
| 60 V, 1 s, 5 % | 1233 | 0.20 | 0.29 | 1.2 / 1.0 | out of window |
| 78 V, 0.2 s, 5 % | 1131 | 0.10 | 0.13 | 0.0 / 0.4 | out of window |
| 78 V, 1 s, 20 % | 3063 | 34.5 | 38.7 | 13.2 / 61.6 | 0.21 (0.25) |
| 70 V, 1 s, 5 % | 1534 | 13.0 | 17.9 | 28.4 / 47.3 | 0.60 (0.51) |
| 78 V, 2 s, 5 % | 2595 | 9.7 | 10.4 | 15.5 / 42.0 | 0.37 (0.41) |
| 78 V, 1 s, 10 % | 2707 | 26.8 | 30.3 | 15.0 / 59.5 | 0.25 (0.25) |
| 70 V, 1 s, 10 % | 2340 | 24.8 | 28.7 | 16.1 / 58.4 | 0.28 (0.26) |
| 57.7 V, 1 s, 10 % | 1800 | 19.1 | 23.8 | 20.3 / 54.3 | 0.37 (0.33) |
| 44.8 V, 1 s, 20 % | 1800 | 23.6 | 28.7 | 18.4 / 57.7 | 0.32 (0.27) |
| 97.1 V, 0.5 s, 5 % | 1800 | 37.6 | 47.2 | 21.1 / 62.1 | 0.34 (0.38) |
| 61.4 V, 2 s, 5 % | 1800 | 7.1 | 8.5 | 20.6 / 36.4 | 0.57 (0.52) |
| 122.5 V, 0.2 s, 5 % | 1800 | 74.0 | new | 15.9 / 37.0 | 0.43 |

Which claims survive:

1. Anchor against steady at matched conversion: survives. 21.3 against
   52.6 percent benzene at 17.3 percent conversion (ratio 0.41; was 0.36).
   The correction moved the ratio toward the steady element by a quarter,
   which is the size of the acetylene overstatement the old march carried.
2. Peak decides, higher peak less benzene: survives. Ratio 0.60 at 1534 C,
   0.41 at 1800, 0.37 at 2595, 0.28 at 2340, 0.25 at 2707, 0.21 at 3063.
   The one out-of-order pair, 2 s at 2595 C above 1 s at 2340 C, was out
   of order on the old march too (0.41 against 0.26 then, 0.37 against 0.28 now); the 2 s case has a
   235 C floor and spends most of its cycle below reaction, so it is the
   least peak-like of the family.
3. At fixed peak the shape sets conversion, not selectivity: survives for
   the four approved shapes. Pulse benzene 18.4 to 21.3 percent, acetylene
   63 to 66, across conversion 7.1 to 37.6 percent. The unapproved 0.2 s
   case breaks the pattern (benzene 15.9 at 74 percent conversion), and it
   does so because its floor is 1135 C: the vessel never cools, so it is a
   near-steady 1400 C reactor, not a pulse. That is a boundary of the claim
   rather than a counterexample, and it is stated as such in the document.

## Screen

`series_pulse.py` on the lumped constants of `data/lump/aramco-ch4-he.json`
was run over the same knobs first. Its two activation energies are equal
(368 and 362 kJ/mol above 1300 C), so it cannot express the low-temperature
benzene the steady element makes and its ranking is not used to choose or
exclude cases here.
