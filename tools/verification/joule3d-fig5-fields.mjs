import fs from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
const dir='/Users/robin_yeonsu/내 드라이브(fiske@udel.edu)(1)/Yeonsu - Career Overall/LLM-Wiki/B2 working-paper/manuscripts-B2/joule-heating-2d-model/drafts/3d-browser-check/';
const sweep=JSON.parse(fs.readFileSync(dir+'screening.json','utf8'));
const source=fs.readFileSync('/Users/robin_yeonsu/Desktop/Joule.html','utf8');
const page=JSON.parse(source.split('const embeddedPages=')[1].split(';\n')[0])['3d'];
const engine=page.match(/<script[^>]*id="engine"[^>]*>([\s\S]*?)<\/script>/)[1];
const hash=createHash('sha256').update(engine).digest('hex');
if(hash!=='b5ddddd49f3059d1288ca60861df167d22b82e3cff276af221b8f7b8502d274a')throw Error('Engine changed');
const out=dir+'fig5-fields.json';if(fs.existsSync(out))throw Error('Preserve output');
const result={engineHash:hash,scope:'Two existing sweep cases, 30 W, unchanged closures and mesh',rows:[]};
const context=vm.createContext({console,performance});vm.runInContext(engine,context);
for(const contact of [25,100]){
 context.p={...sweep.base,command:30,contact};
 const r=vm.runInContext('solveModel(p)',context,{timeout:120000});
 const expected=sweep.rows[sweep.ys.indexOf(contact)*sweep.xs.length+sweep.xs.indexOf(30)].metrics;
 if(Math.abs(r.stats.max-expected.max)>1e-7||r.stats.energyError>1e-7||r.stats.chargeError>1e-7)throw Error('Reproduction/closure failure');
 result.rows.push({params:context.p,stats:r.stats,xyz:r.mesh.xyz,d:r.mesh.d,termA:r.mesh.termA,termB:r.mesh.termB,T:Array.from(r.T)});
 fs.writeFileSync(out,JSON.stringify(result));console.log(contact,r.stats.max,r.stats.spread);
}
