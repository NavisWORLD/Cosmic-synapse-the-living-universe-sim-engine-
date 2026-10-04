/**
 * Learner Buddy page. All reads and writes stay in localStorage.
 * Muse traits are imported from arcade/lost-cosmos/muse.mjs and are not saved.
 */

import { MuseLink } from '../lost-cosmos/muse.mjs';
import { realConnectionAllowed, simulatedTraits, softCue, withSchema } from './cue.mjs';
import { stageName } from './growth.mjs';
import { activityLabel, suggest } from './preferences.mjs';
import {
  FEELINGS, ROUTINE_ICONS, STORAGE_KEY, createStore, feelingLabel, memoryStorage,
} from './store.mjs';

const VIEWS = ['home', 'activity', 'calm', 'routine', 'feelings', 'goals', 'gate', 'parent'];
const SVG_NS = 'http://www.w3.org/2000/svg';

const el = (id) => {
  const node = document.getElementById(id);
  if (!node) throw new Error(`Missing #${id}`);
  return node;
};

const storage = browserStorage();
const store = createStore(storage);
const sound = createSound();
const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

let currentActivity = 'breathe';
let selectedRoutineId = '';
let routineMarked = false;
let gateAnswer = 4;
let liveTraits = simulatedTraits();
let link = null;
let connecting = false;
let announced = false;
let lastCue = '';
let pendingCue = '';
let pendingCount = 0;
let spinFrame = 0;
let spinAngle = 0;
let spinVelocity = 0;
let spinning = false;
let flowFrame = 0;
let flowing = false;
let hue = 150;
let breathTimer = 0;
let breathIn = true;
let rhythmTimer = 0;
let rhythmOn = false;

function browserStorage() {
  try {
    const probe = `${STORAGE_KEY}-probe`;
    localStorage.setItem(probe, '1');
    localStorage.removeItem(probe);
    return localStorage;
  } catch {
    return memoryStorage();
  }
}

function createSound() {
  let ctx = null;
  let master = null;
  let volume = 0.35;
  let lowSensory = false;
  const outputGain = () => (volume <= 0 ? 0 : (lowSensory ? Math.min(volume, 0.12) : volume));
  return {
    setVolume(value) { volume = value; this.apply(); },
    setLowSensory(value) { lowSensory = value; this.apply(); },
    apply() {
      if (!master || !ctx) return;
      master.gain.setTargetAtTime(outputGain(), ctx.currentTime, 0.25);
    },
    async resume() {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      if (!ctx) {
        ctx = new AudioContext();
        master = ctx.createGain();
        master.gain.value = 0;
        master.connect(ctx.destination);
      }
      if (ctx.state === 'suspended') await ctx.resume();
      this.apply();
    },
    tone(freq, seconds = 0.5) {
      if (!ctx || outputGain() <= 0) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const start = ctx.currentTime;
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, start);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(0.22, start + 0.09);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + seconds);
      osc.connect(gain);
      gain.connect(master);
      osc.start(start);
      osc.stop(start + seconds + 0.03);
    },
  };
}

function allowMotion(settings = store.snapshot().settings) {
  return !settings.lowSensory && !motionQuery.matches;
}

function say(message) {
  el('status').textContent = message;
}

function show(name, { focus = true } = {}) {
  stopEffects();
  document.body.dataset.view = name;
  for (const view of VIEWS) el(`view-${view}`).hidden = view !== name;
  if (name === 'home') renderHome();
  if (name === 'goals') renderGoals();
  if (name === 'routine') renderRoutine();
  if (name === 'parent') renderParent();
  if (name === 'activity') renderActivity();
  const heading = document.querySelector(`#view-${name} h2`);
  if (focus && heading) heading.focus();
}

function applySensory(settings, { writeControls = false } = {}) {
  document.body.classList.toggle('low-sensory', settings.lowSensory);
  document.documentElement.classList.toggle('still', !allowMotion(settings));
  document.documentElement.style.setProperty('--brightness', String(settings.brightness));
  el('low-sensory-banner').hidden = !settings.lowSensory;
  el('low-sensory').setAttribute('aria-pressed', String(settings.lowSensory));
  sound.setVolume(settings.volume);
  sound.setLowSensory(settings.lowSensory);
  if (writeControls) {
    el('volume').value = String(Math.round(settings.volume * 100));
    el('brightness').value = String(Math.round(settings.brightness * 100));
  }
}

