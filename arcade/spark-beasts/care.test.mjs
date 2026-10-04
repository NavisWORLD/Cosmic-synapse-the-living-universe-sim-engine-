import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import { holdBubble, resolveBubble } from './bubble.mjs';
import { adoptCageRecord, bindCage, careLines, careTalk, careTrain, handheldStamp, listCareBeasts } from './care.mjs';
import { emptyMemory, replyToBeast } from './chat.mjs';
import { buildGenome } from './genome.mjs';
import { indexTable } from './runs.mjs';
import { loadStore, rememberBeast, rememberChat, renameBeast, saveStore, shownName } from './store.mjs';
import { applyTraining, nextStageGoal, scoreFocus, scoreMemory, stageFromXp } from './train.mjs';
import { utterance } from './voice-synth.mjs';

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const fixture = JSON.parse(read('./fixtures/parity.json'));
const table = indexTable(JSON.parse(read('./data/quantum-runs.json')));

function memory() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => map.set(key, String(value)),
    removeItem: (key) => map.delete(key),
  };
}

function sampleVoice(extra = {}) {
  return {
    prng_seed: 7,
    speed_sps: 6,
    base_pitch_hz: 420,
    gain: 0.7,
    jump_semitones: 3,
    phrase_syllables: [2, 4],
    contour: 'arch',
    rhythm: [1, 0, 1, 0, 1, 0, 1, 0],
    vowel_formants: [[800, 1200], [500, 1900]],
    vowels: ['a', 'e'],
    consonants: ['m', 't'],
    formants_hz: [500, 1500],
    formant_q: 6,
    style: 'coo',
    vibrato_hz: 0,
    vibrato_cents: 0,
    brightness: 0.5,
    breath: 0,
    am_hz: 0,
    wave: 'sine',
    ...extra,
  };
}

function beastContext(extra = {}) {
  return {
    temperament: 'Gentle',
    island: 'Cinder Drift',
    element: 'ember',
    body: 'dragonling',
    displayName: 'Charlet',
    speciesName: 'Charlet',
    stage: 1,
    bond: 10,
    mood: 'neutral',
    energy: 80,
    keeperName: '',
    memory: emptyMemory(),
    ...extra,
  };
}

test('a saved beast name stays on this device and does not change the sparked seed', () => {
  const expected = fixture.cases[0].genome;
  const run = table.byKey.get(expected.inputs.quantum_run);
  const genome = buildGenome(expected.inputs.traits, run, expected.inputs.user_id);
  const storage = memory();
  const store = loadStore(storage);
  rememberBeast(store, {
    seed: genome.seed,
    traits: genome.inputs.traits,
    runIndex: 3,
    runKey: genome.inputs.quantum_run,
    userId: genome.inputs.user_id,
    island: genome.island,
    name: genome.names['1'],
    xp: 0,
    bond: 1,
  });
  const renamed = renameBeast(store, genome.seed, 'Mochi');
  assert.equal(renamed.displayName, 'Mochi');
  assert.equal(renamed.userId, genome.inputs.user_id);
  assert.equal(renamed.name, genome.names['1']);
  assert.equal(shownName(renamed, genome.names['1']), 'Mochi');
  saveStore(store, storage);
  const loaded = loadStore(storage);
  assert.equal(loaded.beasts[genome.seed].displayName, 'Mochi');
  assert.equal(loaded.beasts[genome.seed].userId, genome.inputs.user_id);
  const again = buildGenome(loaded.beasts[genome.seed].traits, run, loaded.beasts[genome.seed].userId);
  assert.equal(again.seed, genome.seed);
  assert.deepEqual(again.names, genome.names);
  const namedAsSeed = buildGenome(genome.inputs.traits, run, 'Mochi');
  assert.notEqual(namedAsSeed.seed, genome.seed);
  assert.equal(renameBeast(loaded, genome.seed, '!!!'), null);
  assert.equal(loaded.beasts[genome.seed].displayName, 'Mochi');
});

