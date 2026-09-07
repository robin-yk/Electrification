# Small-volume absolute-tolerance diagnosis

The mole reactor's amount scale decreased with volume from 1 m3 to about
9e-9 m3, while the absolute mole tolerance stayed 1e-15. Hypothesis: numerical
noise at the smaller state scale prevents the 1e-8 stationarity gate.
Diagnose one 1:1 condition with nominal atol and with atol scaled by V/1 m3.
Keep rtol, closure, physical conditions and stationarity threshold unchanged.
This tightens the numerical requirement; it does not relax the scientific gate.
Save histories before assertions, including pressure, mass, major species,
outlet/inlet flow ratio, total moles and solver statistics. If the scaled case
passes, compare every species mol/feed-C to the archived anchor within 1e-5.
No downstream feed-ratio calculation is allowed by this diagnostic script.
Reserve 140 s total, at most 60 s per worker, single-thread, no automatic retry.
