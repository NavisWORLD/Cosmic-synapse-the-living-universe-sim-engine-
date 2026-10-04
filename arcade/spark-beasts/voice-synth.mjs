/**
 * WebAudio babble. Same utterance function as the Python prototype's live/voice.js.
 * No samples and no network. The same seed, stage, mood, and drive speak the same line.
 */

function mulberry(a) {
  return function next() {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const STAGE_PITCH = { 1: 1.28, 2: 1.0, 3: 0.8 };
const STAGE_RATE = { 1: 1.12, 2: 1.0, 3: 0.9 };
const VL = { a: 'a', e: 'e', i: 'i', o: 'o', u: 'u', ee: 'ee', aw: 'aw', ü: 'u' };
const GLIDE = { chirp: 6, coo: -2.5, growl: -3, trill: 0, beep: 0, purr: -1 };
const END = { spark: '!', calm: '~', focus: '.', neutral: '?' };

export function utterance(v, stage, mood, idx, drive) {
  const r = mulberry((v.prng_seed ^ Math.imul(idx + 1, 0x9E3779B1)) >>> 0);
  const floor = (ch) => (mood === ch ? 0.65 : 0);
  const dc = Math.min(1.2, Math.max(floor('calm'), drive.calm || 0));
  const ds = Math.min(1.2, Math.max(floor('spark'), drive.spark || 0));
  const df = Math.min(1.2, Math.max(floor('focus'), drive.focus || 0));
  const rate = v.speed_sps * STAGE_RATE[stage] * (1 + 0.38 * ds - 0.32 * dc + 0.08 * df);
  const pitch = v.base_pitch_hz * STAGE_PITCH[stage] * (1 + 0.24 * ds - 0.10 * dc);
  const gain = v.gain * (1 - 0.45 * dc + 0.1 * ds);
  const jump = v.jump_semitones * (1 + 0.8 * ds - 0.45 * dc - 0.3 * df);
  const [lo, hi] = v.phrase_syllables;
  const n = lo + Math.floor(r() * (hi - lo + 1)) + (ds > 0.6 ? 1 : 0) - (dc > 0.7 && lo > 2 ? 1 : 0);
  const contour = ds > 0.6 ? 'bounce' : v.contour;
  const syl = [];
  const words = [];
  let t = 0;
  for (let i = 0; i < n; i++) {
    const long = v.rhythm[(idx + i) % v.rhythm.length] === 1;
    const dur = (long ? 1.65 : 1.0) / rate * (0.9 + 0.2 * r());
    const u = n > 1 ? i / (n - 1) : 0;
    let semi = contour === 'rise' ? jump * u : contour === 'fall' ? jump * (1 - u) : contour === 'arch' ? jump * Math.sin(Math.PI * u) : (i % 2) * jump;
    semi += (r() - 0.5) * (1.5 + 3 * ds);
    if (v.style === 'beep') semi = Math.round(semi / 2) * 2;
    const f0 = pitch * 2 ** (semi / 12);
    const f1 = f0 * 2 ** ((GLIDE[v.style] * (ds > 0.5 ? 1.4 : 1) * (i === n - 1 && mood === 'spark' ? 1.6 : 1)) / 12);
    const vi = (idx + i) % v.vowel_formants.length;
    const vf = v.vowel_formants[vi];
    const F = [0.5 * v.formants_hz[0] + 0.5 * vf[0], 0.5 * v.formants_hz[1] + 0.5 * vf[1]];
    const amp = gain * (long ? 1 : 0.85) * (0.9 + 0.2 * r());
    syl.push({ t, dur, f0, f1, F, amp });
    const cons = v.consonants[(idx + i * 3) % v.consonants.length];
    let vw = VL[v.vowels[vi]] || 'a';
    if (long) vw += vw.slice(-1);
    words.push(cons + vw);
    t += dur + (0.22 + 0.25 * dc - 0.08 * ds) / rate * (0.7 + 0.6 * r());
  }
  let text = words.join(r() < 0.5 ? '-' : ' ');
  text = text[0].toUpperCase() + text.slice(1) + (END[mood] || '!');
  if (mood === 'spark' && r() < 0.6) text += '!';
  return { syl, text, dur: t, style: v.style };
}

const noiseCache = new WeakMap();

function noiseBuf(ac) {
  if (noiseCache.has(ac)) return noiseCache.get(ac);
  const buffer = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
  const data = buffer.getChannelData(0);
  const r = mulberry(0xC0FFEE);
  for (let i = 0; i < data.length; i++) data[i] = r() * 2 - 1;
  noiseCache.set(ac, buffer);
  return buffer;
}

export function master(ac) {
  const gain = ac.createGain();
  gain.gain.value = 0.4;
  const shaper = ac.createWaveShaper();
  const curve = new Float32Array(2049);
  for (let i = 0; i < curve.length; i++) {
    const x = (i / 1024 - 1) * 3;
    curve[i] = Math.tanh(x) / Math.tanh(3);
  }
  shaper.curve = curve;
  gain.connect(shaper);
  shaper.connect(ac.destination);
  return gain;
}

export function schedule(ac, out, t0, v, u) {
  for (const s of u.syl) {
    const ts = t0 + s.t;
    const te = ts + s.dur;
    const osc = ac.createOscillator();
    osc.type = v.wave;
    osc.frequency.setValueAtTime(s.f0, ts);
    osc.frequency.exponentialRampToValueAtTime(Math.max(40, s.f1), te);
    if (v.vibrato_hz > 0.05) {
      const lfo = ac.createOscillator();
      lfo.frequency.value = v.vibrato_hz;
      const lg = ac.createGain();
      lg.gain.value = s.f0 * (2 ** (v.vibrato_cents / 1200) - 1);
      lfo.connect(lg);
      lg.connect(osc.frequency);
      lfo.start(ts);
      lfo.stop(te + 0.03);
    }
    const env = ac.createGain();
    const att = Math.min(0.025, s.dur * 0.25);
    const rel = Math.min(0.06, s.dur * 0.35);
    env.gain.setValueAtTime(0, ts);
    env.gain.linearRampToValueAtTime(s.amp, ts + att);
    env.gain.setValueAtTime(s.amp, te - rel);
    env.gain.linearRampToValueAtTime(0, te);
    let src = osc;
    if (v.am_hz > 0) {
      const am = ac.createGain();
      am.gain.value = 0.55;
      const lfo = ac.createOscillator();
      lfo.type = 'triangle';
      lfo.frequency.value = v.am_hz;
      const lg = ac.createGain();
      lg.gain.value = 0.45;
      lfo.connect(lg);
      lg.connect(am.gain);
      lfo.start(ts);
      lfo.stop(te + 0.03);
      osc.connect(am);
      src = am;
    }
    const dry = ac.createBiquadFilter();
    dry.type = 'lowpass';
    dry.frequency.value = 900 + 3200 * v.brightness;
    const dg = ac.createGain();
    dg.gain.value = 0.45;
    const b1 = ac.createBiquadFilter();
    b1.type = 'bandpass';
    b1.frequency.value = s.F[0];
    b1.Q.value = v.formant_q;
    const g1 = ac.createGain();
    g1.gain.value = 1.6;
    const b2 = ac.createBiquadFilter();
    b2.type = 'bandpass';
    b2.frequency.value = s.F[1];
    b2.Q.value = v.formant_q;
    const g2 = ac.createGain();
    g2.gain.value = 0.5 + 0.9 * v.brightness;
    src.connect(dry); dry.connect(dg); dg.connect(env);
    src.connect(b1); b1.connect(g1); g1.connect(env);
    src.connect(b2); b2.connect(g2); g2.connect(env);
    if (v.breath > 0.005) {
      const nz = ac.createBufferSource();
      nz.buffer = noiseBuf(ac);
      nz.loop = true;
      const nb = ac.createBiquadFilter();
      nb.type = 'bandpass';
      nb.frequency.value = s.F[1];
      nb.Q.value = 1.2;
      const ng = ac.createGain();
      ng.gain.value = v.breath * 0.6;
      nz.connect(nb); nb.connect(ng); ng.connect(env);
      nz.start(ts, (s.t * 7919) % 0.9);
      nz.stop(te + 0.02);
    }
    env.connect(out);
    osc.start(ts);
    osc.stop(te + 0.03);
  }
}
