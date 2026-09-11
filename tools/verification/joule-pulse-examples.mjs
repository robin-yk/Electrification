import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {integratePulsedElement,steadyElementTemperature} from '../../apps/rphcjh/solver.js';
const file=new URL('../../docs/research/joule-v6-2026-09-07/pulse-examples.json',import.meta.url);
if(fs.existsSync(file))throw Error('Preserve existing results');
const base={voltage:30,period:1,duty:.05,tolC:.001};
const groups=[{axis:'period',values:[.2,1,2]},{axis:'duty',values:[.02,.05,.1]},{axis:'voltage',values:[20,30,40]}];
const out={status:'running',model:'Separate RPH thermal ODE, no reaction or Joule2D enclosure',solverHash:createHash('sha256').update(fs.readFileSync(new URL('../../apps/rphcjh/solver.js',import.meta.url))).digest('hex'),groups:[],rows:[]};
for(const g of groups){const ids=[];for(const value of g.values){const cfg={...base,[g.axis]:value},id=JSON.stringify(cfg);ids.push(id);if(out.rows.some(r=>r.id===id))continue;
const s=integratePulsedElement(cfg);if(!s.converged||!Number.isFinite(s.tPeak)||Math.abs(s.energyResidual)>.01)throw Error('Convergence/energy gate');
out.rows.push({id,cfg,...s,continuousC:steadyElementTemperature({power:s.avgPower})});console.log(cfg,s.tPeak,s.avgPower,s.energyResidual);}
out.groups.push({...g,ids});}
out.status='complete';fs.writeFileSync(file,JSON.stringify(out));
