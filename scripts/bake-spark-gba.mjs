/**
 * Bake recorded Spark Beasts into the Sol GBA ROM.
 * Each island contributes its three-stage evolution line from sparkWilds().
 * Twelve rares come from arcade/spark-beasts/data/rare-field.json, each a
 * recorded run whose generated name is that rare. Sprites are the web renderer.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { buildGenome } from '../arcade/spark-beasts/genome.mjs';
import { renderSprite } from '../arcade/spark-beasts/render.mjs';
import { sparkWilds } from '../arcade/spark-beasts/explore.mjs';
import { spriteToGbaSize, spritesToSharedGba, walkFrame } from '../arcade/spark-beasts/gba-tiles.mjs';

const RARE_ORDER = [
  'Ferrotitan', 'Gearwarden', 'Cogknight', 'Nyxleviath', 'Nyxwyrm', 'Noctveil', 'Chartyrant',
  'Calderwyvern', 'Snowleviath', 'Frostphoenix', 'Reefwing', 'Calderwarden',
];
const RARE_WORLD = {
  Ferrotitan: 7, Gearwarden: 7, Cogknight: 7,
  Nyxwyrm: 4, Noctveil: 4, Nyxleviath: 4,
  Chartyrant: 1, Calderwyvern: 1, Calderwarden: 1,
  Reefwing: 2,
  Snowleviath: 6, Frostphoenix: 6,
};
const ISLAND_WORLD = {
  'Eridoria Prime': 0,
  'Cinder Drift': 1,
  'The Shattered Reef': 2,
  'Hollow Verdance': 3,
  'Umbral Deep': 4,
  'The Crown': 5,
  'The Pale Expanse': 6,
  'Rust Meridian': 7,
};
/* World 0 opens in Brindlemark beside tile (20, 43). The evolution line stands
   there. Later homes step away so the three nearest sprites are the line. */
const ANCHOR = {
  0: [20, 43], 1: [22, 36], 2: [24, 36], 3: [22, 36],
  4: [22, 36], 5: [22, 36], 6: [22, 36], 7: [22, 36],
};
const HOME_STEP = [[2, 1], [-2, 1], [4, 0], [8, -6], [-8, -4], [0, -8], [10, 2], [-10, 4]];

