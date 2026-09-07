# Refinement 02 stopped at a comparison bookkeeping error

Run: https://github.com/robin-yk/Electrification-Suite/actions/runs/34085150481
Generation commit: fccd3ce. Raw status and outputs are retained unchanged.

The first gate passed. The second integration completed its convergence and
balance checks, but compare() required identical dictionary keys. The solver
exports species_out_kmol only for positive amounts. C8H131-5,3,TAO was present
at about 1e-31 mol/feed-C in the baseline and absent from the refined output.
The failure was not a reaction integration or material-balance failure.
No third gate or new map point ran. Only the first gate was accepted by the
original comparison code, as recorded in gates.json and status.json.

A failing-first regression test reproduces negligible positive-only omission.
The corrected comparison uses the species union; unmatched entries must be
<=1e-12 mol/feed-C and every absolute species/conversion difference must
still be <1e-5. Material omissions fail. Core chemistry solver unchanged.

Manual continuation, not an automatic retry: retain the charged elapsed time,
reserve a new bounded batch, verify this archive, copy only completed raw gate
files, and let the existing cache verifier check parameters, mechanism hash,
convergence and balances before reusing them. Recompute comparisons, perform
the third gate, then proceed to twelve new points only if all three pass.

Reproduction: python -m unittest discover -s tools/openmkm_dynamic -p
'test_cjh_refine_02.py'; raw times and completion are in data/status.json.
The scientific limitations of CJH-REFINE-02-RUN-CARD.md remain in force.
