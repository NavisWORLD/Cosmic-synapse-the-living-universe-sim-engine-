/**
 * Synapse OS cage. The beast is a ledger entry with an allowlist, not a
 * program. Growth uses epoch, layer, and points so the cartridge fields
 * never overflow. Nothing here claims the creature is aware.
 */
import { crc32 } from './mailbox.mjs';
import { bytesToHex, cartridgeEpoch, sha256Hex } from './qbeast.mjs';

export const PERMISSIONS = Object.freeze(['sense', 'world', 'memory']);
export const LEDGER_KEY = 'lc-synapse-os-v1';
const ZERO = '0'.repeat(64);

export function emptyLedger() {
  return { version: 1, identities: {}, events: [] };
}

export function growthGain(sense, world) {
  const bio = Math.max(0, Math.min(1, Number(world.biosphere) || 0));
  const life = Math.max(0, Math.trunc(Number(world.lifeEvents) || 0));
  return 1
    + Math.floor(sense.focus / 25)
    + Math.floor(sense.calm / 34)
    + Math.floor(sense.spark / 40)
    + Math.floor(bio * 3)
    + Math.min(3, life);
}

function project(input) {
  if (!input || typeof input !== 'object') throw new Error('The cage refused an unnamed input');
  if ('samples' in input || 'eeg' in input || 'waveform' in input) throw new Error('Raw sensor samples cannot enter the cage');
  const permissions = input.permissions;
  if (!Array.isArray(permissions) || permissions.length !== PERMISSIONS.length || PERMISSIONS.some((name, i) => permissions[i] !== name)) {
    throw new Error('The cage only accepts sense, world, and memory');
  }
  const sense = input.sense || {};
  const world = input.world || {};
  for (const [bag, allowed] of [[sense, ['focus', 'calm', 'spark']], [world, ['name', 'biosphere', 'evolution', 'lifeEvents']]]) {
    if (Object.keys(bag).some((key) => !allowed.includes(key))) throw new Error('The cage refused an extra field');
  }
  for (const [name, value] of [['focus', sense.focus], ['calm', sense.calm], ['spark', sense.spark]]) {
    if (!Number.isInteger(value) || value < 0 || value > 100) throw new Error(`${name} must be an integer 0..100`);
  }
  return {
    sense: { focus: sense.focus, calm: sense.calm, spark: sense.spark },
    world: {
      name: String(world.name || 'WORLD').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12) || 'WORLD',
      biosphere: Number(world.biosphere) || 0,
      evolution: Number(world.evolution) || 0,
      lifeEvents: Math.max(0, Math.trunc(Number(world.lifeEvents) || 0)),
    },
  };
}

function memoryLine(view) {
  const bio = Math.max(0, Math.min(999, Math.trunc(view.world.biosphere * 1000)));
  const evo = Math.max(0, Math.min(999, Math.trunc(view.world.evolution * 1000)));
  return `WORLD ${view.world.name} BIO ${bio} EVO ${evo} F${view.sense.focus} C${view.sense.calm} S${view.sense.spark}`.slice(0, 48);
}

function compareProgress(a, b) {
  const epoch = BigInt(a.epoch) - BigInt(b.epoch);
  if (epoch !== 0n) return epoch > 0n ? 1 : -1;
  if (a.layer !== b.layer) return a.layer > b.layer ? 1 : -1;
  if (a.points !== b.points) return a.points > b.points ? 1 : -1;
  return 0;
}

function maxProgress(a, b) {
  return compareProgress(a, b) >= 0 ? a : b;
}

async function link(prev, event) {
  const text = `lc1|${prev}|${event.kind}|${event.id}|${event.epoch}|${event.layer}|${event.points}`;
  return sha256Hex(text);
}

async function appendEvent(ledger, row, kind) {
  const event = { kind, id: row.id, epoch: row.epoch, layer: row.layer, points: row.points, prev: row.chain };
  event.hash = await link(row.chain, event);
  row.chain = event.hash;
  ledger.events.push({ ...event });
  if (ledger.events.length > 64) ledger.events.splice(0, ledger.events.length - 64);
}

function rowProgress(row) {
  return { epoch: row.epoch, layer: row.layer, points: row.points, trade: false, grown: row.epoch !== '0' || row.layer !== 0 || row.points !== 0, memoryCrc: 0, chainCrc: 0 };
}

export async function fingerprint(record) {
  return sha256Hex(record.profile.bcp1);
}

export function randomTransfer() {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return bytesToHex(bytes);
}

