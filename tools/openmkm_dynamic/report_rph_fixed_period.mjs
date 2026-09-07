import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=process.cwd();
const dirs=['docs/research/rph-fixed-period-01-2026-09-07/data','docs/research/rph-fixed-pulse-02-2026-09-07/data'];
const files=[`${dirs[0]}/half-refined.json`,`${dirs[1]}/refined.json`,`${dirs[0]}/double-refined.json`];
for(const dir of dirs)if(JSON.parse(fs.readFileSync(path.join(root,dir,'status.json'))).status!=='completed')throw Error('Incomplete batch');
const rows=files.map(file=>{const raw=fs.readFileSync(file);const d=JSON.parse(raw);return {file,sha256:crypto.createHash('sha256').update(raw).digest('hex'),period_s:d.inputs.period_s,cycles:d.cycles,carbon_yield_percent:Object.fromEntries(['C2H2','C2H4','CO','C6H6'].map(k=>[k,100*(d.carbon_yields[k]||0)])),product_g_per_g_CFP_h:Object.fromEntries(['C2H2','CO'].map(k=>[k,d.product_g_per_g_CFP_h[k]||0])),max_element_residual:Math.max(...d.history.flatMap(h=>Object.values(h.elemental_residuals).map(Math.abs)))};});
console.log(JSON.stringify({scope:'Fixed-flow three-period comparison; not global or Bayesian optimization',rows},null,2));
