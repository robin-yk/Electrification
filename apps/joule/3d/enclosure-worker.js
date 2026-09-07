import {solveEnclosure3D} from './enclosure.js';
import {calculate,solveThermal2D} from '../solver.js';
self.onmessage=({data})=>{
  try {
    const {x,cfg,plan,compare}=data;
    if(plan.initialSteady){
      const initial=solveEnclosure3D(x,cfg,{study:'steady'},p=>self.postMessage({type:'progress',...p}));
      plan.startField=initial.T;
    }
    const result=solveEnclosure3D(x,cfg,plan,p=>self.postMessage({type:'progress',...p}));
    if(compare){
      if(plan.study==='transient')throw Error('Paired comparison currently requires steady mode.');
      const r=solveThermal2D(x,calculate(x),cfg,x.material);
      if(r.errors.length||!r.converged)throw Error('The paired 2D solve did not converge.');
      result.comparison={avgK2D:r.avgK,deltaAvgK:result.avgK-r.avgK,
        deltaMaxK:result.tMax-r.tMax,deltaGasK:result.loss.gasOutletK-r.heOutletK,
        closure2D:r.closure,closure3D:result.closure};
    }
    self.postMessage({type:'done',result});
  }catch(error){self.postMessage({type:'error',message:error.message});}
};
