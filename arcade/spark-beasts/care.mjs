/**
 * Shared Spark Beasts care. Spark Beasts and the Synapse OS model bay
 * both call this module, so name, memory, bond, experience, and earned
 * evolution stay on one device ledger.
 */
import { replyToBeast } from './chat.mjs';
import { loadStore, rememberBeast, rememberChat, renameBeast, saveStore, shownName, stageFromXp, STORE_KEY } from './store.mjs';
import { applyTraining, nextStageGoal, trainingBlurb } from './train.mjs';
import { xpFromGrowth } from './trade.mjs';

export { loadStore, saveStore, shownName, stageFromXp, nextStageGoal, trainingBlurb, STORE_KEY, xpFromGrowth };

export function findByCage(store, cageId) {
  const id = String(cageId || '').toLowerCase();
  if (!/^[0-9a-f]{8}$/.test(id)) return null;
  for (const beast of Object.values(store?.beasts || {})) {
    if (beast.cageId === id) return beast;
  }
  return null;
}

export function bindCage(store, seed, cageId) {
  const beast = store?.beasts?.[seed];
  const id = String(cageId || '').toLowerCase();
  if (!beast || !/^[0-9a-f]{8}$/.test(id)) return beast || null;
  beast.cageId = id;
  return beast;
}

export function listCareBeasts(store) {
  return Object.values(store?.beasts || {}).filter((beast) => beast.cageId || beast.origin === 'cage' || String(beast.seed).startsWith('cage:'));
}

export function adoptCageRecord(store, record) {
  const cageId = String(record?.publicHex || '').toLowerCase();
  if (!/^[0-9a-f]{8}$/.test(cageId)) throw new Error('The cage beast has no public id');
  const existing = findByCage(store, cageId);
  if (existing) return existing;
  const sparkLike = String(record.growth?.epoch ?? '0') === '0' && !(record.growth?.layer > 0);
  const startXp = sparkLike ? Math.max(0, Math.min(999, record.growth?.points || 0)) : 0;
  return rememberBeast(store, {
    seed: `cage:${cageId}`,
    traits: {
      focus: Number.isInteger(record.focus) ? record.focus : 50,
      calm: Number.isInteger(record.calm) ? record.calm : 50,
      spark: Number.isInteger(record.spark) ? record.spark : 50,
    },
    runIndex: 0,
    runKey: 'cage',
    userId: null,
    origin: 'cage',
    island: record.speciesName || 'Cage',
    name: record.callsign || 'Beast',
    displayName: '',
    xp: startXp,
    bond: 1,
    cageId,
  });
}

export function careLines(beast, name) {
  if (!beast) return 'Choose a caged beast to talk and train.';
  const title = name || shownName(beast, beast.name);
  const goal = nextStageGoal(beast.xp || 0);
  const effort = beast.effort || { hp: 0, atk: 0, def: 0, spd: 0, spark: 0 };
  const next = goal ? `${beast.xp}/${goal} xp to the next form` : 'final form earned';
  return `${title} · stage ${beast.stage || 1} · energy ${Math.round(beast.energy ?? 100)} · bond ${Math.round(beast.bond || 0)} · ${next} · effort HP ${effort.hp} ATK ${effort.atk} DEF ${effort.def} SPD ${effort.spd} SPK ${effort.spark}`;
}

export async function careTalk(store, seed, message, extra = {}, options = {}) {
  const beast = store?.beasts?.[seed];
  if (!beast) return { ok: false, source: 'rules', text: 'Choose a beast first.', memory: null };
  const result = await replyToBeast(message, {
    temperament: extra.temperament || 'Gentle',
    island: extra.island || beast.island || 'the cage',
    element: extra.element || 'spark',
    body: extra.body || 'beast',
    displayName: extra.displayName || shownName(beast, beast.name),
    speciesName: extra.speciesName || beast.name || 'Beast',
    stage: beast.stage || 1,
    bond: beast.bond || 0,
    mood: extra.mood || 'neutral',
    energy: beast.energy,
    keeperName: extra.keeperName || '',
    memory: beast.memory,
  }, options);
  rememberChat(store, seed, result.memory);
  return result;
}

export function careTrain(store, seed, activity, score) {
  return applyTraining(store, seed, activity, score);
}

export function careRename(store, seed, displayName) {
  return renameBeast(store, seed, displayName);
}

export function handheldStamp(record, beast) {
  if (!record) throw new Error('There is no beast to send.');
  const careXp = Math.max(0, Math.floor(Number(beast?.xp) || 0));
  const growthXp = Math.max(0, xpFromGrowth(record.growth));
  const kept = Math.max(careXp, growthXp);
  const nick = String(beast?.displayName || '').trim();
  const call = nick
    ? nick.toUpperCase().replace(/[^A-Z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 12)
    : record.callsign;
  return {
    callsign: call || record.callsign,
    growth: {
      ...record.growth,
      layer: Math.min(999, Math.floor(kept / 1000)),
      points: kept % 1000,
      grown: kept > 0 || Boolean(record.growth?.grown),
    },
  };
}

export function stampRecord(record, beast) {
  const stamp = handheldStamp(record, beast);
  return {
    ...record,
    callsign: stamp.callsign,
    profile: record.profile ? { ...record.profile, callsign: stamp.callsign } : record.profile,
    growth: stamp.growth,
  };
}
