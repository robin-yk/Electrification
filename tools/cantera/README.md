# Cantera precompute pipeline

Generates `apps/rphcjh/data/cantera.json`: detailed-mechanism reference data
that the RPH vs CJH visualizer shows as a cross-check next to its
lumped-parameter model. Nothing on the site runs Python (GitHub Pages only
serves static files), so all Cantera work happens here (offline or in CI) and
only the JSON result ships.

## What is computed

For each mechanism, over a 400–1400 °C grid at 1 atm with a CH4:CO2 = 1:1 feed:

- `keff_1_s`: effective first-order CH4 consumption rate at the fresh feed
  (initiation-limited; a reproducible metric, not a conversion prediction)
- `Ea_eff_kJ_mol`: Arrhenius fit of that rate over 1000–1400 °C, to compare
  with the app's lumped default (422 kJ/mol)
- `D_ch4_m2_s`, `lambda_W_mK`, `mu_Pa_s`: mixture-averaged transport
  coefficients, with fitted power-law exponents `beta_*` to ground the app's
  β slider
- `eq_ch4_conversion`, `eq_ch4_molefrac`: constant-TP equilibrium of the
  closed feed (mass-fraction based, so conversion is exact)

## Mechanisms

- **GRI-Mech 3.0**: bundled with Cantera. Natural-gas combustion mechanism;
  not validated for oxygen-free pyrolysis above ~1200 °C. Kept as the
  zero-friction baseline.
- **AramcoMech 2.0** (`mechanisms/aramco20.yaml`): NUI Galway C0–C4
  mechanism with validated C2 chemistry, converted from the CHEMKIN
  distribution with `ck2yaml --permissive`. Redistribution follows the
  mechanism's free-for-research terms; cite the Aramco publications when the
  data is used in academic work.

To add a mechanism, drop its Cantera-format `.yaml` under `mechanisms/` and
append an entry to `MECHANISMS` in `precompute.py`.

## Usage

```bash
pip install -r tools/cantera/requirements.txt
python tools/cantera/precompute.py          # regenerate the JSON
python tools/cantera/precompute.py --check  # verify committed JSON is current
```

CI (`.github/workflows/cantera-data.yml`) runs the `--check` mode whenever
this directory changes, so a stale committed JSON fails the build instead of
silently drifting from the scripts.

## Transient cost pilot (AramcoMech 2.0)

`aramco_transient_pilot.py` answers the scoping question for a possible
Aramco extension of the transient pipeline in `tools/openmkm_dynamic/`: how
much slower is one pulsed-CSTR cycle under AramcoMech 2.0 than under
GRI-Mech 3.0, and how much does the sparse preconditioned solver
(`run_cstr_case.py --jacobian sparse`) recover? Results land in
`data/aramco-transient-pilot.json`; the ratios are the result, the absolute
seconds are machine-specific.

```bash
python tools/cantera/aramco_transient_pilot.py   # ~3 min, single thread
```

Measured 2026-09: Aramco costs 65-73x GRI per cycle on the dense path and
19-23x on the sparse path, with CH4 conversion agreeing between the two
paths to about 7 significant digits. At 20x, regenerating the full 349-case
transient ground truth projects to roughly 1.5 single-threaded days, and
the worst GRI case (251 s) projects to about 90 minutes, inside CI job
limits. The sparse path is for large mechanisms only: on GRI itself it is
30-75% slower than dense, so the canonical GRI pipeline stays on the
default dense path.

This is a cost pilot, not ground truth: it fixes a small cycle budget
instead of converging and replaces the stored element-drive waveform with a
trapezoid between the same temperature bounds. Nothing it produces may be
promoted to `tools/openmkm_dynamic/data/canonical/`.
