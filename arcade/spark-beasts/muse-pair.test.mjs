import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import { bandPowers, deriveTraits } from '../lost-cosmos/muse.mjs';
import {
  bindRecipe, bluetoothSupport, decodeAthena, decodeLegacy, decodeTelemetry, demoSamples, encodeCommand, encodeLegacy,
  fftBandPowers, liveReaction, loadSnapshots, makeSnapshot, microvoltsToCodes, MusePair, relativeBands,
  resparkFromSnapshot, saveSnapshot, signalQuality, snapshotTraits, UNSUPPORTED_TEXT, LEGACY_EEG, CONTROL_UUID, MUSE_SERVICE,
} from './muse-pair.mjs';
import { buildGenome } from './genome.mjs';
import { emptyStore, rememberBeast } from './store.mjs';
import { emptyLedger } from './trade.mjs';
import { preparePlay } from './play-save.mjs';

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const fixture = JSON.parse(read('./fixtures/muse-sample-packets.json'));
const table = JSON.parse(read('./data/quantum-runs.json'));
const hex = (h) => Uint8Array.from(h.match(/../g), (x) => parseInt(x, 16));

function memory() {
  const map = new Map();
  return { getItem: (k) => (map.has(k) ? map.get(k) : null), setItem: (k, v) => map.set(k, String(v)), removeItem: (k) => map.delete(k) };
}

test('legacy Muse packets decode: sequence, 12 samples, microvolt scale', () => {
  // Hand-built packet: sequence 0x1234, first pair 0xABC/0xDEF, rest at the 0x800 midpoint.
  const bytes = new Uint8Array(20);
  bytes[0] = 0x34; bytes[1] = 0x12;
  bytes.set([0xab, 0xcd, 0xef], 2);
  for (let o = 5; o < 20; o += 3) bytes.set([0x80, 0x08, 0x00], o);
  const out = decodeLegacy(new DataView(bytes.buffer));
  assert.equal(out.sequence, 0x1234);
  assert.equal(out.samples.length, 12);
  assert.equal(out.samples[0], 0.48828125 * (0xabc - 0x800));
  assert.equal(out.samples[1], 0.48828125 * (0xdef - 0x800));
  assert.deepEqual(out.samples.slice(2), Array(10).fill(0));
  assert.throws(() => decodeLegacy(new Uint8Array(8)), /too short/);
});

test('sample packets from the Beast Box parser decode identically and map to the same traits', () => {
  for (const [name, row] of Object.entries(fixture.legacy)) {
    const samples = [];
    row.packets_hex.forEach((h, i) => {
      const packet = decodeLegacy(hex(h));
      assert.equal(packet.sequence, row.sequences[i], `${name} sequence ${i}`);
      samples.push(...packet.samples);
    });
    row.first_samples_uv.forEach((uv, i) => assert.ok(Math.abs(samples[i] - uv) < 1e-9, `${name} sample ${i}`));
    const window = Float64Array.from(samples.slice(0, 256));
    const shares = relativeBands(fftBandPowers(window));
    for (const [band, want] of Object.entries(row.relative_bands)) assert.ok(Math.abs(shares[band] - want) < 1e-6, `${name} ${band}`);
    assert.deepEqual(deriveTraits(fftBandPowers(window)), row.traits, `${name} traits`);
    // Our encoder is the exact inverse of the shared decoder.
    row.packets_hex.forEach((h, i) => {
      const codes = microvoltsToCodes(decodeLegacy(hex(h)).samples);
      assert.equal(Buffer.from(encodeLegacy(row.sequences[i], codes)).toString('hex'), h);
    });
  }
  assert.ok(fixture.legacy.AF7.traits.calm > 80, 'alpha-heavy AF7 reads calm');
  assert.ok(fixture.legacy.AF8.traits.focus > 80, 'beta-heavy AF8 reads focus');
});

test('Muse S Athena multiplexed packets decode AF7 like the Beast Box parser', () => {
  const af7 = [];
  for (const h of fixture.athena.packets_hex) {
    const out = decodeAthena(hex(h));
    assert.equal(out.AF7.length, 4);
    assert.ok(out.TP9.every((x) => x === 0) && out.AF8.every((x) => x === 0));
    af7.push(...out.AF7);
  }
  fixture.athena.af7_first_samples_uv.forEach((uv, i) => assert.ok(Math.abs(af7[i] - uv) < 1e-9));
  assert.deepEqual(deriveTraits(fftBandPowers(Float64Array.from(af7))), fixture.athena.traits);
  assert.deepEqual(decodeAthena(new Uint8Array(5)).AF7, []);
});

test('the small FFT matches the shared DFT band powers bin for bin', () => {
  for (const mix of [0, 35, 100]) {
    const window = demoSamples(1.25, 256, mix, 2);
    const slow = bandPowers(window);
    const fast = fftBandPowers(window);
    for (const band of Object.keys(slow)) assert.ok(Math.abs(fast[band] - slow[band]) <= 1e-9 * Math.max(1, slow[band]), `${band} at mix ${mix}`);
  }
});