function renderCue() {
  const cue = softCue(liveTraits);
  const hint = liveTraits.source === 'headset'
    ? 'A soft hint from the headset, not a test.'
    : 'A simulated soft signal, not a test.';
  const line = `${cue.label}. ${hint}`;
  if (!announced) {
    announced = true;
    lastCue = cue.cue;
    el('buddy-cue').textContent = line;
  } else if (cue.cue === lastCue) {
    pendingCue = '';
    pendingCount = 0;
    el('buddy-cue').textContent = line;
  } else if (pendingCue === cue.cue) {
    pendingCount += 1;
    if (pendingCount >= 2) {
      lastCue = cue.cue;
      el('buddy-cue').textContent = line;
    }
  } else {
    pendingCue = cue.cue;
    pendingCount = 1;
  }
  el('muse-source').textContent = liveTraits.source === 'headset'
    ? 'Headset soft signal. Not a reading of a person.'
    : 'Simulated soft signal. Not a reading of a person.';
  el('muse-traits').textContent = `Focus ${liveTraits.focus} · Calm ${liveTraits.calm} · Spark ${liveTraits.spark}. These numbers are a noisy hint, not a grade.`;
}

function useSimulated() {
  liveTraits = simulatedTraits();
  announced = false;
  renderCue();
}

function paintBeasts(state) {
  const stage = state.growth.stage;
  for (const beast of document.querySelectorAll('.beast')) {
    beast.dataset.stage = String(stage);
    beast.style.setProperty('--stage', String(stage));
  }
  for (const label of document.querySelectorAll('.stage-label')) label.textContent = stageName(stage);
  el('buddy-name').textContent = state.buddyName;
  const finished = state.growth.goalsCompleted;
  el('growth-line').textContent = `${state.buddyName} is a ${stageName(stage)}. ${finished} ${finished === 1 ? 'goal' : 'goals'} finished. ${state.buddyName} only grows.`;
  document.title = `${state.buddyName} · Learner Buddy`;
}

function renderHome() {
  const state = store.snapshot();
  paintBeasts(state);
  const ranked = suggest(state.preferences, Date.now());
  const top = ranked[0];
  const open = el('suggestion-open');
  if (top && top.score > 0) {
    el('suggestion').textContent = `A favorite lately: ${activityLabel(top.id)}.`;
    open.hidden = false;
    open.textContent = `Open ${activityLabel(top.id)}`;
    open.dataset.activity = top.id;
  } else {
    el('suggestion').textContent = 'You can try any of these. There is nothing to get wrong.';
    open.hidden = true;
  }
  const preview = el('goal-preview');
  preview.replaceChildren();
  const kicker = document.createElement('p');
  kicker.className = 'kicker';
  kicker.textContent = 'A goal';
  const task = document.createElement('p');
  task.className = 'task';
  const next = state.goals.find((goal) => !goal.done);
  if (!next) {
    task.textContent = 'You can add a goal when you want. Mote will wait.';
    preview.append(kicker, task);
    return;
  }
  task.textContent = next.label;
  const done = document.createElement('button');
  done.type = 'button';
  done.className = 'big primary';
  done.textContent = 'I did this';
  done.addEventListener('click', () => finishGoal(next.id));
  preview.append(kicker, task, done);
}

function finishGoal(id) {
  const before = store.snapshot().growth.stage;
  const name = store.snapshot().buddyName;
  store.completeGoal(id);
  const after = store.snapshot();
  renderHome();
  if (!el('view-goals').hidden) renderGoals();
  if (after.growth.stage > before) say(`${name} grew into a ${stageName(after.growth.stage)}. ${name} only grows.`);
  else say('You finished a goal. Thank you for telling me.');
}

function renderGoals() {
  const list = el('goal-list');
  list.replaceChildren();
  const state = store.snapshot();
  if (state.goals.length === 0) {
    const item = document.createElement('li');
    item.textContent = 'No goals yet.';
    list.append(item);
    return;
  }
  for (const goal of state.goals) {
    const item = document.createElement('li');
    const name = document.createElement('span');
    name.textContent = goal.done ? `${goal.label} — finished` : goal.label;
    item.append(name);
    if (!goal.done) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = 'I did this';
      button.addEventListener('click', () => finishGoal(goal.id));
      item.append(document.createTextNode(' '), button);
    }
    list.append(item);
  }
}

