import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {radialParabola,annulusDrops} from './joule.mjs';
const file=new URL('../../docs/research/joule-v6-2026-09-07/limits.json',import.meta.url);
if(fs.existsSync(file))throw Error('Preserve previous output');
// Finite cylinders must approach, not equal, infinite-cylinder formulas.
const rows=[50,100].map(ar=>({ar,radial:radialParabola(ar),annulus:annulusDrops(ar)}));
const worst=r=>Math.max(...r.annulus.map(x=>x.relative));
if(!(worst(rows[1])<worst(rows[0])))throw Error('Annulus limit does not improve');
if(!(rows[1].radial.worstRelative<rows[0].radial.worstRelative))throw Error('Radial limit does not improve');
fs.writeFileSync(file,JSON.stringify({commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),rows},null,2));
console.log(JSON.stringify(rows));
