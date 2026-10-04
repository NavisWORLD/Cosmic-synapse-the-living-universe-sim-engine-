import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  FIXTURE, MAILBOX_BYTES, MAILBOX_OFFSET, SRAM_SIZE,
  beastProfile, buildSave, crc32, expectedGenesis, fixtureSave, livingProfile, livingSeed, profileFromBeastJson,
} from './mailbox.mjs';
import { deriveTraits, encodeCommand, mockTraits } from './muse.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));

test('crc32 matches the ISO sample', () => {
  assert.equal(crc32(new TextEncoder().encode('123456789')), 0xcbf43926);
});

test('living fixture keeps the stat budget and stays inside the mailbox', () => {
  const profile = livingProfile(FIXTURE);
  const genesis = expectedGenesis(profile.seed);
  assert.equal(genesis.stats.reduce((a, b) => a + b, 0), 500);
  assert.equal(profile.bcp1.length, 64);
  const { sav } = fixtureSave();
  assert.equal(sav.length, SRAM_SIZE);
  assert.equal(String.fromCharCode(...sav.subarray(MAILBOX_OFFSET, MAILBOX_OFFSET + 4)), 'LCX1');
  for (let i = 0; i < sav.length; i++) {
    if (i < MAILBOX_OFFSET || i >= MAILBOX_OFFSET + MAILBOX_BYTES) assert.equal(sav[i], 0xff);
  }
  assert.equal(MAILBOX_OFFSET + MAILBOX_BYTES <= 25600, true);
  assert.equal(Buffer.from(sav).includes(Buffer.from('EEGRAW')), false);
});

test('fixture bytes match the Python mailbox', () => {
  const py = spawnSync('python3', ['gba/lost-cosmos-living-multiverse/tools/lc_mailbox.py', '--dump'], {
    cwd: root, encoding: 'utf8',
  });
  assert.equal(py.status, 0, py.stderr);
  const remote = JSON.parse(py.stdout);
  const { sav, profile } = fixtureSave();
  const sha = createHash('sha256').update(sav).digest('hex');
  assert.equal(sha, remote.sha256);
  assert.equal(profile.species, remote.species);
  assert.equal(profile.speciesName, remote.species_name);
  assert.equal(profile.publicId.toString(16).padStart(8, '0'), remote.public_id);
  assert.equal(profile.gameSeed.toString(16).padStart(8, '0'), remote.game_seed);
  assert.equal(profile.seed, remote.seed);
  assert.equal(profile.callsign, remote.callsign);
  assert.equal(profile.hue, remote.hue);
  assert.equal(livingSeed(FIXTURE.world, FIXTURE.evolution, FIXTURE.biosphere, FIXTURE.lifeEvents), remote.seed);
});

test('Beast Box nebula-test profile matches Python', () => {
  const py = spawnSync('python3', ['-c', `
import json, hashlib, sys
sys.path.insert(0, 'gba/lost-cosmos-living-multiverse/tools')
from lc_mailbox import beast_profile, build_save
p = beast_profile('nebula-test', 'void', 0, 50, 50, 50)
sav = build_save(p)
print(json.dumps({
  'species': p['species'],
  'callsign': p['callsign'],
  'public_id': f"{p['public_id']:08x}",
  'sha256': hashlib.sha256(sav).hexdigest(),
}))
`], { cwd: root, encoding: 'utf8' });
  assert.equal(py.status, 0, py.stderr);
  const remote = JSON.parse(py.stdout);
  const profile = beastProfile({ seed: 'nebula-test', familyName: 'void' });
  const sav = buildSave(profile);
  assert.equal(profile.species, remote.species);
  assert.equal(profile.callsign, remote.callsign);
  assert.equal(profile.publicId.toString(16).padStart(8, '0'), remote.public_id);
  assert.equal(createHash('sha256').update(sav).digest('hex'), remote.sha256);
  const wrapped = profileFromBeastJson({
    schema: 'beast-cage-creature-v1', version: 1, seed: 'nebula-test', family: 'void',
    game: { stats: Object.fromEntries(['hp', 'energy', 'signal', 'memory', 'resonance', 'agility', 'chaos', 'stability', 'curiosity', 'evolution'].map((name, i) => [name, expectedGenesis('nebula-test').stats[i]])) },
  });
  assert.equal(wrapped.species, 130);
});

test('trait derivation uses band power and Muse commands do not enter the save', () => {
  assert.deepEqual(deriveTraits({ delta: 1, theta: 1, alpha: 2, beta: 4, gamma: 2 }), { focus: 40, calm: 20, spark: 20 });
  const traits = mockTraits();
  for (const value of Object.values(traits)) assert.equal(Number.isInteger(value) && value >= 0 && value <= 100, true);
  const command = encodeCommand('p21');
  assert.equal(command[0], command.length - 1);
  assert.equal(new TextDecoder().decode(command.subarray(1)), 'p21\n');
  const sav = buildSave(livingProfile({ ...FIXTURE, ...traits }));
  assert.equal(Buffer.from(sav).includes(command), false);
});
