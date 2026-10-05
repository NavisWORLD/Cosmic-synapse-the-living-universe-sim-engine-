import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import {
  ACTION_MAP, apiOrigin, applyMuseActions, CONNECTOR_URL, CONSENT, defaultDeviceName, errorText, LINK_KEY,
  MAX_SNAPSHOT_BYTES, museApi, readLink, SNAPSHOT_SCHEMA, sparkSnapshot, writeLink,
} from './meta-muse-link.mjs';
import { buildGenome } from './genome.mjs';
import { emptyStore, rememberBeast } from './store.mjs';

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const table = JSON.parse(read('./data/quantum-runs.json'));

function memory() {
  const map = new Map();
  return { getItem: (k) => (map.has(k) ? map.get(k) : null), setItem: (k, v) => map.set(k, String(v)), removeItem: (k) => map.delete(k) };
}
function sparked(name = 'Moss') {
  const genome = buildGenome({ focus: 40, calm: 40, spark: 20 }, table.runs[0], 'keeper');
  const store = emptyStore();
  const beast = rememberBeast(store, { seed: genome.seed, traits: genome.inputs.traits, runIndex: 0, runKey: genome.inputs.quantum_run, userId: 'keeper', origin: 'spark', island: genome.island, name: genome.names['1'], displayName: name, xp: 10, bond: 5 });
  beast.memory = { playerName: 'Cory', facts: [{ topic: 'food', detail: 'likes plums' }] };
  return { genome, store, beast };
}

test('connector is the Beast Box MCP URL; only localhost pages may point at a local dev server', () => {
  assert.equal(CONNECTOR_URL, 'https://www.beastboxcosmos.xyz/api/mcp');
  assert.equal(apiOrigin({ hostname: 'navisworld.github.io', search: '?beastbox=http://localhost:3100' }), 'https://www.beastboxcosmos.xyz');
  assert.equal(apiOrigin({ hostname: 'localhost', search: '?beastbox=http://localhost:3100' }), 'http://localhost:3100');
  assert.equal(apiOrigin({ hostname: '127.0.0.1', search: '?beastbox=https://evil.example' }), 'https://www.beastboxcosmos.xyz');
  assert.equal(apiOrigin({ hostname: 'localhost', search: '' }), 'https://www.beastboxcosmos.xyz');
});

test('device name defaults to "Beast Box · <beast name>" with Beast Box name rules', () => {
  assert.equal(defaultDeviceName('Moss'), 'Beast Box · Moss');
  assert.equal(defaultDeviceName(''), 'Beast Box · my beast');
  assert.ok(defaultDeviceName('x'.repeat(100)).length <= 60);
  assert.equal(defaultDeviceName('<b>Moss</b>'), 'Beast Box · bMossb');
});

test('Spark beast maps to the Beast Box minimal snapshot (schema v1) without chat, memory or keeper name', () => {
  const { genome, store, beast } = sparked();
  const snap = sparkSnapshot({ beast, genome, store, now: Date.UTC(2026, 9, 4) });
  assert.equal(snap.schema, SNAPSHOT_SCHEMA);
  assert.equal(snap.beast.seed, genome.seed);
  assert.equal(snap.beast.displayName, 'Moss');
  assert.equal(snap.beast.xp, 10);
  assert.equal(snap.beast.bond, 5);
  assert.equal(snap.beast.energy, 100);
  assert.equal(snap.beast.stage, 1);
  assert.equal(snap.beast.genome.element, genome.element);
  assert.equal(snap.beast.genome.names['1'], genome.names['1']);
  assert.deepEqual(snap.beast.genome.stats['1'], genome.stats['1']);
  assert.equal(snap.beast.genome.quantum.counts_sha256, genome.quantum.counts_sha256);
  assert.equal(snap.place, genome.island);
  assert.equal(snap.bestiaryCount, 1);
  assert.equal(snap.syncedAt, '2026-10-04T00:00:00.000Z');
  const text = JSON.stringify(snap);
  assert.ok(text.length < MAX_SNAPSHOT_BYTES, `snapshot ${text.length} bytes`);
  for (const secret of ['plums', 'Cory', 'keeper', 'engine', 'voice', 'behavior']) assert.ok(!text.includes(secret), secret);
  assert.equal(sparkSnapshot({ beast: null, genome, store }), null);
});

