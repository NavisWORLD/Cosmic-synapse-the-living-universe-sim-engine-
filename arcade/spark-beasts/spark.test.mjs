import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { buildGenome } from './genome.mjs';
import { renderSprite } from './render.mjs';
import { indexTable } from './runs.mjs';
import { presentClips, safeMediaPath } from './showcase.mjs';
import { simulate, simulateStable, stabilize } from './signal.mjs';
import { eraseStore, grant, loadStore, rememberBeast, saveStore, stageFromXp } from './store.mjs';
import { admit, emptyLedger, genomeFromRecipe, openShare, releaseForTrade, sanitizeName, sealShare, sparkRecord, xpFromGrowth } from './trade.mjs';
import { wildRunIndex } from './explore.mjs';

const root = fileURLToPath(new URL('./', import.meta.url));
const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const fixture = JSON.parse(read('./fixtures/parity.json'));
const table = indexTable(JSON.parse(read('./data/quantum-runs.json')));
const manifest = JSON.parse(read('./media/rare/manifest.json'));

function sha(bytes) {
  return createHash('sha256').update(Buffer.from(bytes)).digest('hex');
}

function memory() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => map.set(key, String(value)),
    removeItem: (key) => map.delete(key),
  };
}

function runOf(key) {
  const run = table.byKey.get(key);
  assert.ok(run, `missing recorded run ${key}`);
  return run;
}

const RARE_NAMES = [
  'Ferrotitan', 'Gearwarden', 'Cogknight', 'Nyxleviath', 'Nyxwyrm', 'Noctveil', 'Chartyrant',
  'Calderwyvern', 'Snowleviath', 'Frostphoenix', 'Reefwing', 'Calderwarden',
];

test('the same signal, run, and name always spark the same genome', () => {
  const run = runOf(fixture.cases[0].genome.inputs.quantum_run);
  const traits = fixture.cases[0].genome.inputs.traits;
  const first = buildGenome(traits, run, 'u1');
  const second = buildGenome(traits, run, 'u1');
  assert.deepEqual(second, first);
  assert.equal(first.seed, fixture.cases[0].genome.seed);
});

test('genomes match the Python fixtures, including the original seven runs', () => {
  for (const item of fixture.cases) {
    const expected = item.genome;
    const run = runOf(expected.inputs.quantum_run);
    const genome = buildGenome(expected.inputs.traits, run, expected.inputs.user_id);
    assert.deepEqual(genome, expected, item.label);
  }
  const traits = { focus: 30, calm: 30, spark: 30 };
  fixture.o7_keys.forEach((key, index) => {
    const genome = buildGenome(traits, runOf(key), null);
    assert.equal(genome.seed, fixture.o7_seeds[index], key);
  });
});

test('sprites match the Python pixel digests', { timeout: 120000 }, () => {
  const views = {
    1: [1, {}],
    2: [2, {}],
    3: [3, {}],
    back: [2, { layer: 'back' }],
    main_round: [2, { layer: 'main', eyes: 'round' }],
  };
  for (const item of fixture.cases) {
    for (const [name, [stage, options]] of Object.entries(views)) {
      const sprite = renderSprite(item.genome, stage, options);
      assert.equal(sprite.width, 64);
      assert.equal(sprite.height, 64);
      assert.equal(sha(sprite.rgba), item.sprites[name], `${item.label} ${name}`);
    }
  }
});

test('stabilization uses the median of eight windows and bucket 10', () => {
  assert.deepEqual(simulateStable('balanced'), fixture.stab.balanced);
  assert.deepEqual(stabilize(fixture.stab.windows0), { focus: 30, calm: 30, spark: 30 });
  for (const session of fixture.stab.sessions) {
    assert.deepEqual(session, { focus: 30, calm: 30, spark: 30 });
  }
  const mock = simulate('mock');
  assert.equal(mock.focus, fixture.stab.mock.focus);
  assert.equal(mock.calm, fixture.stab.mock.calm);
  assert.equal(mock.spark, fixture.stab.mock.spark);
});

