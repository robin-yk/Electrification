import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {geometry,enclosureHeatLoss,operatingAt,calculate,validateInput} from '../../apps/joule/solver.js';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url),file=new URL('target-maps.json',dir);
if(fs.existsSync(file))throw Error('Preserve existing data');
const old=JSON.parse(fs.readFileSync(new URL('data-v6-final.json',dir)));
const hash=createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex');
if(hash!==old.solverHash)throw Error('Solver changed');
const base={...old.selectedInput,volumeCm3:20,aspectRatio:30,targetK:1473.15,supplyMode:'auto'};
const out={status:'running',solverHash:hash,commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),base,maps:[],pilot:[],count:0};
const start=performance.now(),save=()=>{out.seconds=(performance.now()-start)/1000;fs.writeFileSync(file,JSON.stringify(out));};
function point(x){
 if(validateInput(x).length)throw Error('Input gate');
 const g=geometry(x),op=operatingAt(x.targetK,x,g),loss=enclosureHeatLoss(x.targetK,x,g),ratio=op.power/loss.total;
 if(!Number.isFinite(ratio)||ratio<=0||x.enclosure.contactRho!==0)throw Error('Power accounting gate');
 out.count++;return {ratio,available:op.power,required:loss.total,wallC:loss.wallK-273.15,constraint:op.constraint,R:op.resistance,I:op.current,U:op.voltage};
}
const log=(a,b)=>Array.from({length:41},(_,i)=>a*(b/a)**(i/40));
try{
 // API agreement and a nonreacting boundary bracket precede the maps.
 for(const [V,ar] of [[40,30],[80,30],[40,15]]){
  const x={...base,volumeCm3:V*.5,aspectRatio:ar},p=point(x),z=calculate(x);
  if(z.errors.length||Math.abs(p.ratio-z.power/z.requiredPower)>1e-10)throw Error('Public API agreement gate');
  out.pilot.push({V,ar,...p});
 }
 if(!out.pilot.some(q=>q.ratio<1)||!out.pilot.some(q=>q.ratio>1))throw Error('Boundary bracket gate');
 const c=point(base);out.anchor=c;
 for(const factor of [.8,1.2]){
  const x={...base,imax:factor*Math.sqrt(c.required/c.R)},p=point(x);
  if((factor<1)!==(p.ratio<1))throw Error('Current threshold gate');
 }
 const specs=[
  {name:'volume-shape',xs:log(1,100),ys:log(10,1000),input:(ar,V)=>({...base,aspectRatio:ar,volumeCm3:V*.5})},
  {name:'resistivity-shape',xs:log(1,100),ys:log(.0001,1),input:(ar,rho)=>({...base,aspectRatio:ar,material:{...base.material,rhoOhmCm:rho}})},
  {name:'supply',xs:log(1,1000),ys:log(1,1000),input:(v,i)=>({...base,vmax:v,imax:i})}
 ];
 for(const s of specs){const m={name:s.name,x:s.xs,y:s.ys,rows:[]};for(const y of s.ys){if(performance.now()-start>60000)throw Error('One-minute budget gate');m.rows.push(s.xs.map(x=>point(s.input(x,y))));}if(!m.rows.flat().some(q=>q.ratio<1)||!m.rows.flat().some(q=>q.ratio>1))throw Error('Map lacks boundary '+s.name);out.maps.push(m);save();}
 out.status='complete';save();console.log(JSON.stringify({status:out.status,count:out.count,seconds:out.seconds,anchor:out.anchor}));
}catch(e){out.status='stopped';out.reason=e.message;save();throw e;}
