# Return to EI after two exploration observations

Fit NEXTorch to 71 source-hashed observations, including the separately labeled exploration batch. Keep objective, domain, waveform and reactor closures unchanged. Retain the short-hold exploration phase-error warning. This fit uses the passing observation at its existing numerical tolerance; it is not an uncertainty-aware numerical-noise model.

Select one EI candidate with the existing seeded search, independent acquisition comparison and duplicate gate. One fit/search capped at 120 s, one 400/800 direct verification capped at 300 s, 140 s per child, one thread. Use rtol=1e-11 and unchanged eight-cycle and acceptance criteria. Stop on failure, record elapsed time in the existing ledger, preserve bo-01/02 and explore-01. No automatic fourth recommendation. Store all round-three files in bo-03. Do not claim convergence or global optimality from this step.
