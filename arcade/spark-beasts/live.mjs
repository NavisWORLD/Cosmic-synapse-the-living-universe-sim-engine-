/**
 * Seeded live companion. Gait, habits, quirks, and reactions come from the genome.
 * The sprite is drawn from the same renderer as the spark portrait.
 */
import { renderSprite } from './render.mjs';
import { utterance, schedule, master } from './voice-synth.mjs';
import { holdBubble, resolveBubble } from './bubble.mjs';

const LINES = {
  Serene: { calm: ['Mm. The stars are humming.', 'So soft. Stay like this.'], focus: ['I see it too.', 'Quiet eyes, clear sky.'], spark: ['Oh. Little lights.', 'A warm fizz in my core.'], neutral: ['Breathe with me.', 'The island is calm today.'] },
  Curious: { calm: ['Is this what dreaming feels like?'], focus: ['What is that pattern?', 'Let me look closer.'], spark: ['Everything is sparkly.', 'Again. Do it again.'], neutral: ['What is over there?', 'Hmm. I wonder.'] },
  Fierce: { calm: ['A short rest. That is all.'], focus: ['I am ready. Are you?'], spark: ['Feel that fire.', 'Burn bright, keeper.'], neutral: ['Got anything to chase?'] },
  Dreamy: { calm: ['Cosmic marshmallows.'], focus: ['Oh. I am awake.'], spark: ['Fireflies in my head.'], neutral: ['The moon told me a secret.'] },
  Steadfast: { calm: ['Steady. Always steady.'], focus: ['Holding the line.'], spark: ['Power rising.'], neutral: ['On guard.'] },
  Playful: { calm: ['Nap time.'], focus: ['Peekaboo. I see you.'], spark: ['Zoom zoom zoom.', 'Catch me.'], neutral: ['Play with me?'] },
  Bold: { calm: ['Even heroes rest.'], focus: ['Eyes forward.'], spark: ['Charge.'], neutral: ['Lead the way, keeper.'] },
  Gentle: { calm: ['There, there.'], focus: ['I am listening.'], spark: ['Oh my, sparkles.'], neutral: ['Hello, friend.'] },
};
const HABIT_LINE = { yawn: '*yawn*', sniff: 'sniff sniff', doze_off: 'zz', stretch: 'nnngh', look_around: 'hm?', sparkle_burst: 'sparkle', peek: 'peek' };
const GLY = { z: ['111', '001', '010', '100', '111'], '!': ['1', '1', '1', '0', '1'], n: ['011', '010', '010', '110', '110'] };

