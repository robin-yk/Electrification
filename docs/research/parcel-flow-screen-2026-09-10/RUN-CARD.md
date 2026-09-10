# Fixed-volume flow pilot

Approved purpose: increase flow until acetylene production per input energy shows a sampled maximum and two consecutive decreases. Fixed 1500 C CH4 10%/He ideal-PFR material-history model. Derive one gas volume from 50 sccm and 40 ms, accounting for molar expansion. No new reactor geometry is inferred.

Flow candidates: 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800 sccm. Stop after two consecutive declines. Reuse the isothermal chemistry trajectory across flows through V = inlet molar flow * RT/P * integral(total moles / initial moles dt). The gas volume and assumed radiating area stay fixed. Reference thermal assumptions are the preceding 90%-reduced radiation scenario.

One nonreacting check and two reacting trajectories, with refined tolerances and quadrature. Require atom residual below 1e-6 mol on the one-mol CH4 basis, selected metric differences below 0.1 percentage point, and prior 1500 C endpoint agreement below 0.05 percentage point. Preserve selected full compositions, volume integral, checks, hashes, and report. No subsequent optimization is queued.

External cap 300 seconds including loading; expected under one minute from the preceding pilot. Launch through parcel_flow_screen.py. No earlier data or manuscript figures are invalidated.