test('band mapping: alpha leads to calm/serene, beta leads to focus/energetic', () => {
  const serene = relativeBands(fftBandPowers(demoSamples(0, 256, 0)));
  const energetic = relativeBands(fftBandPowers(demoSamples(0, 256, 100)));
  assert.ok(serene.alpha > serene.beta);
  assert.ok(energetic.beta > energetic.alpha);
  assert.equal(liveReaction(serene).mood, 'serene');
  assert.equal(liveReaction(energetic).mood, 'energetic');
  assert.ok(liveReaction(serene).calm > liveReaction(energetic).calm);
  assert.ok(liveReaction(energetic).spark > liveReaction(serene).spark);
  assert.equal(liveReaction({ alpha: 0.2, beta: 0.2, gamma: 0 }).mood, 'balanced');
  const sum = Object.values(serene).reduce((a, b) => a + b, 0);
  assert.ok(Math.abs(sum - 1) < 1e-12);
});

test('signal quality flags flat, good, and noisy sensors', () => {
  assert.equal(signalQuality(new Float64Array(256)).level, 'off');
  assert.equal(signalQuality(demoSamples(0, 256, 30)).level, 'good');
  const noisy = Float64Array.from({ length: 256 }, (_, i) => (i % 2 ? 160 : -160));
  assert.equal(signalQuality(noisy).level, 'poor');
  assert.equal(signalQuality(Float64Array.from({ length: 256 }, () => 999)).level, 'off');
  assert.equal(signalQuality([]).level, 'none');
});

test('the same snapshot always rebuilds the same beast, and it plays with the same save path', async () => {
  const shares = relativeBands(fftBandPowers(demoSamples(0, 256, 20)));
  const snap = makeSnapshot({ source: 'muse', model: 'legacy', seconds: 10, windows: 40, sensors: ['AF8', 'AF7'], shares, capturedAt: '2026-10-04T00:00:00.000Z' });
  assert.deepEqual(snap.sensors, ['AF7', 'AF8']);
  assert.deepEqual(Object.keys(snap.bands), ['delta', 'theta', 'alpha', 'beta', 'gamma']);
  assert.ok(!('samples' in snap), 'no raw samples in a snapshot');
  const traits = snapshotTraits(snap);
  assert.deepEqual({ focus: snap.traits.focus, calm: snap.traits.calm, spark: snap.traits.spark }, traits);
  const runIndex = 3;
  const genome = buildGenome(traits, table.runs[runIndex], 'CORY');
  const bound = bindRecipe(snap, { runIndex, runKey: genome.inputs.quantum_run, keeper: 'CORY', seed: genome.seed });
  // Round-trip through JSON (download / localStorage) and rebuild twice.
  const copy = JSON.parse(JSON.stringify(bound));
  const a = resparkFromSnapshot(copy, table, buildGenome);
  const b = resparkFromSnapshot(JSON.parse(JSON.stringify(copy)), table, buildGenome);
  assert.ok(a.matches && b.matches);
  assert.equal(a.genome.seed, genome.seed);
  assert.deepEqual(a.genome, b.genome);
  // A different snapshot gives a different seed input.
  const other = makeSnapshot({ source: 'muse', seconds: 10, windows: 40, sensors: ['AF7'], shares: relativeBands(fftBandPowers(demoSamples(0, 256, 100))) });
  assert.notDeepEqual(snapshotTraits(other), traits);
  // Tampered recipe is caught.
  assert.equal(resparkFromSnapshot({ ...copy, recipe: { ...copy.recipe, keeper: 'SOMEONE' } }, table, buildGenome).matches, false);
  assert.throws(() => snapshotTraits({ ...copy, bands: { ...copy.bands, alpha: -1 } }), /share/);
  // Local snapshot book.
  const storage = memory();
  saveSnapshot(storage, copy);
  assert.equal(loadSnapshots(storage).bySeed[genome.seed].recipe.seed, genome.seed);
  // Same store record and save bytes as an ordinary spark with the same traits, run, and keeper.
  const mk = (origin) => {
    const store = emptyStore();
    rememberBeast(store, { seed: genome.seed, traits: genome.inputs.traits, runIndex, runKey: genome.inputs.quantum_run, userId: 'CORY', origin, island: genome.island, name: genome.names['1'], xp: 0, bond: 0 });
    return store;
  };
  const viaMuse = await preparePlay({ store: mk('muse'), ledger: emptyLedger(), table, seed: genome.seed });
  const viaSpark = await preparePlay({ store: mk('spark'), ledger: emptyLedger(), table, seed: genome.seed });
  assert.equal(viaMuse.bytes.length, 32768);
  assert.deepEqual([...viaMuse.bytes], [...viaSpark.bytes]);
});

