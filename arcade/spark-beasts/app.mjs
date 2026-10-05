import { renderSprite } from './render.mjs';
import { spriteToGba } from './gba-tiles.mjs';
import { attachFieldArt } from '../lost-cosmos/mailbox.mjs';
import { paintSprite } from './draw.mjs';
import { buildGenome } from './genome.mjs';
import { loadTable, runChoices } from './runs.mjs';
import { SensorHub } from './sensors.mjs';
import { LiveShow } from './live.mjs';
import { IslandExplore, sparkWilds } from './explore.mjs';
import { eraseStore, grant, loadStore, rememberBeast, saveStore, shownName, stageFromXp, STORE_KEY } from './store.mjs';
import { resolveBubble } from './bubble.mjs';
import { scoreFocus, scoreMemory } from './train.mjs';
import { bindCage, careLines, careRename, careTalk, careTrain, nextStageGoal, stampRecord, trainingBlurb } from './care.mjs';
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
  preview: false,
  chats: new Map(),
  game: null,
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
  }
  bindCage(state.store, genome.seed, admitted.publicHex || id);
  saveStore(state.store, localStorage);
  return admitted;
}

function activeBeast() {
  if (!state.genome) return null;
  return state.store.beasts[state.genome.seed] || null;
}

function speciesAt(stage) {
  return state.genome?.names?.[String(stage)] || 'Beast';
}

function titleOf(stage) {
  const beast = activeBeast();
  const earned = beast?.stage || stage || 1;
  return shownName(beast, speciesAt(stage || earned));
}

function publicLabel(beast, species) {
  const nick = shownName(beast, species);
  if (!species || nick.toLowerCase() === String(species).toLowerCase()) return nick;
  return `${nick} (${species})`;
}

/** "Play in Lost Cosmos" opens the in-browser handheld with this beast's starter save. */
function playLink(seed, link = document.createElement('a')) {
  link.className = 'play-lc';
  link.href = new URL(`./play.html?beast=${encodeURIComponent(String(seed || ''))}`, import.meta.url).href;
  link.textContent = '\u25B6 Play in Lost Cosmos';
  // Inside the Living Universe frame, open the full player in its own tab.
  if (window.parent !== window) {
    link.target = '_blank';
    link.rel = 'noopener';
  } else {
    link.removeAttribute('target');
  }
  return link;
}

function paintStages(genome) {
  const root = $('stages');
  root.replaceChildren();
  const earned = state.store.beasts[genome.seed]?.stage || 1;
  const nick = shownName(state.store.beasts[genome.seed], genome.names['1']);
  for (const stage of [1, 2, 3]) {
    const figure = document.createElement('figure');
    if (stage <= earned) figure.className = 'earned';
    const canvas = document.createElement('canvas');
    paintSprite(canvas, renderSprite(genome, stage), 2);
    const caption = document.createElement('figcaption');
    const mark = stage <= earned ? 'earned' : 'locked until trained';
    caption.textContent = `${nick} · ${genome.names[String(stage)]} · stage ${stage} · ${mark}`;
    figure.append(canvas, caption);
    root.append(figure);
  }
  const q = genome.quantum;
  const keeper = genome.inputs.user_id || 'no keeper name';
  $('provenance').textContent = `${nick} the ${genome.temperament} ${genome.body} of ${genome.island}. Sparked form ${genome.names['1']}. Voice ${genome.voice.style} at ${genome.voice.base_pitch_hz} Hz. Quantum seed ${q.backend} job ${q.job_id} pub ${q.pub_index}, ${q.num_bits}-bit recorded counts ${q.counts_sha256.slice(0, 12)}. These counts are historical. They are not a live link.`;
  $('seed-lock').textContent = `Look locked. Seed keeper name: ${keeper}. Traits ${genome.inputs.traits.focus}/${genome.inputs.traits.calm}/${genome.inputs.traits.spark}. Run ${genome.inputs.quantum_run}. Renaming ${nick} does not change this seed.`;
  playLink(genome.seed, $('play-lc'));
  $('portrait').hidden = false;
  $('live-meta').textContent = `${genome.island} · ${genome.temperament} · reacts to ${genome.behavior.reacts_most_to} · tic ${genome.behavior.tic}`;
}

