import { makeGrid } from './solver.js';
'use strict';
const $=id=>document.getElementById(id);
const keys=['shape','length','width','height','bore','n','rho','k','alpha','density','cp','contact','offsetA','offsetB','mode','command','vmax','imax','pmax','ambient','sink','h','emissivity','hc','maxTemp','study','duration','dt','period','duty','initial'];
const strings=new Set(['shape','mode','study']);
const presets={SiC:[1e-4,120,3210,750],TiO2:[1e-3,8,4230,690],Fe:[1e-7,80,7874,449],C:[8e-6,25,2200,710]};
let model,result=null,worker=null,yaw=1.05,pitch=.4,zoom=1,drawn=[],drag=null,dirty=false;
const params=()=>Object.fromEntries(keys.map(k=>[k,strings.has(k)?$(k).value:Number($(k).value)]));
const fmt=(x,d=3)=>!Number.isFinite(x)?'--':Math.abs(x)!==0&&(Math.abs(x)<.001||Math.abs(x)>=1e5)?x.toExponential(2):x.toLocaleString('en-US',{maximumFractionDigits:d});
function status(s,error=false){$('status').textContent=s;$('status').classList.toggle('error',error);}
function controls(){const p=params();$('heightrow').hidden=!['block','neck'].includes(p.shape);$('borerow').hidden=p.shape!=='tube';$('timeinputs').hidden=p.study!=='transient';$('contactval').textContent=p.contact+'%';$('commandlabel').firstChild.textContent='Setpoint ('+p.mode+')';}
function invalidate(){
  if(worker)return;controls();result=null;$('csv').disabled=true;$('budget').hidden=true;$('chartpanel').hidden=true;
  for(const k of ['R','P','max','avg','rate','seconds'])$('s'+k).textContent='--';
  try{model=makeGrid(params());status(model.N.toLocaleString()+' cells · inputs changed; calculate to update fields.');draw();}catch(e){model=null;status(e.message,true);draw();}
}
for(const k of keys)$(k).addEventListener('input',()=>{if(['rho','k','alpha','density','cp'].includes(k))$('material').value='custom';if(k==='rho'&&Number($('rho').value)>0)$('rhoslider').value=Math.log10(Number($('rho').value));invalidate();});
$('material').onchange=()=>{const v=presets[$('material').value];if(v){['rho','k','density','cp'].forEach((k,i)=>$(k).value=v[i]);$('alpha').value=0;$('rhoslider').value=Math.log10(v[0]);invalidate();}};
$('rhoslider').oninput=()=>{$('rho').value=Number((10**Number($('rhoslider').value)).toPrecision(5));$('material').value='custom';invalidate();};
function setBusy(b){for(const el of document.querySelectorAll('.inputs input,.inputs select'))el.disabled=b;$('material').disabled=b;$('solve').disabled=b;$('cancel').disabled=!b;$('progress').hidden=!b;}
function run(){
  if(worker)return;let p=params();try{model=makeGrid(p);}catch(e){status(e.message,true);return;}
  result=null;for(const k of ['R','P','max','avg','rate','seconds'])$('s'+k).textContent='--';$('csv').disabled=true;$('budget').hidden=true;$('chartpanel').hidden=true;setBusy(true);draw();status('Solving '+model.N.toLocaleString()+' cells…');$('progress').removeAttribute('value');
  try{worker=new Worker(new URL('./worker.js',import.meta.url),{type:'module'});}catch(e){setBusy(false);status('Cannot start worker: '+e.message,true);return;}
  worker.onmessage=e=>{const data=e.data;if(data.progress){const z=data.progress;status((p.study==='transient'?'t = '+fmt(z.time)+' / '+p.duration+' s · ':'')+(z.iteration?'iteration '+z.iteration+' · ΔT '+fmt(z.delta,6)+' K':'time step completed'));if(p.study==='transient'){$('progress').max=p.duration;$('progress').value=z.time;}return;}worker.terminate();worker=null;setBusy(false);if(data.error){status(data.error,true);return;}result=data.done;model=result.mesh;showResults();};
  worker.onerror=e=>{worker.terminate();worker=null;setBusy(false);status(e.message||'Worker failed.',true);};worker.postMessage(p);
}
$('solve').onclick=run;$('cancel').onclick=()=>{if(worker){worker.terminate();worker=null;setBusy(false);status('Cancelled. No new converged result.');}};
function showResults(){const s=result.stats;for(const k of ['R','P','max','avg','rate','seconds'])$('s'+k).textContent=fmt(s[k],k==='R'?5:2);$('csv').disabled=false;
  status(s.limiter+' · '+fmt(s.V)+' V · '+fmt(s.I)+' A · '+model.N.toLocaleString()+' cells · heat balance residual '+fmt(s.energyError*100,6)+'%');
  const parts=[['To ambient',fmt(s.ambient)+' W'],['To electrodes',fmt(s.contacts)+' W'],['Current balance residual',fmt(s.chargeError*100,7)+'%'],['Solid volume',fmt(s.volume*1e6)+' cm³']];
  if(result.params.study==='transient')parts.push(['Integrated input',fmt(s.inputEnergy)+' J'],['Stored heat',fmt(s.stored)+' J'],['Integrated heat loss',fmt(s.lossEnergy)+' J'],['Integrated balance residual',fmt(s.integratedError*100,6)+'%']);
  $('budget').replaceChildren(...parts.map(([k,v])=>{const el=document.createElement('div');el.textContent=k+': '+v;return el;}));$('budget').hidden=false;$('chartpanel').hidden=result.params.study!=='transient';draw();chart();
}
function sizeCanvas(canvas){const box=canvas.getBoundingClientRect(),ratio=window.devicePixelRatio||1;canvas.width=Math.max(1,Math.round(box.width*ratio));canvas.height=Math.max(1,Math.round(box.height*ratio));const c=canvas.getContext('2d');c.setTransform(ratio,0,0,ratio,0,0);return[c,box.width,box.height];}
const stops=[[22,13,61],[89,18,105],[168,46,94],[232,91,56],[253,164,45],[246,251,164]];
function colour(v){const t=Math.max(0,Math.min(.999999,v))*(stops.length-1),i=Math.floor(t),f=t-i;return 'rgb('+stops[i].map((n,j)=>Math.round(n+(stops[i+1][j]-n)*f)).join(',')+')';}
function rotation(q){const a=q[0]*Math.cos(yaw)+q[2]*Math.sin(yaw),b=-q[0]*Math.sin(yaw)+q[2]*Math.cos(yaw);return[a,q[1]*Math.cos(pitch)-b*Math.sin(pitch),q[1]*Math.sin(pitch)+b*Math.cos(pitch)];}
function draw(){
  const[c,w,h]=sizeCanvas($('scene'));c.clearRect(0,0,w,h);drawn=[];if(!model)return;
  const m=model,scale=.79*Math.min(w,h)/(Math.max(m.L,m.W,m.H))*zoom,proj=q=>{const r=rotation(q);return[w/2+r[0]*scale,h/2-r[1]*scale,r[2]];};
  const field=$('field').value,values=result&&field!=='geometry'?result[field]:null;let lo=Infinity,hi=-Infinity;if(values)for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}
  $('legendtitle').textContent=values?$('field').selectedOptions[0].textContent:'Electrode patches';$('minvalue').textContent=values?fmt(lo):'A · cyan';$('maxvalue').textContent=values?fmt(hi):'B · orange';document.querySelector('.ramp').style.background=values?'':'linear-gradient(90deg,#26b9cf,#f39c43)';
  const axis=$('cut').value==='none'?-1:Number($('cut').value),dims=[m.W,m.H,m.L],threshold=axis<0?0:(Number($('slice').value)/100-.5)*dims[axis];
  const shown=Uint8Array.from(m.xyz,q=>axis<0||q[axis]<=threshold),faces=m.faces.filter(f=>shown[f[0]]);
  if(axis>=0)for(const [a,b,k]of m.edges)if(shown[a]!==shown[b])faces.push(shown[a]?[a,k,1,0]:[b,k,-1,0]);
  for(const [a,k,sign,terminal]of faces){
    const normal=[0,0,0];normal[k]=sign;if(rotation(normal)[2]<=1e-7)continue;
    const center=m.xyz[a].slice();center[k]+=sign*m.d[k]/2;const axes=[0,1,2].filter(n=>n!==k),points=[];
    for(const[u,v]of [[-1,-1],[1,-1],[1,1],[-1,1]]){const q=center.slice();q[axes[0]]+=u*m.d[axes[0]]/2;q[axes[1]]+=v*m.d[axes[1]]/2;points.push(proj(q));}
    drawn.push({a,k,sign,terminal,points,depth:proj(center)[2],fill:values?colour(hi===lo?.5:(values[a]-lo)/(hi-lo)):terminal===1?'#26b9cf':terminal===2?'#f39c43':'#8ba3bb'});
  }
  drawn.sort((a,b)=>a.depth-b.depth);
  for(const face of drawn){c.beginPath();face.points.forEach((q,i)=>i?c.lineTo(q[0],q[1]):c.moveTo(q[0],q[1]));c.closePath();c.fillStyle=face.fill;c.fill();c.strokeStyle=$('mesh').checked?'rgba(20,35,60,.35)':face.fill;c.lineWidth=$('mesh').checked?.55:.5;c.stroke();}
  for(const[list,label]of [[m.termA,'A'],[m.termB,'B']]){const q=[0,0,label==='A'?-m.L/2:m.L/2];for(const a of list){q[0]+=m.xyz[a][0]/list.length;q[1]+=m.xyz[a][1]/list.length;}const r=proj(q);c.fillStyle='#10273f';c.beginPath();c.arc(r[0],r[1],11,0,2*Math.PI);c.fill();c.fillStyle='#fff';c.font='14px Arial';c.textAlign='center';c.textBaseline='middle';c.fillText(label,r[0],r[1]);}
  [['X','#a5373c',[1,0,0]],['Y','#247858',[0,1,0]],['Z','#235fbc',[0,0,1]]].forEach(([name,color,q])=>{const r=rotation(q);c.strokeStyle=color;c.beginPath();c.moveTo(48,h-49);c.lineTo(48+r[0]*30,h-49-r[1]*30);c.stroke();c.fillStyle=color;c.font='13px Arial';c.fillText(name,48+r[0]*40,h-49-r[1]*40);});
  $('viewhint').textContent=(result?'Solved field':'Geometry preview')+' · drag to rotate · scroll to zoom'+(axis>=0?' · '+['X','Y','Z'][axis]+' ≤ '+fmt(threshold*1000)+' mm':'');
}
function inside(x,y,points){let hit=false;for(let i=0,j=points.length-1;i<points.length;j=i++){const a=points[i],b=points[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;}
$('scene').onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,total:0};$('scene').setPointerCapture(e.pointerId);};
$('scene').onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.total+=Math.abs(dx)+Math.abs(dy);yaw+=dx*.008;pitch=Math.max(-1.4,Math.min(1.4,pitch+dy*.008));drag.x=e.clientX;drag.y=e.clientY;draw();};
$('scene').onpointerup=e=>{const moved=drag?.total||0;drag=null;if(moved>5||!model)return;const box=$('scene').getBoundingClientRect(),face=[...drawn].reverse().find(f=>inside(e.clientX-box.left,e.clientY-box.top,f.points));if(!face)return;
  const pick=$('pick').value;if(pick!=='none'&&!worker){const sign=pick==='A'?-1:1;if(face.k!==2||face.sign!==sign||Math.abs(model.xyz[face.a][2]-sign*(model.L/2-model.d[2]/2))>1e-9){$('probe').textContent='Rotate to the '+(sign<0?'−Z':' +Z')+' end face.';return;}$('offset'+pick).value=Math.max(-80,Math.min(80,Math.round(model.xyz[face.a][0]/(model.W/2)*100)));invalidate();return;}
  const q=model.xyz[face.a].map(v=>fmt(v*1000,2)).join(', '),field=$('field').value;$('probe').textContent='('+q+') mm'+(result&&field!=='geometry'?' · '+fmt(result[field][face.a])+' '+{T:'°C',phi:'V',q:'W/m³',J:'A/m²'}[field]:'');};
