# RPH composition response at the equimolar incumbent

## Current execution gate

Remote retry explicitly approved after the local loading timeout. Output is now `feed-pilot-02/`; preserve `feed-pilot-01/` unchanged. Full mechanism loading for the inlet check runs in a subprocess with a 30 s timeout. Both reacting children retain 90 s limits and share the 180 s aggregate budget with that check. No automatic retry or additional composition follows this one paired point.

Only the 60% CH4 pilot is enabled: two 400/800-sample integrations, 180 s aggregate limit, 90 s per child. Expected calculation time is tens of seconds, but the cap is binding. Output: `feed-pilot-01/`. Review its closure, periodicity, and phase-resolution result before approving any remaining composition points. The six-point screen below is the proposed extent, not an enabled batch. This pilot is not Bayesian optimization. Existing 92 equimolar conditions were re-scored first in `ratio-scenarios-01/`; they do not validate this new composition axis.

Seven CH4 fractions: 20%, 33.3333%, 40%, 50%, 60%, 66.6667%, 80%. Reuse the source-hashed accepted 50% point. Calculate the other six as paired 400/800 integrations, stopping at the first failure. First pair is the reacting pilot; proceed only after its closure and resolution gates pass. The existing N2 nonreacting waveform verification is retained; analytic inlet checks explicitly confirm constant standard molar flow with composition-dependent mass flow.

Fixed: 1800 °C peak, 450 °C floor, hot hold 0.8 s, period 1 s, rise 0.025 s, fall 0.1 s, pressure target 1 atm, gas volume 0.009228077898 cm3, total 50 sccm at 273.15 K and 101325 Pa. Undiluted CH4/CO2. Both feed components contain one carbon atom, so total feed carbon equals total feed molar amount; conversions use each component's own inlet fraction. CFP normalization: 0.0288 g. Flow mass must change with composition, not remain fixed.

This is a new composition axis, not a four-dimensional optimized result or an automatic addition to the equimolar GP. Do not transfer feature importance or optimum claims. Report C2H2 and CO carbon yields and CFP-normalized productivities, with major other species and closure retained in data. Compare with CJH composition screen only with its distinct temperature history labeled.

Twelve integrations maximum, 90 s per child, 540 s aggregate, single thread. rtol=1e-11, eight cycles, original unchanged acceptance gates. Use the existing budget ledger and preserve all failures. No retries or further feed conditions without review. Source and run card committed before execution. Estimate about 2–4 minutes based on preceding paired timings; cap is a limit, not a promise of completion.
