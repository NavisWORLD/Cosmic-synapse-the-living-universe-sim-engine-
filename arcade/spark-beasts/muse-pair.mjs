/**
 * Pair Muse: Web Bluetooth client for Muse 2 / Muse S (service 0xfe8d) that
 * keeps all four EEG sensors, rates contact per sensor, and turns each 1 s
 * window into delta/theta/alpha/beta/gamma shares with a small radix-2 FFT.
 *
 * Reuses the shared Lost Cosmos Muse code (command framing, 12-bit packet
 * decoding, band edges, and the cosmic-muse-traits-v1 mapping) and mirrors the
 * Beast Box Muse kit parser (PR #179) for Muse S Athena multiplexed packets.
 *
 * Soft consumer EEG for a game. Not medical, not mind-reading. Raw samples live
 * only in the 256-sample ring buffers below and are never saved or uploaded.
 */
import { bandPowers, decodeEegPacket, deriveTraits, encodeCommand, EEG_RATE, WINDOW } from '../lost-cosmos/muse.mjs';

export const MUSE_SERVICE = 0xfe8d;
export const CONTROL_UUID = '273e0001-4c4d-454d-96be-f03bac821358';
export const TELEMETRY_UUID = '273e000b-4c4d-454d-96be-f03bac821358';
export const SENSORS = ['TP9', 'AF7', 'AF8', 'TP10'];
export const LEGACY_EEG = {
  TP9: '273e0003-4c4d-454d-96be-f03bac821358',
  AF7: '273e0004-4c4d-454d-96be-f03bac821358',
  AF8: '273e0005-4c4d-454d-96be-f03bac821358',
  TP10: '273e0006-4c4d-454d-96be-f03bac821358',
};
export const ATHENA_DATA = ['273e0013-4c4d-454d-96be-f03bac821358', '273e0014-4c4d-454d-96be-f03bac821358'];
export const BANDS = ['delta', 'theta', 'alpha', 'beta', 'gamma'];
export const SNAPSHOT_SCHEMA = 'spark-muse-snapshot-v1';
export const TRAIT_SCHEMA = 'cosmic-muse-traits-v1';
export const UNSUPPORTED_TEXT = 'Bluetooth pairing needs Chrome or Edge on Android, Windows, Mac or ChromeOS';
export const CAPTURE_SECONDS = 10;
export const TICK_MS = 250;
export { EEG_RATE, WINDOW, encodeCommand };

const LEGACY_SCALE = 0.48828125;
const ATHENA_SCALE = 1450 / 16383;
const ATHENA_MID = 1 << 13;
const ATHENA_HEADER = 14;
const ATHENA_SUB = 5;
// tag -> [sensor, channels, samples, dataLen, variable]  (Beast Box packets.py)
const ATHENA_TAGS = {
  0x11: ['eeg', 4, 4, 28, false], 0x12: ['eeg', 8, 2, 28, false],
  0x34: ['optics', 4, 3, 30, false], 0x35: ['optics', 8, 2, 40, false], 0x36: ['optics', 16, 1, 40, false],
  0x47: ['acc_gyro', 6, 3, 36, false], 0x53: ['unknown', 2, 6, 24, false],
  0x88: ['battery', 1, 1, 0, true], 0x98: ['battery', 1, 1, 20, false],
};

/* ------------------------------------------------------------------ support */

/** Feature check before any button is offered. Pure so tests can pass a fake navigator. */
export function bluetoothSupport(nav = globalThis.navigator, win = globalThis) {
  if (!nav || !nav.bluetooth || typeof nav.bluetooth.requestDevice !== 'function') {
    return { ok: false, reason: UNSUPPORTED_TEXT };
  }
  if (win && win.isSecureContext === false) {
    return { ok: false, reason: `${UNSUPPORTED_TEXT}, on an HTTPS page.` };
  }
  return { ok: true, reason: '' };
}

/* ----------------------------------------------------------------- decoding */

const bytesOf = (packet) => (packet instanceof DataView
  ? new Uint8Array(packet.buffer, packet.byteOffset, packet.byteLength)
  : packet instanceof Uint8Array ? packet : new Uint8Array(packet));

