/**
 * Local-only Learner Buddy document.
 * Schema learner-buddy-v1. Stored in the provided storage (localStorage in the page).
 * Raw EEG is not a field. Import drops anything that is not part of the schema.
 */

import { advance, emptyGrowth, stageForCount } from './growth.mjs';
import {
  ACTIVITY_IDS, CALM, PICK, addEvent, emptyPreferences,
} from './preferences.mjs';

export const SCHEMA = 'learner-buddy-v1';
export const VERSION = 1;
export const STORAGE_KEY = 'learner-buddy-v1';
export const LOG_LIMIT = 200;
export const FEELING_LIMIT = 100;
export const EVENT_LIMIT = 400;
export const ROUTINE_LIMIT = 12;
export const GOAL_LIMIT = 40;

export const FEELINGS = [
  { id: 'calm', label: 'Calm' },
  { id: 'glad', label: 'Glad' },
  { id: 'wiggly', label: 'Wiggly' },
  { id: 'tired', label: 'Tired' },
  { id: 'unsure', label: 'Unsure' },
  { id: 'proud', label: 'Proud' },
  { id: 'break', label: 'Need a break' },
];

export const FEELING_IDS = FEELINGS.map((item) => item.id);
export const ROUTINE_ICONS = ['moon', 'sun', 'cup', 'tree', 'heart', 'star', 'book', 'home'];

const LOG_DETAIL_KEYS = ['activity', 'feeling', 'goalId', 'label', 'stage', 'grew', 'routineId'];

export class StoreError extends Error {
  constructor(message) {
    super(message);
    this.name = 'StoreError';
  }
}

export function feelingLabel(id) {
  return FEELINGS.find((item) => item.id === id)?.label || id;
}

export function memoryStorage() {
  const items = new Map();
  return {
    getItem: (key) => (items.has(key) ? items.get(key) : null),
    setItem: (key, value) => items.set(key, String(value)),
    removeItem: (key) => items.delete(key),
  };
}

export function defaultRoutines() {
  return [
    { id: 'routine-quiet', first: 'Quiet time', then: 'A snack', icon: 'moon' },
    { id: 'routine-dress', first: 'Get dressed', then: 'Go outside', icon: 'sun' },
  ];
}

export function defaultGoals() {
  return [{ id: 'goal-hello', label: 'Say hello to Mote', done: false, completedAt: null }];
}

export function emptyState(now = 0) {
  return {
    schema: SCHEMA,
    version: VERSION,
    updatedAt: now,
    buddyName: 'Mote',
    growth: emptyGrowth(),
    preferences: emptyPreferences(),
    routines: defaultRoutines(),
    feelings: [],
    log: [],
    goals: defaultGoals(),
    settings: {
      lowSensory: false,
      volume: 0.35,
      brightness: 1,
      museConsent: false,
    },
  };
}

function cleanName(value) {
  if (typeof value !== 'string') throw new StoreError('Buddy name must be text');
  const name = value.trim().slice(0, 24);
  return name || 'Mote';
}

function cleanText(value, label, max = 80) {
  if (typeof value !== 'string') throw new StoreError(`${label} must be text`);
  const text = value.trim().slice(0, max);
  if (!text) throw new StoreError(`${label} is empty`);
  return text;
}

function cleanSettings(settings) {
  if (!settings || typeof settings !== 'object' || Array.isArray(settings)) {
    throw new StoreError('Settings are missing');
  }
  for (const key of ['lowSensory', 'museConsent']) {
    if (typeof settings[key] !== 'boolean') throw new StoreError(`Setting ${key} must be yes or no`);
  }
  if (typeof settings.volume !== 'number' || !Number.isFinite(settings.volume)) {
    throw new StoreError('Volume must be a number');
  }
  if (typeof settings.brightness !== 'number' || !Number.isFinite(settings.brightness)) {
    throw new StoreError('Brightness must be a number');
  }
  return {
    lowSensory: settings.lowSensory,
    volume: Math.max(0, Math.min(1, settings.volume)),
    brightness: Math.max(0.8, Math.min(1.15, settings.brightness)),
    museConsent: settings.museConsent,
  };
}

function cleanDetail(detail) {
  if (!detail || typeof detail !== 'object' || Array.isArray(detail)) {
    throw new StoreError('Log detail is missing');
  }
  const copy = {};
  for (const key of LOG_DETAIL_KEYS) {
    if (!(key in detail)) continue;
    const value = detail[key];
    if (typeof value === 'string') copy[key] = value.slice(0, 80);
    else if (typeof value === 'number' && Number.isFinite(value)) copy[key] = value;
    else if (typeof value === 'boolean') copy[key] = value;
  }
  return copy;
}

