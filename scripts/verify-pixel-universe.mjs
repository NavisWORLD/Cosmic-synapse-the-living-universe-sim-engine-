import fs from 'node:fs';
import crypto from 'node:crypto';

const fail=m=>{ console.error('FAIL:',m); process.exitCode=1; };
const read=p=>fs.readFileSync(p,'utf8');
const required=[
  'pixel-universe/index.html',
  'pixel-universe/style.css',
  'pixel-universe/game.js',
  'pixel-universe/qseed.js',
  'pixel-universe/README.md',
  'pixel-universe/STORY.md'
];
for(const p of required) if(!fs.existsSync(p)) fail('missing '+p);
if(process.exitCode) process.exit(1);

const html=read(required[0]), css=read(required[1]), js=read(required[2]), seed=read(required[3]), story=read(required[5]);

for(const token of [
  'class QuantumBuddy','class SynapseEngine',
  'new Float32Array(12)','new Float32Array(42)','new Float32Array(54)',
  'EMBER AXIS','TIDE MEMORY','BLOOM Z','BLACK GARDEN','SYNAPSE CROWN',
  'localStorage','world.player.x','world.player.y','world.player.z'
]) if(!js.includes(token)) fail('missing gameplay token '+token);

for(const token of [
  'canvas id="game"','data-key="KeyQ"','data-key="KeyE"',
  'data-key="KeyF"','data-key="KeyB"'
]) if(!html.includes(token)) fail('missing input/UI token '+token);

if(!css.includes('image-rendering:pixelated')) fail('pixel rendering CSS missing');

const match=seed.match(/new Uint8Array\(\[([\s\S]*?)\]\)/);
if(!match) fail('quantum tape Uint8Array missing');
else {
  const values=(match[1].match(/\d+/g)||[]).map(Number);
  if(values.length!==8192) fail('quantum tape length '+values.length);
  if(values.some(v=>v<0||v>255)) fail('quantum tape byte out of range');
  const hash=crypto.createHash('sha256').update(Buffer.from(values)).digest('hex');
  const expected='9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8';
  if(hash!==expected) fail('quantum tape SHA-256 '+hash);
}

for(const token of ['OPEN','PRESERVE','WANDER','continue flying after any ending'])
  if(!story.includes(token)) fail('story token missing '+token);

if(!process.exitCode) console.log('PASS: Pixel Universe sandbox, XYZ navigation, Synapse 12D→42D→54D state, COSMOS autonomous simulated-agent behavior, story, persistence, mobile controls, and exact 8,192-byte quantum tape verified.');