function syncCompanion({ place = false, announce = true } = {}) {
  const beast = activeBeast();
  if (!state.genome || !beast) return;
  const earned = beast.stage || 1;
  const showing = state.preview && earned < 3 ? earned + 1 : earned;
  const species = speciesAt(showing);
  const title = titleOf(earned);
  if (state.live.stage !== showing) state.live.setStage(showing);
  if (announce) state.live.hooks.onName?.(`${title} · ${species}  ${'I'.repeat(showing)}`);
  $('beast-title').textContent = publicLabel(beast, speciesAt(earned));
  if (document.activeElement !== $('beast-name')) $('beast-name').value = beast.displayName || '';
  $('preview-note').hidden = !state.preview;
  $('preview-note').textContent = state.preview
    ? `Preview of stage ${showing}, ${species}. This form is not earned yet. Train to evolve.`
    : '';
  $('preview-next').textContent = state.preview ? 'Show earned form' : (earned < 3 ? 'Preview next form' : 'Final form earned');
  $('care-stats').textContent = careLines(beast, title);
  if (place) state.explore.setCompanion({ ...beast, genome: state.genome, label: title });
  else {
    state.explore.setLabel(title);
    state.explore.setCompanionStage(earned);
  }
}

function activate(entry) {
  state.genome = entry.genome;
  state.preview = false;
  const stage = entry.stage || 1;
  paintStages(entry.genome);
  state.live.show(entry.genome, stage);
  state.live.setTarget(state.traits);
  syncCompanion({ place: true, announce: false });
  renderChat();
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
  status(`${publicLabel(entry, genome.names['1'])} sparked on ${genome.island}. The look is locked to this signal, run, and keeper name. Name them on the Live tab without changing the seed.`);
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
    const form = genome.names[String(beast.stage || 1)] || beast.name;
    const label = document.createElement('div');
    label.textContent = `${publicLabel(beast, form)} · ${beast.island} · stage ${beast.stage} · bond ${Math.round(beast.bond)} · energy ${Math.round(beast.energy ?? 100)} · ${beast.origin}`;
    card.append(label);
    card.addEventListener('click', () => {
      activate({ ...beast, genome });
      showView('live');
    });
    const cell = document.createElement('div');
    cell.className = 'play-cell';
    cell.append(card, playLink(beast.seed));
    root.append(cell);
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
  else {
    state.live.stop();
    stopGame();
  }
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
    state.explore.setCompanion({ genome: state.genome, seed: state.genome.seed, stage: beast?.stage || 1, label: shownName(beast, state.genome.names[String(beast?.stage || 1)]) });
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
  $('rename').addEventListener('click', () => saveBeastName());
  $('beast-name').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') saveBeastName();
  });
  $('preview-next').addEventListener('click', () => {
    const beast = activeBeast();
    if (!beast) { status('Spark a beast before previewing a form.'); return; }
    if ((beast.stage || 1) >= 3 && !state.preview) {
      status(`${titleOf()} is already the final earned form.`);
      return;
    }
    state.preview = !state.preview;
    syncCompanion();
    status(state.preview ? $('preview-note').textContent : `${titleOf()} is showing the earned form.`);
  });
  $('act-play').addEventListener('click', () => finishTraining('play', { quality: 1 }));
  $('act-rest').addEventListener('click', () => finishTraining('rest', { quality: 1 }));
  $('act-focus').addEventListener('click', () => startFocus());
  $('act-memory').addEventListener('click', () => startMemory());
  $('chat-form').addEventListener('submit', (event) => {
    event.preventDefault();
    sendChat();
  });
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
      const record = stampRecord(await currentRecord(), activeBeast());
      const entry = activeEntry();
      let bytes = cageSave(record, buildSave, buildGrowth, attachGrowth);
      if (entry?.genome) {
        const stage = entry.stage || 1;
        bytes = attachFieldArt(bytes, spriteToGba(renderSprite(entry.genome, stage, { shadow: false })));
      }
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
  hold(genome, beast.runIndex, beast.xp).catch((error) => status(error.message));
}