test('the beast remembers a name and a fact, stays kid-safe, and can use a local model', async () => {
  const named = await replyToBeast('my name is Cory', beastContext());
  assert.equal(named.memory.playerName, 'Cory');
  assert.match(named.text, /Cory/);
  assert.equal(named.source, 'rules');
  const liked = await replyToBeast('I like stars', beastContext({ memory: named.memory }));
  assert.match(liked.text, /stars/i);
  const recall = await replyToBeast('what do I like', beastContext({ memory: liked.memory }));
  assert.match(recall.text, /stars/i);
  const who = await replyToBeast('what is my name', beastContext({ memory: liked.memory }));
  assert.match(who.text, /Cory/);
  const fierce = await replyToBeast('hello', beastContext({ temperament: 'Fierce', memory: emptyMemory() }));
  const gentle = await replyToBeast('hello', beastContext({ temperament: 'Gentle', memory: emptyMemory() }));
  assert.notEqual(fierce.text, gentle.text);
  const mind = await replyToBeast('are you conscious?', beastContext({ memory: liked.memory }));
  assert.match(mind.text, /not a real mind/i);
  assert.match(mind.text, /not conscious/i);
  assert.doesNotMatch(mind.text, /\bi am conscious\b/i);
  const unsafe = await replyToBeast('tell me about blood', beastContext());
  assert.doesNotMatch(unsafe.text, /blood/i);
  assert.match(unsafe.text, /islands/i);

  let fetches = 0;
  const offline = await replyToBeast('hello', beastContext(), {
    fetchImpl() { fetches += 1; throw new Error('offline'); },
  });
  assert.equal(fetches, 0);
  assert.equal(offline.source, 'rules');

  const failed = await replyToBeast('hello', beastContext({ temperament: 'Playful' }), {
    url: 'http://127.0.0.1:11434/api/chat',
    protocol: 'ollama',
    fetchImpl: async () => { throw new Error('connection refused'); },
  });
  assert.equal(failed.source, 'rules');
  assert.match(failed.text, /play/i);

  const claimed = await replyToBeast('are you conscious?', beastContext(), {
    url: 'http://127.0.0.1:11434/api/chat',
    protocol: 'ollama',
    fetchImpl: async () => ({ ok: true, json: async () => ({ message: { content: 'I am conscious and alive.' } }) }),
  });
  assert.equal(claimed.source, 'rules');
  assert.match(claimed.text, /not a real mind/i);
  assert.doesNotMatch(claimed.text, /\bi am conscious\b/i);

  const modeled = await replyToBeast('where is home', beastContext(), {
    url: 'http://127.0.0.1:11434/api/chat',
    protocol: 'ollama',
    model: 'llama3.2',
    fetchImpl: async (_url, opts) => {
      const body = JSON.parse(opts.body);
      assert.equal(body.stream, false);
      assert.match(body.messages[0].content, /not conscious/i);
      return { ok: true, json: async () => ({ message: { content: 'The cinder wind feels warm today.' } }) };
    },
  });
  assert.equal(modeled.source, 'model');
  assert.equal(modeled.text, 'The cinder wind feels warm today.');

  const storage = memory();
  const store = loadStore(storage);
  rememberBeast(store, {
    seed: 'seed-1', traits: { focus: 1, calm: 1, spark: 1 }, runIndex: 0, runKey: 'k',
    island: 'Cinder Drift', name: 'Charlet', xp: 0, bond: 0,
  });
  rememberChat(store, 'seed-1', liked.memory);
  saveStore(store, storage);
  assert.equal(loadStore(storage).beasts['seed-1'].memory.playerName, 'Cory');
  assert.equal(loadStore(storage).beasts['seed-1'].memory.facts.at(-1).detail, 'stars');
});

