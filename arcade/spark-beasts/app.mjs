import { renderSprite } from './render.mjs';
import { paintSprite } from './draw.mjs';
import { buildGenome } from './genome.mjs';
import { loadTable, runChoices } from './runs.mjs';
import { SensorHub } from './sensors.mjs';
import { LiveShow } from './live.mjs';
import { IslandExplore, sparkWilds } from './explore.mjs';
import { eraseStore, grant, loadStore, rememberBeast, saveStore, stageFromXp } from './store.mjs';
import { sha256Hex } from './hash.mjs';
import { sanitizeName } from './trade.mjs';
import {
  admit, attachGrowth, buildGrowth, buildSave, cageSave, emptyLedger, encodeTicket, genomeFromRecipe,
  importPayload, loadCage, releaseForTrade, saveCage, sealShare, sparkRecord, ticketLink, xpFromGrowth,
} from './trade.mjs';
import { drawQr } from '../lost-cosmos/qr.mjs';
import { simulateStable } from './signal.mjs';
import { presentClips } from './showcase.mjs';

const $ = (id) => document.getElementById(id);
const status = (text) => { $('status').textContent = text; };

const state = {
  table: null,
  store: loadStore(localStorage),
  ledger: loadCage(localStorage),
  traits: { focus: 30, calm: 30, spark: 20 },
  genome: null,
  runIndex: 0,
  wilds: [],
  world: 'EARTH',
  sensors: null,
  live: null,
  explore: null,
};

function consented() {
  return $('consent').checked;
}

function playerName() {
  const name = sanitizeName($('player-name').value);
  state.store.playerName = name || '';
  saveStore(state.store, localStorage);
  return name;
}

function showTraits(traits) {
  state.traits = traits;
  for (const key of ['focus', 'calm', 'spark']) {
    $(key).value = String(traits[key]);
    $(`${key}-read`).textContent = String(traits[key]);
  }
  state.live?.setTarget(traits);
}

function selectedRunIndex() {
  const value = $('run').value;
  if (value === 'auto') {
    const name = playerName() || '';
    const hex = sha256Hex(`spark-auto:${state.traits.focus}:${state.traits.calm}:${state.traits.spark}:${name}`);
    return Number(BigInt(`0x${hex.slice(0, 12)}`) % BigInt(state.table.runs.length));
  }
  return Number(value);
}

function entryFromGenome(genome, runIndex, origin, xp = 0, bond = 0) {
  const saved = rememberBeast(state.store, {
    seed: genome.seed,
    traits: genome.inputs.traits,
    runIndex,
    runKey: genome.inputs.quantum_run,
    userId: genome.inputs.user_id,
    origin,
    island: genome.island,
    name: genome.names['1'],
    xp,
    bond,
  });
  state.store.active = genome.seed;
  saveStore(state.store, localStorage);
  return { ...saved, genome };
}

async function hold(genome, runIndex, xp) {
  const record = sparkRecord(genome, runIndex, xp);
  const id = record.publicId.toString(16).padStart(8, '0');
  const row = state.ledger.identities[id];
  if (row && !row.held) {
    status(`${record.callsign} is already out for trade. Import that share to bring the same beast back.`);
    return record;
  }
  const admitted = await admit(state.ledger, record, 'local');
  saveCage(state.ledger, localStorage);
  const carried = xpFromGrowth(admitted.growth);
  const beast = state.store.beasts[genome.seed];
  if (beast && carried > beast.xp) {
    beast.xp = carried;
    beast.stage = stageFromXp(beast.xp);
    saveStore(state.store, localStorage);
  }
  return admitted;
}

