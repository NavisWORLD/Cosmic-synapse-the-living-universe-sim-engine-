import { FIXTURE, attachGrowth, buildGrowth, buildSave, livingProfile } from './mailbox.mjs';
import { MuseLink, mockTraits } from './muse.mjs';
import { askModel, encodeTicket, importPayload, suggestionFromText, ticketLink } from './qbeast.mjs';
import { drawQr } from './qr.mjs';
import { admit, cageSave, loadLedger, releaseForTrade, saveLedger, tend } from './synapse-os.mjs';

const $ = (id) => document.getElementById(id);
const status = (text) => { $('status').textContent = text; };
const storage = window.localStorage;
let ledger = loadLedger(storage);
let endpointKey = '';

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

function postSave(play) {
  const bytes = cageSave(state.record, buildSave, buildGrowth, attachGrowth);
  if (window.parent !== window) {
    window.parent.postMessage({ type: 'lc-cage-save', save: bytes, callsign: state.record.callsign, species: state.record.speciesName, play }, '*');
  }
  return bytes;
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
    postSave(true);
    status(`${state.record.callsign} is in the handheld mailbox, including cage epoch ${state.record.growth.epoch}. Start a new game on the cartridge.`);
  } catch (err) {
    status(err.message || 'The handheld save was rejected.');
  }
});

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
