# First acetylene yield recommendation

User approved proceeding with Bayesian optimization from accepted partial
grid and hot-boundary data. The previous complete-grid prerequisite is an
execution choice, not a statistical requirement; it is superseded here.
Keep failed grid and 2100 C points excluded and their stops preserved.

Fit 59 grid points, six accepted .20/.40-second points also inside the
continuous bounds, and two accepted high-temperature pairs: 67 in total.
The first inventory check stopped before model fitting because it expected
61 and omitted those six off-grid but in-domain points. This bookkeeping
correction preserves the failed preflight in preflight-01.json; no numerical
or model quality gate was changed.
Bounds: peak 1400 to 2000 C, hold .10 to .80 s, log flow 12.5 to 200 sccm.
All other closures are unchanged. Maximize total-feed-carbon C2H2 yield.
Do not mix productivity into the objective. Retain all off-domain data.

Reserve 120 seconds for NEXTorch fitting and audited multistart EI search.
Fixed seed 17 selects 12 development holdout points; require RMSE below
2 percentage points and maximum error below 5 points before full-data fit.
This is a predeclared engineering check, not experimental validation or a
sealed test. Save predictions and errors even on failure. Require independent
acquisition-quality, bounds and nonduplicate checks. Stop any failed gate.

Commit the recommendation before direct chemistry. Verify one recommendation
at 400 and 800 phase samples on Ubuntu with unchanged solver gates and
all-species difference below 1e-4. Reserve that verification separately from
the same remaining budget. Do not claim optimality from a single iteration.
