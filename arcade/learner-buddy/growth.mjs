/**
 * Gentle growth. Completing a goal can move the beast forward.
 * Nothing in this module reduces a stage or a completion count.
 */

export const STAGES = [
  { stage: 0, name: 'Seed', minGoals: 0 },
  { stage: 1, name: 'Sprout', minGoals: 1 },
  { stage: 2, name: 'Buddy', minGoals: 3 },
  { stage: 3, name: 'Companion', minGoals: 6 },
  { stage: 4, name: 'Keeper', minGoals: 10 },
];

export function emptyGrowth() {
  return { stage: 0, goalsCompleted: 0 };
}

export function stageName(stage) {
  return STAGES.find((item) => item.stage === stage)?.name || STAGES[0].name;
}

function whole(value) {
  const number = Math.floor(Number(value) || 0);
  return number > 0 ? number : 0;
}

export function stageForCount(count) {
  const goals = whole(count);
  let found = STAGES[0];
  for (const stage of STAGES) {
    if (goals >= stage.minGoals) found = stage;
  }
  return found;
}

function clampStage(stage) {
  const number = Math.floor(Number(stage) || 0);
  if (number < 0) return 0;
  if (number > STAGES[STAGES.length - 1].stage) return STAGES[STAGES.length - 1].stage;
  return number;
}

/**
 * Raise the high-water mark to at least `completedCount`.
 * A lower count leaves both fields where they are.
 */
export function reconcile(growth, completedCount) {
  const currentGoals = whole(growth?.goalsCompleted);
  const currentStage = clampStage(growth?.stage);
  const goalsCompleted = Math.max(currentGoals, whole(completedCount));
  const stage = Math.max(currentStage, stageForCount(goalsCompleted).stage);
  return {
    stage,
    goalsCompleted,
    grew: stage > currentStage,
    stageName: stageName(stage),
  };
}

export function advance(growth) {
  const currentGoals = whole(growth?.goalsCompleted);
  return reconcile(growth, currentGoals + 1);
}
