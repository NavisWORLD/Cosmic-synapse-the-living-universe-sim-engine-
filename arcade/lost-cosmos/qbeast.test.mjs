import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { FIXTURE, attachGrowth, beastProfile, buildGrowth, buildSave, crc32, expectedGenesis, livingProfile } from './mailbox.mjs';
import {
  acceptSuggestion, canonical, encodeTicket, fromQbeastSnapshot, importPayload, parseTicket,
  readZipAllowlist, sealShare, sha256Hex, suggestionFromText, ticketLink,
} from './qbeast.mjs';
import { admit, emptyLedger, releaseForTrade, tend } from './synapse-os.mjs';
import { qrMatrix } from './qr.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));
const text = (value) => new TextEncoder().encode(value);

function creature(seed, family) {
  const genesis = expectedGenesis(seed);
  const names = ['hp', 'energy', 'signal', 'memory', 'resonance', 'agility', 'chaos', 'stability', 'curiosity', 'evolution'];
  return {
    schema: 'beast-cage-creature-v1',
    version: 1,
    seed,
    family,
    game: { stats: Object.fromEntries(names.map((name, i) => [name, genesis.stats[i]])) },
  };
}

function storeZip(entries) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const [name, data] of entries) {
    const nameBytes = text(name);
    const header = new Uint8Array(30 + nameBytes.length);
    const view = new DataView(header.buffer);
    view.setUint32(0, 0x04034b50, true);
    view.setUint16(4, 20, true);
    view.setUint16(6, 0x800, true);
    view.setUint32(14, crc32(data), true);
    view.setUint32(18, data.length, true);
    view.setUint32(22, data.length, true);
    view.setUint16(26, nameBytes.length, true);
    header.set(nameBytes, 30);
    locals.push(header, data);
    const central = new Uint8Array(46 + nameBytes.length);
    const cd = new DataView(central.buffer);
    cd.setUint32(0, 0x02014b50, true);
    cd.setUint16(4, 20, true);
    cd.setUint16(6, 20, true);
    cd.setUint16(8, 0x800, true);
    cd.setUint32(16, crc32(data), true);
    cd.setUint32(20, data.length, true);
    cd.setUint32(24, data.length, true);
    cd.setUint16(28, nameBytes.length, true);
    cd.setUint32(42, offset, true);
    central.set(nameBytes, 46);
    centrals.push(central);
    offset += header.length + data.length;
  }
  const centralBytes = concat(centrals);
  const eocd = new Uint8Array(22);
  const end = new DataView(eocd.buffer);
  end.setUint32(0, 0x06054b50, true);
  end.setUint16(8, entries.length, true);
  end.setUint16(10, entries.length, true);
  end.setUint32(12, centralBytes.length, true);
  end.setUint32(16, offset, true);
  return concat([...locals, centralBytes, eocd]);
}

function concat(parts) {
  const size = parts.reduce((sum, part) => sum + part.length, 0);
  const out = new Uint8Array(size);
  let cursor = 0;
  for (const part of parts) { out.set(part, cursor); cursor += part.length; }
  return out;
}

test('cage record matches Python and stays out of the manual slots', () => {
  const py = spawnSync('python3', ['-c', `
import hashlib, json, sys
sys.path.insert(0, 'gba/lost-cosmos-living-multiverse/tools')
from lc_mailbox import attach_growth, build_growth, fixture_save
sav, profile = fixture_save()
growth = build_growth(profile['public_id'], 4, 2, 10, 1, 2, True, True)
out = attach_growth(sav, growth)
print(json.dumps({'sha256': hashlib.sha256(out).hexdigest(), 'public_id': profile['public_id']}))
`], { cwd: root, encoding: 'utf8' });
  assert.equal(py.status, 0, py.stderr);
  const remote = JSON.parse(py.stdout);
  const profile = livingProfile(FIXTURE);
  const growth = buildGrowth({ publicId: profile.publicId, epoch: 4, layer: 2, points: 10, memoryCrc: 1, chainCrc: 2, trade: true, grown: true });
  const sav = attachGrowth(buildSave(profile), growth);
  assert.equal(createHash('sha256').update(sav).digest('hex'), remote.sha256);
  assert.equal(sav[25476], 0x4c);
  assert.equal(sav[25540], 0xff);
  assert.equal(sav[25600], 0xff);
});

test('a model label cannot rewrite stats or identity', async () => {
  const profile = beastProfile({ seed: 'nebula-test', familyName: 'void' });
  const suggestion = suggestionFromText('Sure {"callsign":"MIRA","note":"A PUBLIC GAME NOTE"} thanks');
  assert.deepEqual(suggestion, { callsign: 'MIRA', note: 'A PUBLIC GAME NOTE' });
  assert.throws(() => acceptSuggestion({ callsign: 'MIRA', note: 'A PUBLIC GAME NOTE', stats: { hp: 80 } }), /fields/);
  assert.throws(() => acceptSuggestion({ callsign: 'MIRA', note: 'sk-secretkeyvalue' }), /note/);
  const record = await importPayload(text(JSON.stringify(creature('nebula-test', 'void'))));
  record.callsign = suggestion.callsign;
  assert.equal(record.publicId, profile.publicId);
  assert.equal(record.profile.bcp1[8], profile.bcp1[8]);
});

test('duplicate identities are refused and the same beast is idempotent', async () => {
  const ledger = emptyLedger();
  const first = await importPayload(text(JSON.stringify(creature('nebula-test', 'void'))));
  await admit(ledger, first, 'local');
  await admit(ledger, first, 'receive');
  assert.equal(Object.keys(ledger.identities).length, 1);
  const other = await importPayload(text(JSON.stringify(creature('nebula-test', 'nebula'))));
  await assert.rejects(() => admit(ledger, other, 'receive'), /different beast/);
  assert.equal(Object.keys(ledger.identities).length, 1);
});

