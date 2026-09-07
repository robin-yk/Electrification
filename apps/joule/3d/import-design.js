import { geometry, propertiesAt, validateInput } from '../solver.js';

// Transfer a dense element with an explicit constant-property approximation.
export function importDesign(input) {
  const errors = validateInput(input);
  if (errors.length) throw Error(errors.join(' '));
  if (input.solidFraction !== 1) throw Error('3D import requires a dense element (void fraction 0). Porous homogenization is not implemented in 3D.');
  const g = geometry(input), p = propertiesAt(input.material, 298.15);
  return {
    shape: input.shape === 'box' ? 'block' : 'rod',
    length: g.L * 1000, width: (g.W || g.D) * 1000, height: (g.H || g.D) * 1000,
    rho: p.rhoOhmCm * 0.01, alpha: 0, k: p.k, cp: p.cp, density: input.material.density,
    vmax: input.vmax, imax: input.imax, pmax: input.pmax,
    mode: input.supplyMode === 'cc' ? 'I' : input.supplyMode === 'cv' ? 'V' : 'P',
    command: input.supplyMode === 'cc' ? input.iset : input.supplyMode === 'cv' ? input.vset : input.pmax,
    ambient: input.ambientK - 273.15, initial: input.ambientK - 273.15,
    h: input.convection ? input.h : 0, emissivity: input.emissivity,
    study: 'steady'
  };
}
