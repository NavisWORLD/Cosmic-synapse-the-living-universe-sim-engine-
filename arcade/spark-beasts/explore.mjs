/**
 * Eight-island range. Beasts wander, sniff, chase sparks, nap, and follow.
 * A full 3D Earth scene would mean editing the Reality Body renderer, so the
 * ranges live here as a walkable map of the same eight islands.
 */
import { buildGenome } from './genome.mjs';
import { simulateStable } from './signal.mjs';
import { renderSprite } from './render.mjs';
import { sha256Hex } from './hash.mjs';

export const ISLANDS = [
  { name: 'Eridoria Prime', x: 0.18, y: 0.30, biome: 'verdant', tint: '#2f8f4a', profile: 'serene' },
  { name: 'Hollow Verdance', x: 0.38, y: 0.20, biome: 'grove', tint: '#1d6a42', profile: 'steady' },
  { name: 'The Crown', x: 0.60, y: 0.18, biome: 'radiant', tint: '#e2c56a', profile: 'focused' },
  { name: 'The Pale Expanse', x: 0.82, y: 0.32, biome: 'frost', tint: '#d5e6f6', profile: 'dreamy' },
  { name: 'Rust Meridian', x: 0.20, y: 0.68, biome: 'machine', tint: '#d07a3a', profile: 'restless' },
  { name: 'Cinder Drift', x: 0.42, y: 0.74, biome: 'ember', tint: '#e07038', profile: 'sparky' },
  { name: 'Umbral Deep', x: 0.64, y: 0.60, biome: 'umbral', tint: '#6d4d9c', profile: 'dreamy' },
  { name: 'The Shattered Reef', x: 0.84, y: 0.74, biome: 'crystal', tint: '#3ec6c0', profile: 'balanced' },
];

const ACTS = ['wander', 'sniff', 'chase', 'nap', 'biome'];

export function wildRunIndex(islandIndex, count) {
  const hex = sha256Hex(`spark-wild-v1:${islandIndex}`);
  return Number(BigInt(`0x${hex.slice(0, 12)}`) % BigInt(count));
}

