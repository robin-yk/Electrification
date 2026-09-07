"""Read-only acquisition quality audit of the frozen yield model; no refitting."""
import time
import json
import torch
import numpy as np
from nextorch import bo
from propose_rph_yield_01 import DEST,write

def main():
    start=time.monotonic();torch.set_num_threads(1)
    t=json.loads((DEST/'training.json').read_text());p=json.loads((DEST/'proposal.json').read_text())
    e=bo.Experiment('audit-yield');e.input_data(np.array([r['x'] for r in t['points']]),np.array([r['y'] for r in t['points']]),X_ranges=[[0,1]]*3,unit_flag=True)
    m=bo.SingleTaskGP(e.X,e.Y);m.load_state_dict(torch.load(DEST/'model-state.pt',map_location='cpu'));m.eval()
    acq=bo.get_acq_func(m,'EI',best_f=e.Y.max())
    chosen=torch.tensor(p['normalized_x']).reshape(1,1,3)
    incumbent=torch.tensor(p['incumbent']['x']).reshape(1,1,3)
    grid=torch.quasirandom.SobolEngine(3,scramble=True,seed=1).draw(2048).reshape(-1,1,3)
    with torch.no_grad():
        a=acq(chosen).item();b=acq(incumbent).item();v=acq(grid)
    best=v.max().item()
    d=dict(status='passed' if a>=max(b,best)*(1-1e-5) else 'failed',chosen_EI_standardized=a,
        incumbent_EI_standardized=b,sobol_best_EI_standardized=best,sobol_best_normalized_x=grid[v.argmax(),0].tolist(),
        audit='Frozen model, correct standardized incumbent, 2048 deterministic Sobol evaluations; not a new proposal or global maximum proof',
        wall_s=time.monotonic()-start,reaction_runs=0)
    write(DEST/'acquisition-audit.json',d);print(json.dumps(d,indent=2))

if __name__=='__main__':main()