/** Legacy Muse 2 / Muse S notification: 16-bit sequence then twelve 12-bit samples. */
export function decodeLegacy(packet) {
  const bytes = bytesOf(packet);
  if (bytes.length < 20) throw new Error('Muse EEG packet is too short');
  return decodeEegPacket(bytes);
}

/** Inverse of the 12-bit packer, for the demo signal and tests. */
export function encodeLegacy(sequence, codes) {
  const values = [...codes];
  if (values.length % 2) values.push(0x800);
  const out = new Uint8Array(2 + (values.length / 2) * 3);
  out[0] = sequence & 0xff;
  out[1] = (sequence >> 8) & 0xff;
  for (let i = 0, o = 2; i < values.length; i += 2, o += 3) {
    const a = values[i] & 0xfff;
    const b = values[i + 1] & 0xfff;
    out[o] = a >> 4;
    out[o + 1] = ((a & 0xf) << 4) | (b >> 8);
    out[o + 2] = b & 0xff;
  }
  return out;
}

export function microvoltsToCodes(samples) {
  return Array.from(samples, (uv) => Math.max(0, Math.min(4095, Math.round(uv / LEGACY_SCALE + 0x800))));
}

function readBits(bytes, start, width) {
  let value = 0;
  for (let bit = 0; bit < width; bit++) {
    const at = start + bit;
    if ((at >> 3) >= bytes.length) break;
    if ((bytes[at >> 3] >> (at & 7)) & 1) value |= 1 << bit;
  }
  return value;
}

function athenaEeg(tag, payload, out) {
  const cfg = ATHENA_TAGS[tag];
  if (!cfg || cfg[0] !== 'eeg') return;
  const [, channels, count] = cfg;
  for (let s = 0; s < count; s++) {
    for (let c = 0; c < 4; c++) {
      const start = (s * channels + c) * 14;
      if (start + 14 > payload.length * 8) return;
      out[SENSORS[c]].push((readBits(payload, start, 14) - ATHENA_MID) * ATHENA_SCALE);
    }
  }
}

/** Muse S Athena multiplexed notification -> per-sensor microvolts (published layout, as in Beast Box). */
export function decodeAthena(packet) {
  const data = bytesOf(packet);
  const out = { TP9: [], AF7: [], AF8: [], TP10: [] };
  let offset = 0;
  while (data.length - offset >= ATHENA_HEADER) {
    const length = data[offset];
    if (length < ATHENA_HEADER || offset + length > data.length) break;
    const block = data.subarray(offset, offset + length);
    offset += length;
    const payload = block.subarray(ATHENA_HEADER);
    let at = 0;
    const primary = ATHENA_TAGS[block[9]];
    if (!primary) at = payload.length;
    else {
      const len = primary[4] ? payload.length : Math.min(primary[3], payload.length);
      athenaEeg(block[9], payload.subarray(0, len), out);
      at = len;
    }
    while (at + ATHENA_SUB <= payload.length) {
      const tag = payload[at];
      const cfg = ATHENA_TAGS[tag];
      if (!cfg) break;
      const remaining = payload.length - at - ATHENA_SUB;
      const len = cfg[4] ? remaining : cfg[3];
      if (len <= 0 || len > remaining) break;
      athenaEeg(tag, payload.subarray(at + ATHENA_SUB, at + ATHENA_SUB + len), out);
      at += ATHENA_SUB + len;
    }
  }
  return out;
}

/** muse-js telemetry layout: big-endian sequence, battery/512 percent. */
export function decodeTelemetry(packet) {
  const bytes = bytesOf(packet);
  if (bytes.length < 4) return null;
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  return { battery: Math.max(0, Math.min(100, Math.round(view.getUint16(2) / 512))) };
}

/* --------------------------------------------------------------- band powers */

/** In-place iterative radix-2 FFT. n must be a power of two. */
export function fft(re, im) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      [re[i], re[j]] = [re[j], re[i]];
      [im[i], im[j]] = [im[j], im[i]];
    }
  }
  for (let size = 2; size <= n; size <<= 1) {
    const half = size >> 1;
    const step = (-2 * Math.PI) / size;
    for (let start = 0; start < n; start += size) {
      for (let k = 0; k < half; k++) {
        const wr = Math.cos(step * k);
        const wi = Math.sin(step * k);
        const a = start + k;
        const b = a + half;
        const tr = re[b] * wr - im[b] * wi;
        const ti = re[b] * wi + im[b] * wr;
        re[b] = re[a] - tr;
        im[b] = im[a] - ti;
        re[a] += tr;
        im[a] += ti;
      }
    }
  }
}