test('unsupported browsers get the Chrome/Edge message and never a fake connection', async () => {
  assert.deepEqual(bluetoothSupport({}, {}), { ok: false, reason: UNSUPPORTED_TEXT });
  assert.deepEqual(bluetoothSupport(undefined, {}), { ok: false, reason: UNSUPPORTED_TEXT });
  assert.equal(bluetoothSupport({ bluetooth: {} }, {}).ok, false);
  assert.equal(bluetoothSupport({ bluetooth: { requestDevice() {} } }, { isSecureContext: false }).ok, false);
  assert.equal(bluetoothSupport({ bluetooth: { requestDevice() {} } }, { isSecureContext: true }).ok, true);
  assert.equal(UNSUPPORTED_TEXT, 'Bluetooth pairing needs Chrome or Edge on Android, Windows, Mac or ChromeOS');
  const states = [];
  const pair = new MusePair({ onState: (s) => states.push(s.state) }, { bluetooth: undefined });
  await assert.rejects(pair.connect(), /Chrome or Edge/);
  assert.equal(pair.state, 'idle');
  assert.deepEqual(states, []);
  // A cancelled chooser stays unpaired.
  const cancelled = new MusePair({}, { bluetooth: { requestDevice: async () => { const e = new Error('cancel'); e.name = 'NotFoundError'; throw e; } } });
  await assert.rejects(cancelled.connect(), /No headband was chosen/);
  assert.equal(cancelled.state, 'idle');
});

/** Minimal fake Web Bluetooth GATT that plays packets after the 'd' resume command. */
function fakeBluetooth({ mix = 10 } = {}) {
  const sent = [];
  const chars = new Map();
  const make = (uuid) => {
    const listeners = [];
    return {
      uuid,
      listeners,
      async startNotifications() {},
      addEventListener(type, fn) { if (type === 'characteristicvaluechanged') listeners.push(fn); },
      async writeValue(bytes) { sent.push(new TextDecoder().decode(bytes.subarray(1)).trim()); },
      emit(bytes) { for (const fn of listeners) fn({ target: { value: new DataView(bytes.buffer) } }); },
    };
  };
  for (const uuid of [CONTROL_UUID, ...Object.values(LEGACY_EEG)]) chars.set(uuid, make(uuid));
  const device = {
    name: 'Muse-TEST', listeners: [],
    addEventListener(type, fn) { this.listeners.push(fn); },
    removeEventListener() {},
    gatt: {
      connected: true,
      async connect() {
        return { async getPrimaryService(id) { assert.equal(id, MUSE_SERVICE); return { async getCharacteristics() { return [...chars.values()]; }, async getCharacteristic(u) { if (!chars.has(u)) throw new Error('no char'); return chars.get(u); } }; } };
      },
      disconnect() { this.connected = false; },
    },
  };
  let seq = 0;
  let clock = 0;
  const pump = (n) => {
    for (let p = 0; p < n; p++) {
      Object.values(LEGACY_EEG).forEach((uuid, c) => chars.get(uuid).emit(encodeLegacy(seq, microvoltsToCodes(demoSamples(clock, 12, mix, c)))));
      seq += 1;
      clock += 12 / 256;
    }
  };
  return { sent, device, pump, bluetooth: { async requestDevice(opts) { assert.deepEqual(opts.filters, [{ services: [MUSE_SERVICE] }]); return device; } } };
}

test('pairing a (fake) Muse sends h/p21/s/d, reads all four sensors, and a 10 s capture yields a snapshot', async () => {
  const fake = fakeBluetooth({ mix: 0 });
  let now = 1000;
  const timers = { setInterval: () => 1, clearInterval() {} };
  const frames = [];
  const pair = new MusePair({ onFrame: (f) => frames.push(f) }, { bluetooth: fake.bluetooth, now: () => now, timers });
  await pair.connect();
  assert.equal(pair.state, 'paired');
  assert.equal(pair.model, 'legacy');
  assert.deepEqual(fake.sent, ['h', 'p21', 's', 'd']);
  assert.deepEqual([...encodeCommand('d')], [2, 100, 10]);
  const capture = pair.captureSnapshot(10);
  for (let t = 0; t < 44; t++) { fake.pump(6); now += 250; pair.tick(); }
  const snap = await capture;
  assert.equal(snap.source, 'muse');
  assert.deepEqual(snap.sensors, ['TP9', 'AF7', 'AF8', 'TP10']);
  assert.ok(snap.windows >= 30);
  assert.ok(snap.traits.calm > snap.traits.focus);
  const last = frames.at(-1);
  assert.equal(last.usable.length, 4);
  assert.equal(last.reaction.mood, 'serene');
  for (const q of Object.values(last.quality)) assert.equal(q.level, 'good');
  await pair.disconnect();
  assert.equal(pair.state, 'idle');
  assert.equal(fake.sent.at(-1), 'h');
  assert.equal(fake.device.gatt.connected, false);
  assert.ok(Object.values(pair.rings).every((r) => r.filled === 0), 'samples cleared on disconnect');
  assert.equal(decodeTelemetry(Uint8Array.from([0, 1, 0xc8, 0x00, 0, 0])).battery, 100);
});
