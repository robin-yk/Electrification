# Boundary test stopped before a reacting result

The 2100 C inert control passed. The 1900 C, .80 s, 50 sccm reacting
400-sample worker reached its 100-second timeout with an empty log and no
completed-cycle diagnostic. No 2000 or 2100 C reacting job was started.
No new yield is accepted. Existing 1800 C data remain unchanged.

See data/status.json for measured batch wall time and data/manifest.json
for source hashes. The campaign ledger charges this failed attempt.
Do not attribute the timeout to kinetics without locating the execution stage.
A separate report process also stalled before producing output while loading
the mechanism and was terminated. Mechanism initialization should be timed
separately before any reviewed retry. No tolerance or time cap was relaxed.
