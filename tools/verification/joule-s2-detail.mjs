// Author-requested S2 expansion: six steady solves and four connected transient legs.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {radialParabola,annulusDrops} from './joule.mjs';
import {calculate,solveTransient2D} from '../../apps/joule/solver.js';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url);
const file=new URL('s2-detail.json',dir);if(fs.existsSync(file))throw Error('Preserve existing output');
const d=JSON.parse(fs.readFileSync(new URL('data-v6-final.json',dir)));
const hash=createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex');
if(hash!==d.solverHash)throw Error('Solver cache mismatch');
const out={status:'running',solverHash:hash,limits:[],transients:[]},start=performance.now();
const save=()=>{out.seconds=(performance.now()-start)/1000;fs.writeFileSync(file,JSON.stringify(out,null,2));};
try{
 for(const ar of [25,75,150]){out.limits.push({ar,radial:radialParabola(ar),annulus:annulusDrops(ar)});save();console.log('L/D',ar);}
 for(const dt of [2,1]){
  const x={...d.selectedInput,enclosure:{...d.selectedInput.enclosure,nr:20,nz:40}},z=calculate(x);let previous;
  for(const phase of ['heat','cool']){
   if(performance.now()-start>500000)throw Error('Budget gate');
   const y=phase==='heat'?x:{...x,supplyMode:'cc',iset:0};
   const s=solveTransient2D(y,z,y.enclosure,y.material,{dt,steps:300/dt,startField:previous,picardMax:60,picardTol:1e-5});
   if(s.errors.length||!s.converged||s.worstClosure>1e-4)throw Error('Transient gate');
   out.transients.push({dt,phase,avg:s.avgK-273.15,max:s.tMax-273.15,closure:s.worstClosure});previous=s.T;save();console.log('Transient',dt,phase,s.avgK-273.15);
  }
 }
 out.status='complete';save();
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
