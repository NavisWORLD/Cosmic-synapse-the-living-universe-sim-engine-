import assert from 'node:assert/strict';
import test from 'node:test';

import { advance, emptyGrowth, reconcile, stageForCount } from './growth.mjs';

test('stage follows goals and never skips backward inside a threshold', () => {
  assert.equal(stageForCount(0).name, 'Seed');
  assert.equal(stageForCount(1).name, 'Sprout');
  assert.equal(stageForCount(2).stage, 1);
  assert.equal(stageForCount(3).name, 'Buddy');
  assert.equal(stageForCount(5).stage, 2);
  assert.equal(stageForCount(6).name, 'Companion');
  assert.equal(stageForCount(9).stage, 3);
  assert.equal(stageForCount(10).name, 'Keeper');
  assert.equal(stageForCount(40).stage, 4);
  assert.equal(stageForCount(-4).stage, 0);
});

test('each completion advances the high-water mark and does not mutate the previous growth', () => {
  const start = emptyGrowth();
  const sprout = advance(start);
  assert.deepEqual(start, { stage: 0, goalsCompleted: 0 });
  assert.equal(sprout.stage, 1);
  assert.equal(sprout.goalsCompleted, 1);
  assert.equal(sprout.grew, true);
  assert.equal(sprout.stageName, 'Sprout');

  const still = advance(sprout);
  assert.equal(still.stage, 1);
  assert.equal(still.goalsCompleted, 2);
  assert.equal(still.grew, false);

  const buddy = advance(still);
  assert.equal(buddy.stage, 2);
  assert.equal(buddy.stageName, 'Buddy');
});

test('the last stage stays put while completions continue', () => {
  let growth = { stage: 4, goalsCompleted: 10 };
  growth = advance(growth);
  assert.equal(growth.stage, 4);
  assert.equal(growth.goalsCompleted, 11);
  assert.equal(growth.grew, false);
  assert.equal(growth.stageName, 'Keeper');
});

test('a lower count does not shrink stage or completions', () => {
  const keeper = { stage: 4, goalsCompleted: 10 };
  const kept = reconcile(keeper, 0);
  assert.equal(kept.stage, 4);
  assert.equal(kept.goalsCompleted, 10);
  assert.equal(kept.grew, false);

  const caughtUp = reconcile({ stage: 0, goalsCompleted: 0 }, 6);
  assert.equal(caughtUp.stage, 3);
  assert.equal(caughtUp.goalsCompleted, 6);
  assert.equal(caughtUp.grew, true);
  assert.equal(caughtUp.stageName, 'Companion');

  const afterDelete = reconcile(advance(emptyGrowth()), -8);
  assert.equal(afterDelete.stage, 1);
  assert.equal(afterDelete.goalsCompleted, 1);
});
