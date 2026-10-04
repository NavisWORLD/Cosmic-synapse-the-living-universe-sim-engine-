import fs from 'node:fs';
import crypto from 'node:crypto';

const file = 'standalone/SIM_EARTH_7_08_REALITY_BODY.html';
const EXPECTED = '47bf8b6379c425b77dca15bfe2de95e87af451ec994368d43b3253cebe373dfd';
const fail = (m) => { console.error(`FAIL: ${m}`); process.exitCode = 1; };
if (!fs.existsSync(file)) { fail(`missing ${file}`); process.exit(1); }
const buf = fs.readFileSync(file);
const html = buf.toString('utf8').replace(/\r\n/g, '\n');
const normalized = Buffer.from(html, 'utf8');
const sha = crypto.createHash('sha256').update(normalized).digest('hex');
if (sha !== EXPECTED) fail(`canonical SHA mismatch after LF normalization: ${sha}`);

for (const [label, token] of [
  ['12D state', 'new Float32Array(12)'],
  ['42D state', 'new Float32Array(42)'],
  ['54D state', 'new Float32Array(54)'],
  ['12D name map', "this.names12=['frequency_mass'"],
  ['42D name map', 'this.names42=[...this.names12'],
  ['54D name map', 'this.names54=[...this.names42'],
  ['CSTStateEngine', 'class CSTStateEngine'],
  ['SensorFusion', 'class SensorFusion'],
  ['SimEarth app ancestry', 'class SimEarth707App'],
  ['Genesis Universe ancestry', 'class Universe'],
  ['Reality Body WebGL2 renderer', 'class RealityRenderer708'],
  ['LUNA-ARC vessel', 'LUNA-ARC'],
  ['ship flight mode', 'this.flightMode'],
  ['desktop Reality Body view control', 'sim708-view'],
  ['desktop Reality Body ship control', 'sim708-ship'],
  ['mobile Reality Body view control', 's708-touch-view'],
  ['mobile Reality Body ship control', 's708-touch-ship'],
  ['closable control panel', 'sim707-panel-close'],
  ['full HUD close', 'sim707-ui-close'],
  ['persistent UI restore control', 'sim707-ui-reopen'],
  ['active visual settings tab', 'sim707-pane-visuals'],
  ['graphics quality bridge', 'setGraphicsQuality'],
  ['world visual invalidation', 'invalidateWorldVisuals'],
  ['WebGL live daylight calculation', 'baseDay=a.renderer.skyInfo().day'],
  ['Lost Cosmos handheld pane', 'sim707-pane-cosmos'],
  ['Lost Cosmos handheld frame', 'lc-arcade-frame'],
  ['Learner Buddy pane', 'sim707-pane-buddy'],
  ['Learner Buddy frame', 'lb-buddy-frame'],
  ['Synapse OS pane', 'sim707-pane-synapse'],
  ['Synapse OS frame', 'lc-synapse-frame'],
  ['Pocket Reality brand', 'Cute Beast Pocket Reality Learners']
]) if (!html.includes(token)) fail(`missing ${label}`);

if (fs.existsSync('standalone/SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html')) fail('legacy 7.07 canonical still present beside 7.08');
if (fs.existsSync('.reality708')) fail('temporary Reality Body transfer directory survived cleanup');
if (fs.existsSync('.build708')) fail('temporary 7.08 native-build trigger survived cleanup');
if (fs.existsSync('scripts/apply_reality_708.py')) fail('temporary Reality Body reconstruction script survived cleanup');
if (fs.existsSync('.github/workflows/apply-reality-708.yml')) fail('temporary Reality Body reconstruction workflow survived cleanup');
if (fs.existsSync('.github/workflows/build-reality-708.yml')) fail('temporary one-shot Reality Body build workflow survived cleanup');

for (const req of [
  'app/manifest.webmanifest','app/sw.js','desktop/main.cjs','capacitor.config.json',
  'docs/TEACHER_GUIDE.md','docs/VISUAL_REALISM.md','docs/REALITY_BODY_7_08.md',
  'BUILD_VERIFICATION_7.08.md','paper/SIM_EARTH_7_07_TECHNICAL_PAPER.md'
]) if (!fs.existsSync(req)) fail(`missing packaging/document surface: ${req}`);

const buddyPage = 'arcade/learner-buddy/index.html';
if (!fs.existsSync(buddyPage)) fail(`missing ${buddyPage}`);
else {
  const buddy = fs.readFileSync(buddyPage, 'utf8');
  if (!buddy.includes('not a medical device')) fail('Learner Buddy disclaimer missing');
  if (/src="https?:/.test(buddy)) fail('Learner Buddy must not load remote scripts');
  for (const file of [
    'arcade/learner-buddy/app.mjs',
    'arcade/learner-buddy/store.mjs',
    'arcade/learner-buddy/preferences.mjs',
    'arcade/learner-buddy/growth.mjs',
    'arcade/learner-buddy/cue.mjs',
  ]) {
    if (!fs.existsSync(file)) fail(`missing ${file}`);
    else if (/\bfetch\(/.test(fs.readFileSync(file, 'utf8'))) fail(`${file} must not call fetch`);
  }
}

if (!process.exitCode) console.log(`PASS: SIM EARTH 7.08 Reality Body verified. Canonical LF SHA-256 ${sha}; WebGL2 Reality Body + LUNA-ARC + Luna field body + 12D/42D/54D surfaces + 7.08 verification receipt + UI/graphics hotfix controls present.`);