$('scene').onpointercancel=()=>drag=null;$('scene').addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.45,Math.min(3,zoom*Math.exp(-e.deltaY*.001)));draw();},{passive:false});
for(const k of ['field','mesh','slice','cut'])$(k).oninput=()=>{$('slice').hidden=$('cut').value==='none';draw();};$('fit').onclick=()=>{yaw=1.05;pitch=.4;zoom=1;draw();};
function chart(){if(!result||result.params.study!=='transient')return;const[c,w,h]=sizeCanvas($('history')),rows=result.history,left=62,right=w-18,top=25,bottom=h-42;const low=Math.min(...rows.map(r=>r.avg)),high=Math.max(...rows.map(r=>r.max)),pad=Math.max(1,(high-low)*.08),y0=low-pad,y1=high+pad;const x=t=>left+t/result.params.duration*(right-left),y=t=>bottom-(t-y0)/(y1-y0)*(bottom-top);c.clearRect(0,0,w,h);c.font='13px Arial';c.strokeStyle='#d5dce6';c.fillStyle='#405269';c.textBaseline='middle';
  for(let i=0;i<=4;i++){const v=y0+(y1-y0)*i/4,yy=y(v);c.beginPath();c.moveTo(left,yy);c.lineTo(right,yy);c.stroke();c.textAlign='right';c.fillText(fmt(v,1),left-7,yy);const t=result.params.duration*i/4;c.textAlign='center';c.fillText(fmt(t,2),x(t),bottom+17);}
  c.textAlign='left';c.fillText('°C',left,12);c.textAlign='right';c.fillText('Time (s)',right,h-5);
  for(const[key,col]of [['max','#b63750'],['avg','#2267bb']]){c.strokeStyle=col;c.lineWidth=2;c.beginPath();rows.forEach((r,i)=>i?c.lineTo(x(r.t),y(r[key])):c.moveTo(x(r.t),y(r[key])));c.stroke();}}
