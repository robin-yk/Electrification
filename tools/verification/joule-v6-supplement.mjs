import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {calculate,operatingAt,MATERIALS} from '../../apps/joule/solver.js';
import {defaultInput} from './joule.mjs';
import {integratePulsedElement,steadyElementTemperature} from '../../apps/rphcjh/solver.js';
const dir=new URL('../../docs/research/joule-v6-2026-09-07/',import.meta.url);
const file=new URL('supplement.json',dir);if(fs.existsSync(file))throw Error('Preserve existing data');
const base=JSON.parse(fs.readFileSync(new URL('data-v6-final.json',dir))).selectedInput;
const seq=(a,b,n=31)=>Array.from({length:n},(_,i)=>a*(b/a)**(i/(n-1)));
const hash=p=>createHash('sha256').update(fs.readFileSync(new URL(p,import.meta.url))).digest('hex');
const out={commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),solverHash:hash('../../apps/joule/solver.js'),pulseSolverHash:hash('../../apps/rphcjh/solver.js'),count:0};
function row(x){const z=calculate(x);if(z.errors.length||!Number.isFinite(z.tss))throw Error(JSON.stringify(z.errors));out.count++;return {T:z.tss-273.15,wall:z.steadyLoss.wallK-273.15,mass:z.mass*1000,g:z.g,op:operatingAt(z.tss,x,z.g)};}
out.supplies=[{name:'62020H-150S',vmax:150,imax:40,pmax:2000},{name:'62050H-40',vmax:40,imax:125,pmax:5000},{name:'62050H-450',vmax:450,imax:11.5,pmax:5000}];
out.supplyShape=out.supplies.map(s=>({s,rows:seq(1,100).map(ar=>({ar,...row({...base,...s,aspectRatio:ar})}))}));
out.resistances=seq(.001,1000,121);out.supplyPower=out.supplies.map(s=>out.resistances.map(R=>Math.min(s.imax*s.imax*R,s.vmax*s.vmax/R,s.pmax)));
const cfp=MATERIALS.find(m=>m.name==='CFP');
const strip=defaultInput({material:cfp,shape:'box',lengthMm:38,widthMm:8,heightMm:.21,solidFraction:1,porousMode:'legacy',vmax:150,imax:40,pmax:2000});
out.stripInput=strip;
out.stripSweeps=[['widthMm',seq(1,100)],['lengthMm',seq(1,1000)],['heightMm',seq(.01,1)]].map(([axis,values])=>({axis,rows:values.map(value=>({value,...row({...strip,[axis]:value})}))}));
out.stripMap={ars:seq(1,100),volumes:seq(.001,1),heightMm:.21};
out.stripMap.rows=out.stripMap.volumes.map(V=>out.stripMap.ars.map(ar=>row({...strip,lengthMm:Math.sqrt(V*1000/.21*ar),widthMm:Math.sqrt(V*1000/.21/ar)})));
out.resistivity=seq(.001,1).map(rho=>({rho,...row({...base,material:{...base.material,rhoOhmCm:rho,rhoTable:undefined}})}));
// Separate published CFP thermal ODE; no gas-phase chemistry or Joule2D enclosure.
out.pulseConfig={voltage:30,period:1,duty:.05,tolC:.001};
out.pulse=integratePulsedElement(out.pulseConfig);
if(!out.pulse.converged||Math.abs(out.pulse.energyResidual)>.01)throw Error('Pulse gate');
out.continuousC=steadyElementTemperature({power:out.pulse.avgPower});
fs.writeFileSync(file,JSON.stringify(out));console.log('Completed',out.count,'lumped cases');
