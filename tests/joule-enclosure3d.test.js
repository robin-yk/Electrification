import test from 'node:test';
import assert from 'node:assert/strict';
import {MATERIALS, calculate, solveThermal2D, solveTransient2D, operating2DAt,
  multiply2DSystem} from '../apps/joule/solver.js';
import {buildEnclosure3D, solveEnclosure3D, assembleEnclosure3D,
  solveEnclosureElectrical} from '../apps/joule/3d/enclosure.js';

const cfg={nr:16,nz:12,nAir:4,nAirZ:2,nt:4,wallMaterial:'quartz',wallK:1.4,
  wallThickness:.002,wallEmissivity:.93,gap:.001,gapK:.03,endMode:'ambient',
  endK:298.15,endH:200,contactRho:1e-7,currentField:true,maxIter:240,tolerance:1e-5};
const x={shape:'cylinder',material:MATERIALS[1],solidFraction:1,volumeCm3:1,aspectRatio:3,
  imax:20,vmax:100,pmax:20,supplyMode:'auto',ambientK:298.15,targetK:900,
  emissivity:.8,convection:true,h:15,gasK:298.15,biLimit:.1,enclosure:cfg};

test('Enclosed 3D reproduces the full 2D steady operator and loss channels',t=>{
  const a=solveThermal2D(x,calculate(x),cfg,x.material),b=solveEnclosure3D(x,cfg);
  assert.ok(a.converged && b.converged);
  assert.ok(Math.abs(a.avgK-b.avgK)<.003,`${a.avgK} vs ${b.avgK}`);
  assert.ok(Math.abs(a.heOutletK-b.loss.gasOutletK)<.003);
  for(const key of Object.keys(a.lossByChannel))assert.ok(Math.abs(a.lossByChannel[key]-b.loss.byChannel[key])<1e-4,key);
  assert.ok(b.closure<1e-5);
  assert.ok(b.op.pContact>0);
  assert.ok(b.op.electrical.chargeError<1e-7);
  assert.ok(Math.abs(b.op.qCell.reduce((s,q)=>s+q,0)-b.op.pBulk)<1e-9);
  t.diagnostic(JSON.stringify({deltaMean_K:b.avgK-a.avgK,deltaGas_K:b.loss.gasOutletK-a.heOutletK,closure:b.closure}));
});

test('Angular faces transport heat conservatively, not independent 2D copies',()=>{
  const d=buildEnclosure3D(x,cfg),T=new Float64Array(d.count).fill(400);
  const base=assembleEnclosure3D(T,x,cfg,d,{pBulk:0});
  const angular=base.edges.filter(([p,q])=>Math.floor(p/d.ns)!==Math.floor(q/d.ns));
  assert.equal(angular.length,d.count);
  const system={diag:new Float64Array(d.count),rhs:new Float64Array(d.count),edges:angular};
  for(const [p,q,G] of angular){system.diag[p]+=G;system.diag[q]+=G;}
  const uniform=new Float64Array(d.count);multiply2DSystem(system,T,uniform);
  assert.ok(Math.max(...uniform.map(Math.abs))<1e-8);
  T[0]+=10;const residual=new Float64Array(d.count);multiply2DSystem(system,T,residual);
  assert.ok(residual[0]>0 && residual[d.ns]<0);
  assert.ok(Math.abs(residual.reduce((s,v)=>s+v,0))<1e-8);
});

test('3D potential solves angular conductivity variation with charge closure',()=>{
  const d=buildEnclosure3D(x,cfg),T=new Float64Array(d.count);
  const variable={...x,material:MATERIALS[2]};
  for(let a=0;a<d.nt;a++)for(let p=0;p<d.ns;p++)T[a*d.ns+p]=350+60*a*(1+Math.floor(p/d.mesh.nr)/d.mesh.nz)+100*(p%d.mesh.nr)/d.mesh.nr;
  const op=operating2DAt(700,variable,d.g,cfg,variable.material);
  const e=solveEnclosureElectrical(T,variable,cfg,d,op);
  assert.ok(e.chargeError<1e-7);
  assert.ok(Math.abs(e.qCell.reduce((s,v)=>s+v,0)-op.pBulk)<1e-8);
  assert.ok(e.fieldResistance>0);
  assert.ok(e.J.some(j=>j>0));
});

test('Angular Fourier-mode conduction converges at second order',()=>{
  const errors=[];
  for(const nt of [8,16]){
    const d=buildEnclosure3D(x,{...cfg,nt}),m=d.mesh,T=new Float64Array(d.count);
    for(let a=0;a<nt;a++)T.fill(400+Math.cos((a+.5)*d.dtheta),a*d.ns,(a+1)*d.ns);
    const s=assembleEnclosure3D(T,x,cfg,d,{pBulk:0}),j=m.activeStart+1,i=3,p=j*m.nr+i;
    let action=0;
    for(const [a,b,G] of s.edges)if(Math.floor(a/d.ns)!==Math.floor(b/d.ns)){
      if(a===p)action+=G*(T[a]-T[b]);if(b===p)action+=G*(T[b]-T[a]);
    }
    const exact=x.material.k/m.centers[i]**2*Math.cos(d.dtheta/2);
    errors.push(Math.abs(action/(m.cellVolume(i,j)/nt)/exact-1));
  }
  assert.ok(errors[0]/errors[1]>3.8 && errors[0]/errors[1]<4.2);
});

test('Porous current redistribution and electrode boundaries retain 2D parity',()=>{
  const c={...cfg,porosityContrast:.4,endMode:'electrode',endK:350};
  const porous={...x,solidFraction:.7,enclosure:c};
  const a=solveThermal2D(porous,calculate(porous),c,porous.material),b=solveEnclosure3D(porous,c);
  assert.ok(a.converged);
  assert.ok(Math.abs(a.avgK-b.avgK)<.005);
  assert.ok(b.closure<1e-5);
});

test('Temperature-dependent transient carries wall/gas storage and matches 2D',()=>{
  const variable={...x,material:MATERIALS[2]},plan={study:'transient',dt:.1,duration:.3,startK:500};
  const a=solveTransient2D(variable,calculate(variable),cfg,variable.material,{dt:.1,steps:3,startK:500,picardMax:100,picardTol:1e-5});
  const b=solveEnclosure3D(variable,cfg,plan);
  assert.ok(a.converged);
  assert.ok(Math.abs(a.avgK-b.avgK)<.002,`${a.avgK} vs ${b.avgK}`);
  assert.ok(b.worstClosure<1e-4);
  assert.ok(Math.abs(b.integratedResidual)<1e-4);
  assert.ok(b.wallAvgK!==500);
});

test('Pulse edges preserve short on-windows and account separately for contacts',()=>{
  const b=solveEnclosure3D(x,cfg,{study:'transient',dt:.19,duration:.5,period:.5,duty:.1});
  assert.ok(Math.abs(b.inputEnergy+b.contactEnergy-20*.05)<1e-7);
  assert.ok(b.inputEnergy>0 && b.contactEnergy>0);
  assert.ok(Math.abs(b.integratedResidual)<1e-4);
  assert.ok(b.history.some(h=>h.pBulk===0));
});

test('Unsupported geometry, bad mesh and invalid initial fields are rejected',()=>{
  assert.throws(()=>buildEnclosure3D({...x,shape:'box',lengthMm:20,widthMm:5,heightMm:2},cfg),/cylinder/);
  assert.throws(()=>buildEnclosure3D(x,{...cfg,nt:1}),/Angular/);
  assert.throws(()=>solveEnclosure3D(x,cfg,{startField:[300]}),/Initial field/);
});
