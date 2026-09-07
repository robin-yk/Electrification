import { test } from 'node:test';
import assert from 'node:assert/strict';
import { importDesign } from '../apps/joule/3d/import-design.js';
import { MATERIALS } from '../apps/joule/solver.js';

const base = {material:MATERIALS[1],solidFraction:1,porosity:0,shape:'box',
  lengthMm:40,widthMm:10,heightMm:2,volumeCm3:0.8,aspectRatio:1.5,
  imax:20,vmax:100,pmax:2000,supplyMode:'cv',vset:8,iset:10,
  ambientK:298.15,targetK:1000,emissivity:0.8,convection:true,h:15,biLimit:0.1};
test('3D import preserves rectangular dimensions, supply and SI resistivity',()=>{
  const p=importDesign(base);
  assert.equal(p.shape,'block');assert.equal(p.length,40);assert.equal(p.height,2);
  assert.equal(p.rho,MATERIALS[1].rhoOhmCm*0.01);
  assert.equal(p.mode,'V');assert.equal(p.command,8);assert.equal(p.ambient,25);
});
test('3D import rejects porous geometry instead of silently changing inventory',()=>{
  assert.throws(()=>importDesign({...base,solidFraction:0.5,porosity:0.5}),/dense element/);
});
test('3D import preserves constant-current command',()=>{
  const p=importDesign({...base,supplyMode:'cc'});
  assert.equal(p.mode,'I');assert.equal(p.command,10);
});
test('3D import uses a stated constant-property approximation for tabulated materials',()=>{
  const p=importDesign({...base,material:MATERIALS[2]});
  assert.equal(p.alpha,0);assert.ok(p.rho>0);assert.ok(p.rho<MATERIALS[2].rhoOhmCm*0.01);
});
