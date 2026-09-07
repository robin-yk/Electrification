// Cylindrical r/theta/z finite volumes. The r/z operators and material laws
// are shared with Joule2D; periodic theta faces are solved, not copied fields.
import {
  geometry, validateInput, validate2DConfig, build2DMesh, porosityFactor2D,
  cellK2D, cellSigma2D, assemble2DSystem, assembleElectrical2D, operating2DAt,
  boundaryLoss2D, storageRate2D, bicgstab2D, pcg2D
} from '../solver.js';

export function buildEnclosure3D(x, cfg) {
  const errors = [...validateInput(x), ...validate2DConfig(cfg)];
  if (errors.length) throw Error(errors.join(' '));
  if (x.shape !== 'cylinder') throw Error('Enclosed 3D requires a cylinder. No implicit rectangular-to-cylinder conversion.');
  const nt = cfg.nt ?? 8;
  if (!Number.isInteger(nt) || nt < 3 || nt > 32) throw Error('Angular cells must be an integer from 3 to 32.');
  const g = geometry(x), mesh = build2DMesh(g, cfg), ns = mesh.nr * mesh.nz;
  if (ns * nt > 250000 || mesh.nActiveZ <= 0 || !mesh.centers.every(Number.isFinite)) throw Error('Invalid or excessive mesh.');
  return {g, mesh, nt, ns, count: ns * nt, dtheta: 2 * Math.PI / nt,
    porosity: porosityFactor2D(mesh, cfg)};
}

const rows = (flat, a, d) => Array.from({length:d.mesh.nz}, (_,j) =>
  Array.from(flat.slice(a*d.ns+j*d.mesh.nr, a*d.ns+(j+1)*d.mesh.nr)));

function empty(count) {
  return {diag:new Float64Array(count), rhs:new Float64Array(count), edges:[], directed:[]};
}
function append(system, slice, offset, scale) {
  for (let i=0; i<slice.diag.length; i++) {
    system.diag[offset+i] += slice.diag[i]*scale;
    system.rhs[offset+i] += slice.rhs[i]*scale;
  }
  for (const [i,j,G] of slice.edges) system.edges.push([offset+i,offset+j,G*scale]);
  for (const [i,j,G] of slice.directed || []) system.directed.push([offset+i,offset+j,G*scale]);
}
function angularFaces(system, T, d, conductivity, elementOnly=false) {
  const m=d.mesh;
  for (let a=0; a<d.nt; a++) for (let j=0; j<m.nz; j++) for (let i=0; i<m.nr; i++) {
    if (elementOnly && m.materialAt(i,j)!==0) continue;
    const local=j*m.nr+i, p=a*d.ns+local, q=((a+1)%d.nt)*d.ns+local;
    // Midpoint quadrature for integral(k/r dr dz)/dtheta, including the
    // central wedge. The axis is an impermeable zero-area radial face.
    const area=(m.edges[i+1]-m.edges[i])*(m.zEdges[j+1]-m.zEdges[j]);
    const kp=conductivity(T[p],i,j), kq=conductivity(T[q],i,j);
    const G=area/(m.centers[i]*d.dtheta*(0.5/kp+0.5/kq));
    system.diag[p]+=G;system.diag[q]+=G;system.edges.push([p,q,G]);
  }
}