/** Same bins and edges as muse.mjs bandPowers (1..<45 Hz, no taper), computed with the FFT. */
export function fftBandPowers(samples, rate = EEG_RATE) {
  const n = samples.length;
  if (!n || (n & (n - 1))) return bandPowers(samples, rate);
  const re = Float64Array.from(samples);
  const im = new Float64Array(n);
  fft(re, im);
  const bands = { delta: 0, theta: 0, alpha: 0, beta: 0, gamma: 0 };
  for (let k = 1; k < n >> 1; k++) {
    const freq = (k * rate) / n;
    if (freq >= 45) break;
    const power = re[k] * re[k] + im[k] * im[k];
    if (freq < 4) bands.delta += power;
    else if (freq < 8) bands.theta += power;
    else if (freq < 13) bands.alpha += power;
    else if (freq < 30) bands.beta += power;
    else bands.gamma += power;
  }
  re.fill(0);
  im.fill(0);
  return bands;
}

export function relativeBands(bands) {
  let total = 0;
  for (const name of BANDS) total += Math.max(0, Number(bands[name]) || 0);
  const out = {};
  for (const name of BANDS) out[name] = total > 0 ? Math.max(0, Number(bands[name]) || 0) / total : 0;
  return out;
}

export function meanShares(rows) {
  const out = { delta: 0, theta: 0, alpha: 0, beta: 0, gamma: 0 };
  if (!rows.length) return out;
  for (const row of rows) for (const name of BANDS) out[name] += row[name];
  for (const name of BANDS) out[name] /= rows.length;
  return out;
}

/**
 * Rough contact estimate from 1 s of one sensor (mean removed). Muse apps use a
 * similar spread test. It is a hint for fitting the band, not a measurement.
 */
export function signalQuality(samples) {
  const n = samples?.length || 0;
  if (n < 32) return { level: 'none', label: 'no data', spread: 0 };
  let mean = 0;
  for (let i = 0; i < n; i++) mean += samples[i];
  mean /= n;
  let sq = 0;
  let peak = 0;
  for (let i = 0; i < n; i++) {
    const d = samples[i] - mean;
    sq += d * d;
    peak = Math.max(peak, Math.abs(samples[i]));
  }
  const spread = Math.sqrt(sq / n);
  if (peak > 950 || spread < 0.4) return { level: 'off', label: 'no contact', spread };
  if (spread <= 30) return { level: 'good', label: 'good', spread };
  if (spread <= 70) return { level: 'fair', label: 'fair', spread };
  return { level: 'poor', label: 'noisy', spread };
}

/**
 * Live mirror for the companion: calm alpha leans serene, high beta leans energetic.
 * Uses the alpha:beta balance so it moves visibly even though delta usually
 * dominates raw EEG. This only steers the animation. It never changes a seed.
 */
export function liveReaction(shares) {
  const a = Math.max(0, shares.alpha || 0);
  const b = Math.max(0, shares.beta || 0);
  const g = Math.max(0, shares.gamma || 0);
  const r = a + b > 0 ? a / (a + b) : 0.5;
  const calm = Math.round(100 * r);
  const focus = Math.round(100 * (1 - r));
  const spark = Math.max(0, Math.min(100, Math.round(70 * (1 - r) + 300 * g)));
  const mood = r >= 0.58 ? 'serene' : r <= 0.42 ? 'energetic' : 'balanced';
  return { calm, focus, spark, mood };
}

/* ----------------------------------------------------------------- snapshot */

const round4 = (x) => Math.round(x * 1e4) / 1e4;

export function snapshotTraits(snapshot) {
  if (!snapshot || snapshot.schema !== SNAPSHOT_SCHEMA) throw new Error('Not a Spark Muse snapshot');
  const bands = {};
  for (const name of BANDS) {
    const value = snapshot.bands?.[name];
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 1) throw new Error(`snapshot band ${name} must be a share in 0..1`);
    bands[name] = value;
  }
  return deriveTraits(bands);
}