function iconSvg(name) {
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', '0 0 64 64');
  svg.setAttribute('aria-hidden', 'true');
  const add = (tag, attrs) => {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    svg.append(node);
  };
  if (name === 'sun') {
    add('circle', { cx: '32', cy: '32', r: '12' });
    add('path', { d: 'M32 8v8M32 48v8M8 32h8M48 32h8M14 14l6 6M44 44l6 6M50 14l-6 6M20 44l-6 6', fill: 'none', stroke: 'currentColor', 'stroke-width': '4', 'stroke-linecap': 'round' });
  } else if (name === 'cup') {
    add('path', { d: 'M16 18h28v16a14 14 0 0 1-28 0V18z' });
    add('path', { d: 'M44 22h6a8 8 0 0 1 0 16h-6', fill: 'none', stroke: 'currentColor', 'stroke-width': '4' });
  } else if (name === 'tree') {
    add('circle', { cx: '32', cy: '24', r: '14' });
    add('rect', { x: '28', y: '34', width: '8', height: '18', rx: '2' });
  } else if (name === 'heart') {
    add('path', { d: 'M32 52 12 32a12 12 0 0 1 18-16l2 2 2-2a12 12 0 0 1 18 16z' });
  } else if (name === 'star') {
    add('path', { d: 'M32 8l6 14h16l-12 10 4 16-14-8-14 8 4-16L10 22h16z' });
  } else if (name === 'book') {
    add('path', { d: 'M10 14h20v38H14a4 4 0 0 1-4-4V14zm24 0h20v34a4 4 0 0 1-4 4H34V14z' });
  } else if (name === 'home') {
    add('path', { d: 'M8 30 32 10l24 20v24H36V38H28v16H8V30z' });
  } else {
    add('path', { d: 'M40 12a18 18 0 1 0 8 30 14 14 0 1 1-8-30z' });
  }
  return svg;
}

function renderRoutine() {
  const state = store.snapshot();
  const choices = el('routine-choices');
  const board = el('routine-board');
  choices.replaceChildren();
  board.replaceChildren();
  if (!state.routines.some((item) => item.id === selectedRoutineId)) {
    selectedRoutineId = state.routines[0]?.id || '';
    routineMarked = false;
  }
  el('routine-empty').hidden = state.routines.length > 0;
  el('routine-finished').hidden = state.routines.length === 0;
  for (const routine of state.routines) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = routine.first;
    button.setAttribute('aria-pressed', String(routine.id === selectedRoutineId));
    button.addEventListener('click', () => {
      selectedRoutineId = routine.id;
      routineMarked = false;
      renderRoutine();
    });
    choices.append(button);
  }
  const routine = state.routines.find((item) => item.id === selectedRoutineId);
  if (!routine) return;
  board.append(stepCard('First', routine.first, routine.icon, routineMarked), bridge(), stepCard('Then', routine.then, 'heart', false));
  const finished = el('routine-finished');
  finished.textContent = routineMarked ? 'Start this card again' : 'I finished the first part';
}

function stepCard(kicker, text, icon, done) {
  const card = document.createElement('article');
  card.className = done ? 'card step done' : 'card step';
  const label = document.createElement('p');
  label.className = 'kicker';
  label.textContent = done ? `${kicker} · done` : kicker;
  const picture = document.createElement('div');
  picture.className = 'icon';
  picture.append(iconSvg(icon));
  const task = document.createElement('p');
  task.className = 'task';
  task.textContent = text;
  card.append(label, picture, task);
  return card;
}

function bridge() {
  const node = document.createElement('p');
  node.className = 'bridge';
  node.textContent = 'then';
  return node;
}

function renderActivity() {
  const id = currentActivity;
  el('activity-title').textContent = activityLabel(id);
  for (const panel of ['breathe', 'flow', 'fidget', 'bubbles', 'rhythm']) {
    el(`panel-${panel}`).hidden = panel !== id;
  }
}

function sentence(entry) {
  const when = new Date(entry.at).toLocaleString();
  if (entry.kind === 'pick') return `${when} — Chose ${activityLabel(entry.detail.activity)}`;
  if (entry.kind === 'calm') return `${when} — Marked ${activityLabel(entry.detail.activity)} as calming`;
  if (entry.kind === 'feeling') return `${when} — Feeling: ${feelingLabel(entry.detail.feeling)}`;
  if (entry.kind === 'calm-corner') return `${when} — Visited the calm corner`;
  if (entry.kind === 'goal') return `${when} — Finished a goal: ${entry.detail.label || 'a goal'}`;
  if (entry.kind === 'routine') return `${when} — Finished the first part of a routine`;
  return `${when} — ${entry.kind}`;
}

