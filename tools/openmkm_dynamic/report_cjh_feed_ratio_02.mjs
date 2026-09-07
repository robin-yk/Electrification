import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
const base=path.resolve('docs/research/cjh-feed-ratio-02-2026-09-07'),data=path.join(base,'data');
const names=['ratio-1-4','ratio-1-2','anchor','ratio-2-1','ratio-4-1'],labels=['1:4','1:2','1:1','2:1','4:1'];
const rows=names.map((n,i)=>({ratio:labels[i],...JSON.parse(fs.readFileSync(path.join(data,n+'.json')))}));
const status=JSON.parse(fs.readFileSync(path.join(data,'status.json')));
if(status.status!=='completed')throw Error('incomplete');
let report='# Fixed-volume CJH feed-ratio pilot\n\nRun 34139549926; source 8c4aa17. All seven integrations completed, including cold control and strict anchor. Five feed compositions, fixed 1750 C, 50 sccm at 0 C/1 atm, fixed equivalent volume, pressure target 1 atm. Residence time varies with composition. This is not an isolated fixed-residence-time composition effect or physical heating-volume validation.\n\n';
report+='| CH4:CO2 | Residence time ms | C2H2 C% | C2H4 C% | CO C% | C6H6 C% | C2H2 g/h | CO g/h | C2H2 g/gCFP/h |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n';
for(const r of rows)report+='| '+[r.ratio,r.mass_residence_time_s*1000,...['C2H2','C2H4','CO','C6H6'].map(s=>100*r.carbon_yields[s]),r.product_g_h.C2H2,r.product_g_h.CO,r.product_g_per_g_CFP_h.C2H2].map(v=>typeof v==='number'?v.toFixed(6):v).join(' | ')+' |\n';
report+='\nProductivity assumes 28.8 mg CFP and does not establish heating capacity. All carbon yields use total feed carbon. All conditions keep temperature, volume and total standard volumetric feed fixed, not mass feed or mass residence time. No global composition optimum is inferred from five samples. Tight-tolerance comparison applies to the 1:1 anchor only. Total elapsed: '+status.wall_s+' s.\n';
fs.writeFileSync(path.join(base,'REPORT.md'),report);fs.writeFileSync(path.join(base,'summary.json'),JSON.stringify(rows,null,2)+'\n');
fs.writeFileSync(path.join(base,'checksums.json'),JSON.stringify(Object.fromEntries(fs.readdirSync(data).sort().map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(path.join(data,f))).digest('hex')])),null,2)+'\n');
console.log(report);

