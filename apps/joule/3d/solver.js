/* Joule3D: cell-centred, conservative Cartesian finite volumes. SI internally. */
'use strict';
function makeGrid(p) {
  const nx=p.n,ny=p.n,nz=3*p.n,W=p.width/1000,H=(p.shape==='block'||p.shape==='neck'?p.height:p.width)/1000,L=p.length/1000;
  if(![W,H,L].every(v=>v>0&&Number.isFinite(v))||!Number.isInteger(nx)||nx<3||nx>24) throw Error('Invalid dimensions or mesh resolution.');
  if(p.shape==='tube'&&!(p.bore>=0&&p.bore<p.width)) throw Error('Bore must be smaller than the outer diameter.');
  const d=[W/nx,H/ny,L/nz],area=[d[1]*d[2],d[0]*d[2],d[0]*d[1]],vol=d[0]*d[1]*d[2];
  const map=new Int32Array(nx*ny*nz).fill(-1),xyz=[],ijk=[];
  const id=(i,j,k)=>(k*ny+j)*nx+i;
  for(let k=0;k<nz;k++)for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
    const x=(i+.5)*d[0]-W/2,y=(j+.5)*d[1]-H/2,z=(k+.5)*d[2]-L/2;
    const r=Math.hypot(x,y),neck=Math.abs(z)<L*.23;
    if((p.shape==='rod'||p.shape==='tube')&&r>W/2)continue;
    if(p.shape==='tube'&&r<p.bore/2000)continue;
    if(p.shape==='neck'&&neck&&Math.abs(x)>W*.25)continue;
    map[id(i,j,k)]=xyz.length;xyz.push([x,y,z]);ijk.push([i,j,k]);
  }
  const edges=[],faces=[],termA=[],termB=[];
  for(let a=0;a<xyz.length;a++)for(let axis=0;axis<3;axis++)for(const sign of [-1,1]){
    const q=ijk[a].slice();q[axis]+=sign;
    const b=q[0]<0||q[0]>=nx||q[1]<0||q[1]>=ny||q[2]<0||q[2]>=nz?-1:map[id(...q)];
    if(b>=0){if(sign===1)edges.push([a,b,axis]);continue;}
    let terminal=0;
    if(axis===2&&((sign<0&&ijk[a][2]===0)||(sign>0&&ijk[a][2]===nz-1))){
      const offset=(sign<0?p.offsetA:p.offsetB)/100*W/2;
      if(Math.abs(xyz[a][0]-offset)<=p.contact/100*W/2+1e-12)terminal=sign<0?1:2;
    }
    faces.push([a,axis,sign,terminal]);
    if(terminal===1)termA.push(a);if(terminal===2)termB.push(a);
  }
  if(!termA.length||!termB.length)throw Error('An electrode covers no cells. Increase contact width or refine the mesh.');
  // Every component must reach a terminal; disjoint solids have no defined potential.
  const seen=new Uint8Array(xyz.length),adj=Array.from({length:xyz.length},()=>[]);
  for(const [a,b]of edges){adj[a].push(b);adj[b].push(a);}
  const stack=[termA[0]];seen[termA[0]]=1;let connected=0;
  while(stack.length){const a=stack.pop();connected++;for(const b of adj[a])if(!seen[b]){seen[b]=1;stack.push(b);}}
  if(connected!==xyz.length)throw Error('The voxel solid is disconnected. Refine the mesh or increase wall thickness.');
  return {N:xyz.length,nx,ny,nz,W,H,L,d,area,vol,xyz,edges,faces,termA,termB};
}
function cg(diag,edges,g,b,initial,tol=1e-10){
  const n=b.length,x=initial?Float64Array.from(initial):new Float64Array(n),r=new Float64Array(n),z=new Float64Array(n),v=new Float64Array(n),a=new Float64Array(n);
  function mul(src,dst){for(let i=0;i<n;i++)dst[i]=diag[i]*src[i];for(let e=0;e<edges.length;e++){const [i,j]=edges[e];dst[i]-=g[e]*src[j];dst[j]-=g[e]*src[i];}}
  mul(x,a);let rz=0,b2=0;
  for(let i=0;i<n;i++){if(!(diag[i]>0))throw Error('No thermal reference: add heat loss or select transient.');r[i]=b[i]-a[i];v[i]=z[i]=r[i]/diag[i];rz+=r[i]*z[i];b2+=b[i]*b[i];}
  const threshold=Math.max(1e-26,b2*tol*tol);
  for(let it=0;it<2400;it++){
    let r2=0;for(let i=0;i<n;i++)r2+=r[i]*r[i];if(r2<=threshold)return x;
    mul(v,a);let va=0;for(let i=0;i<n;i++)va+=v[i]*a[i];
    if(!(va>0))throw Error('Linear solve lost positive definiteness.');
    const step=rz/va;let next=0;
    for(let i=0;i<n;i++){x[i]+=step*v[i];r[i]-=step*a[i];z[i]=r[i]/diag[i];next+=r[i]*z[i];}
    const beta=next/rz;for(let i=0;i<n;i++)v[i]=z[i]+beta*v[i];rz=next;
  }
  throw Error('Linear solve did not converge.');
}
function solveModel(p,progress=()=>{}){
  const started=Date.now(),m=makeGrid(p),N=m.N,SB=5.670374419e-8,Ta=p.ambient+273.15,Tc=p.sink+273.15;
  for(const key of ['rho','k','cp','density','vmax','imax','pmax','maxTemp'])if(!(p[key]>0&&Number.isFinite(p[key])))throw Error(key+' must be positive.');
  for(const key of ['h','hc','command'])if(!(p[key]>=0&&Number.isFinite(p[key])))throw Error(key+' must be nonnegative.');
  if(!(Ta>0&&Tc>0&&p.initial>-273.15&&p.emissivity>=0&&p.emissivity<=1&&Number.isFinite(p.alpha)))throw Error('Invalid temperature, emissivity or resistivity coefficient.');
  if(p.study==='transient'&&!(p.dt>0&&p.duration>0&&p.period>0&&p.duty>=0&&p.duty<=1))throw Error('Invalid time or pulse settings.');
  if(p.study==='steady'&&p.h===0&&p.hc===0&&p.emissivity===0)throw Error('Steady heating needs a path for heat to leave the solid.');
  let T=new Float64Array(N).fill(p.study==='steady'?Ta:p.initial+273.15),phi=new Float64Array(N);
  const gt=new Float64Array(m.edges.length),base=new Float64Array(N),capacity=p.density*p.cp*m.vol;
  m.edges.forEach(([a,b,axis],e)=>{gt[e]=p.k*m.area[axis]/m.d[axis];base[a]+=gt[e];base[b]+=gt[e];});
  function electrical(temp,on){
    const res=Float64Array.from(temp,t=>p.rho*(1+p.alpha*(t-298.15)));
    if(res.some(r=>!Number.isFinite(r)||r<=0))throw Error('The linear resistivity law reached zero or a negative value. Change its coefficient or temperature range.');
    const diag=new Float64Array(N),rhs=new Float64Array(N),ge=new Float64Array(m.edges.length);
    m.edges.forEach(([a,b,axis],e)=>{ge[e]=2*m.area[axis]/(m.d[axis]*(res[a]+res[b]));diag[a]+=ge[e];diag[b]+=ge[e];});
    for(const a of m.termA){const g=2*m.area[2]/(m.d[2]*res[a]);diag[a]+=g;rhs[a]+=g;}
    for(const a of m.termB)diag[a]+=2*m.area[2]/(m.d[2]*res[a]);
    phi=cg(diag,m.edges,ge,rhs,phi);
    let G=0,Gb=0;for(const a of m.termA)G+=2*m.area[2]/(m.d[2]*res[a])*(1-phi[a]);
    for(const a of m.termB)Gb+=2*m.area[2]/(m.d[2]*res[a])*phi[a];
    if(!(G>0))throw Error('No conducting path between electrodes.');
    const req=on?(p.mode==='V'?p.command:p.mode==='I'?p.command/G:Math.sqrt(p.command/G)):0;
    const limits=[req,p.vmax,p.imax/G,Math.sqrt(p.pmax/G)],V=Math.min(...limits),limiter=['Setpoint','Voltage limit','Current limit','Power limit'][limits.indexOf(V)];
    const heat=new Float64Array(N),jx=new Float64Array(N),jy=new Float64Array(N),jz=new Float64Array(N),components=[jx,jy,jz];
    m.edges.forEach(([a,b,axis],e)=>{const dp=(phi[a]-phi[b])*V,watts=ge[e]*dp*dp;heat[a]+=watts*res[a]/(res[a]+res[b]);heat[b]+=watts*res[b]/(res[a]+res[b]);const j=ge[e]*dp/(2*m.area[axis]);components[axis][a]+=j;components[axis][b]+=j;});
    for(const [list,u]of [[m.termA,1],[m.termB,0]])for(const a of list){const g=2*m.area[2]/(m.d[2]*res[a]),dp=(u-phi[a])*V;heat[a]+=g*dp*dp;jz[a]+=(u===1?1:-1)*g*dp/(2*m.area[2]);}
    return {R:1/G,V,I:G*V,P:G*V*V,limiter,heat,potential:Float64Array.from(phi,x=>x*V),J:Float64Array.from(jx,(x,i)=>Math.hypot(x,jy[i],jz[i])),chargeError:Math.abs(G-Gb)/G};
  }
  function boundaries(temp){
    const diag=new Float64Array(N),rhs=new Float64Array(N);let ambient=0,contacts=0;
    for(const [a,axis,sign,terminal]of m.faces){
      const cond=2*p.k/m.d[axis],target=terminal?Tc:Ta;let h=p.hc;
      if(!terminal){
        let surface=temp[a];
        for(let j=0;j<10;j++)surface+=(cond*(temp[a]-surface)-p.h*(surface-Ta)-p.emissivity*SB*(surface**4-Ta**4))/(cond+p.h+4*p.emissivity*SB*surface**3);
        h=p.h+p.emissivity*SB*(surface+Ta)*(surface*surface+Ta*Ta);
      }
      const g=h===0?0:m.area[axis]/(1/cond+1/h);diag[a]+=g;rhs[a]+=g*target;
      if(terminal)contacts+=g*(temp[a]-target);else ambient+=g*(temp[a]-target);
    }
    return {diag,rhs,ambient,contacts};
  }
  let lastE,lastB,lastRate=0,lastError=0,iterations=0;
  function advance(old,dt,on,time){
    let guess=Float64Array.from(old),converged=false;
    for(let it=0;it<140;it++){
      const e=electrical(guess,on),b=boundaries(guess),diag=Float64Array.from(base),rhs=new Float64Array(N),mass=dt?capacity/dt:0;
      for(let i=0;i<N;i++){diag[i]+=b.diag[i]+mass;rhs[i]=e.heat[i]+b.rhs[i]+mass*old[i];}
      const next=cg(diag,m.edges,gt,rhs,guess);let delta=0;
      for(let i=0;i<N;i++){delta=Math.max(delta,Math.abs(next[i]-guess[i]));guess[i]+=.7*(next[i]-guess[i]);if(!Number.isFinite(guess[i])||guess[i]>p.maxTemp+273.15||guess[i]<=0)throw Error('Temperature left the specified calculation range. Reduce the input or adjust the model.');}
      iterations++;if(it%5===0)progress({time,iteration:it+1,delta,cells:N});
      if(delta<2e-6){converged=true;break;}
    }
    if(!converged)throw Error('Electrothermal iteration did not converge. A steady solution has not been established.');
    lastE=electrical(guess,on);lastB=boundaries(guess);
    const storage=dt?guess.reduce((s,t,i)=>s+capacity*(t-old[i])/dt,0):0;
    lastRate=dt?storage/(capacity*N):0;
    lastError=Math.abs(lastE.P-lastB.ambient-lastB.contacts-storage)/Math.max(Math.abs(lastE.P),Math.abs(lastB.ambient)+Math.abs(lastB.contacts),Math.abs(storage),1e-8);
    return {temp:guess,storage};
  }
  const history=[];let inputEnergy=0,lossEnergy=0,time=0,steps=0;
  const summarize=()=>{let max=-Infinity,avg=0;for(const t of T){max=Math.max(max,t);avg+=t;}return {max:max-273.15,avg:avg/N-273.15};};
  const initialEnergy=T.reduce((s,t)=>s+capacity*t,0);
  if(p.study==='steady'){T=advance(T,0,true,0).temp;history.push({t:0,...summarize(),P:lastE.P});}
  else{
    history.push({t:0,...summarize(),P:0});
    while(time<p.duration-1e-10){
      if(++steps>1200)throw Error('More than 1,200 time steps. Increase the time step or reduce the duration.');
      let on=true,toEvent=Infinity;
      if(p.duty<=0)on=false;else if(p.duty<1){let phase=(time+1e-10)%p.period;on=phase<p.duty*p.period;toEvent=(on?p.duty*p.period:p.period)-phase+1e-10;}
      const dt=Math.min(p.dt,p.duration-time,toEvent);if(dt<1e-12)throw Error('Time step too small.');
      T=advance(T,dt,on,time+dt).temp;time+=dt;inputEnergy+=lastE.P*dt;lossEnergy+=(lastB.ambient+lastB.contacts)*dt;
      history.push({t:time,...summarize(),P:lastE.P});progress({time,iteration:0,delta:0,cells:N});
    }
  }
  const stored=T.reduce((s,t)=>s+capacity*t,0)-initialEnergy;
  return {params:p,mesh:m,T:Float64Array.from(T,t=>t-273.15),phi:lastE.potential,q:Float64Array.from(lastE.heat,q=>q/m.vol),J:lastE.J,history,
    stats:{...summarize(),R:lastE.R,V:lastE.V,I:lastE.I,P:lastE.P,limiter:lastE.limiter,ambient:lastB.ambient,contacts:lastB.contacts,rate:lastRate,energyError:lastError,chargeError:lastE.chargeError,inputEnergy:p.study==='transient'?inputEnergy:null,lossEnergy:p.study==='transient'?lossEnergy:null,stored:p.study==='transient'?stored:null,integratedError:p.study==='transient'?Math.abs(inputEnergy-lossEnergy-stored)/Math.max(Math.abs(inputEnergy),Math.abs(stored),1e-8):null,seconds:(Date.now()-started)/1000,iterations,steps,volume:N*m.vol}};
}
export { makeGrid, solveModel };