/**
 * The only thing a brainwave spark keeps: five averaged band shares (4 dp),
 * how they were gathered, and the recorded run + keeper used for the seed.
 */
export function makeSnapshot({ source, model = '', seconds, windows, sensors = [], shares, capturedAt = new Date().toISOString() }) {
  const bands = {};
  for (const name of BANDS) bands[name] = round4(Math.max(0, shares[name] || 0));
  const snapshot = {
    schema: SNAPSHOT_SCHEMA,
    source: source === 'demo' ? 'demo' : 'muse',
    model: String(model || ''),
    seconds: Math.round((seconds || 0) * 10) / 10,
    windows: windows | 0,
    window_samples: WINDOW,
    rate_hz: EEG_RATE,
    sensors: SENSORS.filter((name) => sensors.includes(name)),
    bands,
    capturedAt,
  };
  const traits = snapshotTraits(snapshot);
  snapshot.traits = { schema: TRAIT_SCHEMA, ...traits };
  return snapshot;
}

/** Attach the recorded run and keeper that the seed used, so anyone can rebuild it. */
export function bindRecipe(snapshot, { runIndex, runKey, keeper, seed }) {
  return { ...snapshot, recipe: { runIndex, runKey, keeper: keeper ?? null, seed } };
}

/** Rebuild the beast from a saved snapshot alone (plus the shipped recorded table). */
export function resparkFromSnapshot(snapshot, table, buildGenome) {
  const traits = snapshotTraits(snapshot);
  const recipe = snapshot.recipe;
  if (!recipe) throw new Error('This snapshot has no recipe yet');
  const run = table.runs[recipe.runIndex];
  if (!run || (recipe.runKey && run.key !== recipe.runKey)) throw new Error('The recorded run in this snapshot is not in this copy of the table');
  const genome = buildGenome(traits, run, recipe.keeper ?? null);
  return { traits, genome, matches: !recipe.seed || genome.seed === recipe.seed };
}

export const SNAPSHOT_KEY = 'spark-beasts-muse-v1';

export function loadSnapshots(storage) {
  try {
    const value = JSON.parse(storage.getItem(SNAPSHOT_KEY) || 'null');
    if (value?.version === 1 && value.bySeed && typeof value.bySeed === 'object') return value;
  } catch { /* fall through */ }
  return { version: 1, bySeed: {} };
}

export function saveSnapshot(storage, snapshot) {
  const book = loadSnapshots(storage);
  const seed = snapshot.recipe?.seed;
  if (!seed) throw new Error('snapshot needs a recipe seed');
  book.bySeed[seed] = snapshot;
  const seeds = Object.keys(book.bySeed);
  while (seeds.length > 24) delete book.bySeed[seeds.shift()];
  storage.setItem(SNAPSHOT_KEY, JSON.stringify(book));
  return book;
}

/* -------------------------------------------------------------- demo signal */

/**
 * Clearly labeled demo: synthetic tones packed into real Muse packets and fed
 * through the same decoder. mix 0 = alpha-heavy (serene), 100 = beta-heavy.
 */
export function demoSamples(t0, count, mix = 50, channel = 0) {
  const m = Math.max(0, Math.min(100, mix)) / 100;
  const out = new Float64Array(count);
  for (let i = 0; i < count; i++) {
    const t = t0 + i / EEG_RATE;
    const wobble = 1 + 0.15 * Math.sin(2 * Math.PI * 0.13 * t + channel);
    out[i] = 18 * Math.sin(2 * Math.PI * 2 * t + channel)
      + 8 * Math.sin(2 * Math.PI * 6 * t + 0.4 * channel)
      + (6 + 26 * (1 - m)) * wobble * Math.sin(2 * Math.PI * 10 * t + 0.7 * channel)
      + (4 + 22 * m) * Math.sin(2 * Math.PI * 21 * t + 1.3 * channel)
      + (1.5 + 4 * m) * Math.sin(2 * Math.PI * 38 * t + channel);
  }
  return out;
}

/* ------------------------------------------------------------------- client */

