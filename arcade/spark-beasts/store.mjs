/** Local spark ledger. Bond and experience only grow. Raw sensors are never written. */

export const STORE_KEY = 'spark-beasts-v1';

export function emptyStore() {
  return { version: 1, playerName: '', active: null, beasts: {} };
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
  store.beasts[beast.seed] = {
    seed: beast.seed,
    traits: beast.traits,
    runIndex: beast.runIndex,
    runKey: beast.runKey,
    userId: beast.userId ?? null,
    origin: beast.origin || prev?.origin || 'spark',
    island: beast.island,
    name: beast.name,
    xp,
    bond,
    stage: stageFromXp(xp),
    discoveredAt: prev?.discoveredAt || beast.discoveredAt || new Date().toISOString(),
  };
  return store.beasts[beast.seed];
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
