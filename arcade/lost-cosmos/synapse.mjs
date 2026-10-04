import { FIXTURE, attachGrowth, buildGrowth, buildSave, livingProfile } from './mailbox.mjs';
import { MuseLink, mockTraits } from './muse.mjs';
import { askModel, encodeTicket, importPayload, suggestionFromText, ticketLink } from './qbeast.mjs';
import { drawQr } from './qr.mjs';
import { admit, cageSave, loadLedger, releaseForTrade, saveLedger, tend } from './synapse-os.mjs';
import { adoptCageRecord, careLines, careRename, careTalk, careTrain, listCareBeasts, loadStore, saveStore, shownName, stampRecord, STORE_KEY, trainingBlurb } from '../spark-beasts/care.mjs';

const $ = (id) => document.getElementById(id);
const status = (text) => { $('status').textContent = text; };
const storage = window.localStorage;
let ledger = loadLedger(storage);
let careStore = loadStore(storage);
let endpointKey = '';
let careSeed = '';
const careLinesLog = new Map();

const state = {
  world: { world: 'EARTH', evolution: 0, biosphere: 0, lifeEvents: 0 },
  traits: { focus: 50, calm: 50, spark: 50 },
  record: null,
  link: '',
};

function consented() {
  return $('consent').checked;
}

function showTraits(traits) {
  state.traits = traits;
  $('focus').textContent = String(traits.focus);
  $('calm').textContent = String(traits.calm);
  $('spark').textContent = String(traits.spark);
}

function paint() {
  const record = state.record;
  if (!record) {
    $('cage').textContent = 'No beast is held.';
    $('memories').replaceChildren();
    return;
  }
  const growth = record.growth;
  $('cage').textContent = `${record.callsign} the ${record.speciesName} is in the cage. Public id ${record.publicHex}. Epoch ${growth.epoch}, layer ${growth.layer}, points ${growth.points}. ${growth.trade ? 'Marked for trade.' : 'Held locally.'} This ledger is play progress.`;
  $('memories').replaceChildren(...(record.memories || []).map((line) => {
    const item = document.createElement('li');
    item.textContent = line;
    return item;
  }));
}

function cageInput() {
  return {
    permissions: ['sense', 'world', 'memory'],
    sense: { ...state.traits },
    world: {
      name: state.world.world,
      biosphere: state.world.biosphere,
      evolution: state.world.evolution,
      lifeEvents: state.world.lifeEvents,
    },
  };
}

async function hold(record, mode = 'receive') {
  state.record = await admit(ledger, record, mode);
  saveLedger(ledger, storage);
  paint();
  refreshCare();
  selectHeldCare();
  return state.record;
}

function onWorld(data) {
  state.world = {
    world: String(data.world || 'EARTH'),
    evolution: Number(data.evolution) || 0,
    biosphere: Number(data.biosphere) || 0,
    lifeEvents: Math.trunc(Number(data.lifeEvents) || 0),
  };
  status(`Linked to ${state.world.world}. Biosphere ${state.world.biosphere.toFixed(3)}, life events ${state.world.lifeEvents}.`);
  if (data.fragment && !state.record) importFragment(data.fragment).catch((err) => status(err.message));
}

async function importFragment(fragment) {
  if (typeof fragment !== 'string') return;
  if (fragment.startsWith('#lcqt=')) {
    const { b64urlToBytes, parseTicket } = await import('./qbeast.mjs');
    await hold(parseTicket(b64urlToBytes(fragment.slice(6))));
    status(`${state.record.callsign} arrived from a share link. The same identity cannot be copied into a second cage slot.`);
  } else if (fragment.startsWith('#lcshare=')) {
    const text = decodeURIComponent(fragment.slice(9));
    const { openShare } = await import('./qbeast.mjs');
    await hold(await openShare(text, $('passphrase').value));
    status(`${state.record.callsign} arrived from a sealed or checksummed share.`);
  }
}

function selectedCareBeast() {
  return careSeed ? careStore.beasts[careSeed] || null : null;
}

function rememberCareStore() {
  saveStore(careStore, storage);
}

