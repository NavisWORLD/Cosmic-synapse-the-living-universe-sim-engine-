/** Training spends energy, raises effort and bond, and earns evolution by experience. */

import { grant, stageFromXp } from './store.mjs';

export const ENERGY_MAX = 100;

export const ACTIVITIES = {
  focus: { energy: 16, xp: 18, bond: 4, effort: { spd: 2, spark: 1 } },
  memory: { energy: 16, xp: 18, bond: 4, effort: { spark: 2, def: 1 } },
  play: { energy: 8, xp: 8, bond: 6, effort: { atk: 1, spd: 1 } },
  rest: { energy: 28, xp: 0, bond: 1, effort: { hp: 1 } },
};

const EMPTY_EFFORT = () => ({ hp: 0, atk: 0, def: 0, spd: 0, spark: 0 });

export function nextStageGoal(xp) {
  if (xp >= 120) return null;
  return xp >= 40 ? 120 : 40;
}

export function scoreFocus(hits, total = 6) {
  const whole = Math.max(1, total | 0);
  const landed = Math.max(0, Math.min(whole, hits | 0));
  return { hits: landed, total: whole, quality: landed / whole };
}

export function scoreMemory(shown, answer) {
  const sequence = Array.isArray(shown) ? shown : [];
  const guess = Array.isArray(answer) ? answer : [];
  let correct = 0;
  for (let i = 0; i < sequence.length; i++) {
    if (sequence[i] !== guess[i]) break;
    correct += 1;
  }
  return { correct, length: sequence.length, quality: sequence.length ? correct / sequence.length : 0 };
}

export function planTraining(activity, score = {}) {
  const base = ACTIVITIES[activity];
  if (!base) throw new Error('Unknown training');
  const quality = activity === 'rest' ? 1 : Math.max(0, Math.min(1, Number(score.quality ?? 1)));
  const scale = activity === 'rest' ? 1 : 0.4 + 0.6 * quality;
  const effort = {};
  for (const [stat, amount] of Object.entries(base.effort)) {
    effort[stat] = quality > 0 || activity === 'rest' ? Math.max(1, Math.round(amount * scale)) : 0;
  }
  return {
    activity,
    energy: base.energy,
    xp: Math.round(base.xp * scale),
    bond: Math.round(base.bond * scale * 10) / 10,
    effort,
    quality,
  };
}

function ensureCare(beast) {
  if (!Number.isFinite(beast.energy)) beast.energy = ENERGY_MAX;
  beast.energy = Math.max(0, Math.min(ENERGY_MAX, beast.energy));
  beast.effort = { ...EMPTY_EFFORT(), ...(beast.effort || {}) };
  for (const key of Object.keys(beast.effort)) beast.effort[key] = Math.max(0, beast.effort[key] | 0);
}

export function applyTraining(store, seed, activity, score) {
  const beast = store.beasts[seed];
  if (!beast) return { ok: false, reason: 'missing', beast: null, plan: null };
  const plan = planTraining(activity, score);
  ensureCare(beast);
  if (activity !== 'rest' && beast.energy < plan.energy) {
    return { ok: false, reason: 'tired', beast, plan };
  }
  const before = beast.stage;
  if (activity === 'rest') beast.energy = Math.min(ENERGY_MAX, beast.energy + plan.energy);
  else beast.energy -= plan.energy;
  for (const [stat, amount] of Object.entries(plan.effort)) beast.effort[stat] += amount;
  const granted = grant(store, seed, plan.xp, plan.bond);
  return {
    ok: true,
    reason: 'trained',
    grew: Boolean(granted?.grew),
    before,
    beast: granted.beast,
    plan,
    stage: stageFromXp(granted.beast.xp),
  };
}

export function trainingBlurb(result, name) {
  if (!result?.ok && result?.reason === 'tired') return `${name} is too tired. Rest together, then train again.`;
  if (!result?.ok) return 'Spark a beast before training.';
  const plan = result.plan;
  if (plan.activity === 'rest') return `${name} rests. Energy is back up.`;
  if (plan.activity === 'play') return `${name} plays and the bond grows.`;
  if (plan.activity === 'focus') return `${name} holds the rhythm. ${plan.quality >= 0.67 ? 'Sharp focus.' : 'Good try.'}`;
  if (plan.activity === 'memory') return `${name} repeats the sparks. ${plan.quality === 1 ? 'Perfect memory.' : 'The pattern is settling.'}`;
  return `${name} trains.`;
}

export { stageFromXp };
