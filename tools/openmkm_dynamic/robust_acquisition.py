"""Bounded multistart acquisition search which never discards better seeds."""
import numpy as np
from scipy.optimize import minimize

def search(value_gradient,seeds,restarts=24):
    seeds=np.asarray(seeds,dtype=float)
    assert seeds.ndim==2 and np.isfinite(seeds).all()
    assert (seeds>=0).all() and (seeds<=1).all()
    scores=np.array([value_gradient(x)[0] for x in seeds])
    assert np.isfinite(scores).all()
    best=int(np.argmax(scores));point=seeds[best].copy();score=float(scores[best]);logs=[]
    for i in np.argsort(scores)[-restarts:]:
        def objective(x):
            v,g=value_gradient(x)
            assert np.isfinite(v) and np.isfinite(g).all()
            return -v,-np.asarray(g)
        result=minimize(objective,seeds[i],jac=True,method='L-BFGS-B',bounds=[(0,1)]*seeds.shape[1],
            options=dict(maxiter=150,ftol=1e-12,gtol=1e-8))
        candidate=np.clip(result.x,0,1);s=float(value_gradient(candidate)[0])
        logs.append(dict(success=bool(result.success),message=str(result.message),score=s))
        if np.isfinite(s) and s>score:point,score=candidate,s
    assert score>=scores.max()-1e-12
    return point,score,dict(seed_best=float(scores.max()),local_searches=logs)
