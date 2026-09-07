// Six additional nonreacting solves; reuse identical-hash cached study points.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {calculate,solveThermal2D} from '../../apps/joule/solver.js';
import {mmsStudy} from './joule.mjs';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url);
const path=new URL('grid-detail.json',dir);if(fs.existsSync(path))throw Error('Preserve existing output');
const d=JSON.parse(fs.readFileSync(new URL('data-v6-final.json',dir)));
const hash=createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex');
if(hash!==d.solverHash)throw Error('Cache hash mismatch');
const out={status:'running',solverHash:hash,commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),mms:d.verification.mms.map((r,i)=>({...r,nr:[30,60,120][i],cached:true})),physical:d.fields.slice(0,2).map(r=>({nr:r.input.enclosure.nr,avg:r.avg,max:r.max,min:r.min,closure:r.closure,cached:true})),input:d.selectedInput};
const start=performance.now();const save=()=>{out.seconds=(performance.now()-start)/1000;fs.writeFileSync(path,JSON.stringify(out));};
try{
 for(const nr of [20,45,90]){const [r]=mmsStudy(1,[{nr,nz:2*nr}]);out.mms.push({...r,nr,cached:false});save();console.log('MMS',nr,r.l2);}
 out.mms.sort((a,b)=>a.nr-b.nr);
 for(let i=1;i<out.mms.length;i++){const a=out.mms[i-1],b=out.mms[i];b.orderL2=Math.log(a.l2/b.l2)/Math.log(b.nr/a.nr);if(b.l2>=a.l2)throw Error('MMS error failed to decrease');}
 for(const nr of [20,60,90]){
  if(performance.now()-start>450000)throw Error('Budget gate');
  const x={...d.selectedInput,enclosure:{...d.selectedInput.enclosure,nr,nz:2*nr}};
  const s=solveThermal2D(x,calculate(x),x.enclosure,x.material);
  if(s.errors.length||!s.converged||s.closure>1e-5)throw Error('Physical gate '+nr);
  out.physical.push({nr,avg:s.avgK-273.15,max:s.tMax-273.15,min:s.tMin-273.15,closure:s.closure,cached:false});save();console.log('Physical',nr,s.tMax-273.15);
 }
 out.physical.sort((a,b)=>a.nr-b.nr);
 out.finestDifference=Math.abs(out.physical.at(-1).max-out.physical.at(-2).max);
 if(out.finestDifference>2)throw Error('Peak refinement exceeds 2 K');
 out.status='complete';save();
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
