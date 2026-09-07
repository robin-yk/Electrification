import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {calculate,solveThermal2D,solveTransient2D,operatingAt,MATERIALS} from '../../apps/joule/solver.js';
import {defaultInput} from './joule.mjs';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url);fs.mkdirSync(dir,{recursive:true});
const file=new URL('data.json',dir);if(fs.existsSync(file))throw Error('Preserve existing run; inspect its status before resuming.');
const start=performance.now(),sha=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out={commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),solverHash:sha(new URL('../../apps/joule/solver.js',import.meta.url)),generatorHash:sha(new URL('./joule-v6.mjs',import.meta.url)),status:'running',fields:[],transients:[],count0D:0};
const save=()=>{out.elapsedSeconds=(performance.now()-start)/1000;fs.writeFileSync(file,JSON.stringify(out));};
const check=()=>{if((performance.now()-start)>570000)throw Error('Budget stop');};
const grid=(a,b,n)=>Array.from({length:n},(_,i)=>a*(b/a)**(i/(n-1)));
const input=(V,ar,phi=.5,k=60)=>defaultInput({volumeCm3:V*(1-phi),solidFraction:1-phi,porousMode:'effective',effectiveK:k,aspectRatio:ar,vmax:150,imax:40,pmax:2000,targetK:1473.15},{nr:30,nz:60,maxIter:800,tolerance:1e-5,currentField:true});
function zrow(x){out.count0D++;const z=calculate(x);if(z.errors.length||!Number.isFinite(z.tss))throw Error('0D failure');const op=operatingAt(z.tss,x,z.g);return {V:z.g.envelopeVolume*1e6,ar:x.aspectRatio,phi:1-x.solidFraction,k:x.effectiveK,T:z.tss-273.15,wall:z.steadyLoss.wallK-273.15,mass:z.mass*1000,L:z.g.L*1000,D:z.g.D*1000,P:op.power,I:op.current,U:op.voltage,R:op.resistance,constraint:op.constraint};}
function field(name,x){check();const t=performance.now(),s=solveThermal2D(x,calculate(x),x.enclosure,x.material);if(s.errors.length||!s.converged||s.closure>1e-5)throw Error('Field gate '+name);const row={name,input:x,z:zrow(x),avg:s.avgK-273.15,max:s.tMax-273.15,min:s.tMin-273.15,closure:s.closure,loss:s.lossByChannel,gas:s.heCooling,P:s.op.pBulk,seconds:(performance.now()-t)/1000,T:s.T,rEdges:s.mesh.edges,zEdges:s.mesh.zEdges,codes:s.T.map((r,j)=>r.map((_,i)=>s.mesh.materialAt(i,j))),profile:s.T.map((r,j)=>({z:s.mesh.zCenters[j]*1000,element:r[0]-273.15,wall:r[s.mesh.nElement+s.mesh.nGap]-273.15,active:j>=s.mesh.activeStart&&j<s.mesh.activeEnd}))};out.fields.push(row);save();console.log(name,row.max,row.seconds);return row;}
try{
 // Sparse pilot, not a global optimization.
 const pilot=[];for(const V of [40,80,160,320])for(const ar of [3,10,30,100])pilot.push(zrow(input(V,ar)));
 const candidate=pilot.reduce((a,b)=>Math.abs(a.T-1120)<Math.abs(b.T-1120)?a:b);
 out.selectedInput=input(candidate.V,candidate.ar);out.pilot=pilot;
 const a=field('selected',out.selectedInput),fine=field('refined',{...out.selectedInput,enclosure:{...out.selectedInput.enclosure,nr:45,nz:90}});
 out.gridDifference=fine.max-a.max;if(Math.abs(out.gridDifference)>5)throw Error('Grid gate');
 if(a.seconds*14+fine.seconds>450)throw Error('Projected budget gate');
 const base=out.selectedInput;
 for(const [name,patch,cfg] of [['low k',{effectiveK:20},{}],['high k',{effectiveK:120},{}],['low h',{h:5},{}],['high h',{h:25},{}],['contact',{}, {contactRho:1e-6}],['electrode',{}, {endMode:'electrode',endH:250}],['short',{aspectRatio:base.aspectRatio*.6},{}],['long',{aspectRatio:base.aspectRatio*1.6},{}]])field(name,{...base,...patch,enclosure:{...base.enclosure,...cfg}});
 // Four connected legs, each heating starts at ambient, cooling at that heated field.
 for(const dt of [5,2.5]){
  const x={...base,enclosure:{...base.enclosure,nr:20,nz:40}},z=calculate(x);let previous;
  for(const phase of ['heat','cool']){check();const y=phase==='heat'?x:{...x,supplyMode:'cc',iset:0};const s=solveTransient2D(y,z,y.enclosure,y.material,{dt,steps:Math.round(300/dt),startField:previous,picardMax:60,picardTol:1e-5});if(s.errors.length||!s.converged||s.worstClosure>1e-4)throw Error('Transient gate');out.transients.push({dt,phase,history:s.history,avg:s.avgK-273.15,max:s.tMax-273.15,closure:s.worstClosure,energy:s.electricalEnergy,stored:s.storedEnergy});previous=s.T;save();}
 }
 out.timeDifference=Math.max(...['heat','cool'].map(p=>Math.abs(out.transients.find(t=>t.dt===5&&t.phase===p).avg-out.transients.find(t=>t.dt===2.5&&t.phase===p).avg)));
 if(out.timeDifference>2)throw Error('Time refinement gate');
 out.map={ars:grid(1,100,41),volumes:grid(10,1000,41)};
 out.map.rows=out.map.volumes.map(V=>out.map.ars.map(ar=>zrow(input(V,ar))));
 out.phi=[20,60,120].map(k=>({k,rows:Array.from({length:21},(_,i)=>zrow(input(candidate.V,candidate.ar,i*.04,k)))}));
 out.shape=grid(1,100,41).map(ar=>zrow(input(candidate.V,ar)));
 out.materials=[];
 for(const [name,lo,hi] of [['SiC',1,100],['SiSiC (Si-infiltrated SiC)',1,100],['Kanthal A-1 (FeCrAl)',10,10000],['Carbon fiber paper (CFP)',1,100]]){
  const m=MATERIALS.find(m=>m.name===name);if(!m){console.log('Missing material',name);continue;}
  const p={name,ars:grid(lo,hi,31),volumes:grid(.01,1000,31)};
  p.rows=p.volumes.map(V=>p.ars.map(ar=>zrow({...input(V,ar,0),porousMode:'legacy',material:m,emissivity:m.emissivity??.8})));out.materials.push(p);
 }
 out.status='complete';save();console.log('COMPLETE',out.elapsedSeconds,out.count0D);
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
