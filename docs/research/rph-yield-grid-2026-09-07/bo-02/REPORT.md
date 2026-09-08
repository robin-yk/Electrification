# Second sequential acetylene-yield observation

NEXTorch refitted 68 source-hashed observations, including the reviewed first recommendation. The objective, normalized inputs, log-flow transform, bounds and EI acquisition remain unchanged. The new model and development predictions are preserved separately from bo-01.

| Quantity | Result | Source |
|---|---:|---|
| Peak temperature, °C | 1824.20086635493 | proposal.json |
| Hot hold, s | 0.80 | proposal.json |
| Flow, sccm | 66.09954569850409 | proposal.json |
| Predicted carbon yield, % | 17.516468048095703 | proposal.json |
| Posterior SD, percentage points | 0.21580620110034943 | proposal.json |
| Verified carbon yield, % | 17.561701406115336 | verification/gates.json |
| Prior best, % | 17.58552665564628 | proposal.json |
| Paired species difference | 6.973513875518922e-6 | verification/gates.json |
| Fit/search time, s | 7.937600958975963 | propose-run.json |
| Direct verification time, s | 18.682591986000006 | verify-run.json |

The paired 400/800 calculation passes the unchanged threshold of 1e-4 and the worker's periodic, temperature, pressure, mass and elemental gates at rtol=1e-11. Accept the n800 observation for the next fit. It does not improve the prior best. The 68-point GP is the model that selected this point; it has not been refitted to 69 points. No third recommendation has been generated.

The 12-point development RMSE is 0.12186 percentage points. Changing dataset length changed the sampled holdout indices, so this is not a fixed-test learning curve and should not be compared as such with the first fit. The holdout is not independent chemical validation. The GP can predict slightly negative yields near zero; it is not a positivity-constrained model.

Actions run: 34179969782. The manifest records the committed generator and source hashes. The local proposal driver initially failed before fitting because it imported Cantera into the separate NEXTorch environment; lazy chemistry imports corrected that bookkeeping issue. This failure launched no chemistry or training. The ledger includes successful fit and verification elapsed times. Raw original observations, models and failed first-round integration remain preserved.
