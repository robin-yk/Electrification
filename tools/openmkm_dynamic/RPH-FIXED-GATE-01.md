# Fixed-volume RPH entry gate

User approved a minimal five-integration RPH sequence on 7 September 2026.
This batch executes only an inert analytic check and the reacting CJH limit.
Cap: 180 seconds, one thread. No downstream pulse dispatch on failure.

Use Aramco 2.0, 1750 C prescribed gas temperature, CH4/CO2 1:1,
50 sccm referenced to 273.15 K and 1 atm, the archived fixed gas volume,
constant inlet mass flow and the existing pressure controller K=1e-8.
The new reactor replaces the temperature derivative, leaving species and
volume equations unchanged. With slope zero it must reproduce the archived
fixed-volume CJH anchor within 1e-5 mol/mol inlet carbon for every species.
Reuse the existing stationarity, mass, pressure and elemental acceptance tests.
The inert closed ramp must preserve mass and volume and satisfy P/T=constant.

Generator, card and reservation are committed before dispatch. Outputs include
raw results, diagnostics, source hashes, gates and elapsed time including failures.
Store under docs/research/rph-fixed-gate-01-2026-09-07/data after completion.
This does not validate periodic integration, phase resolution, product integration,
experimental temperature equivalence, or an advantage of pulsed heating.
Existing CJH archives and manuscript figures are not invalidated or regenerated.
