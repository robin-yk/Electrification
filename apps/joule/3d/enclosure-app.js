import {buildEnclosure3D} from './enclosure.js';
const $=id=>document.getElementById(id),num=id=>Number($(id).value);
let design=null,result=null,worker=null;
const status=text=>{$('status').textContent=text;};
function settings(){
  if(!design)throw Error('Import a cylindrical design first.');
  return {x:design.x,geometryNote:design.geometryNote,cfg:{...design.cfg,nr:num('nr'),nz:num('nz'),nt:num('nt'),currentField:$('currentField').checked,purge:$('purge').checked},
    plan:{study:$('study').value,startK:num('startC')+273.15,duration:num('duration'),dt:num('dt'),period:num('period'),duty:num('duty'),
      initialSteady:$('initialSteady').checked,
      dtGrowth:$('steadyStop').checked&&[0,1].includes(num('duty'))?1.02:1,
      maxDt:num('dt')*20,steadyTol:$('steadyStop').checked&&[0,1].includes(num('duty'))?1e-4:0,
      ...(design.startField?{startField:design.startField}:{})}};
}
function accept(data){
  if(worker)throw Error('Cancel the active run before importing.');
  buildEnclosure3D(data.x,{nr:20,nz:24,nt:8,...data.cfg});
  design={x:data.x,cfg:data.cfg,startField:data.plan?.startField,geometryNote:data.geometryNote??'Cylindrical geometry.'};result=null;
  for(const key of ['nr','nz','nt'])$(key).value=data.cfg[key]??({nr:20,nz:24,nt:8}[key]);
  $('currentField').checked=data.cfg.currentField!==false;$('purge').checked=data.cfg.purge!==false;
  $('startC').value=(data.plan?.startK??data.x.ambientK)-273.15;
  if(data.plan)for(const key of ['study','duration','dt','period','duty'])if(data.plan[key]!==undefined)$(key).value=data.plan[key];
  $('warmStart').checked=false;
  $('initialSteady').checked=!!data.plan?.initialSteady;
  $('steadyStop').checked=(data.plan?.steadyTol??0)>0;
  $('design').textContent=`${data.x.material.name??'Custom material'} · cylinder · ${data.x.volumeCm3} cm³ solid · L/D ${data.x.aspectRatio} · solid fraction ${data.x.solidFraction}. ${design.geometryNote} Material source: ${data.x.material.source??'User supplied'}.`;
  $('solve').disabled=false;$('compare').disabled=false;$('csv').disabled=true;$('history').disabled=true;
  $('metrics').replaceChildren();$('balance').textContent='';$('comparison').textContent='';
  for(const id of ['slice','cross','trace'])$(id).getContext('2d').clearRect(0,0,$(id).width,$(id).height);
  status('Imported complete cylindrical design. Review resolution and operation, then calculate.');
}
window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==parent||event.data?.type!=='joule-enclosure-import')return;
  try{accept(event.data);}catch(error){status(error.message);}
});
function stop(){worker?.terminate();worker=null;$('cancel').disabled=true;$('solve').disabled=!design;$('compare').disabled=!design;}
function run(compare){
  try{
    const input=settings();buildEnclosure3D(input.x,input.cfg);
    if(compare&&input.plan.study!=='steady')throw Error('Select steady state for the paired comparison.');
    if($('warmStart').checked){
      if(input.plan.initialSteady)throw Error('Choose either last field or a newly computed steady start.');
      if(!result)throw Error('Compute a 3D field before selecting a warm start.');
      if(JSON.stringify({...input.cfg})!==JSON.stringify({...result.cfg}))throw Error('Warm start requires the same geometry and mesh settings.');
      input.plan.startField=Array.from(result.T);
    }
    stop();$('solve').disabled=true;$('compare').disabled=true;$('cancel').disabled=false;
    $('csv').disabled=true;$('history').disabled=true;status('Solving coupled 3D fields…');
    worker=new Worker(new URL('./enclosure-worker.js',import.meta.url),{type:'module'});
    worker.onerror=e=>{stop();status(`Worker error: ${e.message}`);};
    worker.onmessage=({data})=>{
      if(data.type==='progress'){status(`Solving · t ${(data.time??0).toFixed(3)} s · iteration ${data.iteration??0} · residual ${data.residual?.toExponential(2)??'checking balance'}`);return;}
      stop();
      if(data.type==='error'){status(data.message);return;}
      result=data.result;render();status(`Completed at t = ${result.tEnd.toPrecision(5)} s (${result.stopReason}). Inspect energy closure and model assumptions before using the result.`);
    };
    worker.postMessage({...input,compare});
  }catch(error){status(error.message);}
}
$('solve').onclick=()=>run(false);$('compare').onclick=()=>run(true);$('cancel').onclick=()=>{stop();status('Cancelled. No new result accepted.');};
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('save').onclick=()=>{try{download('joule-enclosure3d.json',JSON.stringify(settings(),null,2),'application/json');}catch(e){status(e.message);}};
$('load').onchange=async()=>{try{const file=$('load').files[0];if(file)accept(JSON.parse(await file.text()));}catch(e){status(e.message);}};
function render(){
  const r=result,values=[['Mean element',`${(r.avgK-273.15).toFixed(2)} °C`],['Peak element',`${(r.tMax-273.15).toFixed(2)} °C`],['Mean wall',`${(r.wallAvgK-273.15).toFixed(2)} °C`],['Bulk heating',`${r.op.pBulk.toPrecision(5)} W`],['Gas outlet',`${(r.loss.gasOutletK-273.15).toFixed(2)} °C`],['Closure',`${(100*r.closure).toPrecision(3)} %`]];
  $('metrics').replaceChildren(...values.map(([label,value])=>{const div=document.createElement('div');div.className='metric';const s=document.createElement('span'),v=document.createElement('strong');s.textContent=label;v.textContent=value;div.append(s,v);return div;}));
  $('balance').textContent=`Supply: ${r.op.pTotal.toPrecision(6)} W = bulk ${r.op.pBulk.toPrecision(6)} W + external contact dissipation ${r.op.pContact.toPrecision(6)} W\nBulk: loss ${r.loss.total.toPrecision(6)} W + storage ${r.storageRate.toPrecision(6)} W\n${Object.entries(r.loss.byChannel).map(([k,v])=>`${k}: ${v.toPrecision(5)} W`).join('\n')}\nHe enthalpy: ${r.loss.gasAdvective.toPrecision(5)} W\nTransient: input ${r.inputEnergy.toPrecision(5)} J; loss ${r.lossEnergy.toPrecision(5)} J; stored increment ${r.storedEnergy.toPrecision(5)} J\nSupply warnings: ${r.op.violations.join('; ')||'none'}\n${r.op.electrical?`Field resistance: ${r.op.electrical.fieldResistance.toPrecision(5)} Ω; supply bulk resistance: ${r.op.rBulk.toPrecision(5)} Ω`: 'Uniform bulk source selected'}`;
  $('comparison').textContent=r.comparison?`Paired 3D minus 2D\nMean: ${r.comparison.deltaAvgK.toExponential(3)} K\nPeak: ${r.comparison.deltaMaxK.toExponential(3)} K\nGas outlet: ${r.comparison.deltaGasK.toExponential(3)} K\nSame r/z grid, not an independent spatial-convergence certificate.`:'';
  $('angle').max=r.nt-1;$('axial').max=r.mesh.nz-1;$('axial').value=Math.floor(r.mesh.nz/2);
  if(Number.isFinite(r.x.material.meltC)&&r.tMax-273.15>=r.x.material.meltC)$('balance').textContent+=`\nMATERIAL WARNING: peak exceeds the preset ${r.x.material.meltKind??'transition'} threshold (${r.x.material.meltC} °C). No phase change is modeled.`;
  $('csv').disabled=false;$('history').disabled=false;draw();drawTrace();
}
function field(){if($('field').value==='T')return Float64Array.from(result.T,t=>t-273.15);
  if(!result.op.electrical){
    if($('field').value==='q'){const m=result.mesh,ns=m.nr*m.nz;return Float64Array.from(result.T,(_,p)=>{const i=p%m.nr,j=Math.floor((p%ns)/m.nr);return i<m.nElement&&j>=m.activeStart&&j<m.activeEnd?result.op.pBulk/m.elementVolume:0;});}
    return new Float64Array(result.T.length);
  }
  if($('field').value==='potential')return result.op.electrical.potential;
  if($('field').value==='J')return result.op.electrical.J;
  const m=result.mesh,ns=m.nr*m.nz;return Float64Array.from(result.op.qCell,(q,p)=>{const i=p%m.nr,j=Math.floor((p%ns)/m.nr);return q/(Math.PI*(m.edges[i+1]**2-m.edges[i]**2)*(m.zEdges[j+1]-m.zEdges[j])/result.nt);});}
