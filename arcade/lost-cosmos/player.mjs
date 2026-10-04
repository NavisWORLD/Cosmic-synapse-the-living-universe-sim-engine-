import { FIXTURE, buildSave, livingProfile, profileFromBcp1, profileFromBeastJson } from './mailbox.mjs';
import { MuseLink, mockTraits } from './muse.mjs';

const $ = (id) => document.getElementById(id);
const status = (text) => { $('status').textContent = text; };

const state = {
  world: { world: 'EARTH', evolution: 0, biosphere: 0, lifeEvents: 0 },
  traits: null,
  beast: null,
  save: null,
  started: false,
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

function currentProfile() {
  const traits = state.traits || { focus: 50, calm: 50, spark: 50 };
  if (state.beast) {
    return { ...state.beast, focus: traits.focus, calm: traits.calm, spark: traits.spark };
  }
  return livingProfile({ ...state.world, ...traits });
}

function bringIn() {
  if (!consented()) {
    status('Consent is required before a creature can cross over.');
    return;
  }
  const profile = currentProfile();
  state.save = buildSave(profile);
  status(`${profile.speciesName} is ready in the cartridge mailbox as ${profile.callsign}. Sense traits only.`);
}

function writeSav(fs, bytes) {
  const dir = '/data/saves';
  if (!fs.analyzePath(dir).exists) fs.mkdir(dir);
  const names = ['lost-cosmos.srm', 'lost-cosmos.gba.srm'];
  for (const name of names) {
    const path = `${dir}/${name}`;
    if (fs.analyzePath(path).exists) fs.unlink(path);
    fs.writeFile(path, bytes);
  }
}

function installEmulator(bytes) {
  const div = $('game');
  div.replaceChildren();
  const slot = document.createElement('div');
  slot.id = 'lc-ejs';
  slot.style.width = '100%';
  slot.style.height = '100%';
  div.appendChild(slot);
  const webgl2 = !!document.createElement('canvas').getContext('webgl2');
  window.EJS_player = '#lc-ejs';
  window.EJS_core = 'gba';
  window.EJS_gameName = 'lost-cosmos';
  window.EJS_gameUrl = 'rom/lost-cosmos.gba';
  window.EJS_pathtodata = '../third_party/emulatorjs/data/';
  window.EJS_startOnLoaded = false;
  window.EJS_threads = false;
  window.EJS_disableAutoLang = false;
  window.EJS_forceLegacyCores = !webgl2;
  window.EJS_color = '#14343d';
  window.EJS_ready = () => {
    window.EJS_emulator.on('saveDatabaseLoaded', (fs) => {
      if (bytes) writeSav(fs, bytes);
    });
  };
  window.EJS_onGameStart = () => {
    const gm = window.EJS_emulator?.gameManager;
    if (!gm || !bytes) return;
    try {
      const path = gm.getSaveFilePath?.();
      if (path && !gm.FS.analyzePath(path).exists) {
        const parent = path.split('/').slice(0, -1).join('/') || '/data/saves';
        if (!gm.FS.analyzePath(parent).exists) gm.FS.mkdir(parent);
        gm.FS.writeFile(path, bytes);
        if (typeof gm.loadSaveFiles === 'function') gm.loadSaveFiles();
      }
    } catch (err) {
      console.warn(err);
    }
    status('Cartridge running. The title screen is the handheld. A living creature enters when a new game is saved.');
    if (new URLSearchParams(location.search).get('demo') === '1') demoPress(gm);
  };
  const script = document.createElement('script');
  script.src = '../third_party/emulatorjs/data/loader.js';
  document.body.appendChild(script);
  state.started = true;
}

async function demoPress(gm) {
  const press = async (button) => {
    gm.simulateInput(0, button, 1);
    await new Promise((r) => setTimeout(r, 250));
    gm.simulateInput(0, button, 0);
    await new Promise((r) => setTimeout(r, 700));
  };
  try {
    await new Promise((r) => setTimeout(r, 1200));
    await press(8);
    await new Promise((r) => setTimeout(r, 900));
    await press(3);
  } catch (err) {
    console.warn(err);
  }
}

function onWorldMessage(data) {
  state.world = {
    world: String(data.world || 'EARTH'),
    evolution: Number(data.evolution) || 0,
    biosphere: Number(data.biosphere) || 0,
    lifeEvents: Math.trunc(Number(data.lifeEvents) || 0),
  };
  status(`Linked to ${state.world.world}. Biosphere ${state.world.biosphere.toFixed(3)}, life events ${state.world.lifeEvents}.`);
}

window.addEventListener('message', (event) => {
  const data = event.data;
  if (!data || data.source !== 'living-universe' || data.type !== 'lu-state') return;
  if (event.source !== window.parent) return;
  onWorldMessage(data);
});

$('mock').addEventListener('click', () => {
  if (!consented()) { status('Consent is required before a simulated headband runs.'); return; }
  state.beast = null;
  const traits = mockTraits();
  showTraits(traits);
  status('Simulated headband produced focus, calm, and spark. The waveform was discarded.');
});

const muse = new MuseLink((traits) => {
  showTraits(traits);
  status('Muse traits updated from the latest on-device window.');
});

$('muse').addEventListener('click', async () => {
  if (!consented()) { status('Consent is required before a Muse headband connects.'); return; }
  try {
    state.beast = null;
    await muse.connect();
    status('Muse connected. Traits update from AF7. Samples stay in this page.');
  } catch (err) {
    status(err?.message || 'Muse connection failed.');
  }
});

$('world').addEventListener('click', () => {
  state.beast = null;
  status(`This world will shape the creature: ${state.world.world}.`);
  if (window.parent !== window) window.parent.postMessage({ type: 'lc-pull' }, '*');
});

$('json').addEventListener('change', async () => {
  const file = $('json').files?.[0];
  if (!file) return;
  if (!consented()) { status('Consent is required before a Beast Box profile is read.'); return; }
  try {
    const details = JSON.parse(await file.text());
    state.beast = profileFromBeastJson(details, state.traits || {});
    status(`Beast Box ${state.beast.speciesName} loaded from ${file.name}.`);
  } catch (err) {
    status(err?.message || 'Beast Box JSON was rejected.');
  }
});

$('bin').addEventListener('change', async () => {
  const file = $('bin').files?.[0];
  if (!file) return;
  if (!consented()) { status('Consent is required before a BCP1 profile is read.'); return; }
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    state.beast = profileFromBcp1(bytes, state.traits || {});
    status(`BCP1 ${state.beast.speciesName} loaded from ${file.name}.`);
  } catch (err) {
    status(err?.message || 'BCP1 profile was rejected.');
  }
});

$('bring').addEventListener('click', bringIn);
$('play').addEventListener('click', () => {
  if (state.started) {
    status('The cartridge is already running. Reload this pane to start again.');
    return;
  }
  installEmulator(state.save);
  status(state.save ? 'Starting the cartridge with the living-link save.' : 'Starting the cartridge.');
});

if (new URLSearchParams(location.search).get('demo') === '1') {
  $('consent').checked = true;
  state.world = { world: FIXTURE.world, evolution: FIXTURE.evolution, biosphere: FIXTURE.biosphere, lifeEvents: FIXTURE.lifeEvents };
  showTraits({ focus: FIXTURE.focus, calm: FIXTURE.calm, spark: FIXTURE.spark });
  bringIn();
  installEmulator(state.save);
}

window.parent.postMessage({ type: 'lc-ready' }, '*');