test('Muse care maps to Spark care: feed -> Rest, play -> Play, talk -> chat, rename -> name', () => {
  assert.deepEqual({ ...ACTION_MAP }, { feed: 'rest', play: 'play', talk: 'chat', rename: 'rename' });
  const { store, beast } = sparked();
  beast.energy = 50;
  const seed = beast.seed;
  const actions = [
    { id: 'a1', type: 'feed', args: {}, seed },
    { id: 'a2', type: 'play', args: { activity: 'pet' }, seed },
    { id: 'a3', type: 'talk', args: { you: 'hi there', beast: 'mrrp!' }, seed },
    { id: 'a4', type: 'rename', args: { name: 'Nova Moth' }, seed },
    { id: 'a5', type: 'feed', args: {}, seed: 'some-other-beast' },
  ];
  const out = applyMuseActions(store, seed, actions, []);
  assert.deepEqual(out.applied, ['a1', 'a2', 'a3', 'a4', 'a5']);
  assert.equal(out.changed, true);
  const [feed, play, talk, rename, other] = out.results;
  assert.equal(feed.spark, 'rest'); assert.equal(feed.ok, true);
  assert.equal(play.spark, 'play'); assert.equal(play.ok, true);
  assert.deepEqual([talk.spark, talk.you, talk.beast], ['chat', 'hi there', 'mrrp!']);
  assert.equal(rename.name, 'Nova Moth');
  assert.equal(other.ok, false);
  // Rest: +28 energy (capped), +1 bond. Play: -8 energy, +8 xp, +6 bond.
  assert.equal(beast.energy, Math.min(100, 50 + 28) - 8);
  assert.equal(beast.xp, 18);
  assert.equal(beast.bond, 12);
  assert.equal(beast.displayName, 'Nova Moth');
  // Re-delivered actions are not applied twice; acked ids the server dropped are forgotten.
  const again = applyMuseActions(store, seed, actions.slice(0, 2), out.applied);
  assert.equal(again.results.length, 0);
  assert.deepEqual(again.applied, ['a1', 'a2']);
  assert.equal(beast.xp, 18);
});

test('play when tired is acknowledged but does not change the beast', () => {
  const { store, beast } = sparked();
  beast.energy = 3;
  const out = applyMuseActions(store, beast.seed, [{ id: 'p', type: 'play', args: {}, seed: beast.seed }], []);
  assert.deepEqual(out.applied, ['p']);
  assert.equal(out.results[0].ok, false);
  assert.equal(out.results[0].reason, 'tired');
  assert.equal(beast.xp, 10);
});

test('link record keeps only a bbm_dev_ device secret and the paired seed', () => {
  const storage = memory();
  assert.equal(readLink(storage), null);
  writeLink(storage, { deviceSecret: 'nope', seed: 's' });
  assert.equal(readLink(storage), null);
  writeLink(storage, { deviceSecret: 'bbm_dev_abcdefghijklmnopqrstuvwxyz', seed: 'seed1', applied: ['x'] });
  assert.equal(readLink(storage).seed, 'seed1');
  assert.deepEqual(readLink(storage).applied, ['x']);
  assert.ok(storage.getItem(LINK_KEY));
  writeLink(storage, null);
  assert.equal(readLink(storage), null);
});

test('503 storage_not_configured and network failures get clear messages', async () => {
  assert.match(errorText({ status: 503, data: { error: 'storage_not_configured' } }), /storage is not set up yet.*503 storage_not_configured.*Nothing was shared.*Upstash/s);
  assert.match(errorText({ network: true, status: 0 }), /Could not reach Beast Box/);
  assert.match(errorText({ status: 429, data: {} }), /Too many/);
  const calls = [];
  const fake = async (url, init) => { calls.push({ url, init }); return { ok: false, status: 503, json: async () => ({ error: 'storage_not_configured' }) }; };
  const res = await museApi('https://www.beastboxcosmos.xyz', 'link', { method: 'POST', body: { consent: CONSENT }, fetchImpl: fake });
  assert.equal(res.status, 503);
  assert.equal(calls[0].url, 'https://www.beastboxcosmos.xyz/api/muse/link');
  assert.equal(calls[0].init.credentials, 'omit');
  assert.equal(JSON.parse(calls[0].init.body).consent, 'share-beast-snapshot');
  const down = await museApi('https://x', 'storage', { fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  assert.equal(down.network, true);
});

test('page: Meta Muse panel is additive, labelled internet-not-Bluetooth, and the EEG Pair Muse panel and Play links stay', () => {
  const html = read('./index.html');
  const app = read('./app.mjs');
  const panel = read('./meta-muse-panel.mjs');
  const link = read('./meta-muse-link.mjs');
  assert.match(html, /id="meta-muse"/);
  assert.match(html, /PAIR WITH META MUSE/);
  assert.match(html, /NOT BLUETOOTH/);
  assert.match(html, /over the internet through its third-party connectors/);
  for (const id of ['mm-consent', 'mm-pair', 'mm-code', 'mm-qr', 'mm-onetap', 'mm-status', 'mm-sync', 'mm-unpair', 'mm-device', 'mm-connector']) assert.match(html, new RegExp(`id="${id}"`), id);
  assert.match(html, /https:\/\/www\.beastboxcosmos\.xyz\/api\/mcp/);
  // Existing EEG headband panel (#36) and Play in Lost Cosmos (#35) untouched.
  for (const id of ['muse-pair', 'muse-pair-btn', 'muse-demo-btn', 'muse-spark', 'play-lc', 'muse-play']) assert.match(html, new RegExp(`id="${id}"`), id);
  assert.match(app, /mountMusePanel\(\{/);
  assert.match(app, /mountMetaMusePanel\(\{/);
  // No Bluetooth or Meta device imitation in the connector code.
  for (const src of [panel, link]) {
    assert.doesNotMatch(src, /navigator\.bluetooth|requestDevice|GATT|MuseGadget/i);
  }
});
