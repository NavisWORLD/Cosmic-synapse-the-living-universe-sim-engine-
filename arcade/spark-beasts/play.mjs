/** Play in Lost Cosmos: carry one Spark Beast into the V11.2 handheld on this site. */
import { loadTable } from './runs.mjs';
import { renderSprite } from './render.mjs';
import { paintSprite } from './draw.mjs';
import { loadStore, saveStore } from './store.mjs';
import { loadCage, saveCage } from './trade.mjs';
import { preparePlay } from './play-save.mjs';

const $ = (id) => document.getElementById(id);
const status = (text) => { $('status').textContent = text; };
const frame = $('handheld');
const HANDHELD = '../sol-spark-gate/handheld.html';
const PAD_STYLE = '.ejs_virtualGamepad_parent{display:none!important}';
let ready = null;

function handheldWindow() {
  try { return frame.contentWindow; } catch { return null; }
}

function send() {
  const win = handheldWindow();
  if (!ready || !win) return;
  win.postMessage({ source: 'living-universe', type: 'lc-import-save', save: ready.bytes, callsign: ready.callsign, species: ready.species }, location.origin);
}

function fitFrame() {
  let doc;
  try { doc = frame.contentDocument; } catch { return; }
  if (!doc?.documentElement) return;
  // Our pad lives below the screen, so the emulator's own touch overlay stays off.
  if (!doc.getElementById('sb-play-pad-style')) {
    const style = doc.createElement('style');
    style.id = 'sb-play-pad-style';
    style.textContent = PAD_STYLE;
    doc.head?.append(style);
  }
  const fit = () => {
    // The body, not the root, so the frame can also shrink back.
    const height = doc.body?.scrollHeight || 0;
    if (height > 0) frame.style.height = `${Math.ceil(height) + 4}px`;
  };
  fit();
  if (typeof ResizeObserver === 'function' && doc.body) new ResizeObserver(fit).observe(doc.body);
  watchStart(doc);
}

/** Once the cartridge runs, bring the screen and the pad into view together. */
function watchStart(doc) {
  const timer = setInterval(() => {
    const win = handheldWindow();
    if (!win || win.document !== doc) { clearInterval(timer); return; }
    if (!win.EJS_emulator?.gameManager) return;
    clearInterval(timer);
    const game = doc.getElementById('game');
    const top = frame.getBoundingClientRect().top + window.scrollY + (game ? game.offsetTop : 0) - 6;
    window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
    status(`${ready?.label || 'Your beast'} is in the cartridge mailbox. Pick NEW GAME and it joins your party (CONTINUE resumes a saved journey). START, then PARTY, shows it.`);
  }, 500);
}

function bindPad() {
  const held = new Map();
  const input = (key, value) => {
    const gm = handheldWindow()?.EJS_emulator?.gameManager;
    if (!gm?.simulateInput) {
      if (value) status('Start the cartridge in the handheld first. Then these buttons drive the game.');
      return false;
    }
    gm.simulateInput(0, key, value);
    return true;
  };
  for (const button of document.querySelectorAll('#pad [data-key]')) {
    const key = Number(button.dataset.key);
    const press = (event) => {
      event.preventDefault();
      button.setPointerCapture?.(event.pointerId);
      held.set(event.pointerId, button);
      button.classList.add('down');
      input(key, 1);
    };
    const release = (event) => {
      if (held.get(event.pointerId) !== button) return;
      held.delete(event.pointerId);
      button.classList.remove('down');
      input(key, 0);
    };
    button.addEventListener('pointerdown', press);
    button.addEventListener('pointerup', release);
    button.addEventListener('pointercancel', release);
    button.addEventListener('lostpointercapture', release);
    button.addEventListener('contextmenu', (event) => event.preventDefault());
  }
}

async function showCartridge() {
  try {
    const response = await fetch('../lost-cosmos/rom/release.json', { cache: 'no-cache' });
    if (!response.ok) return;
    const receipt = await response.json();
    $('cart').textContent = `Cartridge Lost Cosmos V${receipt.version}, sha256 ${String(receipt.sha256).slice(0, 8)}…, the same file the PLAY GBA tab serves.`;
  } catch { /* The handheld reports a missing cartridge itself. */ }
}

async function boot() {
  bindPad();
  showCartridge();
  const params = new URLSearchParams(location.search);
  const seed = params.get('beast');
  try {
    const table = await loadTable();
    const store = loadStore(localStorage);
    const ledger = loadCage(localStorage);
    ready = await preparePlay({ store, ledger, table, seed });
    saveCage(ledger, localStorage);
    saveStore(store, localStorage);
    paintSprite($('who-art'), renderSprite(ready.genome, ready.stage), 1);
    const species = ready.species;
    $('who-name').textContent = ready.label === species ? species : `${ready.label} (${species})`;
    $('who-meta').textContent = `${ready.genome.island} · stage ${ready.stage} · bond ${Math.round(ready.beast.bond || 0)} · in game as ${ready.callsign}`;
    document.title = `Play ${ready.label} in Lost Cosmos`;
    status(`${ready.label} is packed into a verified starter save. In the handheld below, tick the import box, press Start cartridge, then choose NEW GAME (or CONTINUE for a saved journey).`);
  } catch (error) {
    $('who-name').textContent = 'No beast loaded';
    status(error?.message || 'This beast could not be prepared for the cartridge.');
    $('screen').hidden = true;
    $('pad').hidden = true;
    $('pad-note').hidden = true;
    return;
  }
  window.addEventListener('message', (event) => {
    if (event.origin !== location.origin || event.source !== handheldWindow()) return;
    if (event.data?.type === 'lc-ready') send();
  });
  frame.addEventListener('load', () => { fitFrame(); send(); });
  frame.src = HANDHELD;
}

boot();