export function normalize(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new StoreError('Export must be an object');
  if (data.schema !== SCHEMA) throw new StoreError('Schema name does not match');
  if (data.version !== VERSION) throw new StoreError('Schema version does not match');
  if (data.updatedAt !== undefined && (typeof data.updatedAt !== 'number' || !Number.isFinite(data.updatedAt))) {
    throw new StoreError('Updated time is not valid');
  }
  if (!data.growth || typeof data.growth !== 'object') throw new StoreError('Growth is missing');
  const { stage, goalsCompleted } = data.growth;
  if (!Number.isInteger(stage) || stage < 0 || stage > 4) throw new StoreError('Growth stage is out of range');
  if (!Number.isInteger(goalsCompleted) || goalsCompleted < 0) throw new StoreError('Growth count is out of range');

  if (!data.preferences || !Array.isArray(data.preferences.events)) throw new StoreError('Preferences are missing');
  const events = data.preferences.events.slice(-EVENT_LIMIT).map((event) => {
    if (!event || !ACTIVITY_IDS.includes(event.id) || (event.kind !== PICK && event.kind !== CALM) || !Number.isFinite(event.at)) {
      throw new StoreError('A preference event is not valid');
    }
    return { id: event.id, kind: event.kind, at: event.at };
  });

  if (!Array.isArray(data.routines)) throw new StoreError('Routines are missing');
  const routines = data.routines.slice(0, ROUTINE_LIMIT).map((item) => {
    if (!item || typeof item.id !== 'string' || !item.id) throw new StoreError('A routine is missing an id');
    const icon = ROUTINE_ICONS.includes(item.icon) ? item.icon : 'moon';
    return {
      id: item.id.slice(0, 40),
      first: cleanText(item.first, 'Routine first'),
      then: cleanText(item.then, 'Routine then'),
      icon,
    };
  });

  if (!Array.isArray(data.feelings)) throw new StoreError('Feelings are missing');
  const feelings = data.feelings.slice(0, FEELING_LIMIT).map((item) => {
    if (!item || typeof item.id !== 'string' || !FEELING_IDS.includes(item.feeling) || !Number.isFinite(item.at)) {
      throw new StoreError('A feeling entry is not valid');
    }
    return { id: item.id.slice(0, 40), feeling: item.feeling, at: item.at };
  });

  if (!Array.isArray(data.log)) throw new StoreError('Log is missing');
  const log = data.log.slice(0, LOG_LIMIT).map((item) => {
    if (!item || typeof item.id !== 'string' || typeof item.kind !== 'string' || !Number.isFinite(item.at)) {
      throw new StoreError('A log entry is not valid');
    }
    return { id: item.id.slice(0, 40), at: item.at, kind: item.kind.slice(0, 40), detail: cleanDetail(item.detail) };
  });

  if (!Array.isArray(data.goals)) throw new StoreError('Goals are missing');
  const goals = data.goals.slice(0, GOAL_LIMIT).map((item) => {
    if (!item || typeof item.id !== 'string' || !item.id || typeof item.done !== 'boolean') {
      throw new StoreError('A goal is not valid');
    }
    if (item.completedAt !== null && !Number.isFinite(item.completedAt)) throw new StoreError('A goal time is not valid');
    return {
      id: item.id.slice(0, 40),
      label: cleanText(item.label, 'Goal'),
      done: item.done,
      completedAt: item.done ? item.completedAt : null,
    };
  });

  return {
    schema: SCHEMA,
    version: VERSION,
    updatedAt: typeof data.updatedAt === 'number' ? data.updatedAt : 0,
    buddyName: cleanName(data.buddyName),
    growth: {
      stage: Math.max(stage, stageForCount(goalsCompleted).stage),
      goalsCompleted,
    },
    preferences: { events },
    routines,
    feelings,
    log,
    goals,
    settings: cleanSettings(data.settings),
  };
}

