import assert from 'node:assert/strict';
import test from 'node:test';

import { SCHEMA, STORAGE_KEY, VERSION, createStore, memoryStorage } from './store.mjs';

function harness() {
  let clock = 1_700_000_000_000;
  let n = 0;
  const storage = memoryStorage();
  const store = createStore(storage, {
    now: () => clock,
    id: (prefix) => `${prefix}-${++n}`,
  });
  return {
    storage,
    store,
    tick(ms = 1000) {
      clock += ms;
    },
  };
}

test('export round-trips schema, version, and user data', () => {
  const { store } = harness();
  store.load();
  store.pickActivity('bubbles');
  store.markCalming('breathe');
  store.addFeeling('glad');
  store.completeGoal('goal-hello');
  const exported = store.exportJson();
  const parsed = JSON.parse(exported);
  assert.equal(parsed.schema, SCHEMA);
  assert.equal(parsed.version, VERSION);
  assert.deepEqual(Object.keys(parsed).sort(), [
    'buddyName', 'feelings', 'goals', 'growth', 'log', 'preferences', 'routines', 'schema', 'settings', 'updatedAt', 'version',
  ]);
  assert.equal(parsed.growth.stage, 1);
  assert.equal(parsed.growth.goalsCompleted, 1);
  assert.equal(parsed.preferences.events.some((event) => event.kind === 'calm' && event.id === 'breathe'), true);
  assert.equal(JSON.stringify(parsed).includes('samples'), false);
  assert.equal(JSON.stringify(parsed).includes('eeg'), false);

  const other = harness();
  other.store.importJson(exported);
  const again = JSON.parse(other.store.exportJson());
  assert.equal(again.schema, SCHEMA);
  assert.equal(again.version, VERSION);
  assert.equal(again.growth.goalsCompleted, 1);
  assert.equal(again.feelings[0].feeling, 'glad');
  assert.equal(again.buddyName, 'Mote');
});

test('import rejects the wrong schema or version and keeps the previous document', () => {
  const { storage, store } = harness();
  store.load();
  store.pickActivity('flow');
  const good = JSON.parse(store.exportJson());
  const wrongSchema = { ...good, schema: 'something-else' };
  assert.throws(() => store.importJson(JSON.stringify(wrongSchema)), /Schema name/);
  const wrongVersion = { ...good, version: 2 };
  assert.throws(() => store.importJson(JSON.stringify(wrongVersion)), /Schema version/);
  assert.throws(() => store.importJson('{'), /not valid JSON/);
  const missing = { ...good };
  delete missing.growth;
  assert.throws(() => store.importJson(JSON.stringify(missing)), /Growth/);
  const still = JSON.parse(store.exportJson());
  assert.equal(still.preferences.events[0].id, 'flow');
  assert.equal(storage.getItem(STORAGE_KEY).includes('"id":"flow"'), true);
});

test('import keeps a higher stage, raises a stage that fell behind, and drops unknown fields', () => {
  const { store } = harness();
  store.load();
  const doc = JSON.parse(store.exportJson());
  doc.growth = { stage: 4, goalsCompleted: 0 };
  doc.samples = [1, 2, 3];
  doc.eeg = 'raw';
  doc.log = [{ id: 'log-x', at: 5, kind: 'pick', detail: { activity: 'flow', samples: [9], note: 'nope' } }];
  store.importJson(JSON.stringify(doc));
  const saved = JSON.parse(store.exportJson());
  assert.equal(saved.growth.stage, 4);
  assert.equal(saved.growth.goalsCompleted, 0);
  assert.equal(saved.samples, undefined);
  assert.equal(saved.eeg, undefined);
  assert.deepEqual(saved.log[0].detail, { activity: 'flow' });

  const behind = JSON.parse(store.exportJson());
  behind.growth = { stage: 0, goalsCompleted: 6 };
  store.importJson(JSON.stringify(behind));
  assert.equal(JSON.parse(store.exportJson()).growth.stage, 3);
});

test('delete clears storage and a reload does not bring the old buddy back', () => {
  const { storage, store } = harness();
  store.load();
  store.addGoal('Drink some water');
  store.completeGoal('goal-hello');
  store.updateSettings({ museConsent: true, lowSensory: true, volume: 0.2, brightness: 0.9 });
  store.addRoutine({ first: 'Reading', then: 'Drawing', icon: 'book' });
  assert.equal(storage.getItem(STORAGE_KEY) !== null, true);

  store.deleteAll();
  assert.equal(storage.getItem(STORAGE_KEY), null);
  const exported = JSON.parse(store.exportJson());
  assert.equal(exported.schema, SCHEMA);
  assert.equal(exported.version, VERSION);
  assert.equal(exported.growth.goalsCompleted, 0);
  assert.equal(exported.log.length, 0);
  assert.equal(storage.getItem(STORAGE_KEY), null);

  const reloaded = createStore(storage, { now: () => 50, id: (prefix) => `${prefix}-new` });
  const fresh = reloaded.load();
  assert.equal(fresh.growth.stage, 0);
  assert.equal(fresh.goals.some((goal) => goal.label === 'Drink some water'), false);
  assert.equal(fresh.settings.museConsent, false);
  assert.equal(fresh.routines.some((item) => item.first === 'Reading'), false);
  assert.equal(reloaded.warning(), '');
});

test('removing a finished goal does not shrink growth', () => {
  const { store } = harness();
  store.load();
  store.completeGoal('goal-hello');
  store.removeGoal('goal-hello');
  const saved = store.snapshot();
  assert.equal(saved.goals.some((goal) => goal.id === 'goal-hello'), false);
  assert.equal(saved.growth.stage, 1);
  assert.equal(saved.growth.goalsCompleted, 1);
  store.completeGoal('goal-hello');
  assert.equal(store.snapshot().growth.goalsCompleted, 1);
});

test('a broken save is left in place', () => {
  const storage = memoryStorage();
  storage.setItem(STORAGE_KEY, '{not json');
  const store = createStore(storage, { now: () => 10, id: (prefix) => prefix });
  const loaded = store.load();
  assert.equal(loaded.growth.goalsCompleted, 0);
  assert.match(store.warning(), /left in place/);
  assert.equal(storage.getItem(STORAGE_KEY), '{not json');
});
