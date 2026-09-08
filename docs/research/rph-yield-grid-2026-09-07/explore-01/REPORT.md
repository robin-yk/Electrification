# Two in-domain exploration observations

These points were selected by posterior uncertainty and maximin distance, not EI. Both pass the unchanged 400/800 phase gate and worker convergence/closure gates. No new best was found.

| Selection | Peak °C | Hold s | Flow sccm | Predicted yield % | Calculated yield % | Phase error |
|---|---:|---:|---:|---:|---:|---:|
| max_posterior_sd | 2000.00 | 0.10 | 12.50 | 4.36039 | 1.93978 | 9.7737738e-05 |
| maximin_distance | 2000.00 | 0.80 | 12.50 | 12.33871 | 9.89514 | 4.7090095e-05 |

The short-hold point is within 10% of the phase-error threshold and retains a warning. Passing this absolute gate does not establish tighter relative precision for a minor product. Both calculations overpredict acetylene in the GP, showing that the unobserved corner was less accurately predicted than the second EI neighborhood. Two observations do not establish full-domain model accuracy or rule out undiscovered maxima.

The 69-point model is preserved. observations-for-next-fit.json contains 71 source-linked observations for a future fit; no 71-point GP has been trained. No third point was run. Raw results, manifest and budget are committed. Actions run: 34180507103.

Direct calculation elapsed time: 40.814 s.