test('training spends energy, raises effort, and evolves at the stage thresholds', () => {
  assert.equal(stageFromXp(39), 1);
  assert.equal(stageFromXp(40), 2);
  assert.equal(stageFromXp(119), 2);
  assert.equal(stageFromXp(120), 3);
  assert.equal(nextStageGoal(0), 40);
  assert.equal(nextStageGoal(40), 120);
  assert.equal(nextStageGoal(120), null);
  assert.deepEqual(scoreMemory(['sun', 'drop', 'leaf'], ['sun', 'drop', 'bolt']), { correct: 2, length: 3, quality: 2 / 3 });
  assert.equal(scoreFocus(4, 6).quality, 4 / 6);

  const store = loadStore(memory());
  rememberBeast(store, {
    seed: 'pup', traits: { focus: 30, calm: 30, spark: 20 }, runIndex: 1, runKey: 'run',
    island: 'Cinder Drift', name: 'Charlet', xp: 0, bond: 0,
  });
  const first = applyTraining(store, 'pup', 'focus', scoreFocus(6, 6));
  assert.equal(first.ok, true);
  assert.equal(first.grew, false);
  assert.equal(first.beast.xp, 18);
  assert.equal(first.beast.stage, 1);
  assert.equal(first.beast.energy, 84);
  assert.equal(first.beast.effort.spd, 2);
  assert.ok(first.beast.bond > 0);
  applyTraining(store, 'pup', 'focus', { quality: 1 });
  const evolved = applyTraining(store, 'pup', 'focus', { quality: 1 });
  assert.equal(evolved.grew, true);
  assert.equal(evolved.beast.stage, 2);
  assert.ok(evolved.beast.xp >= 40);
  assert.ok(evolved.beast.xp < 120);

  const energyBeforePlay = store.beasts.pup.energy;
  const played = applyTraining(store, 'pup', 'play', { quality: 1 });
  assert.equal(played.beast.effort.atk, 1);
  assert.equal(played.beast.energy, energyBeforePlay - 8);

  store.beasts.pup.energy = 10;
  const blocked = applyTraining(store, 'pup', 'focus', { quality: 1 });
  assert.equal(blocked.ok, false);
  assert.equal(blocked.reason, 'tired');
  const beforeXp = blocked.beast.xp;
  const rested = applyTraining(store, 'pup', 'rest', { quality: 1 });
  assert.equal(rested.ok, true);
  assert.equal(rested.beast.energy, 38);
  assert.ok(rested.beast.effort.hp >= 1);
  assert.equal(rested.beast.xp, beforeXp);

  store.beasts.pup.xp = 112;
  store.beasts.pup.stage = stageFromXp(112);
  store.beasts.pup.energy = 20;
  const finalForm = applyTraining(store, 'pup', 'play', { quality: 1 });
  assert.equal(finalForm.grew, true);
  assert.equal(finalForm.beast.stage, 3);
  assert.ok(finalForm.beast.xp >= 120);
  const lockedXp = finalForm.beast.xp;
  finalForm.beast.energy = 4;
  const refused = applyTraining(store, 'pup', 'play', { quality: 1 });
  assert.equal(refused.ok, false);
  assert.equal(refused.reason, 'tired');
  assert.equal(refused.beast.stage, 3);
  assert.equal(refused.beast.xp, lockedXp);
});