function fillList(id, items, empty) {
  const list = el(id);
  list.replaceChildren();
  if (items.length === 0) {
    const item = document.createElement('li');
    item.textContent = empty;
    list.append(item);
    return;
  }
  for (const text of items) {
    const item = document.createElement('li');
    item.textContent = text;
    list.append(item);
  }
}

function renderParent() {
  const state = store.snapshot();
  el('buddy-name-input').value = state.buddyName;
  el('muse-consent').checked = state.settings.museConsent;
  el('muse-connect').disabled = !realConnectionAllowed(state.settings.museConsent) || connecting;
  const counts = new Map();
  for (const event of state.preferences.events) {
    if (event.kind !== 'calm') continue;
    counts.set(event.id, (counts.get(event.id) || 0) + 1);
  }
  const helped = [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([id, count]) => `${activityLabel(id)} — marked calming ${count} ${count === 1 ? 'time' : 'times'}`);
  fillList('what-helped', helped, 'No calming marks yet.');
  fillList('activity-log', state.log.map(sentence), 'No visits yet.');
  fillList('feelings-history', state.feelings.map((item) => `${new Date(item.at).toLocaleString()} — ${feelingLabel(item.feeling)}`), 'No check-ins yet.');
  const goals = el('parent-goals');
  goals.replaceChildren();
  for (const goal of state.goals) {
    const item = document.createElement('li');
    item.textContent = goal.done ? `${goal.label} — finished` : goal.label;
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.textContent = 'Remove';
    remove.addEventListener('click', () => {
      store.removeGoal(goal.id);
      renderParent();
      renderHome();
    });
    item.append(document.createTextNode(' '), remove);
    goals.append(item);
  }
  if (state.goals.length === 0) {
    const item = document.createElement('li');
    item.textContent = 'No goals yet.';
    goals.append(item);
  }
  const editor = el('routine-editor');
  editor.replaceChildren();
  for (const routine of state.routines) editor.append(routineRow(routine));
  renderCue();
}

function routineRow(routine) {
  const row = document.createElement('div');
  row.className = 'editor-row';
  const first = field('First', routine.first);
  const then = field('Then', routine.then);
  const iconLabel = document.createElement('label');
  iconLabel.className = 'field';
  iconLabel.append(document.createTextNode('Picture'));
  const icon = document.createElement('select');
  for (const name of ROUTINE_ICONS) {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
    option.selected = name === routine.icon;
    icon.append(option);
  }
  iconLabel.append(icon);
  const remove = document.createElement('button');
  remove.type = 'button';
  remove.textContent = 'Remove';
  const commit = () => {
    try {
      store.updateRoutine(routine.id, { first: first.querySelector('input').value, then: then.querySelector('input').value, icon: icon.value });
      say('Routine saved on this device.');
    } catch (error) {
      say(error.message);
    }
  };
  first.querySelector('input').addEventListener('change', commit);
  then.querySelector('input').addEventListener('change', commit);
  icon.addEventListener('change', commit);
  remove.addEventListener('click', () => {
    if (selectedRoutineId === routine.id) selectedRoutineId = '';
    store.removeRoutine(routine.id);
    renderParent();
  });
  row.append(first, then, iconLabel, remove);
  return row;
}

function field(label, value) {
  const wrap = document.createElement('label');
  wrap.className = 'field';
  wrap.append(document.createTextNode(label));
  const input = document.createElement('input');
  input.type = 'text';
  input.maxLength = 80;
  input.value = value;
  input.autocomplete = 'off';
  wrap.append(input);
  return wrap;
}

function stopEffects() {
  spinning = false;
  flowing = false;
  rhythmOn = false;
  if (spinFrame) cancelAnimationFrame(spinFrame);
  if (flowFrame) cancelAnimationFrame(flowFrame);
  if (breathTimer) clearInterval(breathTimer);
  if (rhythmTimer) clearInterval(rhythmTimer);
  spinFrame = 0;
  flowFrame = 0;
  breathTimer = 0;
  rhythmTimer = 0;
  el('breath-circle').classList.remove('auto');
  el('calm-circle').classList.remove('auto');
  el('rhythm-toggle').setAttribute('aria-pressed', 'false');
  el('rhythm-toggle').textContent = 'Start soft sounds';
}