export function solveEnclosureElectrical(T, x, cfg, d, op) {
  const m=d.mesh, system=empty(d.count), terminals=[], material=x.material;
  for (let a=0; a<d.nt; a++) {
    const s=assembleElectrical2D(rows(T,a,d),material,m,d.porosity);
    append(system,s,a*d.ns,1/d.nt);
    for (const [p,G,end] of s.electrodes) terminals.push([a*d.ns+p,G/d.nt,end]);
  }
  angularFaces(system,T,d,(t,i,j)=>cellSigma2D(t,material)*d.porosity.multiplier[j*m.nr+i],true);
  const guess=new Float64Array(d.count);
  for (let a=0;a<d.nt;a++) for(let j=m.activeStart;j<m.activeEnd;j++) for(let i=0;i<m.nElement;i++)
    guess[a*d.ns+j*m.nr+i]=(m.zCenters[j]-m.zEdges[m.activeStart])/d.g.L;
  const solved=pcg2D(system,guess,4000,1e-11);
  if (solved.relativeResidual>1e-8) throw Error('3D electrical linear solve did not converge.');
  const unit=solved.x;let input=0,output=0;
  for(const [p,G,end] of terminals) {if(end) input+=G*(1-unit[p]);else output+=G*unit[p];}
  if (!(input>0)) throw Error('No conducting path.');
  const qCell=new Float64Array(d.count);
  for(const [p,q,G] of system.edges) {
    const heat=G*(unit[p]-unit[q])**2/2;qCell[p]+=heat;qCell[q]+=heat;
  }
  for(const [p,G,end] of terminals) qCell[p]+=G*(end-unit[p])**2;
  const unitHeat=qCell.reduce((s,v)=>s+v,0);
  for(let p=0;p<d.count;p++) qCell[p]*=op.pBulk/unitHeat;
  const potential=Float64Array.from(unit,v=>v*op.current/input),J=new Float64Array(d.count);
  for(let a=0;a<d.nt;a++)for(let j=m.activeStart;j<m.activeEnd;j++)for(let i=0;i<m.nElement;i++) {
    const p=a*d.ns+j*m.nr+i;
    const lo=i?potential[p-1]:potential[p],hi=i+1<m.nElement?potential[p+1]:potential[p];
    const rlo=i?m.centers[i-1]:m.centers[i],rhi=i+1<m.nElement?m.centers[i+1]:m.centers[i];
    const zlo=j===m.activeStart?m.zEdges[j]:m.zCenters[j-1];
    const zhi=j===m.activeEnd-1?m.zEdges[j+1]:m.zCenters[j+1];
    const vlo=j===m.activeStart?0:potential[p-m.nr],vhi=j===m.activeEnd-1?op.current/input:potential[p+m.nr];
    const vm=potential[((a+d.nt-1)%d.nt)*d.ns+j*m.nr+i],vp=potential[((a+1)%d.nt)*d.ns+j*m.nr+i];
    const sigma=cellSigma2D(T[p],material)*d.porosity.multiplier[j*m.nr+i];
    J[p]=sigma*Math.hypot((hi-lo)/Math.max(rhi-rlo,1e-30),(vhi-vlo)/(zhi-zlo),(vp-vm)/(2*m.centers[i]*d.dtheta));
  }
  return {qCell,potential,J,
    fieldResistance:1/input,chargeError:Math.abs(input-output)/input,
    sourceNormalization:op.current ? op.pBulk/(op.current**2/input) : null,
    closure:'2D-compatible mean-temperature supply resistance; normalized 3D dissipation; J is a cell-centred gradient diagnostic'};
}

export function assembleEnclosure3D(T, x, cfg, d, op, transient=null) {
  const system=empty(d.count), m=d.mesh;
  for(let a=0;a<d.nt;a++) {
    // A slice operator originally represents a full revolution. Scale every
    // term, including purge enthalpy and storage, by its angular fraction.
    const localOp={...op};
    if(op.qCell) localOp.qCell=Float64Array.from(op.qCell.slice(a*d.ns,(a+1)*d.ns),q=>q*d.nt);
    const old=transient ? {dt:transient.dt,Tprev:rows(transient.Tprev,a,d)} : null;
    append(system,assemble2DSystem(rows(T,a,d),x,d.g,cfg,x.material,m,localOp,old),a*d.ns,1/d.nt);
  }
  angularFaces(system,T,d,(t,i,j)=>cellK2D(m.materialAt(i,j),t,x.material,cfg,x)*d.porosity.multiplier[j*m.nr+i]);
  return system;
}

