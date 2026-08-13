import fs from 'node:fs';
import crypto from 'node:crypto';

const file = 'standalone/SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html';
const EXPECTED = '62a2bb449abc28a0860fdaeec15ba4c5b53ae8199679029f97e7270cb4a90647';
const fail = (m) => { console.error(`FAIL: ${m}`); process.exitCode = 1; };
if (!fs.existsSync(file)) { fail(`missing ${file}`); process.exit(1); }
const buf = fs.readFileSync(file);
const html = buf.toString('utf8');
const sha = crypto.createHash('sha256').update(buf).digest('hex');
if (sha !== EXPECTED) fail(`canonical SHA mismatch: ${sha}`);
for (const [label, token] of [
  ['12D state', 'new Float32Array(12)'],
  ['42D state', 'new Float32Array(42)'],
  ['54D state', 'new Float32Array(54)'],
  ['12D name map', "this.names12=['frequency_mass'"],
  ['42D name map', 'this.names42=[...this.names12'],
  ['54D name map', 'this.names54=[...this.names42'],
  ['CSTStateEngine', 'class CSTStateEngine'],
  ['SensorFusion', 'class SensorFusion'],
  ['SimEarth707App', 'class SimEarth707App'],
  ['Genesis Universe ancestry', 'class Universe']
]) if (!html.includes(token)) fail(`missing ${label}`);
for (const req of [
  'app/manifest.webmanifest','app/sw.js','desktop/main.cjs','capacitor.config.json',
  'docs/TEACHER_GUIDE.md','paper/SIM_EARTH_7_07_TECHNICAL_PAPER.md'
]) if (!fs.existsSync(req)) fail(`missing packaging/document surface: ${req}`);
if (!process.exitCode) console.log(`PASS: SIM EARTH 7.07 verified. SHA-256 ${sha}; 12D/42D/54D surfaces present.`);
