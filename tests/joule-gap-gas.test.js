// The gap gas conducts as the gas the page names, at its own temperature.
//
// Before 2026-09-06 the gap, the pore gas and the He purge cells all used one
// constant cfg.gapK shipped at 0.03 W/m·K, which is air near room temperature.
// The page called the gas helium. This test pins the model that replaced it and
// the one number that exposed the problem: the Mittal (2025) CFP strip at the
// paper's effective 29.1 V settles at 1783 C with air in the gap and at 1517
// to 1532 C in the paper's CFD; helium at its film temperature brings the 0D
// model to within 60 K of the paper.
import test from "node:test";
import assert from "node:assert/strict";
import { calculate, kelvin, celsius, gasConductivityAt, gapConductivity,
  enclosureHeatLoss, geometry, validate2DConfig, GAP_GASES } from "../apps/joule/solver.js";

const MITTAL_CFP = { name:"CFP (Mittal 2025, Table 1 at ~1800 K)", rhoOhmCm:123.4e-6*100, density:452, cp:2110, k:400, jmax:1e9, emissivity:0.85 };
const enclosure = (extra) => ({ wallMaterial:"quartz", wallK:1.4, wallThickness:0.001, wallEmissivity:0.93,
  gap:0.0005, gapK:0.03, endMode:"ambient", endK:kelvin(20), endH:250, contactRho:0, maxIter:160, tolerance:1e-4, ...extra });
const mittal = (extra) => ({ shape:"box", lengthMm:38, widthMm:8, heightMm:0.21, material:MITTAL_CFP, solidFraction:1, porosity:0,
  imax:100, vmax:100, pmax:2000, supplyMode:"cv", iset:100, vset:29.1, ambientK:kelvin(20), targetK:kelvin(1500),
  emissivity:0.85, convection:false, h:0, gasK:kelvin(20), biLimit:0.01, enclosure:enclosure(extra) });

test("helium, air and argon conductivities match the tabulated values to 5 percent", () => {
  // NIST / Petersen (1970), W/m·K
  const table = { helium:[[300,0.155],[1000,0.36],[1500,0.48],[2000,0.58]], air:[[300,0.026],[1000,0.068]], argon:[[300,0.0177],[1000,0.043]] };
  for (const [gas, rows] of Object.entries(table)) for (const [T, k] of rows) {
    const model = gasConductivityAt(gas, T);
    assert.ok(Math.abs(model - k) / k < 0.05, `${gas} at ${T} K: model ${model.toFixed(4)} against ${k}`);
  }
  assert.ok(Number.isNaN(gasConductivityAt("custom", 500)));
  assert.equal(GAP_GASES.custom, null);
});

test("a configuration without gapGas keeps the constant gapK, so saved cases do not move", () => {
  const cfg = enclosure({});
  assert.equal(gapConductivity(cfg, 300), 0.03);
  assert.equal(gapConductivity(cfg, 2000), 0.03);
  assert.equal(gapConductivity(enclosure({ gapGas:"custom", gapK:0.2 }), 1500), 0.2);
  assert.deepEqual(validate2DConfig(enclosure({ gapGas:"helium", gapK:undefined })), []);
  assert.ok(validate2DConfig(enclosure({ gapGas:"neon" })).some((e) => /Unknown gap gas/.test(e)));
  assert.ok(validate2DConfig(enclosure({ gapK:0 })).some((e) => /Gap conductivity/.test(e)));
});

test("the Mittal CFP strip at 29.1 V: helium in the gap moves 0D from 1783 C to within 60 K of the paper", () => {
  const air = calculate(mittal({}));
  const helium = calculate(mittal({ gapGas:"helium" }));
  assert.equal(air.errors.length, 0); assert.equal(helium.errors.length, 0);
  assert.ok(Math.abs(celsius(air.tss) - 1783) < 5, `air: ${celsius(air.tss)} C`);
  // Paper (CFD, He at 90 mL/min): 1790 to 1805 K, 1517 to 1532 C.
  assert.ok(celsius(helium.tss) > 1500 && celsius(helium.tss) < 1590, `helium: ${celsius(helium.tss)} C`);
  assert.ok(celsius(air.tss) - celsius(helium.tss) > 180, `gas change moved ${celsius(air.tss) - celsius(helium.tss)} K`);
  // Same electrical power in both: the supply is the same, the gas only changes where the heat goes.
  assert.ok(Math.abs(air.steadyLoss.total - helium.steadyLoss.total) < 1);
});

test("the gap resistance is evaluated at the film temperature, so a hotter gap conducts more", () => {
  const x = mittal({ gapGas:"helium" }), g = geometry(x);
  const cold = enclosureHeatLoss(kelvin(600), x, g), hot = enclosureHeatLoss(kelvin(1600), x, g);
  const kCold = gasConductivityAt("helium", (kelvin(600) + cold.wallK) / 2), kHot = gasConductivityAt("helium", (kelvin(1600) + hot.wallK) / 2);
  assert.ok(kHot > 1.4 * kCold, `k_film cold ${kCold.toFixed(3)} hot ${kHot.toFixed(3)}`);
});