async function boot() {
  state.sensors = new SensorHub((traits) => showTraits(traits));
  $('consent').addEventListener('change', () => state.sensors.setConsent($('consent').checked));
  state.live = new LiveShow($('live-view'), {
    onBubble(text, line) {
      const spoken = resolveBubble(text, line, '...');
      const gloss = String(line || '').trim();
      $('bubble').replaceChildren();
      const strong = document.createElement('b');
      strong.textContent = spoken;
      $('bubble').append(strong);
      if (gloss && gloss !== spoken) {
        const span = document.createElement('span');
        span.textContent = gloss;
        $('bubble').append(span);
      }
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
    const exploring = $('view-explore').classList.contains('on');
    const result = grant(state.store, state.genome.seed, 0, exploring ? 0.4 : 0.1);
    if (!result) return;
    saveStore(state.store, localStorage);
    syncCompanion();
  }, 5000);
  window.addEventListener('message', (event) => {
    const data = event.data;
    if (!data || data.source !== 'living-universe' || data.type !== 'lu-state') return;
    if (event.source !== window.parent) return;
    state.world = String(data.world || 'EARTH');
    $('world-name').textContent = state.world;
  });
  if (window.parent !== window) window.parent.postMessage({ type: 'sb-spark-ready' }, '*');
  window.addEventListener('storage', (event) => {
    if (event.key !== STORE_KEY) return;
    state.store = loadStore(localStorage);
    if (state.genome) {
      syncCompanion();
      paintStages(state.genome);
      renderChat();
    }
    renderBestiary();
  });
}

function saveBeastName() {
  const beast = activeBeast();
  if (!beast) { status('Spark a beast before naming it.'); return; }
  const renamed = careRename(state.store, beast.seed, $('beast-name').value);
  if (!renamed) { status('Use letters or numbers, up to 16 characters.'); return; }
  saveStore(state.store, localStorage);
  paintStages(state.genome);
  syncCompanion();
  renderBestiary();
  status(`${renamed.displayName} is saved on this device. The sparked look stays ${state.genome.names['1']}.`);
}

function renderChat() {
  const root = $('chat-log');
  root.replaceChildren();
  const lines = state.genome ? (state.chats.get(state.genome.seed) || []) : [];
  if (!lines.length) {
    const empty = document.createElement('p');
    empty.textContent = 'Say hello. The beast remembers your name and short notes on this device.';
    root.append(empty);
    return;
  }
  for (const line of lines) {
    const row = document.createElement('p');
    row.className = line.who;
    const strong = document.createElement('b');
    strong.textContent = line.who === 'you' ? 'You' : (line.name || 'Beast');
    row.append(strong, document.createTextNode(` ${line.text}`));
    root.append(row);
  }
  root.scrollTop = root.scrollHeight;
}

function pushChat(who, text, name) {
  if (!state.genome) return;
  const lines = state.chats.get(state.genome.seed) || [];
  lines.push({ who, text, name });
  state.chats.set(state.genome.seed, lines.slice(-24));
  renderChat();
}

async function sendChat() {
  const beast = activeBeast();
  if (!beast || !state.genome) { status('Spark a beast before talking.'); return; }
  const message = $('chat-input').value.trim();
  if (!message) return;
  $('chat-input').value = '';
  pushChat('you', message);
  const result = await careTalk(state.store, beast.seed, message, {
    temperament: state.genome.temperament,
    island: state.genome.island,
    element: state.genome.element,
    body: state.genome.body,
    displayName: titleOf(),
    speciesName: speciesAt(beast.stage || 1),
    keeperName: state.store.playerName || '',
  }, {
    url: $('chat-endpoint').value,
    protocol: $('chat-protocol').value,
    model: $('chat-model').value,
    key: $('chat-key').value,
  });
  saveStore(state.store, localStorage);
  pushChat('beast', result.text, titleOf());
  state.live.present(result.text, result.text, 3.4);
  status(result.source === 'model'
    ? 'Reply from your local model. The beast is still a game companion, not a conscious being.'
    : 'Reply from the on-device rules.');
}

function stopGame() {
  if (state.game?.stop) state.game.stop();
  state.game = null;
  $('game-panel').hidden = true;
  $('rhythm').hidden = true;
  $('memory-pad').hidden = true;
}

function finishTraining(activity, score) {
  const beast = activeBeast();
  if (!beast) { status('Spark a beast before training.'); return; }
  const result = careTrain(state.store, beast.seed, activity, score);
  if (!result.ok) {
    status(trainingBlurb(result, titleOf()));
    return;
  }
  saveStore(state.store, localStorage);
  state.preview = false;
  const beforeSpecies = speciesAt(result.before || 1);
  const species = speciesAt(result.beast.stage);
  syncCompanion();
  paintStages(state.genome);
  const line = trainingBlurb(result, titleOf());
  state.live.present(line, line, 2.8);
  if (result.grew) {
    status(`${titleOf()} evolved from ${beforeSpecies} into ${species}, stage ${result.beast.stage}. This form was earned by training.`);
    state.live.say(`${species}.`, 'spark', 2.6);
  } else {
    const goal = nextStageGoal(result.beast.xp);
    status(goal ? `${line} ${result.beast.xp}/${goal} xp.` : `${line} Final form.`);
  }
}

function startFocus() {
  const beast = activeBeast();
  if (!beast) { status('Spark a beast before training.'); return; }
  if ((beast.energy ?? 100) < 16) { status(trainingBlurb({ ok: false, reason: 'tired' }, titleOf())); return; }
  stopGame();
  $('game-panel').hidden = false;
  $('rhythm').hidden = false;
  $('game-title').textContent = 'Tap Spark when the gold mark sits in the bright band. Six beats.';
  $('game-status').textContent = 'Beat 1 of 6.';
  const mark = $('rhythm-mark');
  let pos = 8;
  let dir = 1;
  let hits = 0;
  let beat = 0;
  let armed = true;
  let beatStarted = performance.now();
  let last = beatStarted;
  let running = true;
  const finish = () => {
    if (!running) return;
    running = false;
    stopGame();
    finishTraining('focus', scoreFocus(hits, 6));
  };
  const settle = (clicked) => {
    if (!armed || !running) return;
    armed = false;
    const center = clicked && Math.abs(pos - 50) <= 12;
    if (center) hits += 1;
    beat += 1;
    $('game-status').textContent = `${hits} of ${beat} in the band. Beat ${Math.min(beat + 1, 6)} of 6.`;
    if (beat >= 6) finish();
    else {
      beatStarted = performance.now();
      setTimeout(() => { if (running) armed = true; }, 220);
    }
  };
  const frame = (now) => {
    if (!running) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    pos += dir * dt * 62;
    if (pos > 92) { pos = 92; dir = -1; }
    if (pos < 8) { pos = 8; dir = 1; }
    mark.style.left = `${pos}%`;
    if (armed && now - beatStarted > 1200) settle(false);
    requestAnimationFrame(frame);
  };
  $('rhythm-hit').onclick = () => settle(true);
  state.game = { stop() { running = false; } };
  requestAnimationFrame(frame);
}

function startMemory() {
  const beast = activeBeast();
  if (!beast) { status('Spark a beast before training.'); return; }
  if ((beast.energy ?? 100) < 16) { status(trainingBlurb({ ok: false, reason: 'tired' }, titleOf())); return; }
  stopGame();
  const glyphs = ['sun', 'drop', 'leaf', 'bolt'];
  const length = Math.min(5, 3 + ((beast.stage || 1) - 1));
  const shown = Array.from({ length }, () => glyphs[Math.floor(Math.random() * glyphs.length)]);
  const answer = [];
  $('game-panel').hidden = false;
  $('memory-pad').hidden = false;
  $('game-title').textContent = 'Watch the sparks, then repeat them in order.';
  $('game-status').textContent = 'Watch...';
  const pad = $('memory-pad');
  pad.replaceChildren();
  const buttons = glyphs.map((glyph) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = glyph;
    button.disabled = true;
    button.addEventListener('click', () => {
      answer.push(glyph);
      button.classList.add('on');
      setTimeout(() => button.classList.remove('on'), 160);
      if (answer.length >= shown.length) {
        pad.querySelectorAll('button').forEach((node) => { node.disabled = true; });
        const score = scoreMemory(shown, answer);
        stopGame();
        finishTraining('memory', score);
      }
    });
    pad.append(button);
    return button;
  });
  let step = 0;
  let timer = null;
  const play = () => {
    if (step >= shown.length) {
      $('game-status').textContent = 'Your turn.';
      buttons.forEach((button) => { button.disabled = false; });
      return;
    }
    const glyph = shown[step];
    $('game-status').textContent = glyph;
    buttons.forEach((button) => button.classList.toggle('on', button.textContent === glyph));
    step += 1;
    timer = setTimeout(() => {
      buttons.forEach((button) => button.classList.remove('on'));
      timer = setTimeout(play, 220);
    }, 560);
  };
  state.game = { stop() { clearTimeout(timer); } };
  timer = setTimeout(play, 400);
}

boot();
