// Four nonreacting steady fields: two terminal layouts at two mesh levels.
// Execute the exact embedded engine supplied by the author, without UI code.
import fs from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
const source=fs.readFileSync('/Users/robin_yeonsu/Desktop/Joule.html','utf8');
const pages=JSON.parse(source.split('const embeddedPages=')[1].split(';\n')[0]);
const engine=pages['3d'].match(/<script[^>]*id="engine"[^>]*>([\s\S]*?)<\/script>/)[1];
const outPath=new URL('../../docs/research/joule-v6-2026-09-07/3d-contact-pilot.json',import.meta.url);
if(fs.existsSync(outPath))throw Error('Preserve prior results');
const context=vm.createContext({console,performance});vm.runInContext(engine,context);
const out={sourceHash:createHash('sha256').update(source).digest('hex'),engineHash:createHash('sha256').update(engine).digest('hex'),status:'running',rows:[]};
const base={shape:'rod',meshType:'cartesian',length:30,width:12,height:12,bore:0,rho:1.45e-6,alpha:0,k:11,density:7100,cp:460,mode:'P',command:30,vmax:150,imax:125,pmax:2000,ambient:25,sink:25,h:15,emissivity:.8,hc:0,maxTemp:1500,study:'steady',initial:25,flow:false,wall:false,contactR:0,thermalR:0,slew:0,jlimit:0,electrodeLength:0,limitAction:'limit',rhoCurve:[],kCurve:[],cpCurve:[]};
try{
 for(const n of [12,18])for(const layout of ['full','offset']){
  context.p={...base,n,nx:n,ny:n,nz:Math.round(n*2.5),contact:layout==='full'?100:50,offsetA:layout==='full'?0:-50,offsetB:layout==='full'?0:50};
  const r=vm.runInContext('solveModel(p)',context,{timeout:150000});
  if(Math.abs(r.stats.P-30)>1e-6||r.stats.energyError>1e-5||r.stats.chargeError>1e-5)throw Error('Power/energy/charge gate');
  out.rows.push({layout,n,params:context.p,stats:r.stats,xyz:r.mesh.xyz,T:Array.from(r.T),J:Array.from(r.J),q:Array.from(r.q),termA:r.mesh.termA,termB:r.mesh.termB});fs.writeFileSync(outPath,JSON.stringify(out));console.log(layout,n,r.stats);
 }
 out.status='complete';fs.writeFileSync(outPath,JSON.stringify(out));
}catch(e){out.status='stopped';out.reason=e.message;fs.writeFileSync(outPath,JSON.stringify(out));throw e;}