test('a sparked beast round-trips through the cage without a second copy', async () => {
  const expected = fixture.cases[0].genome;
  const run = runOf(expected.inputs.quantum_run);
  const runIndex = table.runs.findIndex((row) => row.key === run.key);
  const name = sanitizeName(expected.inputs.user_id);
  const genome = buildGenome(expected.inputs.traits, run, name);
  const record = sparkRecord(genome, runIndex, 150);
  assert.ok(record.seed.length <= 64);
  assert.equal(stageFromXp(150), 3);

  const ledger = emptyLedger();
  const held = await admit(ledger, record, 'local');
  const text = await sealShare(held, 'island-key');
  await assert.rejects(() => openShare(text, 'wrong-key'), /seal/i);
  const opened = await openShare(text, 'island-key');
  assert.equal(opened.seed, record.seed);
  assert.equal(xpFromGrowth(opened.growth), 150);
  const rebuilt = genomeFromRecipe(opened.seed, table);
  assert.equal(rebuilt.genome.seed, genome.seed);
  assert.equal(rebuilt.genome.island, genome.island);
  assert.equal(rebuilt.genome.names['1'], genome.names['1']);

  const flipped = `${text.slice(0, 80)}X${text.slice(81)}`;
  await assert.rejects(() => openShare(flipped, 'island-key'), /checksum|seal|Share/i);

  const duplicate = sparkRecord(genome, runIndex, 150);
  duplicate.transfer = 'ab'.repeat(16);
  await assert.rejects(() => admit(ledger, duplicate, 'receive'), /second copy|already/i);
  await releaseForTrade(ledger, held);
  await assert.rejects(() => admit(ledger, held, 'local'), /released/i);
});

test('experience and bond never shrink', () => {
  const storage = memory();
  const store = loadStore(storage);
  const first = rememberBeast(store, {
    seed: 'abc', traits: { focus: 30, calm: 30, spark: 30 }, runIndex: 0, runKey: 'k',
    island: 'The Crown', name: 'Crest', xp: 50, bond: 10,
  });
  assert.equal(first.stage, 2);
  rememberBeast(store, { ...first, xp: 10, bond: 2 });
  assert.equal(store.beasts.abc.xp, 50);
  assert.equal(store.beasts.abc.bond, 10);
  const grew = grant(store, 'abc', 80, 5);
  assert.equal(grew.beast.xp, 130);
  assert.equal(grew.beast.stage, 3);
  assert.equal(grew.grew, true);
  grant(store, 'abc', 0, 0);
  assert.equal(store.beasts.abc.xp, 130);
  saveStore(store, storage);
  assert.equal(loadStore(storage).beasts.abc.xp, 130);
  eraseStore(storage);
  assert.deepEqual(loadStore(storage).beasts, {});
});

test('wild island encounters stay on the same recorded runs', () => {
  const count = table.runs.length;
  assert.equal(count, 5580);
  for (let island = 0; island < 8; island++) {
    const index = wildRunIndex(island, count);
    assert.equal(wildRunIndex(island, count), index);
    assert.ok(index >= 0 && index < count);
  }
});

test('the rare gallery lists twelve beasts plus the montage and skips missing files', async () => {
  assert.deepEqual(manifest.clips.map((clip) => clip.name), [...RARE_NAMES, 'Montage']);
  assert.equal(manifest.clips.at(-1).video, 'montage.mp4');
  assert.equal(manifest.clips.at(-1).seconds, 80);
  for (const name of RARE_NAMES.slice(0, 7)) {
    const clip = manifest.clips.find((row) => row.name === name);
    assert.equal(existsSync(new URL(`./media/${clip.video}`, import.meta.url)), true, clip.video);
    assert.equal(existsSync(new URL(`./media/${clip.audioLog}`, import.meta.url)), true, clip.audioLog);
  }
  const onDisk = (rel) => existsSync(new URL(`./media/${rel}`, import.meta.url));
  const shown = await presentClips(manifest, onDisk);
  assert.deepEqual(shown.map((clip) => clip.name), RARE_NAMES.slice(0, 7));
  const withLater = await presentClips(manifest, async (rel) => onDisk(rel) || rel === 'montage.mp4' || rel.endsWith('/Calderwyvern.mp4'));
  assert.deepEqual(withLater.map((clip) => clip.name), [...RARE_NAMES.slice(0, 7), 'Calderwyvern', 'Montage']);
  assert.equal(safeMediaPath('../secret.mp4'), null);
  assert.equal(safeMediaPath('/etc/passwd'), null);
  assert.equal(safeMediaPath('rare/Calderwyvern.mp4'), 'rare/Calderwyvern.mp4');
  const page = read('./app.mjs');
  assert.match(page, /video\.autoplay = false/);
  assert.match(page, /video\.muted = false/);
  assert.match(page, /video\.preload = 'none'/);
  assert.doesNotMatch(page, /video\.autoplay = true/);
  assert.doesNotMatch(read('./index.html'), /autoplay/);
  void root;
});
