import assert from 'node:assert/strict';
import {solveModel} from '../apps/joule/3d/solver.js';
const base={shape:'block',length:40,width:10,height:2,bore:6,n:6,rho:1e-4,k:120,alpha:0,density:3210,cp:750,contact:100,offsetA:0,offsetB:0,mode:'V',command:8,vmax:50,imax:30,pmax:100,ambient:25,sink:25,h:15,emissivity:.8,hc:2000,maxTemp:2000,study:'steady',duration:2,dt:.25,period:1,duty:.5,initial:25};
const report=[];
function check(name,fn){const data=fn();report.push({name,pass:true,...data});console.log(name+': PASS',data);}
check('Uniform bar resistance, linear potential and conservation',()=>{
 const r=solveModel(base),expected=base.rho*.04/(.01*.002);
 assert(Math.abs(r.stats.R/expected-1)<1e-8);let error=0;
 r.mesh.xyz.forEach((q,i)=>error=Math.max(error,Math.abs(r.phi[i]/r.stats.V-(.5-q[2]/.04))));assert(error<1e-8);
 assert(r.stats.chargeError<1e-7&&r.stats.energyError<1e-6);
 const watts=r.q.reduce((s,q)=>s+q*r.mesh.vol,0);assert(Math.abs(watts/r.stats.P-1)<1e-7);
 return {R:r.stats.R,expected,heatResidual:r.stats.energyError};
});
check('Asymmetric electrode changes the 3D power distribution',()=>{
 const r=solveModel({...base,n:10,contact:30,offsetA:-40,offsetB:40});
 const ratio=Math.max(...r.q)/(r.stats.P/r.stats.volume);
 assert(ratio>1.5&&r.stats.R>.2);assert(r.stats.chargeError<1e-6&&r.stats.energyError<1e-5);
 return {R:r.stats.R,peakToMeanPowerDensity:ratio};
});
check('Thermal spatial refinement against parabolic solution',()=>{
 const errors=[];
 for(const n of [4,8]){
  const p={...base,n,mode:'P',command:1,h:0,emissivity:0,hc:1e8,k:20};const r=solveModel(p),q=1/r.stats.volume,A=.01*.002,L=.04;
  let e=0;r.mesh.xyz.forEach((xyz,i)=>{const z=xyz[2]+L/2,exact=25+1/(2*A*p.hc)+q*z*(L-z)/(2*p.k);e+=(r.T[i]-exact)**2;});errors.push(Math.sqrt(e/r.mesh.N));
 }
 assert(errors[0]/errors[1]>3.8&&errors[0]/errors[1]<4.2);return {rmsCoarse_K:errors[0],rmsFine_K:errors[1],ratio:errors[0]/errors[1]};
});
check('Adiabatic pulsed transient: integrated P equals stored heat',()=>{
 const p={...base,n:4,study:'transient',mode:'P',command:2,h:0,hc:0,emissivity:0,duration:1,dt:.19,period:.5,duty:.3};const r=solveModel(p),energy=.6;
 assert(Math.abs(r.stats.inputEnergy-energy)<1e-8);assert(Math.abs(r.stats.stored-energy)<1e-5);assert(r.stats.integratedError<1e-5);
 const expected=25+energy/(p.cp*p.density*r.stats.volume);assert(Math.abs(r.stats.avg-expected)<1e-5);
 return {input_J:r.stats.inputEnergy,stored_J:r.stats.stored,Tavg_C:r.stats.avg,expected};
});
check('Temperature-dependent resistivity and power-supply limits',()=>{
 const r=solveModel({...base,alpha:.001,n:6,mode:'I',command:40});
 assert(r.stats.R>.2&&r.stats.P<=100.000001&&r.stats.I<=30.000001&&r.stats.V<=50.000001);
 assert(r.stats.energyError<1e-5);return {R:r.stats.R,limiter:r.stats.limiter,heatResidual:r.stats.energyError};
});
check('Tube and rod resistance use the actual voxel cross-section',()=>{
 const values={};for(const shape of ['rod','tube']){const r=solveModel({...base,shape,n:8}),expected=base.rho*.04**2/r.stats.volume;assert(Math.abs(r.stats.R/expected-1)<1e-7);values[shape]=r.stats.R;}return values;
});