function mulberry32(a) {
  return function next() {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

function bake(sprite) {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  canvas.getContext('2d').putImageData(new ImageData(sprite.rgba, 64, 64), 0, 0);
  return canvas;
}

export class LiveShow {
  constructor(canvas, hooks = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.hooks = hooks;
    this.target = { focus: 30, calm: 30, spark: 20 };
    this.felt = { focus: 30, calm: 30, spark: 20 };
    this.stage = 1;
    this.drift = false;
    this.translate = true;
    this.voiceOn = false;
    this.audio = null;
    this.output = null;
    this.running = false;
    this.last = 0;
    this.T = 0;
    this.utteranceCount = 0;
  }

  setTarget(traits) {
    for (const key of ['focus', 'calm', 'spark']) if (traits[key] != null) this.target[key] = traits[key];
  }

  setDrift(on) { this.drift = Boolean(on); }

  setStage(stage) {
    this.stage = stage;
    if (this.genome) this.sheet = this.makeSheet(this.genome, stage);
  }

  makeSheet(genome, stage) {
    const eyes = genome.eye_style || 'round';
    return {
      back: bake(renderSprite(genome, stage, { layer: 'back', shadow: false })),
      open: bake(renderSprite(genome, stage, { layer: 'main', eyes, shadow: false })),
      sleepy: bake(renderSprite(genome, stage, { layer: 'main', eyes: 'sleepy', shadow: false })),
      closed: bake(renderSprite(genome, stage, { layer: 'main', eyes: 'closed', shadow: false })),
      sparkle: bake(renderSprite(genome, stage, { layer: 'main', eyes: 'sparkle', shadow: false })),
    };
  }

  show(genome, stage = 1) {
    this.genome = genome;
    this.stage = stage;
    this.sheet = this.makeSheet(genome, stage);
    const behavior = genome.behavior;
    this.state = {
      rnd: mulberry32(behavior.prng_seed),
      phase: 0, aphase: 0, bphase: 0,
      facing: genome.facing === 'left' ? -1 : 1,
      nextBlink: 1, blinkUntil: -1,
      habits: behavior.habits.map((habit) => ({ ...habit, next: 2 + habit.every_s * 0.5 })),
      quirks: behavior.quirks.map((quirk) => ({ ...quirk, next: 1.5 + quirk.every_s * 0.5 })),
      act: null, qact: null, wx: 0, wv: 0, parts: [], mood: 'neutral', moodSince: 0,
      lastSay: -99, bubbleUntil: -1, bubbleText: '', bubbleLine: '', prev: { ...this.felt }, dash: 0, paceDir: 1, lastBeat: -1, echo: 0, talk: null, lookFlip: false,
    };
    this.hooks.onName?.(`${genome.names[String(stage)]}  ${'I'.repeat(stage)}`);
    this.say(this.ruleLine('neutral'), 'neutral', 2.2);
  }

  enableVoice() {
    if (!this.audio) {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      this.audio = new Ctx();
      this.output = master(this.audio);
    }
    this.voiceOn = true;
    this.audio.resume();
    if (this.genome) this.say(this.ruleLine('neutral'), 'neutral', 2);
  }

  disableVoice() { this.voiceOn = false; }

  ruleLine(mood) {
    const pool = (LINES[this.genome.temperament] || LINES.Gentle)[mood] || LINES.Gentle.neutral;
    let line = pool[Math.floor(this.state.rnd() * pool.length)];
    if (this.state.rnd() < 0.5) line += ` ${this.genome.behavior.tic}`;
    return line;
  }

  present(text, line, dur = 2.2) {
    if (!this.state) return;
    const next = holdBubble(
      { text: this.state.bubbleText, line: this.state.bubbleLine, until: this.state.bubbleUntil },
      { text, line, dur },
      this.T,
    );
    this.state.bubbleText = next.text;
    this.state.bubbleLine = next.line;
    this.state.bubbleUntil = next.until;
    this.state.lastSay = this.T;
    const gloss = this.translate ? next.line : '';
    this.hooks.onBubble?.(next.text, gloss && gloss !== next.text ? gloss : '');
  }

  say(line, mood, dur = 2.4, drive = null) {
    if (!this.genome || !this.state) return;
    const safeLine = resolveBubble(line, this.genome.behavior?.tic, '...');
    try {
      const felt = drive || this.frameDrive || { focus: 0, calm: 0, spark: 0 };
      const spoken = utterance(this.genome.voice, this.stage, mood, this.utteranceCount, felt);
      this.utteranceCount += 1;
      const text = resolveBubble(spoken.text, safeLine, this.genome.behavior?.tic);
      this.present(text, safeLine, Math.max(dur, spoken.dur + 1.1));
      this.state.talk = { u: spoken, t0: this.T };
      if (this.voiceOn && this.audio) schedule(this.audio, this.output, this.audio.currentTime + 0.03, this.genome.voice, spoken);
    } catch {
      this.present(safeLine, safeLine, dur);
    }
  }

  glyph(ch, x, y, color) {
    const rows = GLY[ch];
    if (!rows) return;
    this.ctx.fillStyle = color;
    rows.forEach((row, j) => [...row].forEach((cell, i) => { if (cell === '1') this.ctx.fillRect(Math.round(x) + i, Math.round(y) + j, 1, 1); }));
  }

  update(dt) {
    const S = this.state;
    const b = this.genome;
    const be = b.behavior;
    this.T += dt;
    if (this.drift) {
      for (const key of ['focus', 'calm', 'spark']) {
        this.target[key] = clamp(this.target[key] + (Math.sin(this.T * (0.21 + 0.07 * key.length) + key.length) * 0.6 + (S.rnd() - 0.5)) * 22 * dt * 2, 0, 100);
      }
      this.hooks.onDrift?.(this.target);
    }
    const follow = 1 - Math.exp(-dt / be.latency_s);
    for (const key of ['focus', 'calm', 'spark']) this.felt[key] += (this.target[key] - this.felt[key]) * follow;
    const drv = {};
    for (const key of ['focus', 'calm', 'spark']) {
      const felt = this.felt[key];
      drv[key] = (0.3 * felt / 100 + 0.7 * clamp((felt - be.thresholds[key]) / (100 - be.thresholds[key]), 0, 1)) * be.sensitivity[key];
    }
    this.frameDrive = drv;
    this.hooks.onDrive?.(drv, this.felt);
    let mood = 'neutral';
    let best = 0.2;
    for (const key of ['focus', 'calm', 'spark']) if (drv[key] > best) { best = drv[key]; mood = key; }
    if (mood !== S.mood && this.T - S.moodSince > 0.8) {
      S.mood = mood;
      S.moodSince = this.T;
      if (S.rnd() < 0.45 + 0.55 * be.chattiness) this.say(this.ruleLine(mood), mood, 2.6, drv);
    }
    const jump = Math.abs(this.felt.spark - S.prev.spark) + Math.abs(this.felt.focus - S.prev.focus) + Math.abs(this.felt.calm - S.prev.calm);
    S.prev = { ...this.felt };
    const fl = be.flavors;
    const dc = drv.calm;
    const df = drv.focus;
    const ds = drv.spark;
    let tempo = be.tempo_hz * (1 + 1.3 * ds - 0.55 * dc) * (fl.focus === 'freezes' ? 1 - 0.5 * df : 1);
    if (S.qact?.name === 'freezes_mid_beat') tempo = 0;
    S.phase += 2 * Math.PI * tempo * dt;
    S.aphase += 2 * Math.PI * tempo * be.appendage_mul * (1 + 1.5 * ds) * dt;
    S.bphase += 2 * Math.PI * be.breath_hz * (1 - 0.35 * dc + 0.6 * ds) * dt;
    const beat = Math.floor(S.phase / (2 * Math.PI));
    const acc = be.accents[((beat % be.accents.length) + be.accents.length) % be.accents.length];
    if (beat !== S.lastBeat) {
      S.lastBeat = beat;
      if (acc && fl.spark === 'spins' && ds > 0.35) S.facing *= -1;
      if (acc && be.quirks.some((quirk) => quirk.name === 'echo_bounce')) S.echo = 0.35;
      if (ds > 0.2 && S.rnd() < ds * (fl.spark === 'glitters' ? 1.6 : 0.6)) this.emit('s', 1 + Math.round(ds * 3));
    }
    S.echo = Math.max(0, S.echo - dt);
    const ph = S.phase + be.swing * Math.sin(S.phase);
    let amp = be.amplitude_px * (1 + 1.6 * ds) * (1 - 0.7 * dc) * (acc ? 1.7 : 1);
    if (fl.focus === 'freezes' || fl.focus === 'stares') amp *= 1 - 0.85 * clamp(df, 0, 1);
    if (fl.spark === 'bounces') amp *= 1 + 1.2 * ds;
    let dx = 0;
    let dy = 0;
    let sw = 0;
    let sh = 0;
    if (be.gait === 'bob') dy = -amp * (0.5 - 0.5 * Math.cos(ph));
    else if (be.gait === 'hop') { const u = Math.abs(Math.sin(ph / 2)); dy = -amp * 2.2 * u; if (u < 0.18) sh = 1; }
    else if (be.gait === 'sway') { dx = amp * Math.sin(ph); dy = -0.5 * amp * Math.abs(Math.sin(ph)); }
    else if (be.gait === 'float') dy = amp * Math.sin(ph * 0.5) - 2;
    else if (be.gait === 'wobble') { sw = Math.round(Math.sin(ph) * Math.min(3, amp * 0.8)); dy = -0.4 * amp * Math.abs(Math.cos(ph)); }
    else if (be.gait === 'scuttle') { dx = Math.sign(Math.sin(ph * 2)) * Math.min(2, amp * 0.6); dy = -(beat % 2); }
    else if (be.gait === 'pulse') { const p = 0.5 + 0.5 * Math.sin(ph); sw = Math.round(p * Math.min(3, amp * 0.7)); sh = -sw; dy = -p * amp * 0.5; }
    if (S.echo > 0) dy -= 2 * Math.sin(Math.PI * S.echo / 0.35);
    if (S.talk) {
      const age = this.T - S.talk.t0;
      if (age > S.talk.u.dur) S.talk = null;
      else if (S.talk.u.syl.some((note) => age >= note.t && age < note.t + note.dur * 0.45)) dy -= 1;
    }
    let eyes = 'open';
    if (dc > 0.35) eyes = 'sleepy';
    if (fl.calm === 'melts') { sh += Math.round(2 * dc); sw += Math.round(2 * dc); }
    if (fl.calm === 'dozes' && dc > 0.6) { eyes = 'closed'; if (S.rnd() < dt * 1.2) this.emit('z'); }
    if (df > 0.3 && eyes === 'open') eyes = 'sparkle';
    if (fl.focus === 'tracks' && df > 0.2) { dx += Math.round(3 * df * Math.sin(this.T * 0.9)); S.facing = Math.cos(this.T * 0.9) > 0 ? 1 : -1; }
    if (fl.focus === 'paces' && df > 0.25) { S.wx += S.paceDir * dt * 7 * df; if (Math.abs(S.wx) > 9) { S.paceDir *= -1; S.facing = S.paceDir; } }
    if (fl.spark === 'zooms' && ds > 0.35 && S.dash <= 0 && S.rnd() < dt * 0.8 * ds) { S.dash = 0.5; S.dashDir = S.rnd() < 0.5 ? -1 : 1; S.facing = S.dashDir; }
    if (S.dash > 0) { S.dash -= dt; S.wx = clamp(S.wx + S.dashDir * dt * 40, -14, 14); }
    for (const quirk of S.quirks) {
      if (quirk.name === 'wanders' || quirk.name === 'moonwalk') {
        S.wv += (S.rnd() - 0.5) * dt * 6 * quirk.strength;
        S.wv *= 0.98;
        S.wx = clamp(S.wx + S.wv * dt * 4, -10, 10);
        if (Math.abs(S.wv) > 0.3) S.facing = (quirk.name === 'moonwalk' ? -1 : 1) * Math.sign(S.wv || 1);
      }
      if (this.T >= quirk.next) {
        quirk.next = this.T + quirk.every_s * (0.6 + 0.8 * S.rnd());
        if (quirk.name === 'hiccups') { S.qact = { name: 'hic', until: this.T + 0.15 }; if (S.rnd() < 0.5) this.present('hic!', '', 1.6); }
        if (quirk.name === 'shivers') S.qact = { name: 'shiver', until: this.T + 0.6 };
        if (quirk.name === 'freezes_mid_beat') S.qact = { name: 'freezes_mid_beat', until: this.T + 0.7 };
      }
    }
    if (be.quirks.some((quirk) => quirk.name === 'startles') && jump / Math.max(dt, 1e-3) > 90 && this.T > (S.startleCD || 0)) {
      S.startleCD = this.T + 2.5;
      S.qact = { name: 'hic', until: this.T + 0.2 };
      this.emit('!', 1);
    }
    if (S.qact) {
      if (this.T > S.qact.until) S.qact = null;
      else {
        if (S.qact.name === 'hic') dy -= 3;
        if (S.qact.name === 'shiver') dx += (Math.floor(this.T * 30) % 2 ? 1 : -1);
      }
    }
    if (!S.act) {
      for (const habit of S.habits) {
        if (this.T < habit.next) continue;
        habit.next = this.T + habit.every_s * (0.6 + 0.8 * S.rnd());
        const dur = { look_around: 1.6, stretch: 1.2, turn_around: 0.2, double_hop: 0.9, doze_off: 2.2, shake: 0.7, sparkle_burst: 0.3, tail_flick: 0.6, peek: 1.0, spin_hop: 0.8, yawn: 1.4, sniff: 1.2 }[habit.name] || 1;
        S.act = { name: habit.name, t0: this.T, dur };
        if (HABIT_LINE[habit.name] && S.rnd() < 0.6 * be.chattiness + 0.2 && this.T > S.bubbleUntil) this.present(HABIT_LINE[habit.name], '', 1.8);
        if (habit.name === 'turn_around') S.facing *= -1;
        if (habit.name === 'sparkle_burst') this.emit('s', 8);
        break;
      }
    }
    if (S.act) {
      const u = (this.T - S.act.t0) / S.act.dur;
      if (u >= 1) S.act = null;
      else if (S.act.name === 'look_around') S.lookFlip = Math.floor(u * 4) % 2 === 1;
      else if (S.act.name === 'stretch') sh += u < 0.6 ? -2 : 1;
      else if (S.act.name === 'double_hop') dy -= 6 * Math.abs(Math.sin(u * 2 * Math.PI));
      else if (S.act.name === 'doze_off') { eyes = 'closed'; if (S.rnd() < dt * 2) this.emit('z'); }
      else if (S.act.name === 'shake') dx += (Math.floor(this.T * 16) % 2 ? 1 : -1);
      else if (S.act.name === 'peek') dy += u < 0.5 ? 3 : 0;
      else if (S.act.name === 'spin_hop') { dy -= 5 * Math.sin(u * Math.PI); if (Math.floor(u * 4) !== Math.floor((u - dt / S.act.dur) * 4)) S.facing *= -1; }
      else if (S.act.name === 'yawn') { eyes = 'closed'; sh -= 1; }
      else if (S.act.name === 'sniff') dx += Math.round(Math.sin(u * Math.PI * 6));
    } else S.lookFlip = false;
    if (this.T >= S.nextBlink) {
      S.blinkUntil = this.T + 0.12;
      const mean = be.blink_mean_s * ((fl.focus === 'stares' && df > 0.3) ? 3 : 1) * (1 - 0.4 * dc);
      S.nextBlink = this.T + (S.rnd() < be.double_blink_p ? 0.25 : -Math.log(1 - S.rnd()) * mean + 0.3);
    }
    if (this.T < S.blinkUntil) eyes = 'closed';
    const breath = Math.round((0.5 - 0.5 * Math.cos(S.bphase)) * (be.breath_px + (dc > 0.5 ? 1 : 0)));
    const appX = Math.round(Math.sin(S.aphase) * be.appendage_px);
    const appY = Math.round(Math.cos(S.aphase) * be.appendage_px * 0.6);
    for (const part of S.parts) {
      part.t += dt;
      part.x += part.vx * dt;
      part.y += part.vy * dt;
      if (part.kind === 's') part.vy += 10 * dt;
    }
    S.parts = S.parts.filter((part) => part.t < part.life).slice(-80);
    this.hooks.onMood?.(`${S.mood} · ${be.gait} ${tempo.toFixed(2)} beats/s`);
    return { dx, dy, sw, sh, eyes, breath, appX, appY, facing: S.facing * (S.lookFlip ? -1 : 1), wx: S.wx };
  }

  emit(kind, n = 1) {
    for (let i = 0; i < n; i++) {
      this.state.parts.push({
        kind,
        x: 24 + 16 + this.state.rnd() * 32 + this.state.wx,
        y: 26 + 14 + this.state.rnd() * 30,
        vx: (this.state.rnd() - 0.5) * 14,
        vy: -8 - this.state.rnd() * 14,
        life: kind === 'z' || kind === 'n' ? 2.2 : 1 + this.state.rnd() * 0.6,
        t: 0,
      });
    }
  }

  draw(frame) {
    const ctx = this.ctx;
    const W = 112;
    const H = 104;
    ctx.fillStyle = '#101834';
    ctx.fillRect(0, 0, W, H);
    const stars = mulberry32(this.genome.behavior.prng_seed ^ 0x5f3759df);
    for (let i = 0; i < 36; i++) {
      const x = Math.floor(stars() * W);
      const y = Math.floor(stars() * 70);
      ctx.fillStyle = Math.sin(this.T * (1 + stars() * 2) + i) > 0.6 ? '#6c7cb0' : '#25305a';
      ctx.fillRect(x, y, 1, 1);
    }
    ctx.fillStyle = '#1a2550';
    ctx.fillRect(0, 88, W, 16);
    ctx.fillStyle = '#22306a';
    ctx.fillRect(0, 88, W, 1);
    const x = Math.round(24 + frame.dx + frame.wx);
    const y = Math.round(26 + frame.dy);
    const lift = Math.max(0, -frame.dy);
    const shadow = Math.max(8, 30 - lift * 2);
    ctx.fillStyle = '#0a1030';
    ctx.fillRect(Math.round(24 + frame.wx + 32 - shadow / 2), 87, Math.round(shadow), 2);
    const home = this.genome.facing === 'left' ? -1 : 1;
    const flip = frame.facing !== home;
    const w = 64 + frame.sw;
    const h = 64 - frame.breath - frame.sh;
    ctx.save();
    if (flip) { ctx.translate(2 * (x + 32), 0); ctx.scale(-1, 1); }
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(this.sheet.back, x + frame.appX, y + frame.appY, 64, 64);
    ctx.drawImage(this.sheet[frame.eyes] || this.sheet.open, x - Math.round(frame.sw / 2), y + (64 - h), w, h);
    ctx.restore();
    for (const part of this.state.parts) {
      if (part.kind === 's') {
        ctx.fillStyle = '#f8c848';
        ctx.fillRect(Math.round(part.x), Math.round(part.y), 1, 1);
      } else this.glyph(part.kind === '!' ? '!' : 'z', part.x, part.y, part.kind === '!' ? '#f8c848' : '#c8e8ff');
    }
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.last = performance.now();
    const loop = (now) => {
      if (!this.running) return;
      const dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;
      if (this.genome && this.state) {
        const frame = this.update(dt);
        this.draw(frame);
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  stop() { this.running = false; }
}
