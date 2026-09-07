// Centered/eccentric through-bore, same nominal and voxel volume at each level.
import fs from 'node:fs';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
const source=fs.readFileSync('/Users/robin_yeonsu/Desktop/Joule.html','utf8');
const pages=JSON.parse(source.split('const embeddedPages=')[1].split(';\n')[0]);
const engine=pages['3d'].match(/<script[^>]*id="engine"[^>]*>([\s\S]*?)<\/script>/)[1];
const file=new URL('../../docs/research/joule-v6-2026-09-07/eccentric-bore.json',import.meta.url);
if(fs.existsSync(file))throw Error('Preserve output');
const ctx=vm.createContext({console,performance});vm.runInContext(engine,ctx);
const base={shape:'cad',meshType:'cartesian',length:30,width:12,height:12,rho:1.45e-6,alpha:0,k:11,density:7100,cp:460,mode:'P',command:30,vmax:40,imax:375,pmax:15000,ambient:25,sink:25,h:15,emissivity:.8,hc:0,maxTemp:1500,study:'steady',initial:25,flow:false,wall:false,contact:100,offsetA:0,offsetB:0,contactR:0,thermalR:0,slew:0,jlimit:0,electrodeLength:0,limitAction:'limit',rhoCurve:[],kCurve:[],cpCurve:[]};
const out={status:'running',sourceHash:createHash('sha256').update(source).digest('hex'),engineHash:createHash('sha256').update(engine).digest('hex'),rows:[]};
try{
 for(const [n,nz] of [[24,20],[36,30]]){
  for(const offset of [0,2]){
   ctx.p={...base,n,nx:n,ny:n,nz,parts:[{type:'cylinder',op:'add',diameter:12,length:30,x:0,y:0,z:0},{type:'cylinder',op:'subtract',diameter:4,length:32,x:offset,y:0,z:0}]};
   const r=vm.runInContext('solveModel(p)',ctx,{timeout:180000});
   if(Math.abs(r.stats.P-30)>1e-6||r.stats.energyError>1e-5||r.stats.chargeError>1e-5)throw Error('Closure gate '+JSON.stringify(r.stats));
   out.rows.push({offset,n,params:ctx.p,stats:r.stats,xyz:r.mesh.xyz,T:Array.from(r.T),J:Array.from(r.J),d:r.mesh.d});fs.writeFileSync(file,JSON.stringify(out));console.log(n,offset,r.stats.max,r.stats.spread,r.stats.R,r.stats.volume);
  }
  const pair=out.rows.slice(-2);if(Math.abs(pair[0].stats.volume/pair[1].stats.volume-1)>1e-10)throw Error('Unequal voxel volume');
  if(n===24&&Math.abs(pair[0].stats.max-pair[1].stats.max)<.5){out.status='pilot-no-material-difference';fs.writeFileSync(file,JSON.stringify(out));process.exit(0);}
 }
 out.status='complete';fs.writeFileSync(file,JSON.stringify(out));
}catch(e){out.status='stopped';out.reason=e.message;fs.writeFileSync(file,JSON.stringify(out));throw e;}