class Ring {
  constructor(n = WINDOW) { this.buf = new Float64Array(n); this.write = 0; this.filled = 0; this.lastAt = 0; this.total = 0; }
  push(samples, now) {
    for (const s of samples) {
      this.buf[this.write] = Number.isFinite(s) ? s : 0;
      this.write = (this.write + 1) % this.buf.length;
      if (this.filled < this.buf.length) this.filled++;
    }
    this.total += samples.length;
    this.lastAt = now;
  }
  ordered() {
    const n = this.buf.length;
    const out = new Float64Array(n);
    for (let i = 0; i < n; i++) out[i] = this.buf[(this.write + i) % n];
    return out;
  }
  clear() { this.buf.fill(0); this.write = 0; this.filled = 0; this.total = 0; this.lastAt = 0; }
}

/**
 * MusePair drives one headband (or the labeled demo). Hooks:
 *   onState({ state, source, model, name, message })
 *   onFrame({ shares, smooth, perSensor, quality, usable, reaction })
 *   onBattery(percent)
 */
export class MusePair {
  constructor(hooks = {}, { bluetooth = globalThis.navigator?.bluetooth, now = () => Date.now(), timers = globalThis } = {}) {
    this.hooks = hooks;
    this.bluetooth = bluetooth;
    this.now = now;
    this.timers = timers;
    this.rings = Object.fromEntries(SENSORS.map((name) => [name, new Ring()]));
    this.state = 'idle';
    this.source = null;
    this.model = '';
    this.device = null;
    this.control = null;
    this.smooth = null;
    this.capture = null;
    this.tickTimer = 0;
    this.demoTimer = 0;
    this.demoMix = 30;
    this.demoClock = 0;
    this.demoSeq = 0;
    this.onGone = () => this.handleGone();
  }

  emitState(message = '') {
    this.hooks.onState?.({ state: this.state, source: this.source, model: this.model, name: this.device?.name || '', message });
  }

  /** Real pairing. Must be called from a click (browser rule). Never fakes success. */
  async connect() {
    if (!this.bluetooth || typeof this.bluetooth.requestDevice !== 'function') throw new Error(UNSUPPORTED_TEXT);
    if (this.state === 'paired' || this.state === 'connecting') return;
    if (this.source === 'demo') this.stop();
    if (typeof this.bluetooth.getAvailability === 'function') {
      const available = await this.bluetooth.getAvailability().catch(() => true);
      if (available === false) throw new Error('Bluetooth looks switched off or missing on this device. Turn it on and try again.');
    }
    this.state = 'connecting';
    this.source = 'muse';
    this.emitState('Choose your Muse in the browser list.');
    try {
      const device = await this.bluetooth.requestDevice({ filters: [{ services: [MUSE_SERVICE] }], optionalServices: [MUSE_SERVICE] });
      this.device = device;
      device.addEventListener?.('gattserverdisconnected', this.onGone);
      this.emitState(`Connecting to ${device.name || 'Muse'}...`);
      const server = await device.gatt.connect();
      const service = await server.getPrimaryService(MUSE_SERVICE);
      let uuids = null;
      if (typeof service.getCharacteristics === 'function') {
        try { uuids = new Set((await service.getCharacteristics()).map((c) => String(c.uuid).toLowerCase())); } catch { uuids = null; }
      }
      const athena = uuids ? uuids.has(ATHENA_DATA[0]) && !uuids.has(LEGACY_EEG.AF7) : false;
      this.model = athena ? 'athena' : 'legacy';
      this.control = await service.getCharacteristic(CONTROL_UUID);
      const send = async (cmd) => {
        await this.control.writeValue(encodeCommand(cmd));
      };
      const listen = async (uuid, handler) => {
        const ch = await service.getCharacteristic(uuid);
        ch.addEventListener('characteristicvaluechanged', (event) => {
          if (this.state !== 'paired' && this.state !== 'connecting') return;
          try { handler(event.target.value); } catch { /* one bad packet is skipped */ }
        });
        await ch.startNotifications();
        return ch;
      };
      if (athena) {
        for (const uuid of ATHENA_DATA) {
          await listen(uuid, (value) => this.ingestAthena(value)).catch(() => null);
        }
        for (const cmd of ['v6', 's', 'h', 'p1041', 's', 'dc001', 'dc001', 'L1', 's']) await send(cmd);
      } else {
        await send('h');
        await send('p21');
        let ok = 0;
        for (const name of SENSORS) {
          const ch = await listen(LEGACY_EEG[name], (value) => this.ingest(name, value)).catch(() => null);
          if (ch) ok++;
        }
        if (!ok) throw new Error('This headband did not offer any EEG sensors over Bluetooth.');
        await listen(TELEMETRY_UUID, (value) => {
          const t = decodeTelemetry(value);
          if (t) this.hooks.onBattery?.(t.battery);
        }).catch(() => null);
        await send('s');
        await send('d');
      }
      this.state = 'paired';
      this.startTicks();
      this.emitState(`Paired with ${device.name || 'Muse'}. Waiting for the first second of signal...`);
    } catch (error) {
      const name = error?.name || '';
      await this.teardown();
      this.state = 'idle';
      this.source = null;
      let message = error?.message || 'Muse did not connect.';
      if (name === 'NotFoundError') message = 'No headband was chosen. Turn the Muse on (lights pulsing), then press Pair Muse again.';
      else if (name === 'SecurityError') message = 'This page is inside a frame that does not allow Bluetooth. Open Spark Beasts in its own tab to pair.';
      else if (name === 'NetworkError') message = 'The Muse dropped the connection while pairing. Keep it close and try again.';
      this.emitState(message);
      throw new Error(message);
    }
  }

