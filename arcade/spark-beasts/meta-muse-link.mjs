/**
 * Pair with Meta Muse: link one sparked beast to the Beast Box Meta Muse connector.
 *
 * Meta Muse (Meta's personal AI agent) reaches Beast Box over the internet through its
 * third-party MCP connectors. This is NOT Bluetooth and it is NOT the Muse EEG headband
 * (that is the separate Pair Muse panel, muse-pair.mjs). Nothing here imitates a Meta
 * device: the page only calls Beast Box's own pairing and sync API.
 *
 * Same API, consent string and snapshot format as Beast Box's own Pair panel
 * (The-beast-box- apps/beastbox-cloud lib/muse/*, docs/meta-muse-connector.md).
 * Pure logic only (no DOM) so it can be tested in node.
 */
import { shownName } from './store.mjs';
import { careRename, careTrain } from './care.mjs';

export const CONNECTOR_ORIGIN = 'https://www.beastboxcosmos.xyz';
export const CONNECTOR_URL = `${CONNECTOR_ORIGIN}/api/mcp`;
export const LINK_KEY = 'spark-beasts-meta-muse-v1';
export const SNAPSHOT_SCHEMA = 'beastbox-muse-snapshot-v1';
export const CONSENT = 'share-beast-snapshot';
export const SYNC_MS = 20000;
export const MAX_SNAPSHOT_BYTES = 12000;
export const DOCS_URL = 'https://github.com/NavisWORLD/The-beast-box-/blob/main/docs/meta-muse-connector.md';

const LOCAL_HOST = /^(localhost|127\.0\.0\.1)$/;
const LOCAL_API = /^http:\/\/(localhost|127\.0\.0\.1):\d{2,5}$/;

/**
 * Which Beast Box to talk to. Always production, except a page served from localhost may
 * point at a local Beast Box dev server with ?beastbox=http://localhost:3100 (testing only).
 */
export function apiOrigin(loc) {
  try {
    if (loc && LOCAL_HOST.test(loc.hostname)) {
      const want = new URLSearchParams(loc.search || '').get('beastbox') || '';
      if (LOCAL_API.test(want)) return want;
    }
  } catch { /* fall through */ }
  return CONNECTOR_ORIGIN;
}

