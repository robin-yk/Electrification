// Deterministic navigation inventory. Never infer validation from completion.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(here), source=path.join(root,'docs/research');
function category(n){
  if(n.startsWith('joule-'))return 'ScreenJoule migration';
  if(/^(h2o-|pah-|porsin-|parcel-temperature)/.test(n))return '03 Feed and mechanism effects';
  if(/energy|pareto|parcel-flow|rph-candidate-flow/.test(n))return '04 Energy and Pareto';
  if(/quickstart|campaign/.test(n))return 'Execution and support';
  return '02 Aramco product design';
}
const dirs=fs.readdirSync(source,{withFileTypes:true}).filter(x=>x.isDirectory()).map(x=>x.name).sort();
let lines=['# Batch inventory','','Generated from the current filesystem by `node research/build-index.mjs`. One row per original archive directory. Nested rounds are retained under their parent. Status is copied only from an explicit top-level status file; consult each report for mixed or partial outcomes.','','| Research route | Original archive | Entry | Recorded status |','|---|---|---|---|'];
for(const n of dirs){
 const dir=path.join(source,n), names=fs.readdirSync(dir);
 const entry=['REPORT.md','README.md','RUNCARD.md','manifest.json'].find(x=>names.includes(x));
 let status='See source records';
 if(names.includes('status.json')){const j=JSON.parse(fs.readFileSync(path.join(dir,'status.json'),'utf8'));const s=j.status??j.state;if(typeof s==='string')status=s;}
 lines.push(`| ${category(n)} | [${n}](../docs/research/${n}/) | ${entry?`[${entry}](../docs/research/${n}/${entry})`:'Directory'} | ${status.replaceAll('|','/').replaceAll('\n',' ')} |`);
}
lines.push('','## Legacy GRI collections','','The GRI atlas and transient campaigns precede the batch archive layout. Start at [canonical](../tools/openmkm_dynamic/data/canonical/), [feed-grid](../tools/openmkm_dynamic/data/feed-grid/), [wide](../tools/openmkm_dynamic/data/wide/) and [runs](../tools/openmkm_dynamic/data/runs/).','','## Standalone archive notes','');
for(const x of fs.readdirSync(source,{withFileTypes:true}).filter(x=>x.isFile()&&x.name.endsWith('.md')).sort((a,b)=>a.name.localeCompare(b.name)))lines.push(`- [${x.name}](../docs/research/${x.name})`);
fs.writeFileSync(path.join(here,'BATCHES.md'),lines.join('\n')+'\n');
console.log(`Indexed ${dirs.length} archive directories; original data unchanged.`);