  ingest(name, value) {
    const ring = this.rings[name];
    if (!ring) return;
    ring.push(decodeLegacy(value).samples, this.now());
  }

  ingestAthena(value) {
    const decoded = decodeAthena(value);
    const at = this.now();
    for (const name of SENSORS) if (decoded[name].length) this.rings[name].push(decoded[name], at);
  }

  /** Labeled demo signal. Not a headband and never reported as one. */
  startDemo(mix = this.demoMix) {
    if (this.source === 'muse') throw new Error('Disconnect the Muse before starting the demo signal.');
    this.demoMix = mix;
    if (this.source === 'demo') return;
    this.source = 'demo';
    this.model = 'demo';
    this.state = 'paired';
    this.demoClock = 0;
    this.demoSeq = 0;
    let last = this.now();
    this.demoTimer = this.timers.setInterval(() => {
      const now = this.now();
      let due = Math.min(40, Math.floor(((now - last) / 1000) * (EEG_RATE / 12)));
      if (due <= 0) return;
      last += (due * 12 * 1000) / EEG_RATE;
      while (due-- > 0) this.pumpDemoPacket();
    }, 40);
    this.startTicks();
    this.emitState('DEMO SIGNAL running. These waves are synthetic, not from a headband.');
  }

  pumpDemoPacket() {
    SENSORS.forEach((name, c) => {
      const uv = demoSamples(this.demoClock, 12, this.demoMix, c);
      this.ingest(name, encodeLegacy(this.demoSeq, microvoltsToCodes(uv)));
    });
    this.demoClock += 12 / EEG_RATE;
    this.demoSeq = (this.demoSeq + 1) & 0xffff;
  }

  setDemoMix(mix) { this.demoMix = Math.max(0, Math.min(100, Number(mix) || 0)); }

  startTicks() {
    if (this.tickTimer) return;
    this.tickTimer = this.timers.setInterval(() => this.tick(), TICK_MS);
  }

