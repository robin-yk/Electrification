# Remote fixed-volume feed-ratio pilot: stationarity gate failed

GitHub run 34138476177, source commit 6e69f95. User explicitly requested
continuation after the local timeout. The remote environment completed loading
and all 100 Aramco anchor observation blocks in about four seconds, then failed
the stationarity assertion. Cold GRI passed. Tight-anchor and four other feed
ratios were not executed. No physical feed-ratio results are available.

Charge data/status.json wall_s to the campaign, including all failed work.
The log identifies stationarity as the failed gate, but the worker did not
persist its per-block history before asserting. Consequently the available
archive cannot distinguish residual size, pressure-controller noise, or a
physical/nonphysical oscillation. Diagnose with persisted histories before
another scientific batch. Do not relax the threshold or call the result physics
without that evidence. No automatic retry after this scientific gate failure.
