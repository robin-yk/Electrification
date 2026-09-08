# First yield recommendation: tighter-integration review

Source: GitHub Actions run 34179234081, code commit 9966749. Raw gates and histories are stored alongside this review. Diagnostic runtime was 17.771375989 seconds; the ledger includes it.

Both phase resolutions passed the unchanged periodic-output, endpoint, temperature, pressure, mass and elemental criteria. The n800 calculation reached acceptance at cycle 3. Its final output change was 1.1057812998593874e-10. The 400/800 all-species difference was 4.830626203933264e-5, below 1e-4. Difference against the original rtol=1e-9 coarse calculation was 4.830709578096393e-5, also below 1e-4. Relative integration tolerance alone changed to 1e-11; no gate or cycle limit was relaxed.

The verified acetylene carbon yield is 17.326936678592897%, below the existing accepted best of 17.5855315572958%. The candidate provides a valid new observation but no improvement. This outcome is consistent with integration sensitivity in the original failure; it does not by itself isolate the numerical error source.

Accept the n800 result for the next training update after this review. The original training.json and saved GP remain the original 67-point fit; they have not yet been overwritten or refit. The diagnostic gate file intentionally retains admit_training=false to distinguish its automatic output from this subsequent review. Preserve all original failed logs. The next fit must record this source hash and its tighter tolerance.