  /** One analysis frame: quality per sensor, FFT shares per usable sensor, averaged. */
  tick() {
    if (this.state !== 'paired') return null;
    const now = this.now();
    const quality = {};
    const perSensor = {};
    const usable = [];
    for (const name of SENSORS) {
      const ring = this.rings[name];
      if (!ring.filled || now - ring.lastAt > 1500) { quality[name] = { level: 'none', label: 'no data', spread: 0 }; continue; }
      if (ring.filled < WINDOW) { quality[name] = { level: 'none', label: 'filling', spread: 0 }; continue; }
      const window = ring.ordered();
      quality[name] = signalQuality(window);
      if (quality[name].level === 'good' || quality[name].level === 'fair') {
        perSensor[name] = relativeBands(fftBandPowers(window));
        usable.push(name);
      }
      window.fill(0);
    }
    const shares = usable.length ? meanShares(usable.map((name) => perSensor[name])) : null;
    if (shares) {
      if (!this.smooth) this.smooth = { ...shares };
      else for (const name of BANDS) this.smooth[name] += 0.35 * (shares[name] - this.smooth[name]);
    }
    const frame = { shares, smooth: this.smooth, perSensor, quality, usable, reaction: this.smooth ? liveReaction(this.smooth) : null };
    if (this.capture) {
      this.capture.ticks += 1;
      if (shares) {
        this.capture.rows.push(shares);
        for (const name of usable) this.capture.sensors.add(name);
      }
      this.capture.onProgress?.(Math.min(1, (now - this.capture.start) / (this.capture.seconds * 1000)), this.capture.rows.length);
      if (now - this.capture.start >= this.capture.seconds * 1000) this.finishCapture();
    }
    this.hooks.onFrame?.(frame);
    return frame;
  }

  /** About 10 s of band averages -> a snapshot. Rejects if the contact was too poor. */
  captureSnapshot(seconds = CAPTURE_SECONDS, onProgress = null) {
    if (this.state !== 'paired') return Promise.reject(new Error('Pair the Muse (or start the demo signal) first.'));
    if (this.capture) return Promise.reject(new Error('A capture is already running.'));
    return new Promise((resolve, reject) => {
      this.capture = { start: this.now(), seconds, rows: [], sensors: new Set(), ticks: 0, onProgress, resolve, reject };
    });
  }

  finishCapture() {
    const cap = this.capture;
    this.capture = null;
    if (!cap) return;
    const needed = Math.max(4, Math.floor((cap.seconds * 1000) / TICK_MS * 0.3));
    if (cap.rows.length < needed) {
      cap.reject(new Error(`Only ${cap.rows.length} clean windows in ${cap.seconds} s. Wet the sensors or adjust the band until two or more read good or fair, then try again.`));
      return;
    }
    const shares = meanShares(cap.rows);
    const windows = cap.rows.length;
    cap.rows.length = 0;
    cap.resolve(makeSnapshot({ source: this.source, model: this.model, seconds: cap.seconds, windows, sensors: [...cap.sensors], shares, capturedAt: new Date(this.now()).toISOString() }));
  }

  cancelCapture(reason = 'Capture stopped.') {
    const cap = this.capture;
    this.capture = null;
    cap?.reject(new Error(reason));
  }

  handleGone() {
    if (this.state === 'idle') return;
    this.cancelCapture('The Muse disconnected during the capture.');
    this.stopTicks();
    this.clearRings();
    this.state = 'idle';
    this.source = null;
    this.emitState('Muse disconnected.');
  }

  stopTicks() {
    if (this.tickTimer) this.timers.clearInterval(this.tickTimer);
    this.tickTimer = 0;
  }

  clearRings() {
    for (const ring of Object.values(this.rings)) ring.clear();
    this.smooth = null;
  }

  async teardown() {
    if (this.demoTimer) this.timers.clearInterval(this.demoTimer);
    this.demoTimer = 0;
    this.stopTicks();
    const device = this.device;
    this.device = null;
    if (this.control && device?.gatt?.connected !== false) {
      try { await this.control.writeValue(encodeCommand('h')); } catch { /* already gone */ }
    }
    this.control = null;
    if (device) {
      device.removeEventListener?.('gattserverdisconnected', this.onGone);
      try { device.gatt?.disconnect(); } catch { /* already gone */ }
    }
    this.clearRings();
  }

  async disconnect() {
    this.cancelCapture('Disconnected before the capture finished.');
    const was = this.source;
    await this.teardown();
    this.state = 'idle';
    this.source = null;
    this.model = '';
    this.emitState(was === 'demo' ? 'Demo signal stopped.' : 'Disconnected. Samples were cleared from this page.');
  }

  stop() {
    this.cancelCapture('Stopped.');
    if (this.demoTimer) this.timers.clearInterval(this.demoTimer);
    this.demoTimer = 0;
    this.stopTicks();
    this.clearRings();
    this.state = 'idle';
    this.source = null;
  }
}