function defaultId(prefix) {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export function createStore(storage, options = {}) {
  const key = options.key || STORAGE_KEY;
  const now = options.now || (() => Date.now());
  const id = options.id || defaultId;
  let state = emptyState(typeof options.now === 'function' ? now() : 0);
  let warning = '';

  function snapshot() {
    return structuredClone(state);
  }

  function persist() {
    state = { ...state, updatedAt: now() };
    storage.setItem(key, JSON.stringify(state));
    warning = '';
  }

  function withLog(kind, detail) {
    const entry = { id: id('log'), at: now(), kind, detail: cleanDetail(detail) };
    return [entry, ...state.log].slice(0, LOG_LIMIT);
  }

  return {
    load() {
      const raw = storage.getItem(key);
      if (!raw) {
        state = emptyState(now());
        warning = '';
        return snapshot();
      }
      try {
        state = normalize(JSON.parse(raw));
        warning = '';
      } catch {
        state = emptyState(now());
        warning = 'Saved data could not be read. It was left in place.';
      }
      return snapshot();
    },
    warning() {
      return warning;
    },
    snapshot,
    exportJson() {
      return JSON.stringify(state, null, 2);
    },
    importJson(text) {
      let parsed = text;
      if (typeof text === 'string') {
        try {
          parsed = JSON.parse(text);
        } catch {
          throw new StoreError('Export is not valid JSON');
        }
      }
      state = normalize(parsed);
      persist();
      return snapshot();
    },
    deleteAll() {
      storage.removeItem(key);
      state = emptyState(now());
      warning = '';
      return snapshot();
    },
    pickActivity(activityId) {
      const preferences = { events: addEvent(state.preferences, activityId, PICK, now()).events.slice(-EVENT_LIMIT) };
      state = { ...state, preferences, log: withLog('pick', { activity: activityId }) };
      persist();
      return snapshot();
    },
    markCalming(activityId) {
      const preferences = { events: addEvent(state.preferences, activityId, CALM, now()).events.slice(-EVENT_LIMIT) };
      state = { ...state, preferences, log: withLog('calm', { activity: activityId }) };
      persist();
      return snapshot();
    },
    addFeeling(feeling) {
      if (!FEELING_IDS.includes(feeling)) throw new StoreError('Unknown feeling');
      const entry = { id: id('feeling'), feeling, at: now() };
      state = {
        ...state,
        feelings: [entry, ...state.feelings].slice(0, FEELING_LIMIT),
        log: withLog('feeling', { feeling }),
      };
      persist();
      return snapshot();
    },
    visitCalmCorner() {
      state = { ...state, log: withLog('calm-corner', {}) };
      persist();
      return snapshot();
    },
    noteRoutine(routineId) {
      state = { ...state, log: withLog('routine', { routineId: String(routineId || '').slice(0, 40) }) };
      persist();
      return snapshot();
    },
    completeGoal(goalId) {
      const goal = state.goals.find((item) => item.id === goalId);
      if (!goal || goal.done) return snapshot();
      const grown = advance(state.growth);
      const goals = state.goals.map((item) => (
        item.id === goalId ? { ...item, done: true, completedAt: now() } : item
      ));
      state = {
        ...state,
        goals,
        growth: { stage: grown.stage, goalsCompleted: grown.goalsCompleted },
        log: withLog('goal', { goalId, label: goal.label, stage: grown.stage, grew: grown.grew }),
      };
      persist();
      return snapshot();
    },
    addGoal(label) {
      const goal = { id: id('goal'), label: cleanText(label, 'Goal'), done: false, completedAt: null };
      state = { ...state, goals: state.goals.concat(goal).slice(0, GOAL_LIMIT) };
      persist();
      return snapshot();
    },
    removeGoal(goalId) {
      state = { ...state, goals: state.goals.filter((item) => item.id !== goalId) };
      persist();
      return snapshot();
    },
    setRoutines(routines) {
      state = { ...state, routines: normalize({ ...state, routines }).routines };
      persist();
      return snapshot();
    },
    addRoutine({ first, then, icon }) {
      const routine = {
        id: id('routine').slice(0, 40),
        first: cleanText(first, 'Routine first'),
        then: cleanText(then, 'Routine then'),
        icon: ROUTINE_ICONS.includes(icon) ? icon : 'moon',
      };
      state = { ...state, routines: state.routines.concat(routine).slice(0, ROUTINE_LIMIT) };
      persist();
      return snapshot();
    },
    updateRoutine(routineId, patch) {
      const routines = state.routines.map((item) => {
        if (item.id !== routineId) return item;
        return {
          ...item,
          first: cleanText(patch.first ?? item.first, 'Routine first'),
          then: cleanText(patch.then ?? item.then, 'Routine then'),
          icon: ROUTINE_ICONS.includes(patch.icon) ? patch.icon : item.icon,
        };
      });
      state = { ...state, routines };
      persist();
      return snapshot();
    },
    removeRoutine(routineId) {
      state = { ...state, routines: state.routines.filter((item) => item.id !== routineId) };
      persist();
      return snapshot();
    },
    updateSettings(partial) {
      state = { ...state, settings: cleanSettings({ ...state.settings, ...partial }) };
      persist();
      return snapshot();
    },
    setBuddyName(name) {
      state = { ...state, buddyName: cleanName(name) };
      persist();
      return snapshot();
    },
  };
}