function openActivity(id) {
  store.pickActivity(id);
  currentActivity = id;
  show('activity');
  el('mark-calming').textContent = 'This feels calming';
  startActivity(id);
}

function startActivity(id) {
  stopEffects();
  renderActivity();
  if (id === 'breathe') startBreath();
  if (id === 'flow') startFlow();
  if (id === 'bubbles') startBubbles();
}

function startBreath() {
  const circle = el('breath-circle');
  const label = el('breath-label');
  const steps = el('breath-steps');
  if (!allowMotion()) {
    steps.hidden = false;
    label.textContent = 'You set the pace.';
    return;
  }
  steps.hidden = true;
  circle.classList.add('auto');
  breathIn = true;
  label.textContent = 'Breathe in';
  breathTimer = setInterval(() => {
    breathIn = !breathIn;
    label.textContent = breathIn ? 'Breathe in' : 'Breathe out';
  }, 4000);
}

function startFlow() {
  paintFlow();
  if (!allowMotion()) return;
  flowing = true;
  const loop = () => {
    if (!flowing) return;
    hue = (hue + 0.08) % 360;
    paintFlow();
    flowFrame = requestAnimationFrame(loop);
  };
  flowFrame = requestAnimationFrame(loop);
}

function paintFlow() {
  const sat = document.body.classList.contains('low-sensory') ? 10 : 38;
  el('flow').style.background = `linear-gradient(145deg, hsl(${hue} ${sat}% 78%), hsl(${(hue + 36) % 360} ${sat}% 88%))`;
}

function startBubbles() {
  const pond = el('bubbles');
  pond.replaceChildren();
  for (let i = 0; i < 5; i += 1) addBubble(pond);
}

function addBubble(pond) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'bubble';
  button.setAttribute('aria-label', 'Bubble');
  const size = 72 + Math.floor(Math.random() * 28);
  button.style.width = `${size}px`;
  button.style.height = `${size}px`;
  button.style.left = `${8 + Math.floor(Math.random() * 68)}%`;
  button.style.top = `${8 + Math.floor(Math.random() * 58)}%`;
  button.style.animationDelay = `${Math.random() * 4}s`;
  button.addEventListener('click', () => {
    button.remove();
    addBubble(pond);
  });
  pond.append(button);
}

function openCalm(message = 'You can stay as long as you like.') {
  store.visitCalmCorner();
  show('calm');
  if (allowMotion()) el('calm-circle').classList.add('auto');
  say(message);
}

function nextQuestion() {
  const left = 2 + Math.floor(Math.random() * 8);
  const right = 2 + Math.floor(Math.random() * 8);
  gateAnswer = left + right;
  el('gate-question').textContent = `What is ${left} + ${right}?`;
  el('gate-answer').value = '';
  el('gate-message').textContent = '';
}

async function stopHeadset() {
  const current = link;
  link = null;
  if (!current) return;
  try { await current.stop(); } catch { /* already stopped */ }
}

function mountBeasts() {
  const template = el('beast-template');
  for (const slot of document.querySelectorAll('[data-beast]')) {
    slot.replaceChildren(template.content.cloneNode(true));
  }
}