function download(name,text,type){const a=document.createElement('a'),url=URL.createObjectURL(new Blob([text],{type}));a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('json').onclick=()=>download('joule3d-settings.json',JSON.stringify({schema:'joule3d-draft-1',parameters:result?result.params:params(),stats:result?.stats},null,2),'application/json');
$('csv').onclick=()=>{if(!result)return;const lines=['x_m,y_m,z_m,T_C,potential_V,qJ_W_m3,J_A_m2'];model.xyz.forEach((q,i)=>lines.push([...q,result.T[i],result.phi[i],result.q[i],result.J[i]].join(',')));download('joule3d-field.csv',lines.join('\n'),'text/csv');};
for(const k of ['work','method'])$(k+'tab').onclick=()=>{$('workspace').hidden=k!=='work';$('method').hidden=k!=='method';$('worktab').setAttribute('aria-pressed',k==='work');$('methodtab').setAttribute('aria-pressed',k==='method');if(k==='work'){draw();chart();}};
new ResizeObserver(()=>{draw();chart();}).observe($('scene'));window.addEventListener('resize',chart);controls();invalidate();run();

window.addEventListener('message',event=>{
  if(event.source!==parent || event.origin!==location.origin || event.data?.type!=='joule3d-import')return;
  if(worker){worker.terminate();worker=null;setBusy(false);}
  const p=event.data.parameters;
  for(const key of keys)if(Object.hasOwn(p,key))$(key).value=p[key];
  $('material').value='custom';
  $('rhoslider').value=Math.log10(Number($('rho').value));
  invalidate();
  status('Imported 0D geometry and constant properties at 25 °C. Review 3D boundaries, then Calculate 3D.');
});
