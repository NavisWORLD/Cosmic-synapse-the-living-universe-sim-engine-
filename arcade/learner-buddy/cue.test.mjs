import assert from 'node:assert/strict';
import test from 'node:test';

import { TRAIT_SCHEMA, realConnectionAllowed, simulatedTraits, softCue, withSchema } from './cue.mjs';

test('simulated traits use the shared Muse schema and stay in range', () => {
  const traits = simulatedTraits();
  assert.equal(traits.schema, TRAIT_SCHEMA);
  assert.equal(traits.schema, 'cosmic-muse-traits-v1');
  assert.equal(traits.source, 'simulated');
  for (const key of ['focus', 'calm', 'spark']) {
    assert.equal(Number.isInteger(traits[key]), true);
    assert.equal(traits[key] >= 0 && traits[key] <= 100, true);
  }
  assert.equal(traits.samples, undefined);
  const cue = softCue(traits);
  assert.equal(cue.cue, 'quiet');
  assert.equal(cue.label, 'Quiet and steady');
  assert.match(`${cue.cue} ${cue.label}`, /quiet|steady/i);
  assert.doesNotMatch(`${cue.cue} ${cue.label}`, /fail|score|bad|wrong/i);
});

test('the cue is a soft description and a headset needs consent', () => {
  assert.deepEqual(softCue({ focus: 80, calm: 10, spark: 40 }), { cue: 'bright', label: 'Bright and ready' });
  assert.equal(softCue({ focus: 40, calm: 40, spark: 40 }).cue, 'quiet');
  assert.equal(softCue({ focus: Number.NaN, calm: 0, spark: 80 }).cue, 'bright');
  assert.equal(realConnectionAllowed(true), true);
  assert.equal(realConnectionAllowed(false), false);
  assert.equal(realConnectionAllowed('yes'), false);
  const wrapped = withSchema({ focus: 140, calm: -4, spark: 12.2 }, 'headset');
  assert.deepEqual(wrapped, { schema: TRAIT_SCHEMA, focus: 100, calm: 0, spark: 12, source: 'headset' });
});
