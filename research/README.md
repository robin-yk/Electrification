# Research entry points

Research is organized by question. Original batch files remain under their existing paths so source hashes and reproduction commands remain usable.

- [GRI CJH-to-RPH surrogate](01-gri-cjh-rph-surrogate/README.md): How accurately can a steady-state atlas approximate transient conversion and product yields?
- [Aramco product-composition design](02-aramco-product-design/README.md): Which continuous or pulsed conditions produce acetylene and CO at a requested outlet molar ratio?
- [Feed and mechanism comparisons](03-feed-mechanism-effects/README.md): How do oxidant, dilution and mechanism choice change the predicted product distribution?
- [Energy and multiobjective Pareto analysis](04-energy-pareto/README.md): Which operating points balance acetylene yield, energy productivity, reaction heat fraction and product ratio?

- [Complete batch inventory](BATCHES.md)
- [Integration and migration record](../archive/README.md)
- [ScreenJoule](https://github.com/robin-yk/ScreenJoule): heater-design development.

A batch can support several questions. The inventory assigns one primary reading route without duplicating its data. Execution status does not establish numerical or experimental validation. Read each batch's gates and provenance.

Regenerate the inventory with `node research/build-index.mjs` after adding an archive.