export async function admit(ledger, record, mode = 'receive') {
  const id = record.publicId.toString(16).padStart(8, '0');
  const bcp1 = await fingerprint(record);
  const incoming = {
    epoch: String(record.growth?.epoch ?? '0'),
    layer: record.growth?.layer ?? 0,
    points: record.growth?.points ?? 0,
  };
  if (!/^\d{1,20}$/.test(incoming.epoch) || incoming.layer < 0 || incoming.layer > 999 || incoming.points < 0 || incoming.points > 999) {
    throw new Error('Incoming growth was rejected');
  }
  let row = ledger.identities[id];
  if (!row) {
    row = {
      id, bcp1, held: true, transfer: record.transfer || randomTransfer(),
      epoch: incoming.epoch, layer: incoming.layer, points: incoming.points,
      memories: Array.isArray(record.memories) ? record.memories.slice(0, 8) : [],
      chain: ZERO,
    };
    ledger.identities[id] = row;
    await appendEvent(ledger, row, 'import');
  } else if (row.bcp1 !== bcp1) {
    throw new Error('This public identity already belongs to a different beast. A duplicate was refused.');
  } else if (!row.held && mode === 'local') {
    throw new Error('This beast was released for trade. Import the share to bring that ticket back.');
  } else if (row.held && record.transfer && record.transfer !== row.transfer) {
    throw new Error('This beast is already in the cage. A second copy was refused.');
  } else if (!row.held) {
    const sameTicket = record.transfer === row.transfer;
    const newer = compareProgress(incoming, row) > 0;
    if (!sameTicket && !newer) throw new Error('This trade ticket does not match the beast that left the cage.');
    row.held = true;
    if (record.transfer) row.transfer = record.transfer;
    const kept = maxProgress(row, incoming);
    row.epoch = kept.epoch;
    row.layer = kept.layer;
    row.points = kept.points;
    if (Array.isArray(record.memories) && record.memories.length) row.memories = record.memories.slice(0, 8);
    await appendEvent(ledger, row, 'import');
  } else {
    const kept = maxProgress(row, incoming);
    row.epoch = kept.epoch;
    row.layer = kept.layer;
    row.points = kept.points;
  }
  record.transfer = row.transfer;
  record.memories = row.memories.slice();
  record.growth = {
    ...rowProgress(row),
    trade: Boolean(record.growth?.trade) || !row.held,
    grown: row.epoch !== '0' || row.layer !== 0 || row.points !== 0,
    memoryCrc: crc32(new TextEncoder().encode(row.memories.join('\n'))),
    chainCrc: crc32(new TextEncoder().encode(row.chain)),
  };
  record.publicHex = id;
  return record;
}

export async function tend(ledger, record, input) {
  const view = project(input);
  const id = record.publicId.toString(16).padStart(8, '0');
  await admit(ledger, record, 'local');
  const row = ledger.identities[id];
  if (!row.held) throw new Error('This beast was released for trade. Importing it again restores the same identity.');
  let points = row.points + growthGain(view.sense, view.world);
  let layer = row.layer;
  let epoch = BigInt(row.epoch);
  while (points >= 1000) {
    points -= 1000;
    layer += 1;
  }
  while (layer >= 1000) {
    layer -= 1000;
    if (epoch < 0xffffffffn) epoch += 1n;
  }
  row.points = points;
  row.layer = layer;
  row.epoch = epoch.toString();
  const line = memoryLine(view);
  row.memories.push(line);
  if (row.memories.length > 8) row.memories.splice(0, row.memories.length - 8);
  await appendEvent(ledger, row, 'tend');
  record.growth = {
    epoch: row.epoch,
    layer: row.layer,
    points: row.points,
    trade: Boolean(record.growth?.trade),
    grown: true,
    memoryCrc: crc32(new TextEncoder().encode(row.memories.join('\n'))),
    chainCrc: crc32(new TextEncoder().encode(row.chain)),
  };
  record.memories = row.memories.slice();
  return record;
}

export async function releaseForTrade(ledger, record) {
  const id = record.publicId.toString(16).padStart(8, '0');
  await admit(ledger, record, 'local');
  const row = ledger.identities[id];
  if (!row.held) throw new Error('This beast is already out for trade.');
  row.held = false;
  row.transfer = randomTransfer();
  record.transfer = row.transfer;
  record.growth = { ...record.growth, trade: true };
  await appendEvent(ledger, row, 'trade');
  record.growth.chainCrc = crc32(new TextEncoder().encode(row.chain));
  return record;
}

export function loadLedger(storage) {
  try {
    const raw = storage.getItem(LEDGER_KEY);
    if (!raw) return emptyLedger();
    const value = JSON.parse(raw);
    if (!value || value.version !== 1 || !value.identities || !Array.isArray(value.events)) return emptyLedger();
    return value;
  } catch {
    return emptyLedger();
  }
}

export function saveLedger(ledger, storage) {
  storage.setItem(LEDGER_KEY, JSON.stringify(ledger));
}

export function cageSave(record, buildSave, buildGrowth, attachGrowth) {
  const growth = buildGrowth({
    publicId: record.publicId,
    epoch: cartridgeEpoch(record.growth.epoch),
    layer: record.growth.layer,
    points: record.growth.points,
    memoryCrc: record.growth.memoryCrc || 0,
    chainCrc: record.growth.chainCrc || 0,
    trade: Boolean(record.growth.trade),
    grown: Boolean(record.growth.grown),
  });
  return attachGrowth(buildSave(record.profile), growth);
}
