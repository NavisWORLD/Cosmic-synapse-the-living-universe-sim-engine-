import { readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const read = (path) => readFileSync(`app/${path}`);
const html = read('index.html').toString();
assert(html.includes('src="arcade/lost-cosmos/index.html"'), 'Prepared handheld iframe is missing');
assert(html.includes('src="arcade/learner-buddy/index.html"'), 'Prepared Learner Buddy iframe is missing');
assert(html.includes('src="arcade/lost-cosmos/synapse.html"'), 'Prepared Synapse OS iframe is missing');
assert(html.includes('src="arcade/spark-beasts/index.html"'), 'Prepared Spark Beasts iframe is missing');
assert(html.includes('Cute Beast Pocket Reality Learners'), 'Pocket Reality brand is missing');
for (const path of ['manifest.webmanifest', 'sw.js', 'offline.html', 'icon-192.png',
  'icon-512.png', 'apple-touch-icon.png', 'arcade/lost-cosmos/index.html',
  'arcade/lost-cosmos/player.mjs', 'arcade/lost-cosmos/mailbox.mjs',
  'arcade/learner-buddy/index.html', 'arcade/learner-buddy/app.mjs',
  'arcade/learner-buddy/store.mjs', 'arcade/learner-buddy/preferences.mjs',
  'arcade/learner-buddy/growth.mjs', 'arcade/learner-buddy/cue.mjs',
  'arcade/lost-cosmos/synapse.html', 'arcade/lost-cosmos/synapse.mjs',
  'arcade/lost-cosmos/qbeast.mjs', 'arcade/lost-cosmos/synapse-os.mjs',
  'arcade/lost-cosmos/qr.mjs', 'arcade/lost-cosmos/qrcodegen.mjs',
  'arcade/spark-beasts/index.html', 'arcade/spark-beasts/app.mjs',
  'arcade/spark-beasts/genome.mjs', 'arcade/spark-beasts/showcase.mjs',
  'arcade/spark-beasts/data/quantum-runs.json',
  'arcade/spark-beasts/media/rare/manifest.json',
  'arcade/spark-beasts/media/rare/Ferrotitan_4a10.mp4',
  'arcade/third_party/emulatorjs/data/loader.js',
  'arcade/third_party/emulatorjs/data/emulator.min.js',
  'arcade/third_party/emulatorjs/data/cores/mgba-wasm.data',
  'arcade/third_party/emulatorjs/data/cores/mgba-legacy-wasm.data']) {
  assert(statSync(`app/${path}`).size > 0, `${path} is absent or empty`);
}
const rom = read('arcade/lost-cosmos/rom/lost-cosmos.gba');
const receipt = JSON.parse(read('arcade/lost-cosmos/rom/release.json'));
assert.equal(rom.length, receipt.bytes);
assert(rom.length >= 1024 * 1024 && rom.length <= 32 * 1024 * 1024);
assert.equal(createHash('sha256').update(rom).digest('hex'), receipt.sha256);
let checksum = 0x19;
for (let i = 0xa0; i <= 0xbc; i++) checksum += rom[i];
assert.equal((-checksum) & 0xff, rom[0xbd], 'GBA header checksum is invalid');
assert.equal(rom[0xb2], 0x96, 'GBA header marker is invalid');
console.log(`PASS: Pages bundle includes verified V${receipt.version} cartridge ${receipt.sha256}`);