function draw(){
  if(!result)return;const m=result.mesh,ns=m.nr*m.nz,a=num('angle'),z=num('axial'),f=field();let low=Infinity,high=-Infinity;for(const v of f){low=Math.min(low,v);high=Math.max(high,v);}
  const color=v=>`hsl(${230-220*(v-low)/Math.max(high-low,1e-12)} 75% 50%)`;
  const c=$('slice'),s=c.getContext('2d');s.clearRect(0,0,c.width,c.height);
  for(let j=0;j<m.nz;j++)for(let i=0;i<m.nr;i++){s.fillStyle=color(f[a*ns+j*m.nr+i]);s.fillRect(m.edges[i]/m.domainRadius*c.width,(m.nz-1-j)/m.nz*c.height,(m.edges[i+1]-m.edges[i])/m.domainRadius*c.width+1,c.height/m.nz+1);}
  const cc=$('cross'),ctx=cc.getContext('2d'),cx=cc.width/2,cy=cc.height/2,R=Math.min(cx,cy)-8;ctx.clearRect(0,0,cc.width,cc.height);
  for(let t=0;t<result.nt;t++)for(let i=m.nr-1;i>=0;i--){ctx.fillStyle=color(f[t*ns+z*m.nr+i]);ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,R*m.edges[i+1]/m.domainRadius,t*2*Math.PI/result.nt,(t+1)*2*Math.PI/result.nt);ctx.closePath();ctx.fill();}
  $('legend').textContent=`${$('field').selectedOptions[0].text}: blue ${low.toPrecision(4)} → red ${high.toPrecision(4)}. Angular sector ${a+1}/${result.nt}; z = ${(m.zCenters[z]*1000).toFixed(2)} mm. Full thermal domain shown.`;
}
for(const id of ['field','angle','axial'])$(id).oninput=draw;
for(const id of ['nr','nz','nt','currentField','purge','study','startC','duration','dt','period','duty','warmStart','initialSteady','steadyStop'])$(id).addEventListener('change',()=>{if(result)status('Settings changed. The displayed result and exports still belong to the previous completed run.');});
function drawTrace(){
  const c=$('trace'),ctx=c.getContext('2d'),h=result.history;ctx.clearRect(0,0,c.width,c.height);
  if(result.plan.study!=='transient')return;
  const keys=['avgK','tMax','tMin','wallAvgK'],colors=['#9b2424','#c57c1e','#256a9d','#697582'];
  let lo=Infinity,hi=-Infinity;for(const row of h)for(const key of keys){lo=Math.min(lo,row[key]);hi=Math.max(hi,row[key]);}
  const tEnd=Math.max(result.tEnd,1e-9),span=Math.max(hi-lo,1),X=t=>65+t/tEnd*(c.width-85),Y=v=>20+(hi-v)/span*(c.height-60);
  ctx.font='12px system-ui';ctx.fillStyle='#344a5c';
  for(let i=0;i<=4;i++){const v=lo+span*i/4;ctx.fillText((v-273.15).toFixed(1),5,Y(v)+4);ctx.fillText((tEnd*i/4).toPrecision(3),Math.min(X(tEnd*i/4),c.width-55),c.height-10);}
  keys.forEach((key,i)=>{ctx.strokeStyle=colors[i];ctx.lineWidth=2;ctx.beginPath();h.forEach((row,n)=>{if(n)ctx.lineTo(X(row.t),Y(row[key]));else ctx.moveTo(X(row.t),Y(row[key]));});ctx.stroke();});
}
$('csv').onclick=()=>{const m=result.mesh,ns=m.nr*m.nz,lines=['r_m,theta_rad,z_m,T_K,potential_V,joule_W'];for(let a=0;a<result.nt;a++)for(let j=0;j<m.nz;j++)for(let i=0;i<m.nr;i++){const p=a*ns+j*m.nr+i;lines.push([m.centers[i],(a+.5)*2*Math.PI/result.nt,m.zCenters[j],result.T[p],result.op.electrical?.potential[p]??'',result.op.qCell?.[p]??''].join(','));}download('joule-enclosure3d-field.csv',lines.join('\n'),'text/csv');};
$('history').onclick=()=>{const keys=['t','avgK','tMin','tMax','wallAvgK','pBulk','pContact','loss','storageRate','closure'];download('joule-enclosure3d-history.csv',[keys.join(','),...result.history.map(h=>keys.map(k=>h[k]??'').join(','))].join('\n'),'text/csv');};
