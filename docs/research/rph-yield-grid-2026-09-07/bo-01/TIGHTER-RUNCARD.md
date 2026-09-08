# Tighter integration diagnostic

Continue the first EI candidate with a separately recorded diagnostic. Change only relative solver tolerance from 1e-9 to 1e-11. Preserve eight cycles, absolute tolerance, reactor closures, waveform, pressure control, preconditioner and all acceptance thresholds. Run 400 then 800 samples per segment; stop at the first failure. One CPU thread, 300 seconds total, 140 seconds per child. Charge failed work to the existing 3600-second ledger. No downstream BO or automatic training admission.

Inputs come from proposal.json: 1682.14294405234 °C peak, 0.80 s hold, 12.5 sccm, equimolar undiluted feed. Existing nonreacting and reacting checks remain archived in the pilot. This diagnostic tests numerical output stability, not new chemistry or a changed objective.

Store manifests, logs, diagnostics, paired outputs and gate status under tighter-01. Preserve the failed original verification. Successful pairing still requires review of tolerances and comparison with the prior coarse result before dataset admission. No existing figure is invalidated until a new accepted result is added.