function cleanName(name) {
  const text = String(name || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
  if (!text) throw new Error('beast name is empty');
  return text;
}

function hexBytes(bytes) {
  const parts = [];
  for (let i = 0; i < bytes.length; i += 16) {
    const row = [];
    for (let j = 0; j < 16 && i + j < bytes.length; j++) row.push(`0x${bytes[i + j].toString(16).padStart(2, '0')}`);
    parts.push(row.join(','));
  }
  return parts.join(',\n');
}

function hexWords(words) {
  return words.map((word) => `0x${(word & 0xffff).toString(16).padStart(4, '0')}`).join(',');
}

export function rosterFromTable(table, rares) {
  const used = {};
  const beasts = [];
  const takeHome = (world) => {
    const n = used[world] || 0;
    const step = HOME_STEP[n];
    if (!step) throw new Error(`no home left on world ${world}`);
    used[world] = n + 1;
    const [ax, ay] = ANCHOR[world];
    return [ax + step[0], ay + step[1]];
  };
  for (const wild of sparkWilds(table)) {
    const world = ISLAND_WORLD[wild.island];
    if (world === undefined) throw new Error(`no GBA world for ${wild.island}`);
    for (const stage of [1, 2, 3]) {
      const [tx, ty] = takeHome(world);
      beasts.push({
        name: cleanName(wild.genome.names[String(stage)]),
        world, tx, ty, rare: 0, stage: stage - 1,
        sprite: renderSprite(wild.genome, stage, { shadow: false }),
      });
    }
  }
  for (const name of RARE_ORDER) {
    const spec = rares[name];
    if (!spec) throw new Error(`missing recorded rare ${name}`);
    const run = table.runs[spec.runIndex];
    if (!run || run.key !== spec.runKey) throw new Error(`rare ${name} does not match the recorded run table`);
    const genome = buildGenome(spec.traits, run, spec.userId ?? null);
    const stage = String(spec.stage);
    if (genome.names[stage] !== name) {
      throw new Error(`rare ${name} rebuilt as ${genome.names[stage]}`);
    }
    const world = RARE_WORLD[name];
    const stageNum = Math.max(1, Math.min(3, Number(spec.stage) || 1));
    const [tx, ty] = takeHome(world);
    beasts.push({
      name: cleanName(name),
      world, tx, ty, rare: 1, stage: stageNum - 1,
      sprite: renderSprite(genome, stageNum, { shadow: false }),
    });
  }
  /* Charlet's line is a companion, not a field spawn. world 255 keeps
     spark_field_tick from planting her on a map. Stage 0 is the callsign. */
  const charletRun = table.runs[635];
  if (!charletRun) throw new Error('Charlet run 635 is missing from the quantum table');
  const charlet = buildGenome({ focus: 30, calm: 30, spark: 30 }, charletRun, 'Phera');
  const charletNames = ['Charlet', 'Ashhound', 'Cinderheart'];
  for (let stage = 1; stage <= 3; stage++) {
    const name = charlet.names[String(stage)];
    if (name !== charletNames[stage - 1]) {
      throw new Error(`Charlet stage ${stage} rebuilt as ${name}`);
    }
    beasts.push({
      name: cleanName(name),
      world: 255, tx: 0, ty: 0, rare: 0, stage: stage - 1,
      sprite: renderSprite(charlet, stage, { shadow: false }),
    });
  }
  return beasts;
}

function framesDiffer(a, b) {
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return true;
  return false;
}

function emit(beasts) {
  const byWorld = Array.from({ length: 8 }, () => []);
  beasts.forEach((beast, index) => {
    if (beast.world < 8) byWorld[beast.world].push(index);
  });
  const palettes = Array.from({ length: 8 }, () => Array(16).fill(0));
  const fieldTiles = beasts.map(() => [new Uint8Array(512), new Uint8Array(512)]);
  const fieldPal = beasts.map(() => Array(16).fill(0));
  const portraits = beasts.map((beast) => spriteToGbaSize(beast.sprite, 64));
  for (let world = 0; world < 8; world++) {
    const group = [];
    for (const index of byWorld[world]) {
      group.push(beasts[index].sprite, walkFrame(beasts[index].sprite));
    }
    const packed = spritesToSharedGba(group);
    palettes[world] = packed.palette;
    byWorld[world].forEach((index, nth) => {
      fieldTiles[index] = [packed.tiles[nth * 2], packed.tiles[nth * 2 + 1]];
      fieldPal[index] = packed.palette;
    });
  }
  for (let index = 0; index < beasts.length; index++) {
    if (beasts[index].world < 8) continue;
    const packed = spritesToSharedGba([beasts[index].sprite, walkFrame(beasts[index].sprite)]);
    fieldTiles[index] = packed.tiles;
    fieldPal[index] = packed.palette;
  }
  const walking = fieldTiles.filter(([stand, step]) => framesDiffer(stand, step)).length;
  if (walking < beasts.length - 2) {
    throw new Error(`walk frames did not change the art (${walking}/${beasts.length})`);
  }
  const lines = [];
  lines.push('/* Generated by scripts/bake-spark-gba.mjs. Recorded runs only. Do not edit. */');
  lines.push('#ifndef SPARK_FIELD_BEASTS_H');
  lines.push('#define SPARK_FIELD_BEASTS_H');
  lines.push(`#define SPARK_FIELD_COUNT ${beasts.length}`);
  lines.push('static const u16 SPARK_WORLD_PAL[8][16]={');
  for (const pal of palettes) lines.push(`{${hexWords(pal)}},`);
  lines.push('};');
  lines.push(`static const u16 SPARK_FIELD_PAL[${beasts.length}][16]={`);
  for (const pal of fieldPal) lines.push(`{${hexWords(pal)}},`);
  lines.push('};');
  lines.push(`static const u8 SPARK_FIELD_TILES[${beasts.length}][2][512]={`);
  for (const [stand, step] of fieldTiles) {
    lines.push(`{{${hexBytes(stand)}},{${hexBytes(step)}}},`);
  }
  lines.push('};');
  lines.push(`static const u16 SPARK_PORTRAIT_PAL[${beasts.length}][16]={`);
  for (const portrait of portraits) lines.push(`{${hexWords(portrait.palette)}},`);
  lines.push('};');
  lines.push(`static const u8 SPARK_PORTRAIT_TILES[${beasts.length}][2048]={`);
  for (const portrait of portraits) lines.push(`{${hexBytes(portrait.tiles)}},`);
  lines.push('};');
  lines.push('static const struct { char name[13]; u8 world, tx, ty, rare, stage; } SPARK_FIELD[SPARK_FIELD_COUNT]={');
  for (const beast of beasts) {
    lines.push(`{"${beast.name}",${beast.world},${beast.tx},${beast.ty},${beast.rare},${beast.stage}},`);
  }
  lines.push('};');
  lines.push('#endif');
  return lines.join('\n') + '\n';
}

const rootArg = process.argv[1];
if (rootArg && rootArg.endsWith('bake-spark-gba.mjs')) {
  const table = JSON.parse(readFileSync(new URL('../arcade/spark-beasts/data/quantum-runs.json', import.meta.url), 'utf8'));
  const rares = JSON.parse(readFileSync(new URL('../arcade/spark-beasts/data/rare-field.json', import.meta.url), 'utf8'));
  const header = emit(rosterFromTable(table, rares));
  const out = new URL('../gba/lost-cosmos-living-multiverse/LOST_COSMOS_V10_SOURCE/spark_field_beasts.h', import.meta.url);
  writeFileSync(out, header);
  console.log(`baked ${header.length} bytes of spark field art`);
}