function paintStages(genome) {
  const root = $('stages');
  root.replaceChildren();
  for (const stage of [1, 2, 3]) {
    const figure = document.createElement('figure');
    const canvas = document.createElement('canvas');
    paintSprite(canvas, renderSprite(genome, stage), 2);
    const caption = document.createElement('figcaption');
    caption.textContent = `${genome.names[String(stage)]} · stage ${stage}`;
    figure.append(canvas, caption);
    root.append(figure);
  }
  const q = genome.quantum;
  $('provenance').textContent = `${genome.names['1']} the ${genome.temperament} ${genome.body} of ${genome.island}. Voice ${genome.voice.style} at ${genome.voice.base_pitch_hz} Hz. Quantum seed ${q.backend} job ${q.job_id} pub ${q.pub_index}, ${q.num_bits}-bit recorded counts ${q.counts_sha256.slice(0, 12)}. These counts are historical. They are not a live link.`;
  $('portrait').hidden = false;
  $('live-meta').textContent = `${genome.island} · ${genome.temperament} · reacts to ${genome.behavior.reacts_most_to} · tic ${genome.behavior.tic}`;
}

function activate(entry) {
  state.genome = entry.genome;
  const stage = entry.stage || 1;
  paintStages(entry.genome);
  state.live.show(entry.genome, stage);
  state.live.setTarget(state.traits);
  state.explore.setCompanion(entry);
  renderBestiary();
}

function sparkFrom(traits, runIndex, origin) {
  const run = state.table.runs[runIndex];
  const name = origin === 'wild' ? null : playerName();
  const genome = buildGenome(traits, run, name);
  const xp = state.store.beasts[genome.seed]?.xp || 0;
  const entry = entryFromGenome(genome, runIndex, origin, xp, state.store.beasts[genome.seed]?.bond || 0);
  hold(genome, runIndex, entry.xp).catch((error) => status(error.message));
  activate(entry);
  status(`${genome.names['1']} sparked on ${genome.island}. Same signal, same run, same name: the same beast.`);
  return entry;
}

function renderBestiary() {
  const root = $('bestiary');
  root.replaceChildren();
  const beasts = Object.values(state.store.beasts);
  if (!beasts.length) {
    const empty = document.createElement('p');
    empty.textContent = 'No beasts yet. Spark one, or meet a wild spark on an island.';
    root.append(empty);
    return;
  }
  for (const beast of beasts) {
    const run = state.table.runs[beast.runIndex];
    if (!run) continue;
    const genome = buildGenome(beast.traits, run, beast.userId);
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'card';
    const canvas = document.createElement('canvas');
    paintSprite(canvas, renderSprite(genome, beast.stage || 1), 2);
    card.append(canvas);
    const label = document.createElement('div');
    label.textContent = `${beast.name} · ${beast.island} · stage ${beast.stage} · bond ${Math.round(beast.bond)} · ${beast.origin}`;
    card.append(label);
    card.addEventListener('click', () => {
      activate({ ...beast, genome });
      showView('live');
    });
    root.append(card);
  }
}

async function mediaExists(rel) {
  const url = new URL(`./media/${rel}`, import.meta.url);
  try {
    let response = await fetch(url, { method: 'HEAD' });
    if (response.status === 405 || response.status === 501) {
      response = await fetch(url, { headers: { Range: 'bytes=0-0' } });
    }
    return response.ok;
  } catch {
    return false;
  }
}

async function loadRare() {
  const response = await fetch(new URL('./media/rare/manifest.json', import.meta.url));
  if (!response.ok) throw new Error('Rare spark gallery is missing');
  const manifest = await response.json();
  const clips = await presentClips(manifest, mediaExists);
  const root = $('rare-gallery');
  root.replaceChildren();
  for (const clip of clips) {
    const card = document.createElement('article');
    card.className = 'card';
    const title = document.createElement('h3');
    title.textContent = clip.name;
    const video = document.createElement('video');
    video.controls = true;
    video.preload = 'none';
    video.autoplay = false;
    video.muted = false;
    video.playsInline = true;
    video.src = new URL(`./media/${clip.video}`, import.meta.url).href;
    const note = document.createElement('p');
    note.className = 'note';
    const log = clip.audioLog ? ` Voice log ${clip.audioLog.split('/').pop()}.` : '';
    note.textContent = `${clip.seconds}s showcase. Tap play to hear it.${log}`;
    card.append(title, video, note);
    root.append(card);
  }
  const waiting = (manifest.clips || []).length - clips.length;
  if (waiting > 0) {
    const pending = document.createElement('p');
    pending.className = 'note';
    pending.textContent = waiting === 1
      ? 'One more showcase clip is listed and will appear here when its video is in this copy.'
      : `${waiting} more showcase clips are listed and will appear here when their videos are in this copy.`;
    root.append(pending);
  }
}