function refreshCare() {
  careStore = loadStore(storage);
  if (state.record?.publicHex) {
    try { adoptCageRecord(careStore, state.record); rememberCareStore(); } catch { /* ledger row without a profile stays listed below */ }
  }
  const select = $('care-beast');
  const previous = careSeed || select.value;
  const beasts = listCareBeasts(careStore);
  select.replaceChildren();
  if (!beasts.length) {
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = 'No caged beast yet';
    select.append(empty);
    careSeed = '';
    $('care-stats').textContent = 'Shape or import a beast, or spark one on the SPARK tab.';
    return;
  }
  for (const beast of beasts) {
    const option = document.createElement('option');
    option.value = beast.seed;
    option.textContent = `${shownName(beast, beast.name)} · stage ${beast.stage || 1} · ${beast.xp || 0} xp`;
    select.append(option);
  }
  const next = beasts.some((beast) => beast.seed === previous) ? previous : beasts[0].seed;
  select.value = next;
  showCare(next);
}

function showCare(seed) {
  careSeed = seed || '';
  const beast = selectedCareBeast();
  if (!beast) {
    $('care-stats').textContent = 'Choose a caged beast to talk and train.';
    return;
  }
  if (document.activeElement !== $('care-name')) $('care-name').value = beast.displayName || '';
  $('care-stats').textContent = careLines(beast);
  renderCareLog();
}

function renderCareLog() {
  const root = $('care-log');
  root.replaceChildren();
  const lines = careLinesLog.get(careSeed) || [];
  if (!lines.length) {
    const empty = document.createElement('p');
    empty.textContent = 'Say hello. The beast remembers your name and short notes on this device.';
    root.append(empty);
    return;
  }
  for (const line of lines) {
    const row = document.createElement('p');
    row.className = line.who;
    const who = document.createElement('b');
    who.textContent = line.who === 'you' ? 'You' : (line.name || 'Beast');
    row.append(who, document.createTextNode(` ${line.text}`));
    root.append(row);
  }
  root.scrollTop = root.scrollHeight;
}

function pushCare(who, text, name) {
  if (!careSeed) return;
  const lines = careLinesLog.get(careSeed) || [];
  lines.push({ who, text, name });
  careLinesLog.set(careSeed, lines.slice(-24));
  renderCareLog();
}

function selectHeldCare() {
  if (!state.record?.publicHex) return;
  const id = String(state.record.publicHex).toLowerCase();
  const beast = Object.values(careStore.beasts || {}).find((row) => row.cageId === id);
  if (!beast) return;
  careSeed = beast.seed;
  const select = $('care-beast');
  if (select.value !== beast.seed) select.value = beast.seed;
  showCare(beast.seed);
}

function postSave(play) {
  if (!state.record) throw new Error('There is no beast to send.');
  const beast = selectedCareBeast();
  const matches = beast && beast.cageId === String(state.record.publicHex || '').toLowerCase();
  const record = matches ? stampRecord(state.record, beast) : state.record;
  const bytes = cageSave(record, buildSave, buildGrowth, attachGrowth);
  if (window.parent !== window) {
    window.parent.postMessage({
      type: 'lc-cage-save',
      save: bytes,
      callsign: record.callsign,
      species: state.record.speciesName,
      play,
    }, '*');
  }
  return record;
}

$('mock').addEventListener('click', () => {
  if (!consented()) { status('Consent is required before a simulated headband runs.'); return; }
  showTraits(mockTraits());
  status('Simulated headband produced focus, calm, and spark. The waveform was discarded.');
});

const muse = new MuseLink((traits) => {
  showTraits(traits);
  status('Muse traits updated from the latest on-device window. Samples stay in this page.');
});

$('muse').addEventListener('click', async () => {
  if (!consented()) { status('Consent is required before a Muse headband connects.'); return; }
  try {
    await muse.connect();
    status('Muse connected. Plug the headband in and keep this page open. Traits update from AF7.');
  } catch (err) {
    status(err?.message || 'Muse connection failed. The simulated headband still works.');
  }
});

$('world').addEventListener('click', () => {
  status(`This world will shape the creature: ${state.world.world}.`);
  if (window.parent !== window) window.parent.postMessage({ type: 'lc-pull' }, '*');
});

