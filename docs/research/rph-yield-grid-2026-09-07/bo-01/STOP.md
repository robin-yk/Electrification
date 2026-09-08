# Direct verification did not pass the periodic-output gate

The first EI recommendation passed development prediction and acquisition
checks. The 400-sample calculation passed. The 800-sample calculation reached
eight cycles without two consecutive output changes below 1e-7. Its last
change was 1.8514211067022224e-7; endpoint state change was about 4.1e-12.
Temperature, pressure and mass/element checks passed. This repeats the
low-flow integrated-output stability issue seen in the earlier grid, not
a demonstrated physical instability. No verified yield is admitted.

Preserve both attempts and the model. Do not relax the acceptance threshold,
silently increase cycle count, or assign a zero yield to the failed point.
A separately reviewed tighter-integration or quadrature diagnostic is needed
before this recommendation can enter the accepted training table. No second
recommendation has been generated. Existing best accepted yield is unchanged.
