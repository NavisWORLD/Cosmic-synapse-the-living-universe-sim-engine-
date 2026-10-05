import {sha256Hex as checkedDigest} from '../sol-spark-gate/digest.mjs';
/**
 * Untrusted beast intake for Lost Cosmos V11.1.
 * A model, a file, or a share can suggest a label. Stats and the public id
 * are rebuilt on this page from the seed. Incoming bytes are never copied
 * into SRAM until they pass these checks.
 */
import {
  FAMILIES, FAMILY_LOOK, SPECIES, beastProfile, buildBcp1, crc32, expectedGenesis,
  fnv1a, livingProfile, profileFromBcp1, profileFromBeastJson,
} from './mailbox.mjs';

export const MAX_JSON_BYTES = 524288;
export const MAX_ZIP_BYTES = 1048576;
const PRIVATE = /(?:api[_ -]?key|password|credential|authorization|biometric|owner[_ -]?memory|private[_ -]?(?:key|state)|-----BEGIN|\bBearer\s|\bsk-[a-z0-9_-]{8,})/i;
const ZIP_ALLOW = new Set([
  'gba/companion_tiles.4bpp',
  'gba/companion_palette.bgr555',
  'gba/companion_state.bin',
  'gba/companion_profile.bin',
  'companion.profile.json',
  'quantum-beast.receipt.json',
  'checksums.json',
]);