/** Same rule as Beast Box cleanDeviceName (letters, digits, space . · ' ( ) - _), 60 chars. */
export function cleanDeviceName(name) {
  return String(name || '').replace(/[^\w .·'()-]/g, '').replace(/\s+/g, ' ').trim().slice(0, 60);
}
export function defaultDeviceName(beastName) {
  return cleanDeviceName(`Beast Box · ${beastName || 'my beast'}`);
}

const clamp = (v, lo, hi, d = 0) => (Number.isFinite(Number(v)) ? Math.max(lo, Math.min(hi, Number(v))) : d);
const str = (v, max) => (typeof v === 'string' ? v.slice(0, max) : '');

/** Spark mood for the connector, from care numbers only. */
export function sparkMood(beast) {
  const energy = clamp(beast?.energy ?? 100, 0, 100, 100);
  if (energy < 16) return 'tired';
  if (energy < 40) return 'sleepy';
  if ((beast?.bond || 0) >= 60) return 'happy';
  return 'curious';
}

/** Only the genome fields the connector tools use (Beast Box re-picks them server side too). */
export function pickGenome(genome) {
  if (!genome || typeof genome !== 'object') return null;
  const q = genome.quantum || {};
  const stats = {};
  for (const s of ['1', '2', '3']) {
    const row = genome.stats?.[s];
    if (row) stats[s] = { hp: clamp(row.hp, 0, 999), atk: clamp(row.atk, 0, 999), def: clamp(row.def, 0, 999), spd: clamp(row.spd, 0, 999), spark: clamp(row.spark, 0, 999) };
  }
  const names = {};
  for (const s of ['1', '2', '3']) if (typeof genome.names?.[s] === 'string') names[s] = str(genome.names[s], 32);
  return {
    seed: str(genome.seed, 96),
    element: str(genome.element, 24),
    body: str(genome.body, 32),
    island: str(genome.island, 48),
    temperament: str(genome.temperament, 24),
    glow: clamp(genome.glow, 0, 360),
    stats,
    names,
    quantum: {
      backend: str(q.backend, 48),
      job_id: str(q.job_id, 64),
      top_state: str(q.top_state, 64),
      counts_sha256: str(q.counts_sha256, 64),
      num_bits: clamp(q.num_bits, 0, 64),
      shots: clamp(q.shots, 0, 1e7),
    },
  };
}

/**
 * Map a Spark beast to Beast Box's minimal snapshot (beastbox-muse-snapshot-v1).
 * Not shared: chat lines, remembered notes, keeper name, sensors, brainwave snapshots.
 */
export function sparkSnapshot({ beast, genome, store, now = Date.now() }) {
  if (!beast) return null;
  const xp = clamp(beast.xp, 0, 1e7);
  return {
    schema: SNAPSHOT_SCHEMA,
    beast: {
      seed: str(beast.seed, 96),
      displayName: str(beast.displayName || '', 24),
      xp,
      bond: clamp(beast.bond, 0, 100),
      energy: clamp(beast.energy ?? 100, 0, 100, 100),
      stage: clamp(beast.stage || 1, 1, 3, 1),
      mood: sparkMood(beast),
      nativeStage: null,
      qbeast: null,
      genome: pickGenome(genome),
    },
    bestiaryCount: Math.min(999, Object.keys(store?.beasts || {}).length),
    train: { rounds: 0, score: 0 },
    emulator: { booted: false, ticks: 0 },
    place: str(genome?.island || beast.island || '', 32),
    syncedAt: new Date(now).toISOString(),
  };
}

/* ---------- link record (device secret stays in this browser) ---------- */

export function readLink(storage) {
  try {
    const v = JSON.parse(storage.getItem(LINK_KEY) || 'null');
    if (!v || typeof v.deviceSecret !== 'string' || !v.deviceSecret.startsWith('bbm_dev_') || typeof v.seed !== 'string') return null;
    return { applied: [], lastSyncAt: null, deviceId: null, deviceName: '', ...v, applied: Array.isArray(v.applied) ? v.applied.slice(-100) : [] };
  } catch { return null; }
}
export function writeLink(storage, link) {
  try { link ? storage.setItem(LINK_KEY, JSON.stringify(link)) : storage.removeItem(LINK_KEY); } catch { /* private mode */ }
}

/* ---------- Muse care actions -> Spark care ---------- */

/** feed -> Rest, play -> Play, talk -> chat, rename -> beast name. */
export const ACTION_MAP = Object.freeze({ feed: 'rest', play: 'play', talk: 'chat', rename: 'rename' });

/**
 * Apply care actions Muse queued for this beast with the Spark care rules.
 * Returns the new acknowledged id list (same bookkeeping as Beast Box's own sync) and
 * one result per freshly applied action. Talk lines are returned for the chat log.
 */
export function applyMuseActions(store, seed, actions, applied = []) {
  const list = Array.isArray(actions) ? actions : [];
  const seen = new Set(applied);
  const fresh = list.filter((a) => a && typeof a.id === 'string' && !seen.has(a.id));
  const results = [];
  for (const a of fresh) {
    if (a.seed && a.seed !== seed) { results.push({ id: a.id, type: a.type, ok: false, reason: 'other_beast' }); continue; }
    if (!store?.beasts?.[seed]) { results.push({ id: a.id, type: a.type, ok: false, reason: 'missing' }); continue; }
    if (a.type === 'feed') {
      const r = careTrain(store, seed, 'rest', { quality: 1 });
      results.push({ id: a.id, type: 'feed', spark: 'rest', ok: r.ok, grew: Boolean(r.grew), reason: r.reason });
    } else if (a.type === 'play') {
      const r = careTrain(store, seed, 'play', { quality: 1 });
      results.push({ id: a.id, type: 'play', spark: 'play', ok: r.ok, grew: Boolean(r.grew), reason: r.reason });
    } else if (a.type === 'rename') {
      const r = careRename(store, seed, String(a.args?.name || ''));
      results.push({ id: a.id, type: 'rename', spark: 'rename', ok: Boolean(r), name: r ? r.displayName : '' });
    } else if (a.type === 'talk') {
      results.push({ id: a.id, type: 'talk', spark: 'chat', ok: true, you: str(String(a.args?.you || ''), 400), beast: str(String(a.args?.beast || ''), 400) });
    } else {
      results.push({ id: a.id, type: String(a.type || ''), ok: false, reason: 'unknown' });
    }
  }
  const still = new Set(list.map((a) => a && a.id));
  const nextApplied = [...applied.filter((id) => still.has(id)), ...fresh.map((a) => a.id)].slice(-100);
  return { applied: nextApplied, results, changed: results.some((r) => r.ok && r.type !== 'talk') };
}

export function describeResult(r, name) {
  if (r.type === 'feed') return r.ok ? `Meta Muse fed ${name}: it rests and energy is back up.` : `Meta Muse tried to feed ${name}.`;
  if (r.type === 'play') return r.ok ? `Meta Muse played with ${name}. The bond grows.` : `Meta Muse wanted to play, but ${name} is too tired. Rest first.`;
  if (r.type === 'rename') return r.ok ? `Meta Muse renamed your beast to ${r.name}.` : 'Meta Muse sent a name this page cannot use.';
  if (r.type === 'talk') return `Meta Muse talked with ${name}.`;
  return '';
}

/* ---------- Beast Box API ---------- */

/** Human message for a failed call. 503 storage_not_configured is the expected state until storage is added. */
export function errorText(res) {
  if (!res) return 'Could not reach Beast Box.';
  if (res.network) return 'Could not reach Beast Box (offline, blocked, or this origin is not allowed yet). Nothing was shared.';
  const code = res.data?.error;
  if (res.status === 503 || code === 'storage_not_configured') {
    return 'Beast Box connector storage is not set up yet (503 storage_not_configured), so pairing is off for now. Nothing was shared. It starts working once the Beast Box owner adds Upstash Redis storage on Vercel.';
  }
  if (res.status === 429) return res.data?.error_description || 'Too many requests. Try again in a minute.';
  if (code === 'consent_required') return 'Tick the consent box first.';
  if (res.status === 403) return 'Beast Box refused this page (origin not allowed).';
  if (res.status === 401) return 'This beast is no longer paired with Meta Muse.';
  return res.data?.error_description || code || `Beast Box answered ${res.status}.`;
}

export async function museApi(base, path, { method = 'GET', body, secret, fetchImpl = globalThis.fetch } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (secret) headers.Authorization = `Bearer ${secret}`;
  let res;
  try {
    res = await fetchImpl(`${base}/api/muse/${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store', mode: 'cors', credentials: 'omit' });
  } catch {
    return { ok: false, status: 0, network: true, data: null };
  }
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  return { ok: res.ok, status: res.status, data };
}

/** Name used in the snapshot-facing UI and the default device name. */
export function beastLabel(beast, genome) {
  return shownName(beast, genome?.names?.[String(beast?.stage || 1)] || beast?.name);
}
