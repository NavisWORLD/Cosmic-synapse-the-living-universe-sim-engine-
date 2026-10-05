/**
 * Pair with Meta Muse panel (Spark tab). DOM and timers only; the logic is in meta-muse-link.mjs.
 *
 * Connects the sparked beast to the Beast Box Meta Muse connector over the internet. Meta Muse
 * reaches it through its third-party MCP connectors. Not Bluetooth, not a Meta device, and not
 * the Muse EEG headband (#muse-pair). The page passes in its own store, genome, refresh and chat
 * hooks so Muse care goes through the same Spark care rules and save as the Live tab buttons.
 */
import {
  apiOrigin, applyMuseActions, beastLabel, CONSENT, defaultDeviceName, describeResult, errorText, museApi,
  readLink, sparkSnapshot, SYNC_MS, writeLink,
} from './meta-muse-link.mjs';
import { drawQr } from '../lost-cosmos/qr.mjs';

const TICK_MS = 1000;
const when = (iso) => (iso ? new Date(iso).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : 'never');
function ago(iso) {
  if (!iso) return 'never';
  const s = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 1000));
  const t = new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' });
  return `${t} (${s < 60 ? `${s} s` : `${Math.round(s / 60)} min`} ago)`;
}

export function mountMetaMusePanel(app) {
  const $ = (id) => document.getElementById(id);
  const root = $('meta-muse');
  if (!root) return null;
  const storage = window.localStorage;
  const base = apiOrigin(window.location);
  const connectorUrl = `${base}/api/mcp`;
  let ready = false;
  let busy = false;
  let storageInfo = null;
  let alertText = '';
  let message = '';
  let serverStatus = null;
  let code = null;
  let nameTouched = false;
  let lastSig = '';
  let kickTimer = null;

  $('mm-connector').textContent = connectorUrl;
  $('mm-local').hidden = base === 'https://www.beastboxcosmos.xyz';
  if (!$('mm-local').hidden) $('mm-local').textContent = `Local test server: ${base} (memory storage). Production uses https://www.beastboxcosmos.xyz.`;

  const activeBeast = () => {
    const seed = app.activeSeed();
    return seed ? app.store().beasts[seed] || null : null;
  };
  const labelOf = (seed) => {
    const beast = app.store().beasts[seed];
    return beast ? beastLabel(beast, app.genomeOf(seed)) : 'your beast';
  };
  const linkNow = () => readLink(storage);

  function copy(text) {
    navigator.clipboard?.writeText(text).then(() => { message = 'Copied.'; render(); }, () => { message = 'Copy failed. Select the text and copy it by hand.'; render(); });
  }

  function render() {
    const link = linkNow();
    const beast = activeBeast();
    const pairedName = link ? labelOf(link.seed) : '';
    const name = beast ? beastLabel(beast, app.genomeOf(beast.seed)) : '';
    const deviceInput = $('mm-device');
    if (!nameTouched && document.activeElement !== deviceInput) {
      deviceInput.value = link?.deviceName || serverStatus?.deviceName || defaultDeviceName(link ? pairedName : (name || 'my beast'));
    }
    root.dataset.state = link ? 'paired' : 'idle';
    $('mm-unpaired').hidden = Boolean(link);
    $('mm-paired').hidden = !link;
    $('mm-save-name').hidden = !link;
    $('mm-consent-text').textContent = `Share a minimal snapshot of ${name || 'the sparked beast'} with the Beast Box connector while paired: name, species, element, stage, mood, stats, care values (experience, bond, energy), seed provenance and island. Not chat, remembered notes, keeper name, sensors or brainwave data. Not used for ads or model training.`;
    const storageOff = storageInfo && storageInfo.configured === false;
    $('mm-pair').disabled = !ready || busy || !beast || !$('mm-consent').checked || storageOff;
    $('mm-pair-hint').textContent = !beast ? 'Spark a beast first, then pair it.' : (storageOff ? 'Pairing is off until Beast Box storage is set up.' : '');
    if (link) {
      const missing = !app.store().beasts[link.seed];
      const other = beast && beast.seed !== link.seed;
      $('mm-status').textContent = missing
        ? 'Paired, but the paired beast is not on this device any more. Unpair, then pair the beast you have.'
        : `Paired · ${pairedName}${other ? ' (not the beast shown now)' : ''} · Meta Muse can see and care for it through the connector`;
    } else {
      $('mm-status').textContent = 'Not paired. Nothing leaves this page.';
    }
    const st = serverStatus;
    $('mm-sync').textContent = link
      ? `Last sync: ${ago(link.lastSyncAt)} · syncs about every ${SYNC_MS / 1000} s while this page is open${st ? ` · ${st.pendingActions || 0} care action${st.pendingActions === 1 ? '' : 's'} waiting` : ''}`
      : 'Last sync: never';
    $('mm-activity').textContent = link && st
      ? `Last Meta Muse activity: ${st.lastActivity ? `${st.lastActivity.tool} at ${when(st.lastActivity.at)}` : 'none yet'} · connections: ${st.connections?.length ? st.connections.map((c) => `${c.client} (${c.readOnly ? 'read only' : 'read + care'})`).join(', ') : 'none yet'}`
      : '';
    $('mm-alert').hidden = !alertText;
    $('mm-alert').textContent = alertText;
    $('mm-message').textContent = message;
    $('mm-code-box').hidden = !(link && code);
    $('mm-code-btn').textContent = code ? 'New pairing code' : 'Show pairing code';
    for (const id of ['mm-code-btn', 'mm-sync-now', 'mm-unpair', 'mm-save-name']) $(id).disabled = busy;
  }

  async function loadStorage() {
    const res = await museApi(base, 'storage');
    if (res.ok && res.data) {
      storageInfo = res.data;
      alertText = res.data.configured ? '' : errorText({ status: 503, data: { error: 'storage_not_configured' } });
    } else {
      storageInfo = null;
      alertText = errorText(res);
    }
    render();
  }

  async function loadStatus() {
    const link = linkNow();
    if (!link) return;
    const res = await museApi(base, 'link', { secret: link.deviceSecret });
    if (res.status === 401) { forget('This beast was unpaired (the pairing was removed or expired).'); return; }
    if (res.ok) { serverStatus = res.data; alertText = ''; } else if (res.status === 503 || res.network) alertText = errorText(res);
    render();
  }

  function forget(text) {
    writeLink(storage, null);
    serverStatus = null;
    code = null;
    message = text;
    render();
  }

  async function sync(reason = 'tick') {
    const link = linkNow();
    if (!link || busy) return;
    if (reason === 'tick' && document.visibilityState === 'hidden') return;
    busy = true;
    try {
      const store = app.store();
      const beast = store.beasts[link.seed];
      const snapshot = beast ? sparkSnapshot({ beast, genome: app.genomeOf(link.seed), store }) : undefined;
      const res = await museApi(base, 'sync', { method: 'POST', secret: link.deviceSecret, body: { snapshot, ack: link.applied } });
      if (res.status === 401) { busy = false; forget('This beast was unpaired (the pairing was removed or expired).'); return; }
      if (!res.ok || !res.data) { alertText = errorText(res); return; }
      alertText = '';
      const out = applyMuseActions(app.store(), link.seed, res.data.actions, link.applied);
      const done = out.results.filter((r) => r.ok);
      if (done.length) {
        app.save();
        const name = labelOf(link.seed);
        for (const r of done) if (r.type === 'talk') app.chat(link.seed, r.you, r.beast, name);
        app.refresh(link.seed);
        message = done.map((r) => describeResult(r, labelOf(link.seed))).join(' ');
        app.status(message);
      }
      for (const r of out.results.filter((x) => !x.ok && x.type === 'play')) message = describeResult(r, labelOf(link.seed));
      if (res.data.status) serverStatus = res.data.status;
      const now = linkNow();
      if (now && now.deviceSecret === link.deviceSecret) writeLink(storage, { ...now, applied: out.applied, lastSyncAt: new Date().toISOString() });
      lastSig = signature();
      if (out.results.length) setTimeout(() => { void sync('after-apply'); }, 1500);
    } finally {
      busy = false;
      render();
    }
  }

  function signature() {
    const link = linkNow();
    const b = link && app.store().beasts[link.seed];
    return b ? `${b.xp}|${b.bond}|${Math.round(b.energy ?? 100)}|${b.stage}|${b.displayName}` : '';
  }

  async function pair() {
    const beast = activeBeast();
    if (!beast || !$('mm-consent').checked || busy) return;
    busy = true; message = ''; render();
    const store = app.store();
    const fallback = defaultDeviceName(beastLabel(beast, app.genomeOf(beast.seed)));
    const deviceName = (nameTouched && $('mm-device').value.trim()) || fallback;
    const snapshot = sparkSnapshot({ beast, genome: app.genomeOf(beast.seed), store });
    const res = await museApi(base, 'link', { method: 'POST', body: { consent: CONSENT, snapshot, deviceName } });
    busy = false;
    if (!res.ok || !res.data?.deviceSecret) { alertText = errorText(res); render(); return; }
    alertText = '';
    writeLink(storage, { deviceSecret: res.data.deviceSecret, deviceId: res.data.deviceId || null, deviceName: res.data.deviceName || deviceName, seed: beast.seed, linkedAt: new Date().toISOString(), lastSyncAt: new Date().toISOString(), applied: [] });
    serverStatus = res.data;
    nameTouched = false;
    lastSig = signature();
    message = `Paired ${beastLabel(beast, app.genomeOf(beast.seed))}. Press Show pairing code, then add the connector in Meta Muse and type the code on the Beast Box consent page.`;
    app.status(message);
    render();
  }

  async function makeCode() {
    const link = linkNow();
    if (!link) return;
    const res = await museApi(base, 'code', { method: 'POST', secret: link.deviceSecret, body: {} });
    if (res.status === 401) { forget('This beast was unpaired.'); return; }
    if (!res.ok) { alertText = errorText(res); render(); return; }
    code = res.data;
    message = '';
    $('mm-code').textContent = code.code;
    $('mm-code-note').textContent = `One use. Expires ${when(code.expiresAt)}. When Meta Muse opens the Beast Box consent page, type this code and choose Read only or Read + care actions.`;
    $('mm-onetap').href = code.link || '#';
    $('mm-onetap').hidden = !code.link;
    $('mm-copy-link').hidden = !code.link;
    try { if (code.link) drawQr($('mm-qr'), code.link); $('mm-qr').hidden = !code.link; } catch { $('mm-qr').hidden = true; }
    render();
  }

  async function saveName() {
    const link = linkNow();
    if (!link) return;
    const res = await museApi(base, 'device', { method: 'POST', secret: link.deviceSecret, body: { name: $('mm-device').value } });
    if (!res.ok) { alertText = errorText(res); render(); return; }
    nameTouched = false;
    writeLink(storage, { ...link, deviceName: res.data.deviceName });
    message = `Device name saved: ${res.data.deviceName}. Meta Muse sees it as the connector's title.`;
    void loadStatus();
    render();
  }

  async function unpair() {
    const link = linkNow();
    if (!link || busy) return;
    busy = true; render();
    const res = await museApi(base, 'link', { method: 'DELETE', secret: link.deviceSecret });
    busy = false;
    if (res.ok || res.status === 401) {
      forget('Unpaired. Every Meta Muse token for this beast is revoked and the Beast Box copy is deleted.');
      app.status(message);
      return;
    }
    alertText = `${errorText(res)} Still paired; try Unpair again.`;
    render();
  }

  $('mm-consent').addEventListener('change', render);
  $('mm-device').addEventListener('input', () => { nameTouched = true; });
  $('mm-pair').addEventListener('click', () => { void pair(); });
  $('mm-code-btn').addEventListener('click', () => { void makeCode(); });
  $('mm-sync-now').addEventListener('click', () => { void sync('manual'); });
  $('mm-unpair').addEventListener('click', () => { void unpair(); });
  $('mm-save-name').addEventListener('click', () => { void saveName(); });
  $('mm-copy-url').addEventListener('click', () => copy(connectorUrl));
  $('mm-copy-link').addEventListener('click', () => { if (code?.link) copy(code.link); });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') void sync('visible'); });

  app.onReady(() => {
    ready = true;
    render();
    void loadStorage();
    void loadStatus().then(() => sync('boot'));
  });
  render();
  setInterval(() => { void sync('tick'); }, SYNC_MS);
  // Re-render the clock and names; push soon after a local care change while paired.
  let shownSeed = null;
  setInterval(() => {
    const seed = app.activeSeed();
    if (seed !== shownSeed) { shownSeed = seed; if (!linkNow()) nameTouched = false; }
    render();
    if (!ready || !linkNow()) return;
    const sig = signature();
    if (sig && sig !== lastSig && !kickTimer) {
      kickTimer = setTimeout(() => { kickTimer = null; void sync('change'); }, 3000);
    }
  }, TICK_MS);
  return { sync, render };
}