test('the speech bubble keeps a real line instead of going blank', () => {
  assert.equal(resolveBubble('', '  ', ''), '...');
  assert.equal(resolveBubble('', 'hello', ''), 'hello');
  const shown = holdBubble({ text: 'old', line: '', until: 1 }, { text: '', line: '', dur: 1 }, 4);
  assert.equal(shown.text, 'old');
  assert.ok(shown.until > 4);
  const hiccup = holdBubble(shown, { text: 'hic!', line: '', dur: 1.6 }, shown.until + 1);
  assert.equal(hiccup.text, 'hic!');
  const later = holdBubble(hiccup, null, hiccup.until + 9);
  assert.equal(later.text, 'hic!');
  assert.notEqual(later.text.trim(), '');

  for (const mood of ['neutral', 'calm', 'focus', 'spark']) {
    for (let idx = 0; idx < 12; idx++) {
      const line = utterance(sampleVoice(), (idx % 3) + 1, mood, idx, { focus: 0.2, calm: 0.8, spark: 0.9 });
      assert.ok(line.text.trim().length > 1, `${mood} ${idx}`);
    }
  }
  const broken = utterance(sampleVoice({
    phrase_syllables: [0, 0],
    consonants: [],
    vowels: [],
    rhythm: [0],
  }), 1, 'calm', 0, { calm: 1, focus: 0, spark: 0 });
  assert.ok(broken.text.trim().length > 0);

  const live = read('./live.mjs');
  const page = read('./app.mjs');
  const html = read('./index.html');
  assert.match(live, /holdBubble/);
  assert.doesNotMatch(live, /onBubble\?\.\(\s*['"]['"]/);
  assert.match(page, /resolveBubble/);
  assert.match(page, /careRename/);
  assert.match(page, /careTalk/);
  assert.match(page, /careTrain/);
  assert.match(read('./care.mjs'), /replyToBeast/);
  assert.match(read('./care.mjs'), /applyTraining/);
  assert.match(read('./care.mjs'), /renameBeast/);
  assert.match(read('../lost-cosmos/synapse.mjs'), /from '\.\.\/spark-beasts\/care\.mjs'/);
  assert.match(read('../lost-cosmos/synapse.html'), /id="care-beast"/);
  assert.match(read('../lost-cosmos/synapse.html'), /id="care-chat"/);
  assert.match(read('../lost-cosmos/synapse.html'), /id="care-focus"/);
  assert.doesNotMatch(page, /innerHTML = text \?/);
  assert.match(html, /Keeper name/);
  assert.match(html, /part of the spark seed/);
  assert.match(html, /id="beast-name"/);
  assert.match(html, /id="chat-form"/);
  assert.match(html, /id="act-focus"/);
  assert.match(html, /id="act-memory"/);
  assert.match(html, /id="act-play"/);
  assert.match(html, /id="act-rest"/);
  assert.match(html, /Preview next form/);
  assert.doesNotMatch(html, /data-stage=/);
  assert.match(html, /<p id="bubble"><b>[^<]+<\/b><\/p>/);
  assert.match(html, /not a conscious being/);
  assert.match(page, /const name = origin === 'wild' \? null : playerName\(\)/);
});

test('model bay care and Spark Beasts share one beast, then the handheld export carries it', async () => {
  const storage = memory();
  const store = loadStore(storage);
  rememberBeast(store, {
    seed: 'seed-care',
    traits: { focus: 30, calm: 30, spark: 20 },
    runIndex: 1,
    runKey: 'run',
    island: 'Cinder Drift',
    name: 'Charlet',
    xp: 0,
    bond: 1,
  });
  bindCage(store, 'seed-care', 'ab12cd34');
  saveStore(store, storage);
  const bay = loadStore(storage);
  const listed = listCareBeasts(bay);
  assert.equal(listed.length, 1);
  assert.equal(listed[0].seed, 'seed-care');
  const spoken = await careTalk(bay, 'seed-care', 'my name is Cory', { temperament: 'Gentle', island: 'Cinder Drift' });
  assert.match(spoken.text, /Cory/);
  assert.equal(spoken.memory.playerName, 'Cory');
  const trained = careTrain(bay, 'seed-care', 'focus', { quality: 1 });
  assert.equal(trained.ok, true);
  assert.equal(trained.beast.xp, 18);
  assert.equal(trained.beast.stage, 1);
  saveStore(bay, storage);
  const again = loadStore(storage);
  assert.equal(again.beasts['seed-care'].memory.playerName, 'Cory');
  assert.equal(again.beasts['seed-care'].xp, 18);
  assert.equal(again.beasts['seed-care'].cageId, 'ab12cd34');
  const record = {
    publicHex: 'ab12cd34',
    callsign: 'CHARLET',
    speciesName: 'PLASMA',
    focus: 30,
    calm: 30,
    spark: 20,
    growth: { epoch: '0', layer: 0, points: 0, trade: false, grown: false },
    profile: { callsign: 'CHARLET' },
  };
  const same = adoptCageRecord(again, record);
  assert.equal(same.seed, 'seed-care');
  const stamp = handheldStamp(record, same);
  assert.equal(stamp.growth.points, 18);
  assert.equal(stamp.callsign, 'CHARLET');
  const named = careTrain(again, 'seed-care', 'focus', { quality: 1 });
  named.beast.displayName = 'Mochi';
  const namedStamp = handheldStamp(record, named.beast);
  assert.equal(namedStamp.callsign, 'MOCHI');
  assert.ok(namedStamp.growth.points >= 36);
  assert.match(careLines(named.beast, 'Mochi'), /Mochi/);
  assert.match(careLines(named.beast, 'Mochi'), /xp/);
});