function showView(name) {
  document.querySelectorAll('nav button').forEach((button) => button.classList.toggle('on', button.dataset.view === name));
  document.querySelectorAll('.view').forEach((view) => view.classList.toggle('on', view.id === `view-${name}`));
  if (name === 'live') state.live.start();
  else state.live.stop();
  if (name === 'explore') {
    state.explore.start();
    if (!state.wilds.length && state.table) wakeWilds();
  } else state.explore.stop();
  if (name === 'bestiary') renderBestiary();
}

function wakeWilds() {
  state.wilds = sparkWilds(state.table);
  const known = new Set(Object.keys(state.store.beasts));
  state.explore.setWilds(state.wilds, known);
  if (state.genome) {
    const beast = state.store.beasts[state.genome.seed];
    state.explore.setCompanion({ genome: state.genome, seed: state.genome.seed, stage: beast?.stage || 1 });
  }
}

function activeEntry() {
  if (!state.genome) return null;
  const saved = state.store.beasts[state.genome.seed];
  return saved ? { ...saved, genome: state.genome } : null;
}

async function currentRecord() {
  const entry = activeEntry();
  if (!entry) throw new Error('Spark a beast before sharing it.');
  const admitted = await hold(entry.genome, entry.runIndex, entry.xp);
  if (!admitted.transfer) throw new Error('The cage did not accept this beast.');
  return admitted;
}

