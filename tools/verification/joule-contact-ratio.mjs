// Nonreacting contact sensitivity, not a measured contact-property range.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {calculate,operating2DAt,solveThermal2D} from '../../apps/joule/solver.js';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url),file=new URL('contact-ratio.json',dir);
if(fs.existsSync(file))throw Error('Preserve existing output');
const d=JSON.parse(fs.readFileSync(new URL('data-v6-final.json',dir))),x=d.selectedInput,z=calculate(x);
const hash=createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex');
if(hash!==d.solverHash)throw Error('Solver mismatch');
const referenceK=1473.15,ref=operating2DAt(referenceK,x,z.g,x.enclosure,x.material);
const out={status:'running',solverHash:hash,commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),referenceK,referenceBulkOhm:ref.rBulk,area:z.g.area,input:x,rows:[]};
const start=performance.now(),save=()=>fs.writeFileSync(file,JSON.stringify(out,null,2));
try{
 for(const ratio of [0,.01,.025,.05,.1,.2,.5]){
  if(performance.now()-start>480000)throw Error('Budget gate');
  const contactRho=ratio*ref.rBulk*z.g.area/2,y={...x,enclosure:{...x.enclosure,contactRho}};
  const s=solveThermal2D(y,calculate(y),y.enclosure,y.material);
  if(s.errors.length||!s.converged||s.closure>1e-5)throw Error('Field gate');
  if(Math.abs((s.op.pBulk+s.op.pContact)-s.op.pTotal)>1e-7)throw Error('Power accounting');
  out.rows.push({ratio,contactRho,avg:s.avgK-273.15,max:s.tMax-273.15,closure:s.closure,op:s.op});save();console.log(ratio,s.tMax-273.15,s.op.pContact,s.op.constraint);
 }
 out.status='complete';out.seconds=(performance.now()-start)/1000;save();
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
