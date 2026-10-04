/**
 * Opt-in signals. Muse and the simulated headband share arcade/lost-cosmos/muse.mjs.
 * Microphone, motion, camera, and keyboard/mouse rhythm are extra soft nudges.
 * Only the three traits are kept. Samples, frames, and key names are discarded.
 */
import { MuseLink } from '../lost-cosmos/muse.mjs';
import { simulateWindows, stabilize, validate } from './signal.mjs';

const clamp = (n) => Math.max(0, Math.min(100, Math.round(n)));

export function blendTraits(base, nudges = {}) {
  const clean = validate(base);
  return {
    focus: clamp(clean.focus + (nudges.focus || 0)),
    calm: clamp(clean.calm + (nudges.calm || 0)),
    spark: clamp(clean.spark + (nudges.spark || 0)),
  };
}

export class SensorHub {
  constructor(onTraits) {
    this.onTraits = onTraits;
    this.consented = false;
    this.windows = [];
    this.base = { focus: 30, calm: 30, spark: 20 };
    this.nudges = { focus: 0, calm: 0, spark: 0 };
    this.mic = null;
    this.camera = null;
    this.motionHandler = null;
    this.rhythmHandler = null;
    this.intervals = [];
    this.muse = new MuseLink((traits) => this.pushWindow(traits));
    this.timer = 0;
  }

  setConsent(on) {
    this.consented = Boolean(on);
    if (!this.consented) this.stopExtras();
  }

  require() {
    if (!this.consented) throw new Error('Consent is required before a signal runs. Raw samples are not stored.');
  }

  pushWindow(traits) {
    this.windows.push(validate(traits));
    if (this.windows.length > 8) this.windows.shift();
    const stable = stabilize(this.windows);
    this.onTraits(stable, { mode: 'window', windows: this.windows.length });
    return stable;
  }

  current() {
    return this.windows.length ? stabilize(this.windows) : blendTraits(this.base, this.nudges);
  }

  holdSliders(traits) {
    this.require();
    this.base = validate(traits);
    return this.pushWindow(blendTraits(this.base, this.nudges));
  }

  simulate(profile = 'mock') {
    this.require();
    this.windows = simulateWindows(profile, 8).map((row) => blendTraits(row, this.nudges));
    const stable = stabilize(this.windows);
    this.base = { ...stable };
    this.onTraits(stable, { mode: 'simulated', profile, windows: this.windows.length });
    return stable;
  }

  async connectMuse() {
    this.require();
    await this.muse.connect();
  }

  async stopMuse() {
    await this.muse.stop();
  }

  async enableMic() {
    this.require();
    if (this.mic || !navigator.mediaDevices?.getUserMedia) throw new Error('Microphone is not available in this browser.');
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    const audio = new AudioContext();
    const source = audio.createMediaStreamSource(stream);
    const analyser = audio.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    const buf = new Uint8Array(analyser.fftSize);
    const timer = setInterval(() => {
      analyser.getByteTimeDomainData(buf);
      let energy = 0;
      for (let i = 0; i < buf.length; i++) {
        const x = (buf[i] - 128) / 128;
        energy += x * x;
      }
      buf.fill(0);
      this.nudges.spark = Math.min(18, Math.sqrt(energy / buf.length) * 90);
    }, 400);
    this.mic = { stream, audio, timer };
  }

  async enableCamera() {
    this.require();
    if (this.camera || !navigator.mediaDevices?.getUserMedia) throw new Error('Camera is not available in this browser.');
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: 64, height: 64 }, audio: false });
    const video = document.createElement('video');
    video.srcObject = stream;
    video.muted = true;
    video.playsInline = true;
    await video.play();
    const canvas = document.createElement('canvas');
    canvas.width = 8;
    canvas.height = 8;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const timer = setInterval(() => {
      ctx.drawImage(video, 0, 0, 8, 8);
      const frame = ctx.getImageData(0, 0, 8, 8);
      let sum = 0;
      for (let i = 0; i < frame.data.length; i += 4) sum += 0.2126 * frame.data[i] + 0.7152 * frame.data[i + 1] + 0.0722 * frame.data[i + 2];
      frame.data.fill(0);
      const brightness = sum / (frame.data.length / 4) / 255;
      this.nudges.calm = Math.max(-12, Math.min(12, (brightness - 0.5) * 24));
    }, 700);
    this.camera = { stream, video, timer };
  }

  async enableMotion() {
    this.require();
    if (this.motionHandler) return;
    if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
      const state = await DeviceMotionEvent.requestPermission();
      if (state !== 'granted') throw new Error('Motion permission was not granted.');
    }
    if (typeof DeviceMotionEvent === 'undefined') throw new Error('Device motion is not available in this browser.');
    this.motionHandler = (event) => {
      const accel = event.accelerationIncludingGravity || event.acceleration;
      if (!accel) return;
      const mag = Math.hypot(accel.x || 0, accel.y || 0, accel.z || 0);
      this.nudges.focus = Math.max(-12, Math.min(12, (mag - 9.8) * 2));
    };
    addEventListener('devicemotion', this.motionHandler);
  }

  enableRhythm() {
    this.require();
    if (this.rhythmHandler) return;
    let last = 0;
    this.rhythmHandler = () => {
      const now = performance.now();
      if (last) {
        this.intervals.push(now - last);
        if (this.intervals.length > 8) this.intervals.shift();
        const mean = this.intervals.reduce((a, b) => a + b, 0) / this.intervals.length;
        const variance = this.intervals.reduce((a, b) => a + (b - mean) ** 2, 0) / this.intervals.length;
        this.nudges.focus = Math.max(this.nudges.focus, Math.min(10, variance / 8000));
        this.nudges.calm = Math.max(-8, Math.min(10, 8 - variance / 6000));
      }
      last = now;
    };
    addEventListener('keydown', this.rhythmHandler);
    addEventListener('pointerdown', this.rhythmHandler);
  }

  stopExtras() {
    if (this.mic) {
      clearInterval(this.mic.timer);
      this.mic.stream.getTracks().forEach((track) => track.stop());
      this.mic.audio.close();
      this.mic = null;
    }
    if (this.camera) {
      clearInterval(this.camera.timer);
      this.camera.stream.getTracks().forEach((track) => track.stop());
      this.camera.video.srcObject = null;
      this.camera = null;
    }
    if (this.motionHandler) {
      removeEventListener('devicemotion', this.motionHandler);
      this.motionHandler = null;
    }
    if (this.rhythmHandler) {
      removeEventListener('keydown', this.rhythmHandler);
      removeEventListener('pointerdown', this.rhythmHandler);
      this.rhythmHandler = null;
    }
    this.nudges = { focus: 0, calm: 0, spark: 0 };
    this.intervals = [];
  }
}