function summarize(T,d) {
  const m=d.mesh;let sum=0,volume=0,tMin=Infinity,tMax=-Infinity,wall=0,wallVolume=0;
  for(let a=0;a<d.nt;a++)for(let j=0;j<m.nz;j++)for(let i=0;i<m.nr;i++) {
    const t=T[a*d.ns+j*m.nr+i],v=m.cellVolume(i,j)/d.nt,code=m.materialAt(i,j);
    if(code===0){sum+=t*v;volume+=v;tMin=Math.min(tMin,t);tMax=Math.max(tMax,t);}
    if(code===2){wall+=t*v;wallVolume+=v;}
  }
  return {avgK:sum/volume,tMin,tMax,deltaT:tMax-tMin,wallAvgK:wall/wallVolume};
}
function losses(T,x,cfg,d,op) {
  const result={total:0,gasAdvective:0,gasOutletK:0,byChannel:{}};
  for(let a=0;a<d.nt;a++) {
    const loss=boundaryLoss2D(rows(T,a,d),x,d.g,cfg,x.material,d.mesh,op);
    for(const key of ['total','gasAdvective','gasOutletK'])result[key]+=loss[key]/d.nt;
    for(const [key,value] of Object.entries(loss.byChannel))result.byChannel[key]=(result.byChannel[key]||0)+value/d.nt;
  }
  return result;
}
function operating(T,x,cfg,d,scale=1) {
  const op=operating2DAt(summarize(T,d).avgK,x,d.g,cfg,x.material);
  for(const key of ['pBulk','pContact','pTotal'])op[key]*=scale;
  // This is the same cycle-averaged power convention as the 2D transient.
  op.current*=Math.sqrt(scale);op.voltage*=Math.sqrt(scale);
  if(cfg.currentField) {
    op.electrical=solveEnclosureElectrical(T,x,cfg,d,op);
    op.qCell=op.electrical.qCell;
  }
  return op;
}
function iterate(T,x,cfg,d,transient,scale,progress) {
  const tolerance=cfg.tolerance,limit=cfg.maxIter;let step=Infinity,relaxation=0.62,stalls=0;
  for(let iteration=0;iteration<limit;iteration++) {
    const op=operating(T,x,cfg,d,scale),system=assembleEnclosure3D(T,x,cfg,d,op,transient);
    const solved=bicgstab2D(system,T,4000,1e-11);
    if(solved.relativeResidual>1e-8)throw Error('3D thermal linear solve did not converge.');
    const previous=step;step=0;
    for(let p=0;p<d.count;p++){
      const next=solved.x[p];if(!Number.isFinite(next)||next<1||next>6000)throw Error('Temperature outside 1 to 6000 K. No accepted result.');
      step=Math.max(step,Math.abs(next-T[p]));T[p]+=relaxation*(next-T[p]);
    }
    if(iteration%5===0)progress({iteration:iteration+1,residual:step});
    if(step<=tolerance)return {iterations:iteration+1,residual:step,op:operating(T,x,cfg,d,scale)};
    if(iteration>=4){stalls=step>previous*.9?stalls+1:0;if(stalls>=2){relaxation=Math.max(.08,relaxation*.6);stalls=0;}else if(iteration===4)relaxation=.86;}
  }
  throw Error('3D nonlinear solve did not converge. No accepted result.');
}

