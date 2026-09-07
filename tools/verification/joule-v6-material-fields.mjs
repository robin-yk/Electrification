// Matched lumped temperature, unchanged material presets; no reaction or pore closure.
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {calculate,solveThermal2D,MATERIALS,propertiesAt} from '../../apps/joule/solver.js';
import {defaultInput} from './joule.mjs';
const path=new URL('../../docs/research/joule-v6-2026-09-07/material-fields-final.json',import.meta.url);
if(fs.existsSync(path))throw Error('Preserve existing output');
const out={status:'running',commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),solverHash:createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex'),targetC:900,rows:[]};
const save=()=>fs.writeFileSync(path,JSON.stringify(out));
function solve(name,fine=false,matched){
 const material=MATERIALS.find(m=>m.name===name);
 // Separate named supply envelopes; a current setpoint matches the lumped temperature.
 const ceramic=['SiC','SiSiC (Si-infiltrated SiC)'].includes(name);
 let x=defaultInput({material,volumeCm3:1.18,aspectRatio:3,solidFraction:1,porousMode:'legacy',emissivity:material.emissivity??.8,vmax:ceramic?150:40,imax:ceramic?40:375,pmax:ceramic?2000:15000,supplyMode:'cc',iset:0},{nr:fine?45:30,nz:fine?90:60,maxIter:1000,tolerance:1e-6,currentField:true});
 if(matched)x={...matched,enclosure:{...matched.enclosure,nr:45,nz:90}};
 else {
  let lo=0,hi=Math.min(x.imax,material.jmax*calculate(x).g.area);
  if(calculate({...x,iset:hi}).tss<1173.15)throw Error('Target infeasible '+name);
  for(let i=0;i<35;i++){const mid=(lo+hi)/2;const z=calculate({...x,iset:mid});if(z.tss<1173.15)lo=mid;else hi=mid;}
  x.iset=(lo+hi)/2;
 }
 const z=calculate(x);if(z.errors.length||Math.abs(z.tss-1173.15)>.01)throw Error('Lumped gate '+name);
 const s=solveThermal2D(x,z,x.enclosure,material);
 if(s.errors.length||!s.converged||s.closure>1e-5||s.op.voltage>x.vmax||s.op.current>x.imax||s.tMax>1473.15)throw Error('Field gate '+name+JSON.stringify({errors:s.errors,conv:s.converged,closure:s.closure,op:s.op,max:s.tMax}));
 const row={name,fine,input:x,zeroC:z.tss-273.15,avg:s.avgK-273.15,max:s.tMax-273.15,min:s.tMin-273.15,op:s.op,k:propertiesAt(material,s.avgK).k,closure:s.closure,T:s.T,codes:s.T.map((r,j)=>r.map((_,i)=>s.mesh.materialAt(i,j))),r:s.mesh.centers,z:s.mesh.zCenters,rEdges:s.mesh.edges,zEdges:s.mesh.zEdges,L:z.g.L,D:z.g.D};
 out.rows.push(row);save();console.log(name,fine,JSON.stringify({avg:row.avg,max:row.max,spread:row.max-row.min,k:row.k,I:s.op.current,V:s.op.voltage}));return row;
}
try{
 // The preserved pilot failed the MoSi2 current-density feasibility gate.
 // Exclude it from this matched-temperature study without relaxing any limit.
 out.excluded=['MoSi₂: 900 C target infeasible within preset current-density limit at this geometry'];
 for(const name of ['SiC','SiSiC (Si-infiltrated SiC)','Kanthal A-1 (FeCrAl)','Inconel 601'])solve(name);
 for(const name of ['SiC','Kanthal A-1 (FeCrAl)']){const a=out.rows.find(r=>r.name===name);const b=solve(name,true,a.input);if(Math.max(Math.abs(a.max-b.max),Math.abs(a.min-b.min))>2)throw Error('Refinement gate '+name);}
 out.status='complete';save();
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