export function canonical(value) {
  if (value === null) return 'null';
  if (typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || (Number.isInteger(value) && !Number.isSafeInteger(value))) throw new Error('Invalid number');
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (!value || typeof value !== 'object') throw new Error('Non-JSON value');
  return `{${Object.keys(value).filter((key) => value[key] !== undefined).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
}

export async function sha256Hex(bytes) { return checkedDigest(bytes); }

export function bytesToHex(bytes) {
  return [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function hexToBytes(hex) {
  if (typeof hex !== 'string' || hex.length % 2 || !/^[a-f0-9]+$/.test(hex)) throw new Error('Invalid hex');
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}

export function bytesToB64url(bytes) {
  let text = '';
  for (let i = 0; i < bytes.length; i += 0x8000) text += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(text).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
}

export function b64urlToBytes(text) {
  if (typeof text !== 'string' || !/^[A-Za-z0-9_-]+$/.test(text) || text.length > 4096) throw new Error('Invalid share ticket');
  const pad = text.replaceAll('-', '+').replaceAll('_', '/').padEnd(text.length + ((4 - (text.length % 4)) % 4), '=');
  const raw = atob(pad);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

export function purify(value, depth = 0) {
  if (depth > 16) throw new Error('JSON nesting limit exceeded');
  if (value === null || typeof value === 'boolean') return value;
  if (typeof value === 'string') {
    if (value.length > 4096) throw new Error('JSON string is too long');
    return value;
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw new Error('Invalid number');
    return value;
  }
  if (Array.isArray(value)) {
    if (value.length > 64) throw new Error('JSON collection too large');
    return value.map((item) => purify(item, depth + 1));
  }
  if (!value || typeof value !== 'object') throw new Error('Non-JSON value');
  const out = {};
  const keys = Object.keys(value);
  if (keys.length > 64) throw new Error('JSON collection too large');
  for (const key of keys) {
    if (key === '__proto__' || key === 'prototype' || key === 'constructor') throw new Error('Forbidden JSON key');
    out[key] = purify(value[key], depth + 1);
  }
  return out;
}

function exactKeys(value, names, optional = []) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Expected an object');
  const keys = Object.keys(value);
  if (!names.every((key) => Object.hasOwn(value, key)) || keys.some((key) => !names.includes(key) && !optional.includes(key))) {
    throw new Error('Unexpected or missing fields');
  }
}

function publicText(value, max, label) {
  if (typeof value !== 'string' || value.length < 1 || value.length > max || /[\u0000-\u001f\u007f]/.test(value) || PRIVATE.test(value)) {
    throw new Error(`Invalid ${label}`);
  }
}

function asciiCallsign(value) {
  const call = String(value || '').toUpperCase().replace(/[^A-Z0-9 ]/g, '').trim().slice(0, 12);
  if (!call) throw new Error('Callsign must use letters or digits');
  return call;
}

function traitTriple(traits = {}) {
  const focus = traits.focus ?? 50;
  const calm = traits.calm ?? 50;
  const spark = traits.spark ?? 50;
  for (const [name, value] of [['focus', focus], ['calm', calm], ['spark', spark]]) {
    if (!Number.isInteger(value) || value < 0 || value > 100) throw new Error(`${name} must be an integer 0..100`);
  }
  return { focus, calm, spark };
}

function beastId(seed) {
  return fnv1a(`identity|1|${seed}`) || 1;
}

function normalizeSeed(seed) {
  if (typeof seed !== 'string') throw new Error('Seed must be text');
  const clean = seed.trim().normalize('NFC');
  if (clean.length < 1 || clean.length > 64 || /[\u0000-\u001f\u007f]/.test(clean)) throw new Error('Seed must have 1 to 64 visible characters');
  return clean;
}

function growthOf(value, fallback = {}) {
  const growth = value || {};
  exactKeys(growth, ['epoch', 'layer', 'points', 'trade', 'grown']);
  if (typeof growth.epoch !== 'string' || !/^\d{1,20}$/.test(growth.epoch)) throw new Error('Invalid cage epoch');
  if (!Number.isInteger(growth.layer) || growth.layer < 0 || growth.layer > 999) throw new Error('Invalid cage layer');
  if (!Number.isInteger(growth.points) || growth.points < 0 || growth.points > 999) throw new Error('Invalid cage points');
  if (typeof growth.trade !== 'boolean' || typeof growth.grown !== 'boolean') throw new Error('Invalid cage flags');
  return {
    epoch: growth.epoch,
    layer: growth.layer,
    points: growth.points,
    trade: growth.trade,
    grown: growth.grown,
    memoryCrc: fallback.memoryCrc >>> 0 || 0,
    chainCrc: fallback.chainCrc >>> 0 || 0,
  };
}

function freshGrowth(trade = false) {
  return { epoch: '0', layer: 0, points: 0, trade, grown: false, memoryCrc: 0, chainCrc: 0 };
}

export function cartridgeEpoch(epoch) {
  const value = BigInt(epoch);
  if (value < 0n) throw new Error('Invalid cage epoch');
  return value > 0xffffffffn ? 0xffffffff : Number(value);
}

export function acceptSuggestion(value) {
  const clean = purify(value);
  exactKeys(clean, ['callsign', 'note']);
  const callsign = asciiCallsign(clean.callsign);
  publicText(clean.note, 48, 'note');
  if (!/^[\x20-\x7e]+$/.test(clean.note)) throw new Error('The note must be public ASCII');
  return { callsign, note: clean.note };
}

function recordFromProfile(profile, { origin, seed, note = 'A PUBLIC GAME COMPANION.', memories = [], transfer = null, growth = null, trade = false }) {
  const callsign = asciiCallsign(profile.callsign);
  return {
    origin,
    seed: seed || null,
    family: profile.family,
    familyName: FAMILIES[profile.family],
    speciesName: profile.speciesName || SPECIES[profile.family],
    hue: profile.hue,
    focus: profile.focus,
    calm: profile.calm,
    spark: profile.spark,
    callsign,
    note,
    profile: { ...profile, callsign },
    publicId: profile.publicId >>> 0,
    growth: growth || freshGrowth(trade),
    memories,
    transfer,
  };
}

function creatureRecord(details, traits, origin) {
  const seed = normalizeSeed(details.seed);
  const family = details.family;
  if (!FAMILIES.includes(family)) throw new Error('Unknown family');
  const expectedId = `bb-${fnv1a(`identity|1|${seed}`).toString(16).padStart(8, '0')}`;
  if (details.id !== undefined && details.id !== expectedId) throw new Error('Beast identity does not match its seed');
  const hue = Number(details.appearance?.hueShift ?? 0);
  if (!Number.isInteger(hue) || hue < -127 || hue > 127) throw new Error('Hue is out of range');
  if (details.baseLook !== undefined && details.baseLook !== FAMILY_LOOK[FAMILIES.indexOf(family)]) throw new Error('Look does not match the family');
  const profile = profileFromBeastJson(details, traitTriple(traits));
  if ((profile.publicId >>> 0) !== beastId(seed)) throw new Error('Public id does not match the seed');
  const rebuilt = buildBcp1({
    family: profile.family,
    stats: [...profile.bcp1.subarray(8, 18)],
    temper: [...profile.bcp1.subarray(18, 23)],
    hue: profile.hue,
    publicId: profile.publicId,
  });
  if (bytesToHex(rebuilt) !== bytesToHex(profile.bcp1)) throw new Error('Rebuilt profile did not match');
  return recordFromProfile(profile, { origin, seed, trade: false });
}

async function hashObject(value) {
  return sha256Hex(new TextEncoder().encode(`QBEAST1\0${canonical(value)}`));
}

async function verifySignature(snapshot, trustedPublicKey) {
  if (!snapshot.signature) {
    if (trustedPublicKey) throw new Error('A trusted signature was required');
    return 'absent';
  }
  exactKeys(snapshot.signature, ['algorithm', 'public_key', 'value']);
  if (snapshot.signature.algorithm !== 'Ed25519') throw new Error('Unsupported signature');
  const keyBytes = hexToBytes(snapshot.signature.public_key);
  const sig = hexToBytes(snapshot.signature.value);
  if (keyBytes.length !== 32 || sig.length !== 64) throw new Error('Invalid Ed25519 signature');
  const key = await crypto.subtle.importKey('raw', keyBytes, { name: 'Ed25519' }, false, ['verify']);
  const ok = await crypto.subtle.verify('Ed25519', key, sig, new TextEncoder().encode(snapshot.digest));
  if (!ok) throw new Error('Invalid source signature');
  if (trustedPublicKey) {
    if (trustedPublicKey !== snapshot.signature.public_key) throw new Error('Signing key does not match the pinned key');
    return 'trusted';
  }
  return 'valid_untrusted';
}

export async function fromQbeastSnapshot(snapshot, traits = {}, trustedPublicKey = '') {
  const clean = purify(snapshot);
  exactKeys(clean, ['format', 'version', 'profile', 'public_state', 'progress', 'events', 'generation', 'lineage_head', 'digest'], ['signature']);
  if (clean.format !== 'QBEAST1' || clean.version !== 1) throw new Error('Unsupported QBEAST format');
  if (!/^[a-f0-9]{64}$/.test(clean.digest) || !/^[a-f0-9]{64}$/.test(clean.lineage_head)) throw new Error('Invalid QBEAST digest');
  const { digest, signature, ...rest } = clean;
  if (await hashObject(rest) !== digest) throw new Error('QBEAST digest mismatch');
  const signatureState = await verifySignature(clean, trustedPublicKey || '');
  const state = clean.public_state;
  exactKeys(state, ['schema', 'mode', 'values', 'source_sha256']);
  if (state.schema !== 'dyn12-public-v1' || !['unavailable', 'approved_projection'].includes(state.mode)) throw new Error('Invalid public projection');
  exactKeys(clean.progress, ['trust', 'bond', 'evolution_stage']);
  const privileged = state.mode !== 'unavailable' || Object.values(clean.progress).some((value) => value !== 0);
  if (privileged && signatureState !== 'trusted') throw new Error('Measured progress is not accepted without a pinned signing key');
  if (!Array.isArray(clean.events) || clean.events.length > 512 || clean.generation !== clean.events.length) throw new Error('Lineage was rejected');
  const record = creatureRecord(clean.profile, traits, 'qbeast');
  record.note = 'IMPORTED FROM A CHECKED QBEAST FILE.';
  return record;
}

async function inflateRaw(bytes) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

function u16(bytes, offset) {
  return bytes[offset] | (bytes[offset + 1] << 8);
}
function u32(bytes, offset) {
  return (bytes[offset] | (bytes[offset + 1] << 8) | (bytes[offset + 2] << 16) | (bytes[offset + 3] << 24)) >>> 0;
}

export async function readZipAllowlist(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length < 22 || bytes.length > MAX_ZIP_BYTES) throw new Error('Zip was rejected');
  let eocd = -1;
  const start = Math.max(0, bytes.length - (22 + 65535));
  for (let i = bytes.length - 22; i >= start; i--) {
    if (u32(bytes, i) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('Zip was rejected');
  const count = u16(bytes, eocd + 10);
  const cdSize = u32(bytes, eocd + 12);
  const cdOffset = u32(bytes, eocd + 16);
  if (!count || count > ZIP_ALLOW.size || cdOffset + cdSize > bytes.length) throw new Error('Zip was rejected');
  const files = new Map();
  let cursor = cdOffset;
  for (let n = 0; n < count; n++) {
    if (u32(bytes, cursor) !== 0x02014b50) throw new Error('Zip was rejected');
    const flags = u16(bytes, cursor + 8);
    const method = u16(bytes, cursor + 10);
    const crc = u32(bytes, cursor + 16);
    const compSize = u32(bytes, cursor + 20);
    const rawSize = u32(bytes, cursor + 24);
    const nameLen = u16(bytes, cursor + 28);
    const extraLen = u16(bytes, cursor + 30);
    const commentLen = u16(bytes, cursor + 32);
    const local = u32(bytes, cursor + 42);
    const name = new TextDecoder().decode(bytes.subarray(cursor + 46, cursor + 46 + nameLen));
    if (flags & ~0x800 || method !== 0 && method !== 8 || !ZIP_ALLOW.has(name) || files.has(name)) throw new Error('Zip entry was rejected');
    if (name.includes('\\') || name.startsWith('/') || name.split('/').includes('..')) throw new Error('Zip entry was rejected');
    if (rawSize > 262144 || compSize > 262144 || local + 30 > bytes.length) throw new Error('Zip entry was rejected');
    if (u32(bytes, local) !== 0x04034b50) throw new Error('Zip was rejected');
    const localName = u16(bytes, local + 26);
    const localExtra = u16(bytes, local + 28);
    const dataStart = local + 30 + localName + localExtra;
    if (dataStart + compSize > bytes.length) throw new Error('Zip was rejected');
    const compressed = bytes.subarray(dataStart, dataStart + compSize);
    const data = method === 0 ? compressed : await inflateRaw(compressed);
    if (data.length !== rawSize || crc32(data) !== crc) throw new Error('Zip checksum failed');
    files.set(name, data);
    cursor += 46 + nameLen + extraLen + commentLen;
  }
  if (cursor !== cdOffset + cdSize) throw new Error('Zip was rejected');
  return files;
}

export async function fromExportZip(bytes, traits = {}) {
  const files = await readZipAllowlist(bytes);
  const profileBytes = files.get('companion.profile.json');
  const bcp = files.get('gba/companion_profile.bin');
  const receiptBytes = files.get('quantum-beast.receipt.json');
  const sumsBytes = files.get('checksums.json');
  if (!profileBytes || !bcp || !receiptBytes || !sumsBytes) throw new Error('Beast Box export is missing a required file');
  if (bcp.length !== 64) throw new Error('BCP1 must be 64 bytes');
  const sums = purify(JSON.parse(new TextDecoder().decode(sumsBytes)));
  for (const [name, raw] of files) {
    if (name === 'checksums.json') continue;
    if (typeof sums[name] !== 'string' || sums[name] !== await sha256Hex(raw)) throw new Error('Export checksum mismatch');
  }
  for (const name of Object.keys(sums)) if (!files.has(name) || name === 'checksums.json') throw new Error('Export checksum list was rejected');
  const receipt = purify(JSON.parse(new TextDecoder().decode(receiptBytes)));
  if (receipt.schema !== 'qbeast-gba-export-v1' || receipt.memory_included !== false || receipt.authority !== false) throw new Error('Export receipt was rejected');
  if (receipt.BCP1 !== 'canonical-seeded-game-stats' || receipt.BCG1 !== 'unmeasured-public-art') throw new Error('Export receipt was rejected');
  const details = purify(JSON.parse(new TextDecoder().decode(profileBytes)));
  const record = creatureRecord(details, traits, 'qbeast');
  const parsed = profileFromBcp1(bcp, traitTriple(traits));
  if (bytesToHex(parsed.bcp1) !== bytesToHex(record.profile.bcp1)) throw new Error('Export profile and BCP1 disagree');
  record.note = 'IMPORTED FROM A BEAST BOX EXPORT.';
  return record;
}

function write32(buf, offset, value) {
  const n = value >>> 0;
  buf[offset] = n & 255;
  buf[offset + 1] = (n >>> 8) & 255;
  buf[offset + 2] = (n >>> 16) & 255;
  buf[offset + 3] = (n >>> 24) & 255;
}

export function encodeTicket(record) {
  if (!record.transfer || !/^[a-f0-9]{32}$/.test(record.transfer)) throw new Error('Trade ticket is missing its id');
  const seed = record.origin === 'bcp1' ? '' : normalizeSeed(record.seed);
  if (record.origin !== 'bcp1' && seed.length > 64) throw new Error('Seed is too long for a ticket');
  const call = asciiCallsign(record.callsign);
  const flags = (record.growth.trade ? 1 : 0) | (record.growth.grown ? 2 : 0) | (record.origin === 'living' ? 4 : 0) | (record.origin === 'bcp1' ? 8 : 0);
  const body = record.origin === 'bcp1' ? 40 + 16 + 64 : 40 + 16 + 1 + seed.length;
  const buf = new Uint8Array(body + 4);
  buf.set([0x4c, 0x43, 0x51, 0x54, 1, flags, record.family, record.hue & 255, record.focus, record.calm, record.spark], 0);
  write32(buf, 12, cartridgeEpoch(record.growth.epoch));
  buf[16] = record.growth.layer & 255;
  buf[17] = (record.growth.layer >>> 8) & 255;
  buf[18] = record.growth.points & 255;
  buf[19] = (record.growth.points >>> 8) & 255;
  write32(buf, 20, record.growth.memoryCrc || 0);
  write32(buf, 24, record.growth.chainCrc || 0);
  buf.set(new TextEncoder().encode(call), 28);
  buf.set(hexToBytes(record.transfer), 40);
  if (record.origin === 'bcp1') buf.set(record.profile.bcp1, 56);
  else {
    buf[56] = seed.length;
    buf.set(new TextEncoder().encode(seed), 57);
  }
  write32(buf, body, crc32(buf.subarray(0, body)));
  return buf;
}

export function parseTicket(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length < 48 || bytes[0] !== 0x4c || bytes[1] !== 0x43 || bytes[2] !== 0x51 || bytes[3] !== 0x54 || bytes[4] !== 1) {
    throw new Error('Trade ticket was rejected');
  }
  const flags = bytes[5];
  if (flags & ~15) throw new Error('Trade ticket was rejected');
  const family = bytes[6];
  if (family > 6) throw new Error('Trade ticket was rejected');
  const hue = (bytes[7] << 24) >> 24;
  const traits = traitTriple({ focus: bytes[8], calm: bytes[9], spark: bytes[10] });
  if (bytes[11]) throw new Error('Trade ticket was rejected');
  const epoch = u32(bytes, 12);
  const layer = bytes[16] | (bytes[17] << 8);
  const points = bytes[18] | (bytes[19] << 8);
  if (layer > 999 || points > 999) throw new Error('Trade ticket was rejected');
  const memoryCrc = u32(bytes, 20);
  const chainCrc = u32(bytes, 24);
  const callsign = asciiCallsign(new TextDecoder().decode(bytes.subarray(28, 40)));
  const transfer = bytesToHex(bytes.subarray(40, 56));
  const raw = Boolean(flags & 8);
  let seed = '';
  let bcp = null;
  let body = 0;
  if (raw) {
    body = 56 + 64;
    if (bytes.length !== body + 4) throw new Error('Trade ticket was rejected');
    bcp = bytes.slice(56, 120);
  } else {
    const len = bytes[56];
    body = 57 + len;
    if (len < 1 || len > 64 || bytes.length !== body + 4) throw new Error('Trade ticket was rejected');
    seed = new TextDecoder().decode(bytes.subarray(57, 57 + len));
  }
  if (crc32(bytes.subarray(0, body)) !== u32(bytes, body)) throw new Error('Trade ticket checksum failed');
  const growth = { epoch: String(epoch), layer, points, trade: Boolean(flags & 1), grown: Boolean(flags & 2), memoryCrc, chainCrc };
  let profile;
  if (raw) {
    profile = profileFromBcp1(bcp, { ...traits, callsign });
    if (profile.family !== family) throw new Error('Trade ticket family was rejected');
  } else if (flags & 4) {
    profile = livingProfile({ world: 'EARTH', evolution: 0, biosphere: 0, lifeEvents: 0, ...traits, ...splitLivingSeed(seed) });
    if (profile.seed !== seed || profile.family !== family || profile.hue !== hue) throw new Error('Living ticket did not rebuild');
    profile = { ...profile, callsign };
  } else {
    profile = beastProfile({ seed, familyName: FAMILIES[family], hue, ...traits });
    if (profile.family !== family || profile.hue !== hue) throw new Error('Beast ticket did not rebuild');
    profile = { ...profile, callsign };
  }
  return recordFromProfile(profile, {
    origin: raw ? 'bcp1' : (flags & 4 ? 'living' : 'beast'),
    seed: raw ? null : seed,
    note: 'IMPORTED FROM A SHARE TICKET.',
    transfer,
    growth,
    trade: growth.trade,
  });
}

function splitLivingSeed(seed) {
  const parts = String(seed).split('|');
  if (parts.length !== 5 || parts[0] !== 'lu1') throw new Error('Living seed was rejected');
  return {
    world: parts[1],
    evolution: Number(parts[2]) / 1000,
    biosphere: Number(parts[3]) / 1000,
    lifeEvents: Number(parts[4]),
  };
}

function shareBody(record) {
  const body = {
    format: 'LCSHARE1',
    version: 1,
    origin: record.origin === 'qbeast' ? 'beast' : record.origin,
    focus: record.focus,
    calm: record.calm,
    spark: record.spark,
    callsign: record.callsign,
    note: record.note,
    growth: {
      epoch: record.growth.epoch,
      layer: record.growth.layer,
      points: record.growth.points,
      trade: true,
      grown: Boolean(record.growth.grown),
    },
    memories: record.memories || [],
    transfer: record.transfer,
  };
  if (body.origin === 'bcp1') body.bcp1 = bytesToHex(record.profile.bcp1);
  else {
    body.seed = record.seed;
    body.family = record.familyName;
    if (body.origin === 'beast') body.hue = record.hue;
  }
  return body;
}

export async function sealShare(record, passphrase = '') {
  if (!record.transfer) throw new Error('Create a cage identity before sharing');
  const body = shareBody(record);
  if (Array.isArray(body.memories)) {
    if (body.memories.length > 8) throw new Error('Too many cage memories');
    for (const line of body.memories) publicText(line, 48, 'memory');
  }
  publicText(body.note, 48, 'note');
  const payload = canonical(body);
  const checksum = await sha256Hex(payload);
  const share = { ...body, checksum };
  if (passphrase) {
    if (typeof passphrase !== 'string' || passphrase.length < 4 || passphrase.length > 80) throw new Error('Passphrase must be 4 to 80 characters');
    const saltBytes = new Uint8Array(16);
    crypto.getRandomValues(saltBytes);
    const salt = bytesToHex(saltBytes);
    const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(passphrase), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const mac = new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${salt}\n${payload}`)));
    share.seal = { alg: 'HMAC-SHA256', salt, mac: bytesToHex(mac) };
  }
  return `${canonical(share)}\n`;
}