$('shape').addEventListener('click', async () => {
  if (!consented()) { status('Consent is required before a beast is shaped.'); return; }
  try {
    const profile = livingProfile({ ...state.world, ...state.traits });
    await hold({
      origin: 'living',
      seed: profile.seed,
      family: profile.family,
      familyName: profile.speciesName.toLowerCase(),
      speciesName: profile.speciesName,
      hue: profile.hue,
      ...state.traits,
      callsign: profile.callsign,
      note: 'SHAPED FROM THIS LIVING WORLD.',
      profile,
      publicId: profile.publicId,
      growth: { epoch: '0', layer: 0, points: 0, trade: false, grown: false, memoryCrc: 0, chainCrc: 0 },
      memories: [],
      transfer: null,
    }, 'local');
    status(`${profile.speciesName} entered the cage as ${profile.callsign}. Stats were rebuilt from the world seed.`);
  } catch (err) {
    status(err.message || 'The beast was rejected.');
  }
});

$('key').addEventListener('input', () => { endpointKey = $('key').value; });

$('ask').addEventListener('click', async () => {
  if (!state.record) { status('Shape or import a beast before asking a model for a label.'); return; }
  try {
    const suggestion = await askModel({
      url: $('endpoint').value,
      key: endpointKey,
      protocol: $('protocol').value,
      model: $('model').value,
      family: state.record.familyName,
      seed: state.record.seed || state.record.publicHex,
    });
    state.record.callsign = suggestion.callsign;
    state.record.note = suggestion.note;
    state.record.profile = { ...state.record.profile, callsign: suggestion.callsign };
    paint();
    status(`Label updated to ${suggestion.callsign}. The public identity and stats stayed the same.`);
  } catch (err) {
    status(err.message || 'The model reply was rejected.');
  }
});

$('file').addEventListener('change', async () => {
  const file = $('file').files?.[0];
  if (!file) return;
  if (!consented()) { status('Consent is required before a beast file is read.'); return; }
  try {
    if (file.size > 1048576) throw new Error('That file is too large for the cage.');
    const bytes = new Uint8Array(await file.arrayBuffer());
    const record = await importPayload(bytes, state.traits, { passphrase: $('passphrase').value });
    await hold(record);
    status(`${record.speciesName} imported as ${record.callsign}. Untrusted stats were rebuilt or checked before the cage accepted them.`);
  } catch (err) {
    status(err.message || 'The beast file was rejected.');
  }
});

$('tend').addEventListener('click', async () => {
  if (!consented()) { status('Consent is required before the cage grows.'); return; }
  if (!state.record) { status('Shape or import a beast first.'); return; }
  try {
    state.record = await tend(ledger, state.record, cageInput());
    saveLedger(ledger, storage);
    paint();
    status(`The cage grew. Epoch ${state.record.growth.epoch}, layer ${state.record.growth.layer}, points ${state.record.growth.points}. The cartridge record stays inside its fields.`);
  } catch (err) {
    status(err.message || 'The cage refused that growth step.');
  }
});

async function traded() {
  const row = state.record.publicHex ? ledger.identities[state.record.publicHex] : null;
  if (!row || row.held) state.record = await releaseForTrade(ledger, state.record);
  saveLedger(ledger, storage);
  const { sealShare } = await import('./qbeast.mjs');
  return sealShare(state.record, $('passphrase').value);
}

