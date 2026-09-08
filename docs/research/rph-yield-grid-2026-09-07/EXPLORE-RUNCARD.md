# In-domain exploration after two EI recommendations

Question: do unobserved parts of the existing domain warrant moving away from the incumbent neighborhood? Fit NEXTorch to 69 reviewed observations, preserving all earlier fits. Keep temperature bounds 1400–2000 °C, hot hold 0.10–0.80 s, log-flow 12.5–200 sccm, fixed volume and equimolar undiluted feed. The 450 °C floor, 1 s period, 0.025 s rise and 0.10 s fall remain unchanged.

Select from 8192 seeded Sobol points plus the 27 coarse-grid nodes. First maximize posterior SD among candidates at least 0.10 normalized Euclidean distance from every training point. Then select the point maximizing distance to the training set and the first new point. Distance uses scaled temperature, scaled hot hold and scaled log-flow, not physical Euclidean units. These are exploration policies, not EI optima or assurances of high yield. No domain expansion or extrapolation is allowed.

Fit/search cap 120 s. Verify two points sequentially with 400/800 samples, rtol=1e-11, eight cycles and all unchanged gates. Four children at most, 120 s each, aggregate 540 s, single CPU thread. Stop on the first failed gate and preserve any completed pair. Use the existing ledger. No third proposal or automatic expansion follows this batch.

Outputs: explore-01 model, source-hashed 69-point training data, predictions, distances, selection seed, paired verification and budget record. Existing pilot nonreacting and reacting checks are inherited because the closures do not change. Failed integration is not assigned zero yield. All source and run-card changes precede execution. This two-point diagnostic is not a learning curve or a proof of global optimization.