async function openShareValue(value, passphrase = '') {
  const clean = purify(value);
  if (clean.format !== 'LCSHARE1' || clean.version !== 1) throw new Error('Unsupported share');
  const { checksum, seal, ...body } = clean;
  if (typeof checksum !== 'string' || checksum !== await sha256Hex(canonical(body))) throw new Error('Share checksum failed');
  if (seal) {
    exactKeys(seal, ['alg', 'salt', 'mac']);
    if (seal.alg !== 'HMAC-SHA256') throw new Error('Unsupported share seal');
    if (!passphrase) throw new Error('This share is sealed. Enter the passphrase.');
    const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(passphrase), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    const mac = bytesToHex(new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${seal.salt}\n${canonical(body)}`))));
    if (mac !== seal.mac) throw new Error('Share seal did not match');
  }
  const traits = traitTriple(body);
  const growth = growthOf(body.growth);
  growth.memoryCrc = crc32(new TextEncoder().encode((body.memories || []).join('\n')));
  let profile;
  if (body.origin === 'living') {
    exactKeys(body, ['format', 'version', 'origin', 'focus', 'calm', 'spark', 'callsign', 'note', 'growth', 'memories', 'transfer', 'seed']);
    profile = livingProfile({ ...splitLivingSeed(normalizeSeed(body.seed)), ...traits });
    if (profile.seed !== body.seed) throw new Error('Living share did not rebuild');
  } else if (body.origin === 'beast') {
    exactKeys(body, ['format', 'version', 'origin', 'focus', 'calm', 'spark', 'callsign', 'note', 'growth', 'memories', 'transfer', 'seed', 'family', 'hue']);
    profile = beastProfile({ seed: normalizeSeed(body.seed), familyName: body.family, hue: body.hue, ...traits });
  } else if (body.origin === 'bcp1') {
    exactKeys(body, ['format', 'version', 'origin', 'focus', 'calm', 'spark', 'callsign', 'note', 'growth', 'memories', 'transfer', 'bcp1']);
    profile = profileFromBcp1(hexToBytes(body.bcp1), { ...traits, callsign: body.callsign });
  } else throw new Error('Unsupported share origin');
  publicText(body.note, 48, 'note');
  if (!/^[a-f0-9]{32}$/.test(body.transfer)) throw new Error('Share ticket id was rejected');
  if (!Array.isArray(body.memories) || body.memories.length > 8) throw new Error('Share memories were rejected');
  for (const line of body.memories) publicText(line, 48, 'memory');
  profile = { ...profile, callsign: asciiCallsign(body.callsign) };
  return recordFromProfile(profile, {
    origin: body.origin,
    seed: body.seed || null,
    note: body.note,
    memories: body.memories.slice(),
    transfer: body.transfer,
    growth,
    trade: true,
  });
}

export async function openShare(text, passphrase = '') {
  if (typeof text !== 'string' || new TextEncoder().encode(text).length > MAX_JSON_BYTES) throw new Error('Share was rejected');
  return openShareValue(purify(JSON.parse(text)), passphrase);
}

export function ticketLink(bytes, pageUrl) {
  const base = String(pageUrl || '').split('#')[0] || './';
  return `${base}#lcqt=${bytesToB64url(bytes)}`;
}

export async function importPayload(bytes, traits = {}, options = {}) {
  if (!(bytes instanceof Uint8Array) || !bytes.length) throw new Error('Empty beast file');
  if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4b && bytes[2] === 0x03 && bytes[3] === 0x04) return fromExportZip(bytes, traits);
  if (bytes.length >= 4 && bytes[0] === 0x4c && bytes[1] === 0x43 && bytes[2] === 0x51 && bytes[3] === 0x54) return parseTicket(bytes);
  if (bytes.length === 64 && bytes[0] === 0x42 && bytes[1] === 0x43 && bytes[2] === 0x50 && bytes[3] === 0x31) {
    const profile = profileFromBcp1(bytes, { ...traitTriple(traits), callsign: options.callsign || 'BEAST' });
    return recordFromProfile(profile, { origin: 'bcp1', note: 'IMPORTED FROM A BCP1 PROFILE.', trade: false });
  }
  if (bytes.length > MAX_JSON_BYTES) throw new Error('Beast file is too large');
  const value = purify(JSON.parse(new TextDecoder().decode(bytes)));
  if (value.format === 'QBEAST1') return fromQbeastSnapshot(value, traits, options.trustedPublicKey || '');
  if (value.format === 'LCSHARE1') return openShareValue(value, options.passphrase || '');
  if (value.schema === 'beast-cage-creature-v1') return creatureRecord(value, traits, 'beast');
  throw new Error('Unrecognized beast file');
}

export function suggestionFromText(text) {
  const start = String(text || '').indexOf('{');
  const end = String(text || '').lastIndexOf('}');
  if (start < 0 || end <= start) throw new Error('The model did not return a creature label');
  return acceptSuggestion(purify(JSON.parse(text.slice(start, end + 1))));
}

export async function askModel({ url, key = '', protocol = 'openai', model = '', family = 'nebula', seed = 'seed' }, fetchImpl = globalThis.fetch) {
  let endpoint;
  try { endpoint = new URL(url); } catch { throw new Error('Enter an http or https model endpoint'); }
  if (endpoint.protocol !== 'http:' && endpoint.protocol !== 'https:') throw new Error('The model endpoint must be http or https');
  const prompt = `Reply with one JSON object and nothing else. Use only the keys callsign and note. callsign is 1 to 12 letters or digits. note is at most 48 ASCII characters of public game flavor. Family ${family}. Seed label ${String(seed).slice(0, 64)}. Do not invent stats or identifiers.`;
  const headers = { 'content-type': 'application/json' };
  if (key) headers.authorization = `Bearer ${key}`;
  let body;
  if (protocol === 'ollama') {
    body = { model: model || 'llama3.2', messages: [{ role: 'user', content: prompt }], stream: false };
  } else {
    body = { model: model || 'gpt-4o-mini', temperature: 0, messages: [{ role: 'user', content: prompt }] };
  }
  const response = await fetchImpl(endpoint.toString(), { method: 'POST', headers, body: JSON.stringify(body) });
  if (!response.ok) throw new Error('The model endpoint refused the request. Check the address and CORS.');
  const payload = purify(await response.json());
  const content = protocol === 'ollama' ? payload.message?.content : payload.choices?.[0]?.message?.content;
  return suggestionFromText(content);
}