function mulberry32(a) {
  return function next() {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function sheetOf(genome, stage) {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  const sprite = renderSprite(genome, stage, { shadow: false });
  canvas.getContext('2d').putImageData(new ImageData(sprite.rgba, 64, 64), 0, 0);
  return canvas;
}

export function sparkWilds(table) {
  return ISLANDS.map((island, index) => {
    const run = table.runs[wildRunIndex(index, table.runs.length)];
    const traits = simulateStable(island.profile);
    const genome = buildGenome({ focus: traits.focus, calm: traits.calm, spark: traits.spark }, run, null);
    return { island: island.name, runIndex: wildRunIndex(index, table.runs.length), runKey: run.key, genome, traits: genome.inputs.traits };
  });
}

export class IslandExplore {
  constructor(canvas, hooks = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.hooks = hooks;
    this.player = { x: 0.18, y: 0.42, vx: 0, vy: 0 };
    this.keys = {};
    this.beasts = [];
    this.sparks = [];
    this.running = false;
    this.last = 0;
    this.met = new Set();
    this.onKey = (event) => { this.keys[event.code] = event.type === 'keydown'; };
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const width = Math.max(320, Math.floor(rect.width || 640));
    const height = Math.max(280, Math.floor(rect.height || 420));
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  setLabel(label) {
    const beast = this.beasts.find((row) => row.follow);
    if (beast) beast.label = label || '';
  }

  setCompanionStage(stage) {
    const beast = this.beasts.find((row) => row.follow);
    if (!beast || beast.stage === stage) return;
    beast.stage = stage;
    beast.sheet = sheetOf(beast.genome, stage);
  }

  setCompanion(entry) {
    this.companionSeed = entry?.seed || null;
    this.beasts = this.beasts.filter((beast) => !beast.follow);
    if (!entry?.genome) return;
    const home = ISLANDS.find((island) => island.name === entry.genome.island) || ISLANDS[0];
    this.beasts.push(this.makeBeast(entry.genome, home, true, entry.stage || 1, entry.label || ''));
  }

  setWilds(wilds, knownSeeds) {
    this.beasts = this.beasts.filter((beast) => beast.follow);
    this.met = new Set(knownSeeds || []);
    wilds.forEach((wild, index) => {
      const island = ISLANDS[index];
      this.beasts.push(this.makeBeast(wild.genome, island, false, 1));
    });
  }

  makeBeast(genome, island, follow, stage, label = '') {
    const rnd = mulberry32(genome.behavior.prng_seed);
    return {
      genome,
      island,
      follow,
      stage,
      label,
      sheet: sheetOf(genome, stage),
      x: island.x + (rnd() - 0.5) * 0.06,
      y: island.y + (rnd() - 0.5) * 0.06,
      act: ACTS[Math.floor(rnd() * ACTS.length)],
      until: 2 + rnd() * 4,
      facing: genome.facing === 'left' ? -1 : 1,
      hop: rnd() * 6,
      rnd,
      z: 0,
    };
  }

  start() {
    if (this.running) return;
    this.running = true;
    addEventListener('keydown', this.onKey);
    addEventListener('keyup', this.onKey);
    this.last = performance.now();
    const loop = (now) => {
      if (!this.running) return;
      const dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;
      this.step(dt);
      this.draw();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  stop() {
    this.running = false;
    removeEventListener('keydown', this.onKey);
    removeEventListener('keyup', this.onKey);
  }

  nudge(x, y) {
    this.player.vx = x;
    this.player.vy = y;
  }

  step(dt) {
    this.resize();
    let ax = 0;
    let ay = 0;
    if (this.keys.KeyA || this.keys.ArrowLeft) ax -= 1;
    if (this.keys.KeyD || this.keys.ArrowRight) ax += 1;
    if (this.keys.KeyW || this.keys.ArrowUp) ay -= 1;
    if (this.keys.KeyS || this.keys.ArrowDown) ay += 1;
    if (ax || ay) { this.player.vx = ax; this.player.vy = ay; }
    const mag = Math.hypot(this.player.vx, this.player.vy) || 1;
    this.player.x = Math.max(0.05, Math.min(0.95, this.player.x + (this.player.vx / mag) * dt * 0.18));
    this.player.y = Math.max(0.08, Math.min(0.92, this.player.y + (this.player.vy / mag) * dt * 0.18));
    if (!(ax || ay)) { this.player.vx *= 0.8; this.player.vy *= 0.8; }
    if (this.sparks.length < 10 && Math.random() < dt * 1.4) {
      const island = ISLANDS[Math.floor(Math.random() * ISLANDS.length)];
      this.sparks.push({ x: island.x + (Math.random() - 0.5) * 0.08, y: island.y + (Math.random() - 0.5) * 0.08, life: 2.5 + Math.random() });
    }
    for (const spark of this.sparks) spark.life -= dt;
    this.sparks = this.sparks.filter((spark) => spark.life > 0);
    for (const beast of this.beasts) this.moveBeast(beast, dt);
    const here = this.islandAt(this.player.x, this.player.y);
    this.hooks.onPlace?.(here?.name || 'Open sea', this.player);
  }

  islandAt(x, y) {
    return ISLANDS.find((island) => Math.hypot(island.x - x, island.y - y) < 0.11) || null;
  }

  moveBeast(beast, dt) {
    beast.hop += dt * (beast.genome.behavior.tempo_hz || 1) * 4;
    beast.until -= dt;
    if (beast.until <= 0) {
      beast.act = ACTS[Math.floor(beast.rnd() * ACTS.length)];
      beast.until = 2.5 + beast.rnd() * 4;
    }
    const home = beast.follow ? this.player : beast.island;
    let tx = home.x;
    let ty = home.y;
    if (beast.act === 'chase') {
      let best = null;
      let bestD = 0.2;
      for (const spark of this.sparks) {
        const d = Math.hypot(spark.x - beast.x, spark.y - beast.y);
        if (d < bestD) { best = spark; bestD = d; }
      }
      if (best) { tx = best.x; ty = best.y; }
    }
    const place = this.islandAt(beast.x, beast.y) || beast.island;
    const native = place.biome === beast.genome.element || place.name === beast.genome.island;
    let speed = beast.act === 'nap' ? 0 : beast.act === 'sniff' ? 0.015 : 0.045;
    if (beast.act === 'biome' && native) speed = 0.02;
    if (!native && beast.act === 'biome') speed = 0.07;
    if (beast.follow) speed = Math.max(speed, 0.06);
    if (beast.act !== 'nap' || beast.follow) {
      const dx = tx - beast.x;
      const dy = ty - beast.y;
      const dist = Math.hypot(dx, dy) || 1;
      const leash = beast.follow ? 0.06 : 0.09;
      if (dist > leash) {
        beast.x += (dx / dist) * speed * dt;
        beast.y += (dy / dist) * speed * dt;
        beast.facing = dx < 0 ? -1 : 1;
      } else if (!beast.follow) {
        beast.x += Math.sin(beast.hop) * 0.01 * dt;
      }
    }
    beast.z = beast.act === 'nap' ? 0 : Math.abs(Math.sin(beast.hop)) * 6;
    const near = Math.hypot(beast.x - this.player.x, beast.y - this.player.y) < 0.045;
    if (near && !beast.follow && !this.met.has(beast.genome.seed)) {
      this.met.add(beast.genome.seed);
      this.hooks.onMeet?.(beast);
    }
  }

  draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    ctx.fillStyle = '#07111c';
    ctx.fillRect(0, 0, w, h);
    for (let i = 0; i < 50; i++) {
      ctx.fillStyle = i % 4 ? '#1c3148' : '#8fd8ff';
      ctx.fillRect((i * 97) % w, (i * 53) % Math.floor(h * 0.75), 2, 2);
    }
    ctx.strokeStyle = '#245066';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ISLANDS.forEach((island, index) => {
      const n = ISLANDS[(index + 1) % ISLANDS.length];
      ctx.moveTo(island.x * w, island.y * h);
      ctx.lineTo(n.x * w, n.y * h);
    });
    ctx.stroke();
    for (const island of ISLANDS) {
      ctx.beginPath();
      ctx.fillStyle = island.tint;
      ctx.globalAlpha = 0.85;
      ctx.ellipse(island.x * w, island.y * h, w * 0.09, h * 0.08, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.fillStyle = '#041018';
      ctx.font = '600 11px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText(island.name, island.x * w, island.y * h + h * 0.1);
    }
    for (const spark of this.sparks) {
      ctx.fillStyle = '#ffe27a';
      ctx.fillRect(spark.x * w, spark.y * h, 3, 3);
    }
    const ordered = this.beasts.slice().sort((a, b) => a.y - b.y);
    for (const beast of ordered) this.drawBeast(beast, w, h);
    const px = this.player.x * w;
    const py = this.player.y * h;
    ctx.fillStyle = '#f4fbff';
    ctx.beginPath();
    ctx.moveTo(px, py - 12);
    ctx.lineTo(px - 7, py + 8);
    ctx.lineTo(px + 7, py + 8);
    ctx.fill();
    ctx.fillStyle = '#7ee7ff';
    ctx.fillRect(px - 2, py - 2, 4, 4);
    ctx.fillStyle = '#d7f6ff';
    ctx.textAlign = 'left';
    ctx.font = '12px ui-monospace, monospace';
    ctx.fillText('Keeper', px + 10, py - 8);
  }

  drawBeast(beast, w, h) {
    const size = beast.follow ? 42 : 34;
    const x = beast.x * w;
    const y = beast.y * h - beast.z;
    const ctx = this.ctx;
    ctx.fillStyle = 'rgba(0,0,0,.35)';
    ctx.fillRect(x - size / 4, beast.y * h + 2, size / 2, 3);
    ctx.save();
    ctx.imageSmoothingEnabled = false;
    if (beast.facing < 0) {
      ctx.translate(x, y);
      ctx.scale(-1, 1);
      ctx.drawImage(beast.sheet, -size / 2, -size + 8, size, size);
    } else {
      ctx.drawImage(beast.sheet, x - size / 2, y - size + 8, size, size);
    }
    ctx.restore();
    if (beast.follow && beast.label) {
      ctx.fillStyle = '#f0c14a';
      ctx.font = '700 12px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText(beast.label, x, y - size - 2);
    }
    if (beast.act === 'nap') {
      ctx.fillStyle = '#cfe8ff';
      ctx.font = '12px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('z', x + 10, y - size + 16);
    }
    if (!beast.follow && !this.met.has(beast.genome.seed)) {
      ctx.fillStyle = '#ffe27a';
      ctx.font = '700 12px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('?', x, y - size + 6);
    }
  }
}