$('export').addEventListener('click', async () => {
  if (!state.record) { status('There is no beast to share.'); return; }
  try {
    const text = await traded();
    const blob = new Blob([text], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${state.record.callsign.trim().replaceAll(' ', '_') || 'beast'}.qbeast`;
    link.click();
    URL.revokeObjectURL(url);
    paint();
    status('Share downloaded. This cage marked the beast out for trade so a second local copy is refused.');
  } catch (err) {
    status(err.message || 'The share was not written.');
  }
});

$('link').addEventListener('click', async () => {
  if (!state.record) { status('There is no beast to share.'); return; }
  try {
    await traded();
    const page = window.parent !== window ? document.referrer || location.href : location.href;
    state.link = ticketLink(encodeTicket(state.record), page);
    await navigator.clipboard?.writeText(state.link);
    paint();
    status('Trade link copied. It lives in the address fragment, so the static host does not receive the beast.');
  } catch (err) {
    status(err.message || 'The trade link was not created.');
  }
});

$('showqr').addEventListener('click', async () => {
  if (!state.record) { status('There is no beast to share.'); return; }
  try {
    if (!state.link) {
      await traded();
      const page = window.parent !== window ? document.referrer || location.href : location.href;
      state.link = ticketLink(encodeTicket(state.record), page);
    }
    const canvas = $('qr');
    canvas.hidden = false;
    drawQr(canvas, state.link);
    paint();
    status('QR ready. Scanning it opens the same trade ticket.');
  } catch (err) {
    status(err.message || 'The QR symbol was not drawn.');
  }
});

$('send').addEventListener('click', () => {
  if (!state.record) { status('There is no beast to send.'); return; }
  try {
    const sent = postSave(true);
    status(`${sent.callsign} is in the handheld mailbox with ${sent.growth.points} growth points and epoch ${sent.growth.epoch}. Start a new game on the cartridge.`);
  } catch (err) {
    status(err.message || 'The handheld save was rejected.');
  }
});

$('care-beast').addEventListener('change', () => showCare($('care-beast').value));

$('care-rename').addEventListener('click', () => {
  const beast = selectedCareBeast();
  if (!beast) { status('Choose a caged beast before naming it.'); return; }
  const named = careRename(careStore, beast.seed, $('care-name').value);
  if (!named) { status('Use letters or numbers, up to 16 characters.'); return; }
  rememberCareStore();
  refreshCare();
  selectHeldCare();
  status(`${named.displayName} is saved on this device for Spark Beasts and this cage.`);
});

$('care-chat').addEventListener('submit', (event) => {
  event.preventDefault();
  sendCare().catch((err) => status(err.message || 'The beast could not answer.'));
});

$('care-play').addEventListener('click', () => runCareTrain('play'));
$('care-focus').addEventListener('click', () => runCareTrain('focus'));
$('care-rest').addEventListener('click', () => runCareTrain('rest'));

async function sendCare() {
  const beast = selectedCareBeast();
  if (!beast) { status('Choose a caged beast before talking.'); return; }
  const message = $('care-input').value.trim();
  if (!message) return;
  $('care-input').value = '';
  const seed = beast.seed;
  pushCare('you', message);
  const result = await careTalk(careStore, seed, message, {
    displayName: shownName(beast, beast.name),
    speciesName: beast.name,
    island: beast.island,
  }, {
    url: $('endpoint').value,
    protocol: $('protocol').value,
    model: $('model').value,
    key: endpointKey,
  });
  rememberCareStore();
  const named = shownName(careStore.beasts[seed], beast.name);
  refreshCare();
  if (careSeed !== seed) showCare(seed);
  pushCare('beast', result.text, named);
  status(result.source === 'model'
    ? 'Reply from your local model. The beast is still a game companion, not a conscious being.'
    : 'Reply from the on-device rules. Memory is saved with this beast.');
}

function runCareTrain(activity) {
  const beast = selectedCareBeast();
  if (!beast) { status('Choose a caged beast before training.'); return; }
  const result = careTrain(careStore, beast.seed, activity, { quality: 1 });
  const name = shownName(beast, beast.name);
  if (!result.ok) {
    status(trainingBlurb(result, name));
    refreshCare();
    return;
  }
  rememberCareStore();
  refreshCare();
  const line = trainingBlurb(result, shownName(result.beast, result.beast.name));
  if (result.grew) status(`${shownName(result.beast, result.beast.name)} evolved to stage ${result.beast.stage}. This form was earned by training.`);
  else status(`${line} ${result.beast.xp} xp.`);
}

window.addEventListener('storage', (event) => {
  if (event.key !== STORE_KEY && event.key !== 'lc-synapse-os-v1') return;
  if (event.key === 'lc-synapse-os-v1') ledger = loadLedger(storage);
  refreshCare();
  selectHeldCare();
});

refreshCare();

window.addEventListener('message', (event) => {
  const data = event.data;
  if (!data || data.source !== 'living-universe' || data.type !== 'lu-state') return;
  if (event.source !== window.parent) return;
  onWorld(data);
});

if (location.hash.startsWith('#lcqt=') || location.hash.startsWith('#lcshare=')) {
  $('consent').checked = true;
  importFragment(location.hash).catch((err) => status(err.message));
}

if (new URLSearchParams(location.search).get('demo') === '1') {
  $('consent').checked = true;
  state.world = { world: FIXTURE.world, evolution: FIXTURE.evolution, biosphere: FIXTURE.biosphere, lifeEvents: FIXTURE.lifeEvents };
  showTraits({ focus: FIXTURE.focus, calm: FIXTURE.calm, spark: FIXTURE.spark });
  $('shape').click();
}

window.parent.postMessage({ type: 'lc-synapse-ready' }, '*');

export { suggestionFromText };
