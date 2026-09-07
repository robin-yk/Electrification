# Diagnosed absolute mole tolerance at small reactor volume

Run 34139030070; generator a80d36c. See data/status.json and each diagnostic
history for exact values. Nominal absolute tolerance 1e-15 failed stationarity.
With the same physical model, relative tolerance and stationarity criterion,
scaling atol by volume/1 m3 passed stationarity and all worker flow/elemental
gates. The resulting full-species mol/feed-C comparison passed the archived
anchor threshold. This supports numerical absolute-tolerance scaling as the
cause of the failed small-volume anchor, not a physical oscillation claim.

Only this anchor has been diagnosed. The remaining feed ratios still require
the corrected numerical setting and a stricter paired verification. No ratio
results are implied. The two-run elapsed time is charged to the campaign.
