# Composition-only ratio bracketing

Question: do CH4 feed fractions 0.70 and 0.80 cross any target outlet CO/C2H2 molar ratios 1, 1.5 or 1.75? This is a two-point deterministic bracket extension, not Bayesian optimization or a dense screen. The user approved continuing after the verified 0.60 pilot. Existing 0.50 and 0.60 points give ratios 4.34343 and 2.72517, so neither brackets the targets. No learning curve or fitted-model accuracy is claimed from two points.

All other inputs retain the verified pilot values: 1800 C peak, 450 C floor, 0.80 s hold, 1 s period, 0.025 s rise, 0.10 s fall, total 50 sccm at 273.15 K and 101325 Pa, 1 atm target pressure, fixed gas volume 0.009228077898 cm3. Undiluted CH4/CO2, AramcoMech 2.0, prescribed gas temperature, unchanged pressure controller and periodic reactor closure. CFP normalization 0.0288 g. Composition-dependent mass flow preserves constant standard molar flow.

Entry requires the accepted 0.60 paired pilot and its phase gate. Four reacting integrations maximum, paired 400/800 phase samples, rtol 1e-11, unchanged element/mass/pressure/temperature and periodic gates. Maximum phase difference 1e-4. Stop before the next composition on any failure. Analytic inlet check in a 30 s child; each reacting child capped at 90 s; aggregate 300 s, below the authorized 600 s per-batch ceiling. Estimate roughly 40 s from the 17.69 s pilot, not a promise.

Output: feed-bracket-01/, source manifest and hashes, raw logs and all-species yields, phase gates, status, and updated shared budget. No overwrite of prior pilot outputs. No retry or third composition in this batch. Save completed and failed outputs durably before any next batch. No HTML optimum claim is invalidated: existing results remain composition-only observations.
