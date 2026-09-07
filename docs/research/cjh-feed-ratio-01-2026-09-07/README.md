# CJH feed-ratio pilot: stopped at the anchor

The user requested a CH4:CO2 Figure 2 at fixed temperature, volume and total
standard flow. Committed generator: 1b0d299. Local execution used Cantera 3.2.0,
one chemistry thread, a 540 s batch reservation and 100 s worker timeout.
The cold GRI control passed. The Aramco 1:1 anchor did not write a result
before its worker timeout. No subsequent jobs ran, no ratio yield is available,
and no fixed-volume equivalence claim passed. An empty anchor log does not
identify mechanism loading versus integration as the cause.

The authoritative elapsed calculation time is data/status.json wall_s; it is
charged in the campaign budget, including the timed-out work. There was no
automatic retry. The cold result, empty anchor log, manifest, gate file and
status are retained. Existing Aramco map outputs remain unchanged. Node
regression tests: 106 passed. This does not validate the new chemical closure.

Next diagnostic, before any further reaction execution: instrument stage
timestamps or inspect the runtime to distinguish loading and integration.
Do not silently extend worker caps or infer a physical failure from timeout.
