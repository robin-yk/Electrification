// One author-requested refinement point, with unchanged manufactured source.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {mmsStudy} from './joule.mjs';
const output=new URL('../../docs/research/joule-v6-2026-09-07/mms-240.json',import.meta.url);
if(fs.existsSync(output))throw Error('Preserve existing result');
const solverHash=createHash('sha256').update(fs.readFileSync(new URL('../../apps/joule/solver.js',import.meta.url))).digest('hex');
const cache=JSON.parse(fs.readFileSync(new URL('../../docs/research/joule-v6-2026-09-07/grid-detail.json',import.meta.url)));
if(cache.solverHash!==solverHash)throw Error('Cached solver differs');
const start=performance.now();
const [point]=mmsStudy(1,[{nr:240,nz:480}]);
const previous=cache.mms.find(r=>r.nr===120);
if(!Number.isFinite(point.l2)||point.l2>=previous.l2)throw Error('Refinement did not reduce error');
const result={solverHash,point:{...point,nr:240},previous,order:Math.log(previous.l2/point.l2)/Math.log(2),seconds:(performance.now()-start)/1000};
fs.writeFileSync(output,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
