# Second acetylene-yield recommendation

Fit the original 67 points plus the reviewed first recommendation. Keep NEXTorch GP, EI, normalized temperature and hot hold, logarithmic flow, bounds and waveform unchanged. The development split is explicitly not a sealed test. Save a new 68-point training snapshot, model, acquisition audit and proposal in bo-02; preserve bo-01.

One fit/search capped at 120 s, then one 400/800 pair capped at 300 s with 140 s per child, single thread. Use rtol=1e-11, as tested by the first recommendation diagnostic. Keep eight cycles and every original numerical gate. Stop on failure, charge elapsed time to the existing ledger, and do not generate a third point automatically. This run estimates the value of one sequential observation; it cannot demonstrate a global optimum or superiority to random search.
