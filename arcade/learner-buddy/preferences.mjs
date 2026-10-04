/**
 * Local preference rules for Learner Buddy.
 *
 * The RAWRPHOS brain lives in NavisWORLD/The-beast-box- and is Python on a
 * server. This pilot does not call it. Pass an adapter with rank(preferences, now)
 * into suggest() if a future on-device model should take over.
 */

export const ACTIVITIES = [
  { id: 'breathe', label: 'Breathing' },
  { id: 'flow', label: 'Color flow' },
  { id: 'fidget', label: 'Fidget spinner' },
  { id: 'bubbles', label: 'Bubble pop' },
  { id: 'rhythm', label: 'Rhythmic sound' },
];

export const ACTIVITY_IDS = ACTIVITIES.map((item) => item.id);
export const PICK = 'pick';
export const CALM = 'calm';
/** A calming mark outweighs casual picks. */
export const CALM_WEIGHT = 3;
/** A week-old event counts as half of a new one. */
export const HALF_LIFE_MS = 7 * 24 * 60 * 60 * 1000;

export function activityLabel(id) {
  return ACTIVITIES.find((item) => item.id === id)?.label || id;
}

export function emptyPreferences() {
  return { events: [] };
}

export function addEvent(preferences, activityId, kind, at) {
  if (!ACTIVITY_IDS.includes(activityId)) throw new Error(`Unknown activity: ${activityId}`);
  if (kind !== PICK && kind !== CALM) throw new Error(`Unknown kind: ${kind}`);
  if (!Number.isFinite(at)) throw new Error('Event time is required');
  return { events: preferences.events.concat([{ id: activityId, kind, at }]) };
}

export function eventWeight(at, now, halfLife = HALF_LIFE_MS) {
  if (!Number.isFinite(halfLife) || halfLife === Number.POSITIVE_INFINITY) return 1;
  const age = Math.max(0, now - at);
  return 0.5 ** (age / halfLife);
}

export function scoreActivity(preferences, activityId, now, halfLife = HALF_LIFE_MS) {
  let score = 0;
  let calming = 0;
  let recent = 0;
  for (const event of preferences.events) {
    if (event.id !== activityId) continue;
    const weight = eventWeight(event.at, now, halfLife);
    if (event.kind === CALM) {
      score += CALM_WEIGHT * weight;
      calming += weight;
    } else if (event.kind === PICK) {
      score += weight;
    }
    if (event.at > recent) recent = event.at;
  }
  return { id: activityId, score, calming, recent };
}

function different(left, right) {
  return Math.abs(left - right) > 1e-9;
}

/**
 * Higher score first. Ties break toward more calming weight, then the more
 * recent event, then the stable activity order (gentler activities first).
 */
export function rankActivities(preferences, now, halfLife = HALF_LIFE_MS) {
  const ranked = ACTIVITY_IDS.map((id) => scoreActivity(preferences, id, now, halfLife));
  ranked.sort((a, b) => {
    if (different(a.score, b.score)) return b.score - a.score;
    if (different(a.calming, b.calming)) return b.calming - a.calming;
    if (a.recent !== b.recent) return b.recent - a.recent;
    return ACTIVITY_IDS.indexOf(a.id) - ACTIVITY_IDS.indexOf(b.id);
  });
  return ranked;
}

export function suggest(preferences, now, adapter, halfLife = HALF_LIFE_MS) {
  if (adapter && typeof adapter.rank === 'function') return adapter.rank(preferences, now);
  return rankActivities(preferences, now, halfLife);
}
