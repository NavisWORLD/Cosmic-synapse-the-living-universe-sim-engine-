import assert from 'node:assert/strict';
import test from 'node:test';

import {
  ACTIVITY_IDS, CALM, HALF_LIFE_MS, PICK,
  addEvent, emptyPreferences, rankActivities, suggest,
} from './preferences.mjs';

const NOW = 1_700_000_000_000;

test('picks and calming marks are stored without mutating the previous list', () => {
  const start = emptyPreferences();
  const picked = addEvent(start, 'bubbles', PICK, NOW);
  const marked = addEvent(picked, 'breathe', CALM, NOW + 5);
  assert.equal(start.events.length, 0);
  assert.equal(picked.events.length, 1);
  assert.deepEqual(marked.events.map((event) => [event.id, event.kind]), [
    ['bubbles', 'pick'],
    ['breathe', 'calm'],
  ]);
});

test('unknown activity, kind, or time is rejected', () => {
  const start = emptyPreferences();
  assert.throws(() => addEvent(start, 'nope', PICK, NOW), /Unknown activity/);
  assert.throws(() => addEvent(start, 'flow', 'skip', NOW), /Unknown kind/);
  assert.throws(() => addEvent(start, 'flow', PICK, Number.NaN), /time/);
  assert.equal(start.events.length, 0);
});

test('a calming mark outranks several picks', () => {
  let prefs = emptyPreferences();
  prefs = addEvent(prefs, 'fidget', PICK, NOW);
  prefs = addEvent(prefs, 'fidget', PICK, NOW);
  prefs = addEvent(prefs, 'rhythm', CALM, NOW);
  const ranked = rankActivities(prefs, NOW);
  assert.equal(ranked[0].id, 'rhythm');
  assert.ok(ranked[0].score > ranked.find((item) => item.id === 'fidget').score);
});

test('equal score prefers the stronger calming mark, then recency, then stable order', () => {
  let tiedCalm = emptyPreferences();
  tiedCalm = addEvent(tiedCalm, 'fidget', PICK, NOW);
  tiedCalm = addEvent(tiedCalm, 'fidget', PICK, NOW);
  tiedCalm = addEvent(tiedCalm, 'fidget', PICK, NOW);
  tiedCalm = addEvent(tiedCalm, 'bubbles', CALM, NOW);
  const calmFirst = rankActivities(tiedCalm, NOW);
  assert.equal(calmFirst[0].score, calmFirst[1].score);
  assert.equal(calmFirst[0].id, 'bubbles');

  let tiedRecent = emptyPreferences();
  tiedRecent = addEvent(tiedRecent, 'fidget', PICK, 10);
  tiedRecent = addEvent(tiedRecent, 'bubbles', PICK, 20);
  const recentFirst = rankActivities(tiedRecent, 100, Number.POSITIVE_INFINITY);
  assert.equal(recentFirst[0].id, 'bubbles');
  assert.equal(recentFirst[1].id, 'fidget');

  let tiedOrder = emptyPreferences();
  tiedOrder = addEvent(tiedOrder, 'rhythm', PICK, 5);
  tiedOrder = addEvent(tiedOrder, 'breathe', PICK, 5);
  const stable = rankActivities(tiedOrder, 5, Number.POSITIVE_INFINITY);
  assert.deepEqual(stable.slice(0, 2).map((item) => item.id), ['breathe', 'rhythm']);
});

test('an empty model suggests the stable gentle order', () => {
  const ranked = rankActivities(emptyPreferences(), NOW);
  assert.deepEqual(ranked.map((item) => item.id), ACTIVITY_IDS);
  assert.equal(ranked[0].id, 'breathe');
  assert.equal(ranked.every((item) => item.score === 0), true);
});

test('older events decay by half each week', () => {
  let prefs = emptyPreferences();
  prefs = addEvent(prefs, 'fidget', PICK, NOW);
  prefs = addEvent(prefs, 'bubbles', PICK, NOW - HALF_LIFE_MS);
  prefs = addEvent(prefs, 'flow', CALM, NOW - (2 * HALF_LIFE_MS));
  const ranked = rankActivities(prefs, NOW);
  const fidget = ranked.find((item) => item.id === 'fidget');
  const bubbles = ranked.find((item) => item.id === 'bubbles');
  const flow = ranked.find((item) => item.id === 'flow');
  assert.ok(Math.abs(fidget.score - 1) < 1e-9);
  assert.ok(Math.abs(bubbles.score - 0.5) < 1e-9);
  assert.ok(Math.abs(flow.score - 0.75) < 1e-9);
  assert.deepEqual(ranked.slice(0, 3).map((item) => item.id), ['fidget', 'flow', 'bubbles']);
});

test('suggest uses an adapter when one is provided', () => {
  const seen = [];
  const ranked = suggest(emptyPreferences(), NOW, {
    rank(preferences, now) {
      seen.push(now);
      assert.equal(preferences.events.length, 0);
      return [{ id: 'rhythm', score: 1, calming: 0, recent: 0 }];
    },
  });
  assert.deepEqual(seen, [NOW]);
  assert.equal(ranked[0].id, 'rhythm');
  assert.equal(suggest(emptyPreferences(), NOW)[0].id, 'breathe');
});
