# Composition-constrained optimization

Authorization: user requested continued work toward the requested product-composition optimum and approved a new total 60-minute budget with at most 5 minutes per batch. Separate from prior ledgers. Count proposal fitting and successful/failed reaction runs. No automatic retries after failed gates.

## First stage

RPH at fixed 50 sccm, undiluted CH4/CO2, existing 0.009228 cm3 fixed volume and pressure controller. Mechanism, waveform closure and numerical gates unchanged from the passed four-condition support pilot. Floor 450 C, rise .025 s, fall .10 s, period 1 s. Allowed peak 1600-2000 C, hot hold .1-.8 s, methane fraction .5-.8. These bounds are a declared finite comparison domain, not all possible reactor operation.

Maximize total-feed-carbon acetylene yield at CO/C2H2 molar ratios 1, 1.5, 1.75 with relative tolerance 2%. Independent NEXTorch GP models predict the two carbon yields. Integrate expected improvement and ratio feasibility using the same acetylene draw; do not multiply marginal EI by an independent feasibility probability. Check acquisition against analytic limits, Monte Carlo integration and doubled quadrature order. Candidate-pool search uses saved seeds, includes hold-time faces, and excludes duplicates. Predictions do not establish optima.

Data selection: raw paired n400/n800 results at common closure; both must pass recorded periodic, element, mass, pressure and temperature gates. Recompute maximum species discrepancy below 1e-4. Deduplicate exact physical inputs. Preserve paths and both file hashes. Development holdout is the four new interaction points, not a sealed test. Stop if either output RMSE exceeds 10 percentage points; this loose preflight checks gross predictability and is not a publication accuracy claim. Posterior uncertainty and direct recommendation errors must be reported independently.

One recommendation per ratio is generated in the first round, then verified with paired direct runs in a separate batch. Stop on any gate failure. Preserve provenance, predictions, realized objective and feasibility separately. Three directly verified recommendations are only the first iteration, not proof of BO efficiency or convergence. CJH needs its own dataset, model and constrained search before heating-mode comparisons.

Reproducibility: commit generator and this run card before proposal or reaction execution; save training data, state dictionaries, seed, bounds, proposals, checks and budget. No electrical-energy inference is authorized by prescribed gas temperature. No reactor-closure changes.
