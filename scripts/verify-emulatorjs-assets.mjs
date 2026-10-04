/**
 * Every path the Lost Cosmos loader can request from the vendored EmulatorJS
 * 4.2.3 tree must exist, hash-match SHA256SUMS, and stay off the CDN.
 *
 * Shaders are compiled into emulator.min.js as window.EJS_SHADERS and written
 * into the core's virtual filesystem. They are not separate HTTP files.
 * The GBA player sets EJS_threads=false and EJS_disableAutoLang=false, so the
 * boot path is the non-thread mGBA core plus extract7z.js. Locale JSON is still
 * vendored because loader.js fetches localization/<locale>.json whenever
 * automatic language is left on.
 */
import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', 'arcade', 'third_party', 'emulatorjs');
const read = (rel) => readFileSync(join(root, rel));

const LOCALES = [
  'af-FR', 'ar-AR', 'ben-BEN', 'de-GER', 'el-GR', 'en-US', 'es-ES', 'fa-AF',
  'hi-HI', 'it-IT', 'ja-JA', 'jv-JV', 'ko-KO', 'pt-BR', 'ro-RO', 'ru-RU',
  'tr-TR', 'vi-VN', 'zh-CN',
];

/** Paths requested while booting the GBA cartridge, plus the other workers the same decompressor loads. */
export const RUNTIME_PATHS = [
  'data/loader.js',
  'data/emulator.min.js',
  'data/emulator.min.css',
  'data/version.json',
  'data/cores/reports/mgba.json',
  'data/cores/mgba-wasm.data',
  'data/cores/mgba-legacy-wasm.data',
  'data/compression/extract7z.js',
  'data/compression/extractzip.js',
  'data/compression/libunrar.js',
  'data/compression/libunrar.wasm',
  ...LOCALES.map((code) => `data/localization/${code}.json`),
];

function parseSums() {
  const sums = new Map();
  for (const line of read('SHA256SUMS').toString('utf8').split('\n')) {
    if (!line.trim()) continue;
    const match = line.match(/^([a-f0-9]{64})  (.+)$/);
    if (!match) throw new Error(`Malformed SHA256SUMS line: ${line}`);
    sums.set(match[2], match[1]);
  }
  return sums;
}

function quotedPaths(source) {
  const found = new Set();
  const re = /["']((?:compression|cores|localization|src)\/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+|emulator\.min\.(?:js|css))["']/g;
  let match;
  while ((match = re.exec(source))) found.add(match[1]);
  return found;
}

export function verifyEmulatorJsAssets() {
  const sums = parseSums();
  for (const [rel, expected] of sums) {
    const file = join(root, rel);
    const size = statSync(file).size;
    if (size <= 0) throw new Error(`${rel} is empty`);
    const hash = createHash('sha256').update(readFileSync(file)).digest('hex');
    if (hash !== expected) throw new Error(`${rel} hash ${hash} != ${expected}`);
  }

  for (const rel of RUNTIME_PATHS) {
    if (!sums.has(rel)) throw new Error(`Runtime path ${rel} is not pinned in SHA256SUMS`);
  }

  const version = JSON.parse(read('data/version.json').toString('utf8'));
  if (version.version !== '4.2.3') throw new Error(`EmulatorJS pin is ${version.version}, expected 4.2.3`);

  const loader = read('data/loader.js').toString('utf8');
  const emulator = read('data/emulator.min.js').toString('utf8');
  const player = readFileSync(join(root, '..', '..', 'lost-cosmos', 'player.mjs')).toString('utf8');

  if (!loader.includes('localization/" + language + ".json"') && !loader.includes('localization/" + language + ".json')) {
    throw new Error('loader.js no longer builds a localization path the asset check understands');
  }
  if (!loader.includes('emulator.min.js') || !loader.includes('emulator.min.css')) {
    throw new Error('loader.js no longer requests the minified emulator');
  }

  const referenced = new Set([...quotedPaths(loader), ...quotedPaths(emulator)]);
  for (const rel of referenced) {
    const path = rel.startsWith('data/') ? rel : `data/${rel}`;
    if (path === 'data/cores/ppsspp-assets.zip') continue;
    if (!sums.has(path)) throw new Error(`EmulatorJS references ${path}, which is not vendored`);
  }
  if (!referenced.has('compression/extract7z.js')) throw new Error('extract7z.js is not referenced');
  if (!emulator.includes('cores/reports/')) throw new Error('core report path is missing');
  if (!emulator.includes('window.EJS_SHADERS=')) throw new Error('shaders are no longer embedded in emulator.min.js');
  if (!emulator.includes('cdn.emulatorjs.org')) {
    throw new Error('Expected the unmodified CDN fallback string to remain detectable');
  }
  if (!player.includes("EJS_pathtodata = '../third_party/emulatorjs/data/'")) {
    throw new Error('Lost Cosmos player is not pointed at the vendored data directory');
  }
  if (!player.includes('EJS_threads = false')) throw new Error('GBA player must stay on the non-thread core');
  if (!player.includes('EJS_disableAutoLang = false')) {
    throw new Error('Changing auto-lang requires confirming the locale file is vendored');
  }

  const core = read('data/cores/mgba-wasm.data');
  const legacy = read('data/cores/mgba-legacy-wasm.data');
  const sevenZip = Buffer.from([0x37, 0x7a, 0xbc, 0xaf, 0x27, 0x1c]);
  if (!core.subarray(0, 6).equals(sevenZip) || !legacy.subarray(0, 6).equals(sevenZip)) {
    throw new Error('mGBA cores are no longer 7z packages, so extract7z.js would not be the worker');
  }
  if (!read('data/compression/extract7z.js').includes('un7zip')) {
    throw new Error('extract7z.js is not the EmulatorJS 7z worker');
  }
  const english = JSON.parse(read('data/localization/en-US.json').toString('utf8'));
  if (!english['Start Game']) throw new Error('en-US locale is missing the start button string');
  for (const code of LOCALES) {
    const text = read(`data/localization/${code}.json`).toString('utf8').trim();
    if (!text.startsWith('{') || !text.endsWith('}')) throw new Error(`${code} locale is not a JSON object file`);
  }
  const license = read('LICENSE').toString('utf8');
  if (!license.includes('GNU GENERAL PUBLIC LICENSE') || !license.includes('Version 3, 29 June 2007')) {
    throw new Error('GPL-3.0 license text is missing from the EmulatorJS vendor tree');
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  verifyEmulatorJsAssets();
  console.log(`PASS: EmulatorJS 4.2.3 runtime paths are vendored (${RUNTIME_PATHS.length} files, shaders embedded, GPL-3.0 present)`);
}
