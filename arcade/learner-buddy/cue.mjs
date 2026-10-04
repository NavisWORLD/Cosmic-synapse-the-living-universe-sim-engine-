/**
 * Soft Muse cue. Imports arcade/lost-cosmos/muse.mjs and does not modify it.
 * Band samples never leave the headset helpers. This module only sees traits.
 */

import { mockTraits } from '../lost-cosmos/muse.mjs';

export const TRAIT_SCHEMA = 'cosmic-muse-traits-v1';

function clampTrait(value) {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function withSchema(traits, source) {
  return {
    schema: TRAIT_SCHEMA,
    focus: clampTrait(traits?.focus),
    calm: clampTrait(traits?.calm),
    spark: clampTrait(traits?.spark),
    source,
  };
}

export function simulatedTraits() {
  return withSchema(mockTraits(), 'simulated');
}

/**
 * A real headset connection is allowed only after an explicit parent consent flag.
 * Simulated traits do not need that flag.
 */
export function realConnectionAllowed(consent) {
  return consent === true;
}

/**
 * Quiet when calm is at least as strong as the average of focus and spark.
 * Both cues are descriptive. Neither is a grade or a fail state.
 */
export function softCue(traits) {
  const calm = clampTrait(traits?.calm);
  const awake = Math.round((clampTrait(traits?.focus) + clampTrait(traits?.spark)) / 2);
  if (calm >= awake) return { cue: 'quiet', label: 'Quiet and steady' };
  return { cue: 'bright', label: 'Bright and ready' };
}