function bind() {
  el('need-break').addEventListener('click', openCalm);
  el('calm-back').addEventListener('click', () => show('home'));
  el('activity-back').addEventListener('click', () => show('home'));
  el('routine-back').addEventListener('click', () => show('home'));
  el('feelings-back').addEventListener('click', () => show('home'));
  el('goals-back').addEventListener('click', () => show('home'));
  el('gate-back').addEventListener('click', () => show('home'));
  el('parent-back').addEventListener('click', () => show('home'));
  el('open-feelings').addEventListener('click', () => show('feelings'));
  el('open-routine').addEventListener('click', () => show('routine'));
  el('open-goals').addEventListener('click', () => show('goals'));
  el('open-grownups').addEventListener('click', () => {
    nextQuestion();
    show('gate');
  });
  el('suggestion-open').addEventListener('click', () => openActivity(el('suggestion-open').dataset.activity));
  for (const button of document.querySelectorAll('[data-activity]')) {
    button.addEventListener('click', () => openActivity(button.dataset.activity));
  }
  for (const button of document.querySelectorAll('[data-feeling]')) {
    button.addEventListener('click', () => {
      const feeling = button.dataset.feeling;
      if (!FEELINGS.some((item) => item.id === feeling)) return;
      store.addFeeling(feeling);
      if (feeling === 'break') openCalm('Thank you for telling me. You can stay as long as you like.');
      else say('Thank you for telling me.');
    });
  }
  el('low-sensory').addEventListener('click', () => {
    const next = !store.snapshot().settings.lowSensory;
    store.updateSettings({ lowSensory: next });
    applySensory(store.snapshot().settings);
    say(next ? 'Low-sensory mode is on.' : 'Low-sensory mode is off.');
    if (document.body.dataset.view === 'activity') startActivity(currentActivity);
  });
  el('volume').addEventListener('input', () => {
    store.updateSettings({ volume: Number(el('volume').value) / 100 });
    sound.setVolume(store.snapshot().settings.volume);
  });
  el('brightness').addEventListener('input', () => {
    store.updateSettings({ brightness: Number(el('brightness').value) / 100 });
    document.documentElement.style.setProperty('--brightness', String(store.snapshot().settings.brightness));
  });
  el('mark-calming').addEventListener('click', () => {
    store.markCalming(currentActivity);
    el('mark-calming').textContent = 'Saved with your favorites';
    say('Saved with your favorites.');
  });
  el('spin').addEventListener('click', () => {
    if (!allowMotion()) {
      el('spin-note').textContent = 'That press is enough. There is no score.';
      return;
    }
    spinVelocity += 9;
    if (spinning) return;
    spinning = true;
    const loop = () => {
      if (!spinning) return;
      spinAngle = (spinAngle + spinVelocity) % 360;
      spinVelocity *= 0.985;
      el('spinner').style.transform = `rotate(${spinAngle}deg)`;
      if (spinVelocity > 0.08) spinFrame = requestAnimationFrame(loop);
      else spinning = false;
    };
    spinFrame = requestAnimationFrame(loop);
  });
  el('flow-warmer').addEventListener('click', () => { hue = (hue + 18) % 360; paintFlow(); });
  el('flow-cooler').addEventListener('click', () => { hue = (hue + 342) % 360; paintFlow(); });
  el('breath-in').addEventListener('click', () => { el('breath-label').textContent = 'Breathe in'; });
  el('breath-out').addEventListener('click', () => { el('breath-label').textContent = 'Breathe out'; });
  el('rhythm-toggle').addEventListener('click', async () => {
    if (rhythmOn) {
      stopEffects();
      renderActivity();
      return;
    }
    await sound.resume();
    if (store.snapshot().settings.volume <= 0) say('Volume is all the way down, so this stays quiet.');
    rhythmOn = true;
    el('rhythm-toggle').setAttribute('aria-pressed', 'true');
    el('rhythm-toggle').textContent = 'Stop soft sounds';
    const pulse = () => sound.tone(196, 0.45);
    pulse();
    rhythmTimer = setInterval(pulse, Number(el('rhythm-gap').value));
  });
  el('rhythm-gap').addEventListener('input', () => {
    const seconds = (Number(el('rhythm-gap').value) / 1000).toFixed(1);
    el('rhythm-note').textContent = `Sounds are about ${seconds} seconds apart. This is not a countdown.`;
    if (!rhythmOn) return;
    clearInterval(rhythmTimer);
    rhythmTimer = setInterval(() => sound.tone(196, 0.45), Number(el('rhythm-gap').value));
  });
  el('routine-finished').addEventListener('click', () => {
    if (!selectedRoutineId) return;
    if (!routineMarked) {
      routineMarked = true;
      store.noteRoutine(selectedRoutineId);
      say('The first part is done. The next part can wait.');
    } else {
      routineMarked = false;
      say('This card is ready whenever you are.');
    }
    renderRoutine();
  });
  el('goal-form').addEventListener('submit', (event) => {
    event.preventDefault();
    try {
      store.addGoal(el('goal-label').value);
      el('goal-label').value = '';
      renderGoals();
      renderHome();
      say('Goal saved on this device.');
    } catch (error) {
      say(error.message);
    }
  });
  el('gate-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const given = Number(el('gate-answer').value.trim());
    if (given === gateAnswer) {
      show('parent');
      say('Grown-up page is open on this device.');
      return;
    }
    nextQuestion();
    el('gate-message').textContent = 'That answer did not open the grown-up page.';
  });
  el('save-name').addEventListener('click', () => {
    store.setBuddyName(el('buddy-name-input').value);
    renderHome();
    say('Name saved on this device.');
  });
  el('muse-consent').addEventListener('change', async () => {
    store.updateSettings({ museConsent: el('muse-consent').checked });
    if (!el('muse-consent').checked) {
      await stopHeadset();
      useSimulated();
      el('muse-status').textContent = 'Headset consent is off. Simulated signal stays on.';
    } else {
      el('muse-status').textContent = 'Consent saved on this device. You can connect a headset when you are ready.';
    }
    el('muse-connect').disabled = !realConnectionAllowed(store.snapshot().settings.museConsent) || connecting;
  });
  el('muse-simulated').addEventListener('click', async () => {
    await stopHeadset();
    useSimulated();
    el('muse-status').textContent = 'Simulated signal is on. Samples are not saved.';
  });
  el('muse-connect').addEventListener('click', async () => {
    if (!realConnectionAllowed(store.snapshot().settings.museConsent)) {
      el('muse-status').textContent = 'A grown-up has to consent before a headset can connect.';
      return;
    }
    connecting = true;
    el('muse-connect').disabled = true;
    try {
      await stopHeadset();
      link = new MuseLink((traits) => {
        if (!realConnectionAllowed(store.snapshot().settings.museConsent)) return;
        liveTraits = withSchema(traits, 'headset');
        renderCue();
      });
      await link.connect();
      el('muse-status').textContent = 'Headset connected. Samples stay in memory and are not saved.';
    } catch (error) {
      await stopHeadset();
      useSimulated();
      el('muse-status').textContent = error?.message || 'The headset did not connect. Simulated signal stays on.';
    } finally {
      connecting = false;
      el('muse-connect').disabled = !realConnectionAllowed(store.snapshot().settings.museConsent);
    }
  });
  el('routine-form').addEventListener('submit', (event) => {
    event.preventDefault();
    try {
      store.addRoutine({
        first: el('routine-first').value,
        then: el('routine-then').value,
        icon: el('routine-icon').value,
      });
      el('routine-first').value = '';
      el('routine-then').value = '';
      renderParent();
      say('Card added on this device.');
    } catch (error) {
      say(error.message);
    }
  });
  el('parent-goal-form').addEventListener('submit', (event) => {
    event.preventDefault();
    try {
      store.addGoal(el('parent-goal-label').value);
      el('parent-goal-label').value = '';
      renderParent();
      say('Goal saved on this device.');
    } catch (error) {
      say(error.message);
    }
  });
  el('export-data').addEventListener('click', () => {
    const blob = new Blob([store.exportJson()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const linkNode = document.createElement('a');
    linkNode.href = url;
    linkNode.download = 'learner-buddy.json';
    document.body.append(linkNode);
    linkNode.click();
    linkNode.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    say('A copy was saved as a file on this device. It was not uploaded.');
  });
  el('import-data').addEventListener('change', async () => {
    const file = el('import-data').files?.[0];
    el('import-data').value = '';
    if (!file) return;
    try {
      store.importJson(await file.text());
      await stopHeadset();
      useSimulated();
      applySensory(store.snapshot().settings, { writeControls: true });
      renderParent();
      renderHome();
      say('Saved data was restored on this device.');
    } catch (error) {
      say(error.message);
    }
  });
  el('delete-data').addEventListener('click', () => { el('delete-confirm').hidden = false; });
  el('delete-no').addEventListener('click', () => { el('delete-confirm').hidden = true; });
  el('delete-yes').addEventListener('click', async () => {
    await stopHeadset();
    store.deleteAll();
    useSimulated();
    el('delete-confirm').hidden = true;
    applySensory(store.snapshot().settings, { writeControls: true });
    show('home');
    say('Everything stored in this browser for Learner Buddy was erased.');
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const tag = document.activeElement?.tagName || '';
    if (/INPUT|SELECT|TEXTAREA/.test(tag)) return;
    if (document.body.dataset.view !== 'home') show('home');
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopEffects();
  });
  motionQuery.addEventListener?.('change', () => {
    applySensory(store.snapshot().settings);
    if (document.body.dataset.view === 'activity') startActivity(currentActivity);
  });
}

function boot() {
  mountBeasts();
  bind();
  const loaded = store.load();
  applySensory(loaded.settings, { writeControls: true });
  useSimulated();
  show('home', { focus: false });
  if (store.warning()) say(store.warning());
}

boot();