function download(filename, text, type = 'application/json') {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function bind() {
  document.querySelectorAll('nav button').forEach((button) => button.addEventListener('click', () => showView(button.dataset.view)));
  for (const key of ['focus', 'calm', 'spark']) {
    $(key).addEventListener('input', () => {
      if (!consented()) { status('Consent is required before the sliders count as a signal.'); return; }
      try {
        const traits = state.sensors.holdSliders({
          focus: Number($('focus').value), calm: Number($('calm').value), spark: Number($('spark').value),
        });
        showTraits(traits);
      } catch (error) { status(error.message); }
    });
  }
  $('sim').addEventListener('click', () => {
    try {
      showTraits(state.sensors.simulate($('profile').value));
      status(`Simulated ${$('profile').value} headband. Eight windows, median, bucket 10. The waveform was discarded.`);
    } catch (error) { status(error.message); }
  });
  $('muse').addEventListener('click', async () => {
    try {
      await state.sensors.connectMuse();
      status('Muse connected. Traits update from the latest on-device window. Samples stay in this page.');
    } catch (error) { status(error.message || 'Muse did not connect. The simulated headband still works.'); }
  });
  for (const [id, method, label] of [['mic', 'enableMic', 'Microphone'], ['motion', 'enableMotion', 'Motion'], ['camera', 'enableCamera', 'Camera'], ['rhythm', 'enableRhythm', 'Rhythm']]) {
    $(id).addEventListener('click', async () => {
      try {
        await state.sensors[method]();
        $(id).classList.add('on');
        status(`${label} is on as a soft nudge. The raw signal is not stored.`);
      } catch (error) { status(error.message); }
    });
  }
  $('spark-btn').addEventListener('click', () => {
    if (!consented()) { status('Consent is required before a beast is sparked.'); return; }
    if (!state.table) { status('The recorded quantum table is still loading.'); return; }
    sparkFrom(state.traits, selectedRunIndex(), 'spark');
  });
  $('wild-btn').addEventListener('click', () => {
    if (!consented()) { status('Consent is required before a wild beast is sparked.'); return; }
    const cursor = state.store.wildCursor || 0;
    const index = Number(BigInt(`0x${sha256Hex(`wild-button:${cursor}`).slice(0, 12)}`) % BigInt(state.table.runs.length));
    state.store.wildCursor = cursor + 1;
    const profiles = ['serene', 'focused', 'sparky', 'dreamy', 'balanced', 'restless', 'steady', 'mock'];
    const rolled = simulateStable(profiles[index % profiles.length]);
    sparkFrom({ focus: rolled.focus, calm: rolled.calm, spark: rolled.spark }, index, 'wild');
  });
  document.querySelectorAll('[data-stage]').forEach((button) => button.addEventListener('click', () => {
    const stage = Number(button.dataset.stage);
    state.live.setStage(stage);
    if (state.genome) state.live.hooks.onName?.(`${state.genome.names[String(stage)]}  ${'I'.repeat(stage)}`);
  }));
  $('voice').addEventListener('click', () => {
    state.live.enableVoice();
    $('voice').classList.add('on');
    status('Voice is on. The babble is synthesized in this page. It is not a language.');
  });
  $('drift').addEventListener('click', () => {
    const on = !$('drift').classList.contains('on');
    $('drift').classList.toggle('on', on);
    state.live.setDrift(on);
  });
  $('translate').addEventListener('click', () => {
    state.live.translate = !state.live.translate;
    $('translate').setAttribute('aria-pressed', String(state.live.translate));
  });
  document.querySelectorAll('[data-move]').forEach((button) => button.addEventListener('click', () => {
    const [x, y] = button.dataset.move.split(',').map(Number);
    state.explore.nudge(x, y);
    state.explore.start();
  }));
  $('export').addEventListener('click', async () => {
    try {
      const record = await currentRecord();
      const released = await releaseForTrade(state.ledger, record);
      saveCage(state.ledger, localStorage);
      const text = await sealShare(released, $('passphrase').value);
      download(`${released.callsign || 'beast'}.qbeast`, text);
      status('Share downloaded. This cage marked the beast out for trade, so a second local copy is refused.');
    } catch (error) { status(error.message); }
  });
  $('link').addEventListener('click', async () => {
    try {
      const record = await currentRecord();
      const released = await releaseForTrade(state.ledger, record);
      saveCage(state.ledger, localStorage);
      const page = window.parent !== window ? document.referrer || location.href : location.href;
      const link = ticketLink(encodeTicket(released), page);
      await navigator.clipboard?.writeText(link);
      status('Trade link copied. It lives in the address fragment.');
    } catch (error) { status(error.message); }
  });
  $('qr-btn').addEventListener('click', async () => {
    try {
      const record = await currentRecord();
      const released = await releaseForTrade(state.ledger, record);
      saveCage(state.ledger, localStorage);
      const page = window.parent !== window ? document.referrer || location.href : location.href;
      const link = ticketLink(encodeTicket(released), page);
      const canvas = $('qr');
      canvas.hidden = false;
      drawQr(canvas, link);
      status('QR ready. Scanning it opens the same trade ticket.');
    } catch (error) { status(error.message); }
  });
  $('send').addEventListener('click', async () => {
    try {
      const record = await currentRecord();
      const bytes = cageSave(record, buildSave, buildGrowth, attachGrowth);
      if (window.parent === window) { status('Open Spark Beasts from the Living Universe SPARK tab to reach the handheld.'); return; }
      window.parent.postMessage({ type: 'lc-cage-save', save: bytes, callsign: record.callsign, species: record.speciesName, play: true }, '*');
      status(`${record.callsign} is in the handheld mailbox. Start a new game on the cartridge.`);
    } catch (error) { status(error.message); }
  });
  $('import-file').addEventListener('change', async () => {
    const file = $('import-file').files?.[0];
    if (!file) return;
    if (!consented()) { status('Consent is required before a beast file is read.'); return; }
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      const record = await importPayload(bytes, state.traits, { passphrase: $('passphrase').value });
      await admit(state.ledger, record, 'receive');
      saveCage(state.ledger, localStorage);
      const built = genomeFromRecipe(record.seed, state.table);
      if (!built) {
        status(`${record.callsign} entered the cage. This file is not a spark recipe, so it stays in the trade ledger.`);
        return;
      }
      const xp = Math.max(xpFromGrowth(record.growth), state.store.beasts[built.genome.seed]?.xp || 0);
      const entry = entryFromGenome(built.genome, built.recipe.runIndex, 'import', xp, 8);
      activate(entry);
      showView('explore');
      status(`${built.genome.names['1']} imported and is roaming with you. A second copy of this identity is refused.`);
    } catch (error) { status(error.message); }
  });
  $('export-ledger').addEventListener('click', () => {
    download('spark-beasts-ledger.json', JSON.stringify(state.store, null, 2));
    status('Ledger exported. It has traits, names, and growth. It has no raw sensor samples.');
  });
  $('erase').addEventListener('click', () => {
    eraseStore(localStorage);
    state.store = loadStore(localStorage);
    state.genome = null;
    $('portrait').hidden = true;
    $('stages').replaceChildren();
    renderBestiary();
    status('Spark ledger erased on this device. The shared cage ledger is unchanged until you clear site data.');
  });
}

