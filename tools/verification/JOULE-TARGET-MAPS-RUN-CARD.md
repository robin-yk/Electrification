# Target-temperature capacity maps

Author requested three Fig. 3 maps after agreeing to compare available element
power with required heat at 1200 C. Three fixed 41 by 41 maps (5043 evaluations)
plus six pilot checks; expected under one minute, hard stop at one minute.
No optimization, training, new solver or chemistry. Density is for smooth map
rendering and contour location, not a statistical inference. No adaptive growth.

Closures: existing 0D enclosure network and electrical operating point. Porous
SiC skeleton properties, 50% porosity, zero contact resistance, default quartz
wall and purge. No reaction heat, channel flow, leads or controller dynamics.
Target power ratio is evaluated at 1473.15 K, not inferred from a hotter root.
Fixed anchor: 40 cm3 envelope, L/D 30, 150 V / 40 A / 2 kW.
Resistivity axis varies only target resistivity; all other properties stay fixed.
Supply map keeps the 2 kW cap and preset current-density ceiling.

Reuse unchanged solver hash and existing nonreacting analytic/grid verification.
Reacting mass/elemental checks do not apply. First check the public calculate
API and cases on either side of capacity ratio one; verify current threshold.
Stop on invalid inputs, nonfinite values, failed brackets or cost gate.
Results: docs/research/joule-v6-2026-09-07/target-maps.json, complete inputs,
ratios and operating quantities, hashes and preserved pilot. No existing data
overwritten. Only Fig. 3 and its explanation are invalidated.

Run: node tools/verification/joule-target-maps.mjs
