import {sha256Hex} from './digest.mjs';
import { verifySparkArt } from './cartridge.mjs';
import { readProgress } from '../sol-beast-lab/design.mjs';
import {batteryName,prepareBattery,keepCoreBattery,cacheNativeBattery,loadNativeBattery} from './battery.mjs';
import {handleOptionalWakeLock} from './wake-lock.mjs';
import {applyHandheldInput,normalizeHandheldInput} from './controls.mjs?controller=beastboy39';
/* Sol Spark handheld adapter. Original living-link player stays unchanged. */
import { FIXTURE, GROWTH_BYTES, GROWTH_OFFSET, MAILBOX_BYTES, MAILBOX_OFFSET, SRAM_SIZE, buildSave, livingProfile, profileFromBcp1, profileFromBeastJson } from '../lost-cosmos/mailbox.mjs';
import { MuseLink, mockTraits } from '../lost-cosmos/muse.mjs';

const $ = (id) => document.getElementById(id);
if(new URLSearchParams(location.search).get('player')==='shell45')document.body.classList.add('player-frame');
const status = (text) => { $('status').textContent = text; };
function startError(message){status(message);window.parent.postMessage({source:'living-universe',type:'sol-spark-start-error',message:String(message).slice(0,180)},location.origin);}

const state = {
  world: { world: 'EARTH', evolution: 0, biosphere: 0, lifeEvents: 0 },
  traits: null,
  beast: null,
  save: null,
  started: false,
  journey: false,
  playerVisible: true,
  audioWanted: false,
};

function gameVolume() {
  return state.audioWanted && state.playerVisible ? 0.35 : 0;
}

// Capture contexts CREATED by the pinned emulator, not only sources currently
// playing: on iOS the OpenAL source list can be empty when audio is suspended.
const createdGameAudioContexts = new Set();
for (const api of ['AudioContext', 'webkitAudioContext']) {
  const Native = window[api];
  if (typeof Native !== 'function') continue;
  try {
    window[api] = new Proxy(Native, {
      construct(target, args) {
        const ctx = Reflect.construct(target, args);
        createdGameAudioContexts.add(ctx);
        return ctx;
      }
    });
  } catch { /* Leave native constructor untouched if this engine forbids patching. */ }
}
function emulatorAudioContexts() {
  const emulator = window.EJS_emulator, gm = emulator?.gameManager;
  const contexts = new Set(createdGameAudioContexts);
  const al = emulator?.Module?.AL?.currentCtx || gm?.Module?.AL?.currentCtx;
  const candidates = [
    al?.audioCtx, al?.ctx, gm?.Module?.SDL2?.audioContext,
    emulator?.Module?.SDL2?.audioContext, emulator?.audioContext
  ];
  for (const ctx of candidates) if (ctx && typeof ctx.resume === 'function') contexts.add(ctx);
  for (const source of al?.sources || []) {
    const ctx = source?.gain?.context;
    if (ctx && typeof ctx.resume === 'function') contexts.add(ctx);
  }
  return [...contexts].filter(ctx => ctx.state !== 'closed');
}

function syncAudioUi(note = '') {
  const button = $('audio');
  const audioStatus = $('audio-status');
  const contexts = emulatorAudioContexts();
  const running = contexts.some((context) => context.state === 'running');
  window.parent.postMessage({source:'living-universe',type:'sol-spark-audio-state',wanted:state.audioWanted,running},location.origin);
  button.setAttribute('aria-pressed', state.audioWanted ? 'true' : 'false');
  button.textContent = state.audioWanted
    ? (running ? '🔊 Game sound on' : '🔊 Tap to resume sound')
    : '🔊 Enable game sound';
  if (audioStatus) {
    audioStatus.textContent = note || (
      state.audioWanted
        ? (running
          ? 'Emulator audio context is running. If silent, check the native cartridge SYSTEM → AUDIO setting and device volume.'
          : 'Safari has not resumed the native emulator context. Tap the sound button in this game frame after the cartridge starts.')
        : 'Game audio stays off until you tap Enable game sound. On iPhone/iPad this tap unlocks Safari audio inside the emulator frame.'
    );
  }
}

async function unlockGameAudio() {
  state.audioWanted = true;
  // Important for iOS Safari: call resume() synchronously from this button's
  // trusted gesture in the same document that owns EmulatorJS.
  const contexts = emulatorAudioContexts();
  const resumes = [];
  for (const context of contexts) {
    if (context.state === 'suspended' || context.state === 'interrupted') {
      try { resumes.push(context.resume()); } catch { /* retry on the next tap */ }
    }
  }
  window.EJS_emulator?.setVolume?.(gameVolume());
  if (resumes.length) await Promise.allSettled(resumes);
  syncAudioUi(contexts.length
    ? ''
    : (state.started
      ? 'The native sound context is not visible yet. Tap again after gameplay begins; also check the cartridge SYSTEM → AUDIO switch.'
      : 'Start the cartridge, then tap this game-frame sound button to unlock iPhone audio.'));
}

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
  state.mailNote = `${profile.speciesName} is ready in the cartridge mailbox as ${profile.callsign}. Sense traits only.`;
  status(state.mailNote);
}