export function solveEnclosure3D(x,cfg,plan={},progress=()=>{}) {
  const d=buildEnclosure3D(x,cfg), transient=plan.study==='transient';
  if(plan.study && !['steady','transient'].includes(plan.study))throw Error('Unknown study type.');
  const startK=plan.startK ?? x.ambientK;
  if(!Number.isFinite(startK)||startK<1||startK>6000)throw Error('Invalid initial temperature.');
  let T=plan.startField ? Float64Array.from(plan.startField) : new Float64Array(d.count).fill(startK);
  if(T.length!==d.count||T.some(t=>!Number.isFinite(t)||t<1||t>6000))throw Error('Initial field does not match the 3D mesh or temperature range.');
  const duration=plan.duration ?? plan.dt*plan.steps;
  if(transient && !(Number.isFinite(plan.dt)&&plan.dt>0&&Number.isFinite(duration)&&duration>0))throw Error('Positive finite duration and time step required.');
  const period=plan.period??1,duty=plan.duty??1;
  if(!(Number.isFinite(period)&&period>0&&Number.isFinite(duty)&&duty>=0&&duty<=1))throw Error('Invalid pulse settings.');
  const growth=plan.dtGrowth??1,maxDt=plan.maxDt??plan.dt,stepLimit=plan.steps??1200;
  if(transient && (!(Number.isFinite(growth)&&growth>=1&&Number.isFinite(maxDt)&&maxDt>0)||!Number.isInteger(stepLimit)||stepLimit<1||stepLimit>1200))throw Error('Invalid step growth or step limit.');
  let time=0,steps=0,inputEnergy=0,lossEnergy=0,storedEnergy=0,contactEnergy=0,worstClosure=0,last;
  let nextDt=plan.dt,peakStorage=0,steadyStreak=0,stopReason=null;
  const history=[{t:0,...summarize(T,d),pBulk:0}];
  do {
    let dt=0,scale=plan.powerScale??1;
    if(transient) {
      if(++steps>1200)throw Error('More than 1200 time steps requested.');
      let until=Infinity;
      if(duty===0)scale=0;
      else if(duty<1){const phase=(time+1e-10)%period,on=phase<duty*period;scale*=on?1:0;until=(on?duty*period:period)-phase+1e-10;}
      dt=Math.min(nextDt,duration-time,until);
      if(typeof plan.sourceIntegral==='function')scale=plan.sourceIntegral(time,time+dt);
      else if(typeof plan.sourceScale==='function')scale=plan.sourceScale(time+dt);
    }
    if(!Number.isFinite(scale)||scale<0)throw Error('Invalid power multiplier.');
    const prev=Float64Array.from(T);
    const solve=iterate(T,x,cfg,d,transient?{dt,Tprev:prev}:null,scale,p=>progress({...p,time}));
    const op=solve.op,loss=losses(T,x,cfg,d,op);let storage=0;
    if(transient)for(let a=0;a<d.nt;a++)storage+=storageRate2D(rows(T,a,d),rows(prev,a,d),cfg,x.material,d.mesh,dt)/d.nt;
    const closure=Math.abs(op.pBulk-loss.total-storage)/Math.max(op.pBulk,Math.abs(loss.total),Math.abs(storage),1e-8);
    worstClosure=Math.max(worstClosure,closure);time+=dt;
    inputEnergy+=op.pBulk*dt;contactEnergy+=op.pContact*dt;lossEnergy+=loss.total*dt;storedEnergy+=storage*dt;
    last={...summarize(T,d),...solve,loss,storageRate:storage,closure};
    history.push({t:time,...summarize(T,d),pBulk:op.pBulk,pContact:op.pContact,loss:loss.total,storageRate:storage,closure});
    progress({time,steps,closure});
    peakStorage=Math.max(peakStorage,Math.abs(storage));
    if(plan.steadyTol>0&&peakStorage>0){steadyStreak=Math.abs(storage)/peakStorage<plan.steadyTol?steadyStreak+1:0;if(steadyStreak>=(plan.steadyHold??3))stopReason='steady';}
    if(transient)nextDt=Math.min(maxDt,nextDt*growth);
  } while(transient && time<duration-1e-10 && steps<stepLimit && !stopReason);
  if(transient && time<duration-1e-10 && steps>=stepLimit && plan.steps===undefined && !stopReason)
    throw Error('The 1200-step safety cap was reached before the requested duration. Increase the step or shorten the run; no completed result accepted.');
  // Functions on the base mesh are intentionally omitted for worker transfer.
  const {materialAt,cellVolume,...mesh}=d.mesh;
  return {x,cfg,plan,mesh,nt:d.nt,T,history,...last,converged:true,steps,tEnd:time,
    worstClosure,inputEnergy,contactEnergy,lossEnergy,storedEnergy,
    stopReason:stopReason??(transient?(time>=duration-1e-10?'duration':'steps'):'steady'),
    integratedResidual:inputEnergy-lossEnergy-storedEnergy,
    contactTreatment:'Contact power leaves through external leads, as in 2D; not deposited in the thermal domain.',
    radiationTreatment:'Sector-local concentric-gap exchange; no nonlocal 3D view-factor solve.'};
}