function restoreActive() {
  const seed = state.store.active;
  const beast = seed && state.store.beasts[seed];
  if (!beast) return;
  const run = state.table.runs[beast.runIndex];
  if (!run) return;
  const genome = buildGenome(beast.traits, run, beast.userId);
  activate({ ...beast, genome });
}

async function boot() {
  state.sensors = new SensorHub((traits) => showTraits(traits));
  $('consent').addEventListener('change', () => state.sensors.setConsent($('consent').checked));
  state.live = new LiveShow($('live-view'), {
    onBubble(text, line) {
      $('bubble').innerHTML = text ? `<b></b><span></span>` : '';
      if (!text) return;
      $('bubble').querySelector('b').textContent = text;
      if (line) $('bubble').querySelector('span').textContent = line;
    },
    onMood(text) { $('mood').textContent = text; },
    onName(text) { $('mood').dataset.name = text; },
    onDrive() {},
    onDrift(target) { showTraits({ focus: Math.round(target.focus), calm: Math.round(target.calm), spark: Math.round(target.spark) }); },
  });
  state.explore = new IslandExplore($('explore-view'), {
    onPlace(name) { $('place').textContent = `${name}. Your beast follows. Wild sparks wander, sniff, chase motes, and nap.`; },
    onMeet(beast) {
      const wild = state.wilds.find((row) => row.genome.seed === beast.genome.seed);
      if (!wild) return;
      const entry = entryFromGenome(beast.genome, wild.runIndex, 'wild', 4, 6);
      grant(state.store, entry.seed, 0, 0);
      saveStore(state.store, localStorage);
      renderBestiary();
      status(`You met ${beast.genome.names['1']} on ${wild.island}. They joined the bestiary.`);
    },
  });
  bind();
  if (state.store.playerName) $('player-name').value = state.store.playerName;
  try {
    state.table = await loadTable();
    const choices = runChoices(state.table, 18);
    const select = $('run');
    const auto = document.createElement('option');
    auto.value = 'auto';
    auto.textContent = 'Auto-pick from this signal';
    select.append(auto);
    state.table.runs.forEach((run, index) => {
      if (!choices.includes(run) && run.num_bits === 1) return;
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = `${run.backend} ${run.job_id.slice(0, 10)} · ${run.num_bits}-bit`;
      select.append(option);
    });
    restoreActive();
    status(`Recorded table ready: ${state.table.runs.length} historical runs. ${state.table.claim}`);
  } catch (error) {
    status(error.message);
  }
  try { await loadRare(); } catch (error) { status(error.message); }
  setInterval(() => {
    if (!state.genome) return;
    const playing = $('view-live').classList.contains('on') || $('view-explore').classList.contains('on');
    if (!playing) return;
    const result = grant(state.store, state.genome.seed, 1, 0.4);
    if (!result) return;
    saveStore(state.store, localStorage);
    if (result.grew) {
      state.live.setStage(result.beast.stage);
      status(`${state.genome.names[String(result.beast.stage)]} grew to stage ${result.beast.stage}. Growth does not shrink.`);
    }
  }, 5000);
  window.addEventListener('message', (event) => {
    const data = event.data;
    if (!data || data.source !== 'living-universe' || data.type !== 'lu-state') return;
    if (event.source !== window.parent) return;
    state.world = String(data.world || 'EARTH');
    $('world-name').textContent = state.world;
  });
  if (window.parent !== window) window.parent.postMessage({ type: 'sb-spark-ready' }, '*');
}

boot();
