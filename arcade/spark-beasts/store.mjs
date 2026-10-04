/** Local spark ledger. Bond and experience only grow. Raw sensors are never written. */

export const STORE_KEY = 'spark-beasts-v1';

export function emptyStore() {
  return { version: 1, playerName: '', active: null, beasts: {} };
}

export function sanitizeDisplayName(name) {
  const clean = String(name || '').replace(/[^A-Za-z0-9 '\-]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 16);
  return clean;
}

export function shownName(beast, speciesName) {
  return sanitizeDisplayName(beast?.displayName) || speciesName || 'Beast';
}

function emptyEffort() {
  return { hp: 0, atk: 0, def: 0, spd: 0, spark: 0 };
}

function hydrateBeast(beast) {
  beast.displayName = sanitizeDisplayName(beast.displayName);
  beast.energy = Number.isFinite(Number(beast.energy)) ? Math.max(0, Math.min(100, Number(beast.energy))) : 100;
  const effort = emptyEffort();
  for (const key of Object.keys(effort)) effort[key] = Math.max(0, Number(beast.effort?.[key]) || 0);
  beast.effort = effort;
  const facts = Array.isArray(beast.memory?.facts) ? beast.memory.facts.slice(-8) : [];
  beast.memory = {
    playerName: String(beast.memory?.playerName || '').slice(0, 16),
    facts: facts.map((fact) => ({
      topic: String(fact?.topic || '').slice(0, 16),
      detail: String(fact?.detail || '').slice(0, 40),
    })).filter((fact) => fact.topic && fact.detail),
  };
  const cageId = String(beast.cageId || '').toLowerCase();
  beast.cageId = /^[0-9a-f]{8}$/.test(cageId) ? cageId : '';
  return beast;
}

export function stageFromXp(xp) {
  if (xp >= 120) return 3;
  if (xp >= 40) return 2;
  return 1;
}

export function loadStore(storage) {
  try {
    const raw = storage.getItem(STORE_KEY);
    if (!raw) return emptyStore();
    const value = JSON.parse(raw);
    if (!value || value.version !== 1 || !value.beasts || typeof value.beasts !== 'object') return emptyStore();
    for (const beast of Object.values(value.beasts)) hydrateBeast(beast);
    return value;
  } catch {
    return emptyStore();
  }
}

export function saveStore(store, storage) {
  storage.setItem(STORE_KEY, JSON.stringify(store));
}

export function rememberBeast(store, beast) {
  const prev = store.beasts[beast.seed];
  const xp = Math.max(prev?.xp || 0, Math.max(0, beast.xp || 0));
  const bond = Math.min(100, Math.max(prev?.bond || 0, Math.max(0, beast.bond || 0)));
  const displayName = beast.displayName != null ? sanitizeDisplayName(beast.displayName) : (prev?.displayName || '');
  store.beasts[beast.seed] = hydrateBeast({
    seed: beast.seed,
    traits: beast.traits,
    runIndex: beast.runIndex,
    runKey: beast.runKey,
    userId: beast.userId ?? null,
    origin: beast.origin || prev?.origin || 'spark',
    island: beast.island,
    name: beast.name,
    displayName,
    energy: beast.energy != null ? beast.energy : prev?.energy,
    effort: beast.effort || prev?.effort,
    memory: beast.memory || prev?.memory,
    cageId: beast.cageId || prev?.cageId || '',
    xp,
    bond,
    stage: stageFromXp(xp),
    discoveredAt: prev?.discoveredAt || beast.discoveredAt || new Date().toISOString(),
  });
  return store.beasts[beast.seed];
}

export function renameBeast(store, seed, displayName) {
  const beast = store.beasts[seed];
  if (!beast) return null;
  const next = sanitizeDisplayName(displayName);
  if (!next) return null;
  beast.displayName = next;
  return beast;
}

export function rememberChat(store, seed, memory) {
  const beast = store.beasts[seed];
  if (!beast) return null;
  beast.memory = hydrateBeast({ memory }).memory;
  return beast.memory;
}

export function grant(store, seed, xpAdd = 0, bondAdd = 0) {
  const beast = store.beasts[seed];
  if (!beast) return null;
  beast.xp += Math.max(0, xpAdd);
  beast.bond = Math.min(100, beast.bond + Math.max(0, bondAdd));
  const next = stageFromXp(beast.xp);
  const grew = next > beast.stage;
  beast.stage = next;
  return { beast, grew };
}

export function eraseStore(storage) {
  storage.removeItem(STORE_KEY);
}