test('growth rolls layers and epochs without leaving the cage fields', async () => {
  const ledger = emptyLedger();
  const record = await importPayload(text(JSON.stringify(creature('nebula-test', 'void'))));
  const input = {
    permissions: ['sense', 'world', 'memory'],
    sense: { focus: 50, calm: 50, spark: 50 },
    world: { name: 'EARTH', biosphere: 0, evolution: 0, lifeEvents: 0 },
  };
  await tend(ledger, record, input);
  const row = ledger.identities[record.publicHex];
  row.points = 996;
  await tend(ledger, record, input);
  assert.equal(record.growth.layer, 1);
  assert.equal(record.growth.points, 1);
  row.layer = 999;
  row.points = 996;
  await tend(ledger, record, input);
  assert.equal(record.growth.epoch, '1');
  assert.equal(record.growth.layer, 0);
  const sav = attachGrowth(buildSave(record.profile), buildGrowth({
    publicId: record.publicId, epoch: record.growth.epoch, layer: record.growth.layer, points: record.growth.points, grown: true,
  }));
  assert.equal(sav.length, 32768);
  await assert.rejects(() => tend(ledger, record, { ...input, samples: [1, 2, 3] }), /samples/);
});

test('trade files are checksummed, sealed, and cannot mint a second copy', async () => {
  const ledger = emptyLedger();
  const record = await importPayload(text(JSON.stringify(creature('nebula-test', 'void'))));
  await admit(ledger, record, 'local');
  await releaseForTrade(ledger, record);
  const share = await sealShare(record, 'pocket-key');
  await assert.rejects(() => tend(ledger, record, {
    permissions: ['sense', 'world', 'memory'],
    sense: { focus: 50, calm: 50, spark: 50 },
    world: { name: 'EARTH', biosphere: 0, evolution: 0, lifeEvents: 0 },
  }), /released/);
  const opened = await importPayload(text(share), {}, { passphrase: 'pocket-key' });
  await admit(ledger, opened, 'receive');
  assert.equal(Object.keys(ledger.identities).length, 1);
  assert.equal(ledger.identities[record.publicHex].held, true);
  const broken = share.replace(opened.callsign, 'NOPE');
  await assert.rejects(() => importPayload(text(broken), {}, { passphrase: 'pocket-key' }));
  await assert.rejects(() => importPayload(text(share), {}, { passphrase: 'wrong-key' }), /seal/);
  const ticket = parseTicket(encodeTicket(record));
  assert.equal(ticket.publicId, record.publicId);
  assert.equal(ticketLink(encodeTicket(record), 'https://navisworld.github.io/game/').includes('#lcqt='), true);
});

test('zip paths outside the Beast Box allowlist are rejected', async () => {
  await assert.rejects(() => readZipAllowlist(storeZip([['../evil.json', text('{"a":1}')]])), /rejected/);
  await assert.rejects(() => readZipAllowlist(storeZip([['/etc/passwd', text('no')]])), /rejected/);
});

test('an unsigned measured QBEAST snapshot is rejected', async () => {
  const details = creature('nebula-test', 'void');
  const genesis = expectedGenesis('nebula-test');
  details.name = genesis.name;
  details.id = `bb-${(await import('./mailbox.mjs')).fnv1a('identity|1|nebula-test').toString(16).padStart(8, '0')}`;
  details.baseLook = 'nebula';
  details.appearance = { hueShift: 0, glow: 40, finPattern: 0, haloPattern: 0, constellation: 0 };
  details.temperament = {
    curiosity: genesis.temper[0], energy: genesis.temper[1], playfulness: genesis.temper[2], caution: genesis.temper[3], independence: genesis.temper[4],
  };
  details.provenance = 'classical-seeded-game-generation';
  details.game.level = 1;
  details.game.experience = 0;
  const unsigned = {
    format: 'QBEAST1', version: 1, profile: details,
    public_state: { schema: 'dyn12-public-v1', mode: 'unavailable', values: Array(12).fill(0), source_sha256: null },
    progress: { trust: 0, bond: 0, evolution_stage: 0 },
    events: [], generation: 0, lineage_head: '0'.repeat(64),
  };
  unsigned.digest = await sha256Hex(text(`QBEAST1\0${canonical(unsigned)}`));
  const record = await fromQbeastSnapshot(unsigned);
  assert.equal(record.familyName, 'void');
  unsigned.progress = { trust: 1, bond: 0, evolution_stage: 0 };
  unsigned.digest = await sha256Hex(text(`QBEAST1\0${canonical({ ...unsigned, digest: undefined })}`));
  const privileged = { ...unsigned };
  delete privileged.digest;
  const again = { ...privileged, digest: await sha256Hex(text(`QBEAST1\0${canonical(privileged)}`)) };
  await assert.rejects(() => fromQbeastSnapshot(again), /Measured progress/);
});

test('QR symbols are deterministic and keep the finder frames', () => {
  const rows = qrMatrix('https://navisworld.github.io/Cosmic-synapse-the-living-universe-sim-engine-/#lcqt=abc');
  assert.equal(rows[0].startsWith('1111111'), true);
  assert.equal(qrMatrix('https://navisworld.github.io/Cosmic-synapse-the-living-universe-sim-engine-/#lcqt=abc').join(''), rows.join(''));
  assert.equal(rows.length, rows[0].length);
});
