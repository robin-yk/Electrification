# Match 39 RPH methane conversions by steady temperature only

User approved comparing all 39 validated 450 C RPH points with CJH. Preserve
each feed, total standard flow, fixed volume, pressure and mechanism. Set
steady gas temperature as the sole search variable. Keep K=1e-7 to match
RPH pressure regulation; residence time is an output, not independently fixed.
Use the established sparse mole CSTR with volume-scaled tolerance. No energy,
device, diffusion or equal-power claim. The prior 600 C pulse series is excluded.

Freeze inventory from observations-39.json and check raw SHA256. Target methane
conversion is 1 minus outlet CH4 divided by inlet CH4, on the existing RPH
cycle-integrated basis. Bracket CJH between 450 C and the RPH peak, then use
Brent root search. Failure to bracket or converge stops the batch. This is a
bracketed solution, not proof that all possible steady states were explored.
Final CJH must pass stricter integration and all-species agreement <1e-5;
conversion error <max(1e-7, target*1e-4). Existing steady mass/element and
pressure checks remain unchanged. Preserve diagnostics and stop on failure.

Report C2H2, C2H4, C2H6, benzene, all six-carbon species and CO yields on total
inlet carbon. Flag very small targets when the RPH 400/800 phase difference is
more than one tenth of the target. Those comparisons are numerically qualified,
not evidence of a robust selectivity advantage. Do not silently correct RPH
conversions or redefine the yield denominator.

Pilot first passes the cold analytic control and archived 1750 C steady
reproduction with the matched pressure coefficient. Then: lowest-conversion
1200 C/.025 s/50 sccm, high-conversion 1800 C/.5 s/50
sccm, and 1800 C/.5 s/1600 sccm. Cap 240 s. Review runtime before batches of
12 remaining matches, each max 450 s and within the remaining cumulative
budget. Previous steady evaluations took seconds; the root count and pilot
time determine whether all 39 fit. Reuse exact-temperature cache only under
identical solver/mechanism hashes. Each match worker max 180 s, no retries.

Commit generator/card before pilot. Raw steady trials, RPH source ids, root
result, strict check, timing and hashes live under cjh-rph-match-{stage}-2026-09-07.
The completed outputs must be committed before follow-on, with budget reconciled.
Do not claim all 39 complete unless 39 verified match files exist.
