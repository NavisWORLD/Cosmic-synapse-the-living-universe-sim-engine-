import { FIXTURE, GROWTH_BYTES, GROWTH_OFFSET, MAILBOX_BYTES, MAILBOX_OFFSET, SRAM_SIZE, buildSave, livingProfile, profileFromBcp1, profileFromBeastJson } from './mailbox.mjs';
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
  if (state.started) {
    status('The cartridge is already running. Reload the handheld before preparing an import.');
    return;
  }
  if (!consented()) {
    status('Consent is required before a creature can cross over.');
    return;
  }
  const profile = currentProfile();
  state.save = buildSave(profile);
  status(`${profile.speciesName} is ready in the cartridge mailbox as ${profile.callsign}. Sense traits only.`);
}

function acceptCageSave(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length !== SRAM_SIZE) throw new Error('The cage save was rejected.');
  const mail = MAILBOX_OFFSET;
  const growth = GROWTH_OFFSET;
  for (let i = 0; i < bytes.length; i++) {
    const inMail = i >= mail && i < mail + MAILBOX_BYTES;
    const inGrowth = i >= growth && i < growth + GROWTH_BYTES;
    if (!inMail && !inGrowth && bytes[i] !== 0xff) throw new Error('The cage save touches a protected region.');
  }
  const magic = String.fromCharCode(...bytes.subarray(mail, mail + 4));
  if (magic !== 'LCX1') throw new Error('The cage save has no mailbox.');
  return bytes;
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

async function installEmulator(bytes) {
  if (state.started) return;
  state.started = true;
  $('play').disabled = true;
  let receipt;
  try {
    const response = await fetch('rom/release.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('The cartridge release is unavailable. Reload and try again.');
    receipt = await response.json();
    const rom = await fetch(`rom/lost-cosmos.gba?v=${receipt.sha256}`);
    if (!rom.ok) throw new Error('The cartridge could not be downloaded. Reload and try again.');
    const data = await rom.arrayBuffer();
    if (data.byteLength !== receipt.bytes || data.byteLength < 0xc0 || new Uint8Array(data)[0xb2] !== 0x96)
      throw new Error('The cartridge download is incomplete. Reload and try again.');
    const digest = await crypto.subtle.digest('SHA-256', data);
    const hash = Array.from(new Uint8Array(digest), (v) => v.toString(16).padStart(2, '0')).join('');
    if (hash !== receipt.sha256) throw new Error('The cartridge download does not match this release. Reload and try again.');
  } catch (err) {
    state.started = false;
    $('play').disabled = false;
    status(err?.message || 'The cartridge could not start. Please try again.');
    return;
  }
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
  window.EJS_gameUrl = `rom/lost-cosmos.gba?v=${receipt.sha256}`;
  window.EJS_pathtodata = '../third_party/emulatorjs/data/';
  window.EJS_startOnLoaded = false;
  window.EJS_threads = false;
  // This pinned loader disables automatic locale fetches only with false.
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
    status(`Lost Cosmos V${receipt.version} is running. Choose NEW GAME or CONTINUE on the title screen.`);
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
  script.onerror = () => {
    state.started = false;
    $('play').disabled = false;
    status('The emulator could not load. Reload the handheld and try again.');
  };
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
  if (!data || data.source !== 'living-universe') return;
  if (event.source !== window.parent) return;
  if (data.type === 'lu-state') onWorldMessage(data);
  if (data.type === 'lc-import-save') {
    try {
      const bytes = acceptCageSave(data.save instanceof Uint8Array ? data.save : new Uint8Array(data.save));
      if (state.started) {
        status('Reload the handheld before another creature enters.');
        return;
      }
      state.save = bytes;
      status(`${data.callsign || 'A beast'} is in the cartridge mailbox from the Synapse OS cage.`);
    } catch (err) {
      status(err.message || 'The cage save was rejected.');
    }
  }
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
