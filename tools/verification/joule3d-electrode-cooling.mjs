// Small nonreacting sensitivity using the exact author-supplied engine.
import fs from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
const source=fs.readFileSync('/Users/robin_yeonsu/Desktop/Joule.html','utf8');
const pages=JSON.parse(source.split('const embeddedPages=')[1].split(';\n')[0]);
const engine=pages['3d'].match(/<script[^>]*id="engine"[^>]*>([\s\S]*?)<\/script>/)[1];
const file=new URL('../../docs/research/joule-v6-2026-09-07/electrode-cooling.json',import.meta.url);
if(fs.existsSync(file))throw Error('Preserve output');
const ctx=vm.createContext({console,performance});vm.runInContext(engine,ctx);
const base={shape:'rod',meshType:'cartesian',length:30,width:12,height:12,bore:0,rho:1.45e-6,alpha:0,k:11,density:7100,cp:460,mode:'P',command:30,vmax:40,imax:375,pmax:15000,ambient:25,sink:25,h:15,emissivity:.8,maxTemp:1500,study:'steady',initial:25,flow:false,wall:false,contact:100,offsetA:0,offsetB:0,contactR:0,thermalR:0,slew:0,jlimit:0,electrodeLength:3,electrodeRho:1.7e-8,electrodeK:400,electrodeCp:385,electrodeDensity:8960,limitAction:'limit',rhoCurve:[],kCurve:[],cpCurve:[]};
const out={status:'running',sourceHash:createHash('sha256').update(source).digest('hex'),engineHash:createHash('sha256').update(engine).digest('hex'),rows:[]};
try{
 for(const [n,nz,hc] of [[12,30,0],[12,30,200],[12,30,2000],[18,60,2000]]){
 ctx.p={...base,n,nx:n,ny:n,nz,hc};const r=vm.runInContext('solveModel(p)',ctx,{timeout:120000});
 if(Math.abs(r.stats.P-30)>1e-6||r.stats.energyError>1e-5||r.stats.chargeError>1e-5)throw Error('Closure gate '+JSON.stringify(r.stats));
 out.rows.push({params:ctx.p,stats:r.stats,xyz:r.mesh.xyz,region:Array.from(r.mesh.region),T:Array.from(r.T)});fs.writeFileSync(file,JSON.stringify(out));console.log(n,nz,hc,r.stats.heaterMax,r.stats.contacts,r.stats.energyError);
 }
 out.status='complete';fs.writeFileSync(file,JSON.stringify(out));
}catch(e){out.status='stopped';out.reason=e.message;fs.writeFileSync(file,JSON.stringify(out));throw e;}
