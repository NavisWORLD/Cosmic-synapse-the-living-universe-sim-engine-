/**
 * Pair Muse panel on the Spark tab. DOM only; the signal work is in muse-pair.mjs.
 * The page passes in its own spark, live-beast, and play-link functions so a
 * brainwave spark goes through exactly the same path (and save format) as any
 * other spark.
 */
import {
  BANDS, bindRecipe, bluetoothSupport, CAPTURE_SECONDS, loadSnapshots, MusePair, resparkFromSnapshot,
  saveSnapshot, SENSORS, SNAPSHOT_KEY,
} from './muse-pair.mjs';
import { buildGenome } from './genome.mjs';
import { renderSprite } from './render.mjs';
import { paintSprite } from './draw.mjs';

const MOOD_TEXT = {
  serene: 'Serene: calm alpha is leading, so your beast slows, breathes deep, and gets sleepy-eyed.',
  energetic: 'Energetic: beta is leading, so your beast speeds up, bounces, and sparkles.',
  balanced: 'Balanced: alpha and beta are close, so your beast keeps its own rhythm.',
};

export function mountMusePanel(app) {
  const $ = (id) => document.getElementById(id);
  const root = $('muse-pair');
  if (!root) return null;
  const support = bluetoothSupport(navigator, window);
  let lastSnapshot = null;
  let mirrorWas = false;

  // Sensor chips and band bars are built once.
  const chips = $('muse-sensors');
  for (const name of SENSORS) {
    const chip = document.createElement('span');
    chip.className = 'muse-chip';
    chip.dataset.sensor = name;
    chip.dataset.level = 'none';
    chip.innerHTML = `<i></i><b>${name}</b> <em>—</em>`;
    chips.append(chip);
  }
  const bars = $('muse-bars');
  const HZ = { delta: '1–4 Hz', theta: '4–8 Hz', alpha: '8–13 Hz', beta: '13–30 Hz', gamma: '30–45 Hz' };
  for (const band of ['alpha', 'beta', 'theta', 'delta', 'gamma']) {
    const row = document.createElement('div');
    row.className = 'muse-bar';
    row.dataset.band = band;
    row.innerHTML = `<span class="muse-band">${band}<small>${HZ[band]}</small></span><span class="muse-track"><span class="muse-fill"></span></span><span class="muse-pct">—</span>`;
    bars.append(row);
  }

  const pairBtn = $('muse-pair-btn');
  const demoBtn = $('muse-demo-btn');
  const offBtn = $('muse-disconnect');
  const sparkBtn = $('muse-spark');
  const mirror = $('muse-mirror');

  if (!support.ok) {
    $('muse-support').hidden = false;
    $('muse-support').textContent = `${support.reason}. iPhone and iPad browsers do not offer Web Bluetooth. The clearly labeled demo signal still works here.`;
    pairBtn.disabled = true;
    root.dataset.support = 'none';
  } else root.dataset.support = 'ok';
  if (window.parent !== window && support.ok) {
    $('muse-frame-note').hidden = false;
    $('muse-open-tab').href = location.href.split('#')[0];
  }

  const pair = new MusePair({
    onState({ state, source, model, name, message }) {
      root.dataset.state = state;
      root.dataset.source = source || '';
      const label = state === 'paired'
        ? (source === 'demo' ? 'DEMO SIGNAL (synthetic, not a headband)' : `Paired: ${name || 'Muse'}${model === 'athena' ? ' (Athena)' : ''}`)
        : state === 'connecting' ? 'Connecting...' : 'Not paired';
      $('muse-conn').textContent = label;
      $('muse-demo-row').hidden = source !== 'demo';
      $('muse-demo-tag').hidden = source !== 'demo';
      pairBtn.disabled = !support.ok || state !== 'idle';
      demoBtn.disabled = state !== 'idle';
      offBtn.disabled = state === 'idle';
      sparkBtn.disabled = state !== 'paired';
      if (state === 'idle') {
        $('muse-battery').textContent = '';
        $('muse-live-note').hidden = true;
        resetBars();
        if (mirrorWas) app.restoreLive();
        mirrorWas = false;
      }
      if (message) app.status(message);
    },
    onFrame(frame) { paint(frame); },
    onBattery(pct) { $('muse-battery').textContent = `battery ${pct}%`; },
  });

  function resetBars() {
    for (const row of bars.children) {
      row.querySelector('.muse-fill').style.width = '0%';
      row.querySelector('.muse-pct').textContent = '—';
    }
    for (const chip of chips.children) {
      chip.dataset.level = 'none';
      chip.querySelector('em').textContent = '—';
    }
    $('muse-mood').textContent = 'Live mirror: waiting for a signal.';
  }

  function paint(frame) {
    for (const chip of chips.children) {
      const q = frame.quality[chip.dataset.sensor];
      chip.dataset.level = q.level;
      chip.querySelector('em').textContent = q.label;
    }
    const s = frame.smooth;
    if (!s) {
      $('muse-mood').textContent = 'Live mirror: no sensor reads good or fair yet. Wet the sensors and settle the band behind your ears.';
      return;
    }
    for (const row of bars.children) {
      const v = s[row.dataset.band];
      row.querySelector('.muse-fill').style.width = `${Math.max(1, Math.round(v * 100))}%`;
      row.querySelector('.muse-pct').textContent = `${Math.round(v * 100)}%`;
    }
    const r = frame.reaction;
    const used = frame.usable.length ? ` from ${frame.usable.join(', ')}` : '';
    $('muse-mood').textContent = `Live mirror${used}: ${MOOD_TEXT[r.mood]} (calm ${r.calm} · energy ${r.focus})`;
    root.dataset.mood = r.mood;
    const note = $('muse-live-note');
    if (mirror.checked) {
      app.live()?.setTarget({ calm: r.calm, focus: r.focus, spark: r.spark });
      mirrorWas = true;
      note.hidden = false;
      note.textContent = `${pair.source === 'demo' ? 'DEMO SIGNAL' : 'Muse'} mirror: ${r.mood} · calm ${r.calm} · energy ${r.focus}. Turn it off on the Spark tab.`;
    } else note.hidden = true;
  }

  pairBtn.addEventListener('click', async () => {
    if (!app.consented()) { app.status('Check the consent box above first. Only averaged band shares are used, and nothing is uploaded.'); return; }
    try { await pair.connect(); } catch { /* message already shown */ }
  });
  demoBtn.addEventListener('click', () => {
    try { pair.startDemo(Number($('muse-demo-mix').value)); } catch (error) { app.status(error.message); }
  });
  $('muse-demo-mix').addEventListener('input', () => pair.setDemoMix(Number($('muse-demo-mix').value)));
  offBtn.addEventListener('click', () => pair.disconnect());
  // Unchecking consent ends a real headband session right away.
  $('consent')?.addEventListener('change', () => { if (!$('consent').checked && pair.source === 'muse') pair.disconnect(); });
  mirror.addEventListener('change', () => { if (!mirror.checked && mirrorWas) { app.restoreLive(); mirrorWas = false; } });
  $('muse-watch').addEventListener('click', () => app.showView('live'));

  sparkBtn.addEventListener('click', async () => {
    if (!app.consented()) { app.status('Consent is required before a beast is sparked.'); return; }
    if (!app.table()) { app.status('The recorded quantum table is still loading.'); return; }
    sparkBtn.disabled = true;
    const bar = $('muse-progress-bar');
    $('muse-progress').hidden = false;
    app.status(`Capturing about ${CAPTURE_SECONDS} s of band averages. Sit still with relaxed eyes. Samples stay in this page.`);
    try {
      const snapshot = await pair.captureSnapshot(CAPTURE_SECONDS, (p, n) => {
        bar.style.width = `${Math.round(p * 100)}%`;
        $('muse-progress-text').textContent = `${Math.round(p * CAPTURE_SECONDS)} / ${CAPTURE_SECONDS} s · ${n} clean windows`;
      });
      const traits = { focus: snapshot.traits.focus, calm: snapshot.traits.calm, spark: snapshot.traits.spark };
      const entry = app.spark(traits, snapshot.source === 'demo' ? 'demo' : 'muse');
      const bound = bindRecipe(snapshot, {
        runIndex: entry.runIndex, runKey: entry.genome.inputs.quantum_run, keeper: entry.genome.inputs.user_id, seed: entry.genome.seed,
      });
      saveSnapshot(localStorage, bound);
      lastSnapshot = bound;
      showResult(bound, entry.genome);
      const tag = snapshot.source === 'demo' ? 'the DEMO SIGNAL (synthetic)' : 'your Muse signal';
      app.status(`${entry.genome.names['1']} sparked from ${tag} plus recorded run ${entry.genome.inputs.quantum_run}. Only five band averages were kept.`);
    } catch (error) {
      app.status(error.message);
    } finally {
      $('muse-progress').hidden = true;
      bar.style.width = '0%';
      sparkBtn.disabled = pair.state !== 'paired';
    }
  });

  function showResult(snapshot, genome) {
    const box = $('muse-result');
    box.hidden = false;
    const canvas = $('muse-result-art');
    paintSprite(canvas, renderSprite(genome, 1), 2);
    const b = snapshot.bands;
    const pct = (x) => `${Math.round(x * 100)}%`;
    const src = snapshot.source === 'demo' ? 'DEMO SIGNAL, synthetic' : `Muse ${snapshot.sensors.join('/') || 'sensors'}`;
    $('muse-result-title').textContent = `${genome.names['1']} · ${genome.temperament} ${genome.body} of ${genome.island}`;
    $('muse-result-bands').textContent = `${snapshot.seconds} s, ${snapshot.windows} windows (${src}): alpha ${pct(b.alpha)} · beta ${pct(b.beta)} · theta ${pct(b.theta)} · delta ${pct(b.delta)} · gamma ${pct(b.gamma)}`;
    $('muse-result-traits').textContent = `Traits focus ${snapshot.traits.focus} (beta share) · calm ${snapshot.traits.calm} (alpha share) · spark ${snapshot.traits.spark} (gamma share) → seeded as ${genome.inputs.traits.focus}/${genome.inputs.traits.calm}/${genome.inputs.traits.spark} with recorded IBM run ${genome.inputs.quantum_run}. Seed ${genome.seed.slice(0, 16)}...`;
    app.playLink(genome.seed, $('muse-play'));
    $('muse-verify-out').textContent = '';
  }

  $('muse-verify').addEventListener('click', () => {
    const snap = lastSnapshot;
    if (!snap) return;
    try {
      const again = resparkFromSnapshot(snap, app.table(), buildGenome);
      $('muse-verify-out').textContent = again.matches
        ? `Rebuilt from the saved snapshot alone: same seed ${again.genome.seed.slice(0, 16)}..., same ${again.genome.names['1']}.`
        : 'The snapshot did not rebuild the same seed.';
    } catch (error) { $('muse-verify-out').textContent = error.message; }
  });
  $('muse-download').addEventListener('click', () => {
    if (!lastSnapshot) return;
    const blob = new Blob([JSON.stringify(lastSnapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `spark-muse-${lastSnapshot.recipe.seed.slice(0, 8)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  });
  // The page's "Erase this device" also drops saved brainwave snapshots.
  $('erase')?.addEventListener('click', () => {
    localStorage.removeItem(SNAPSHOT_KEY);
    lastSnapshot = null;
    $('muse-result').hidden = true;
  });
  addEventListener('pagehide', () => { if (pair.state !== 'idle') pair.disconnect(); });

  // Restore the latest saved snapshot card for the active beast, if any.
  const book = loadSnapshots(localStorage);
  app.onReady?.((seed) => {
    const snap = seed && book.bySeed[seed];
    if (!snap || !app.table()) return;
    try {
      const again = resparkFromSnapshot(snap, app.table(), buildGenome);
      if (again.matches) { lastSnapshot = snap; showResult(snap, again.genome); }
    } catch { /* stale snapshot is ignored */ }
  });

  resetBars();
  return { pair, bands: BANDS };
}