function acceptCageSave(bytes, journey = false) {
  verifySparkArt(bytes);
  const mail=MAILBOX_OFFSET;
  if(journey){
    if(String.fromCharCode(...bytes.subarray(0,4))!=='LCV5'||bytes[4]!==5)throw new Error('The native journey header is missing.');
    const seed=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength).getUint32(mail+10,true);
    const profile=profileFromBcp1(bytes.slice(mail+32,mail+96),{gameSeed:seed});readProgress(profile,bytes);
  }else for(let i=0;i<bytes.length;i++){
    const owned=(i>=MAILBOX_OFFSET&&i<MAILBOX_OFFSET+MAILBOX_BYTES)||(i>=GROWTH_OFFSET&&i<GROWTH_OFFSET+GROWTH_BYTES)||(i>=24704&&i<24832)||i>=31744;
    if(!owned&&bytes[i]!==255)throw new Error('The starter touches a protected journey region.');
  }
  return bytes;
}

async function installEmulator(bytes,{autoStart=false}={}) {
  if (state.started) return;
  if(!bytes){startError('Send your Spark companion first.');return;}
  try{verifySparkArt(bytes);}catch(err){startError(err.message);return;}
  if(bytes&&!consented()){status('Allow the verified companion import before starting the cartridge.');return;}
  try{const cached=!state.journey&&loadNativeBattery(localStorage,bytes);if(cached){bytes=cached;state.resumeFromCheckpoint=true;}}catch(err){startError(err.message);return;}
  state.started = true;
  $('play').disabled = true;
  let receipt;
  let cartridge;
  try {
    const response = await fetch('../lost-cosmos/rom/release.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('The cartridge release is unavailable. Reload and try again.');
    receipt = await response.json();
    const rom = await fetch(`../lost-cosmos/rom/lost-cosmos.gba?v=${receipt.sha256}`);
    if (!rom.ok) throw new Error('The cartridge could not be downloaded. Reload and try again.');
    const data = await rom.arrayBuffer();
    cartridge=data;
    if (data.byteLength !== receipt.bytes || data.byteLength < 0xc0 || new Uint8Array(data)[0xb2] !== 0x96)
      throw new Error('The cartridge download is incomplete. Reload and try again.');
    const hash = await sha256Hex(data);
    if (hash !== receipt.sha256) throw new Error('The cartridge download does not match this release. Reload and try again.');
  } catch (err) {
    state.started = false;
    $('play').disabled = false;
    startError(err?.message || 'The cartridge could not start. Please try again.');
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
  window.EJS_gameName = (bytes?batteryName(bytes):'lost-cosmos')+'.gba';
  // The verified bytes use the creature's stable filename, including its battery.
  window.EJS_gameUrl = URL.createObjectURL(new Blob([cartridge],{type:'application/octet-stream'}));
  window.EJS_pathtodata = '../third_party/emulatorjs/data/';
  window.EJS_startOnLoaded = autoStart;
  window.EJS_threads = false;
  // This pinned loader disables automatic locale fetches only with false.
  window.EJS_disableAutoLang = false;
  window.EJS_forceLegacyCores = !webgl2;
  window.EJS_color = '#14343d';
  window.EJS_volume = gameVolume();
  handleOptionalWakeLock(navigator.wakeLock);
  window.EJS_ready = () => {
    window.EJS_emulator.on('saveDatabaseLoaded', (fs) => {
      if(bytes)try{state.battery=prepareBattery(fs,bytes,{journey:state.journey||state.resumeFromCheckpoint});}catch(err){state.batteryError=err.message;status(err.message);}
    });
    window.EJS_emulator.on('saveSaveFiles',saved=>{try{cacheNativeBattery(localStorage,bytes,saved);}catch{/* Download remains available if browser storage is full. */}});
  };
  window.EJS_onGameStart = () => {
    const gm = window.EJS_emulator?.gameManager;
    window.EJS_emulator?.setVolume?.(gameVolume());
    syncAudioUi();
    if(state.batteryError){gm?.toggleMainLoop?.(1);startError(state.batteryError);return;}
    status(`Lost Cosmos V${receipt.version} is running. Choose NEW GAME or CONTINUE on the title screen.`);
    if (!gm || !bytes) return;
    try {
      const path = gm.getSaveFilePath?.();
      if(path)keepCoreBattery(gm.FS,bytes,path);
      if (path && !gm.FS.analyzePath(path).exists) {
        const parent = path.split('/').slice(0, -1).join('/') || '/data/saves';
        if (!gm.FS.analyzePath(parent).exists) gm.FS.mkdir(parent);
        gm.FS.writeFile(path, state.battery?.bytes||bytes);
        if (typeof gm.loadSaveFiles === 'function') gm.loadSaveFiles();
      }
    } catch (err) {
      console.warn(err);
    }
    status(state.battery?.resumed?'Journey restored. Choose CONTINUE to keep your Spark companion and earned progress.':'Cartridge running. Choose NEW GAME to receive your verified Spark companion.');
    $('save-journey').disabled=false;
    window.parent.postMessage({source:'living-universe',type:'sol-spark-running',resumed:state.battery?.resumed===true},location.origin);
    state.checkpoint=setInterval(checkpointNow,5000);
    if (new URLSearchParams(location.search).get('demo') === '1') demoPress(gm);
  };
  const script = document.createElement('script');
  script.src = '../third_party/emulatorjs/data/loader.js';
  script.onerror = () => {
    state.started = false;
    $('play').disabled = false;
    startError('The game could not load. Please try START LOST COSMOS again.');
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
  const link = `Linked to ${state.world.world}. Biosphere ${state.world.biosphere.toFixed(3)}, life events ${state.world.lifeEvents}.`;
  status(state.mailNote ? `${state.mailNote} ${link}` : link);
}

window.addEventListener('message', (event) => {
  const data = event.data;
  if (!data || data.source !== 'living-universe') return;
  if (event.source !== window.parent || event.origin !== location.origin) return;
  if(data.type==='sol-player-visibility'){
    state.playerVisible=data.active===true;
    window.EJS_emulator?.setVolume?.(gameVolume());syncAudioUi();return;
  }
  if(data.type==='sol-spark-input'){
    const input=normalizeHandheldInput(data.button,data.down);
    const applied=!!input&&applyHandheldInput(window.EJS_emulator?.gameManager,input.button,input.down);
    window.parent.postMessage({source:'living-universe',type:'sol-spark-input-ack',button:input?.button||'',down:input?.down===true,applied},location.origin);
    return;
  }
  if(data.type==='sol-spark-return-request'){
    const bytes=checkpointNow();
    if(!bytes){window.parent.postMessage({source:'living-universe',type:'sol-spark-return-error',message:'Start the cartridge before returning a journey.'},location.origin);return;}
    window.parent.postMessage({source:'living-universe',type:'sol-spark-native-save',save:bytes},location.origin);
    status('Returning the actual native battery to Beast Box.');
    return;
  }
  if (data.type === 'lu-state') onWorldMessage(data);
  if (data.type === 'sol-spark-start') {
    if (!state.save) { startError('Send your Spark companion first.'); return; }
    $('consent').checked = true;
    installEmulator(state.save,{autoStart:true});
    return;
  }
  if (data.type === 'lc-import-save' || data.type === 'sol-spark-journey') {
    try {
      const bytes = acceptCageSave(data.save instanceof Uint8Array ? data.save : new Uint8Array(data.save), data.type === 'sol-spark-journey');
      if (state.started) {
        status('Reload the handheld before another creature enters.');
        return;
      }
      state.save = bytes;
      state.journey = data.type === 'sol-spark-journey';
      state.mailNote = `${data.callsign || 'A beast'} is in the cartridge mailbox with verified Spark art.`;
      status(state.mailNote);
    } catch (err) {
      status(err.message || 'The cage save was rejected.');
    }
  }
});

function checkpointNow(){
 const gm=window.EJS_emulator?.gameManager;if(!gm||!state.save)return null;
 gm.saveSaveFiles();const bytes=gm.getSaveFile(false);
 try{cacheNativeBattery(localStorage,state.save,bytes);}catch{/* The user can still download the exact battery. */}
 return bytes;
}
window.addEventListener('pagehide',checkpointNow);
document.addEventListener('visibilitychange',()=>{if(document.hidden)checkpointNow();});
$('save-journey').addEventListener('click',()=>{
 const bytes=checkpointNow();if(!bytes){status('Start the cartridge before saving a journey.');return;}
 const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'})),a=document.createElement('a');a.href=url;a.download=batteryName(state.save)+'.sav';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 status('Downloaded the actual native battery. Keep it with your Spark .qbeast as a journey backup.');
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
$('audio').addEventListener('click', () => { void unlockGameAudio(); });
syncAudioUi();
$('play').addEventListener('click', () => {
  if (state.started) {
    status('The cartridge is already running. Reload this pane to start again.');
    return;
  }
  installEmulator(state.save);
  if(!state.save||consented())status(state.save ? 'Starting the cartridge with your Spark companion.' : 'Starting the cartridge.');
});

if (new URLSearchParams(location.search).get('demo') === '1') {
  $('consent').checked = true;
  state.world = { world: FIXTURE.world, evolution: FIXTURE.evolution, biosphere: FIXTURE.biosphere, lifeEvents: FIXTURE.lifeEvents };
  showTraits({ focus: FIXTURE.focus, calm: FIXTURE.calm, spark: FIXTURE.spark });
  bringIn();
  installEmulator(state.save);
}

window.parent.postMessage({ type: 'lc-ready' }, '*');
