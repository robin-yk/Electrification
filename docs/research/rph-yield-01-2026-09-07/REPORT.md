# Acetylene yield optimization: recommendation rejected

The single objective is C2H2 carbon yield as percent of total inlet CH4+CO2 carbon. The 39 validated conditions are reused with unchanged input bounds.

The frozen recommendation was 1200 C, hold 0.025 s and 1600 sccm. Predicted yield was 0.200363%, not an Aramco result.

| Acquisition diagnostic | Standardized expected improvement |
|---|---|
| Chosen point | 0.000119602402 |
| Existing incumbent | 0.00290472526 |
| Best of 2048 deterministic Sobol checks | 0.00867192913 |

The selected point scores below readily available alternatives under the same frozen model and acquisition function. The initial explanation based only on uncertainty was insufficient. Acquisition maximization has failed this quality check; no reaction calculation was dispatched.

The verified incumbent remains 11.173435% at 1800 C, 0.5 s hold and 50 sccm. There are still 39 validated 450 C observations.

Preserve this attempt. Before a reviewed retry, improve acquisition initialization/search and require its score to equal or exceed the incumbent and a deterministic reference search. Do not alter chemical gates or report the audit grid point as an optimized or chemically evaluated condition.
