/**
 * Boot Lost Cosmos in headless Chromium through the vendored EmulatorJS build.
 * Serves the repository root, presses Start cartridge, then EmulatorJS Start Game,
 * and requires the GBA title screen with no same-origin 404.
 *
 * The ROM is produced by `npm run build:cartridge` and is not committed.
 */
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { inflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.wasm': 'application/wasm',
  '.data': 'application/octet-stream',
  '.gba': 'application/octet-stream',
  '.png': 'image/png',
};

function decodePng(buf) {
  if (buf.toString('ascii', 1, 4) !== 'PNG') throw new Error('screenshot is not a PNG');
  let p = 8;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  const idat = [];
  while (p < buf.length) {
    const len = buf.readUInt32BE(p);
    p += 4;
    const type = buf.toString('ascii', p, p + 4);
    p += 4;
    const data = buf.subarray(p, p + len);
    p += len + 4;
    if (type === 'IHDR') {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
    } else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
  }
  const bpp = colorType === 6 ? 4 : colorType === 2 ? 3 : null;
  if (!bpp || bitDepth !== 8) throw new Error(`unsupported screenshot PNG ${colorType}/${bitDepth}`);
  const raw = inflateSync(Buffer.concat(idat));
  const stride = width * bpp;
  let s = 0;
  let prev = Buffer.alloc(stride);
  let colored = 0;
  let opaque = 0;
  for (let y = 0; y < height; y++) {
    const filter = raw[s++];
    const row = Buffer.from(raw.subarray(s, s + stride));
    s += stride;
    for (let i = 0; i < stride; i++) {
      const left = i >= bpp ? row[i - bpp] : 0;
      const up = prev[i];
      const ul = i >= bpp ? prev[i - bpp] : 0;
      let add = 0;
      if (filter === 1) add = left;
      else if (filter === 2) add = up;
      else if (filter === 3) add = Math.floor((left + up) / 2);
      else if (filter === 4) {
        const pred = left + up - ul;
        const pa = Math.abs(pred - left);
        const pb = Math.abs(pred - up);
        const pc = Math.abs(pred - ul);
        add = pa <= pb && pa <= pc ? left : pb <= pc ? up : ul;
      } else if (filter !== 0) throw new Error(`PNG filter ${filter}`);
      row[i] = (row[i] + add) & 255;
    }
    for (let x = 0; x < width; x++) {
      const r = row[x * bpp];
      const g = row[x * bpp + 1];
      const b = row[x * bpp + 2];
      const a = bpp === 4 ? row[x * bpp + 3] : 255;
      if (a < 16) continue;
      opaque++;
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      if (max - min > 28 && max > 40) colored++;
    }
    prev = row;
  }
  return { width, height, colored, opaque };
}

function listen(server) {
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => resolve(server.address().port));
  });
}

async function bootFromSite(page, port) {
  const themeErrors = [];
  const onPageError = (error) => themeErrors.push(String(error));
  const onConsole = (msg) => {
    if (msg.type() === 'error') themeErrors.push(msg.text());
  };
  page.on('pageerror', onPageError);
  page.on('console', onConsole);
  await page.goto(`http://127.0.0.1:${port}/standalone/SIM_EARTH_7_08_REALITY_BODY.html`, { waitUntil: 'domcontentloaded' });
  const enter = page.getByRole('button', { name: /enter cute beast pocket reality/i });
  await enter.waitFor({ timeout: 30000 });
  await enter.click();
  const tab = page.getByRole('button', { name: 'PLAY GBA' });
  await tab.waitFor({ timeout: 30000 });
  await tab.click();
  const hand = page.frameLocator('#lc-arcade-frame');
  await hand.locator('#play').click({ timeout: 30000 });
  const start = hand.getByText(/^start game$/i);
  await start.waitFor({ timeout: 30000 });
  await start.click();
  await hand.locator('#status').filter({ hasText: 'title screen' }).waitFor({ timeout: 90000 });
  await page.waitForFunction(() => {
    const frame = document.getElementById('sb-spark-frame');
    return frame && frame.contentWindow && frame.contentWindow.location.href.includes('spark-beasts');
  }, null, { timeout: 60000 });
  const spark = page.frame({ url: /spark-beasts/ });
  const handheld = page.frame({ url: /lost-cosmos\/index\.html/ });
  if (!spark || !handheld) throw new Error('PLAY GBA did not keep the Spark and handheld frames');
  await handheld.evaluate(() => {
    window.__lcImport = null;
    window.addEventListener('message', (event) => {
      const data = event.data;
      if (data && data.type === 'lc-import-save') window.__lcImport = data;
    });
  });
  await spark.evaluate(() => {
    parent.postMessage({
      type: 'lc-cage-save',
      save: [76, 67, 88, 49],
      callsign: 'CHARLET',
      species: 'PLASMA',
      play: false,
    }, '*');
  });
  await handheld.waitForFunction(() => window.__lcImport && window.__lcImport.callsign === 'CHARLET', null, { timeout: 10000 });
  const before = await handheld.evaluate(() => ({
    bootId: window.__lcRuntime?.bootId || '',
    frames: window.__lcRuntime?.frames || 0,
    emulatorId: window.EJS_emulator?.__lcId || '',
  }));
  if (!before.bootId || before.emulatorId !== before.bootId) {
    throw new Error(`emulator instance was not marked (${before.emulatorId} / ${before.bootId})`);
  }
  const png = await hand.locator('#game canvas').first().screenshot({ type: 'png' });
  const { writeFile } = await import('node:fs/promises');
  await writeFile('/tmp/lost-cosmos-emulator/play-gba-title.png', png);
  console.log('PASS: PLAY GBA tab booted the cartridge and forwarded lc-cage-save. Screenshot /tmp/lost-cosmos-emulator/play-gba-title.png');

  await page.getByRole('button', { name: 'MODELS' }).click();
  await page.locator('#gba-player').waitFor();
  const mode = await page.locator('#gba-player').getAttribute('data-mode');
  if (mode !== 'dock' && mode !== 'mini') throw new Error(`Lost Cosmos left the mini player in mode ${mode}`);
  const token = await page.locator('#lc-arcade-frame').getAttribute('data-persist-token');
  if (token !== 'mounted') throw new Error('the handheld iframe was replaced');
  await handheld.waitForFunction(() => window.__lcRuntime && window.__lcRuntime.focused === false, null, { timeout: 5000 });
  const mid = await handheld.evaluate(() => ({
    bootId: window.__lcRuntime?.bootId || '',
    frames: window.__lcRuntime?.frames || 0,
    emulatorId: window.EJS_emulator?.__lcId || '',
  }));
  if (mid.bootId !== before.bootId || mid.emulatorId !== before.emulatorId) {
    throw new Error('the emulator reloaded when the tab changed');
  }
  await handheld.waitForFunction((start) => window.__lcRuntime.frames > start, mid.frames, { timeout: 8000 });
  const after = await handheld.evaluate(() => ({
    bootId: window.__lcRuntime.bootId,
    frames: window.__lcRuntime.frames,
    emulatorId: window.EJS_emulator?.__lcId || '',
    focused: window.__lcRuntime.focused,
  }));
  if (after.bootId !== before.bootId || after.emulatorId !== before.emulatorId) {
    throw new Error('the emulator reloaded when the tab changed');
  }
  if (after.frames <= before.frames) throw new Error('the cartridge clock stopped on tab change');
  const keys = await handheld.evaluate(() => {
    window.__lcRuntime.focused = false;
    window.__lcRuntime.keys = 0;
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', code: 'ArrowRight', bubbles: true, cancelable: true }));
    const blocked = window.__lcRuntime.keys;
    window.__lcRuntime.focused = true;
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', code: 'ArrowRight', bubbles: true, cancelable: true }));
    const taken = window.__lcRuntime.keys;
    window.__lcRuntime.focused = false;
    return { blocked, taken };
  });
  if (keys.blocked !== 0 || keys.taken < 1) throw new Error(`keyboard gate failed ${JSON.stringify(keys)}`);

  const bay = page.frame({ url: /synapse\.html/ });
  if (!bay) throw new Error('MODELS did not keep the Synapse OS frame');
  await bay.locator('#consent').check();
  await bay.locator('#shape').click();
  await bay.waitForFunction(() => {
    const select = document.getElementById('care-beast');
    return select && select.value && !select.value.startsWith('No');
  }, null, { timeout: 15000 });
  await bay.locator('#care-input').fill('my name is Cory');
  await bay.locator('#care-chat button').click();
  await bay.locator('#care-log .beast').getByText(/Cory/).waitFor({ timeout: 10000 });
  await bay.locator('#care-focus').click();
  await bay.waitForFunction(() => {
    const saved = JSON.parse(localStorage.getItem('spark-beasts-v1') || '{"beasts":{}}');
    return Object.values(saved.beasts).some((beast) => beast.memory?.playerName === 'Cory' && beast.xp >= 18 && beast.stage >= 1);
  }, null, { timeout: 10000 });
  const theme = await page.evaluate(() => ({
    sky: !!document.getElementById('cosmic-sky'),
    style: document.getElementById('cosmic-theme')?.textContent.includes('prefers-reduced-motion') || false,
  }));
  if (!theme.sky || !theme.style) throw new Error('cosmic theme did not load');
  const relevant = themeErrors.filter((line) => /cosmic-theme|gba-player|care\.mjs|synapse\.mjs|player\.mjs|SyntaxError|is not defined/i.test(line));
  if (relevant.length) throw new Error(`theme console errors:\n${relevant.join('\n')}`);
  page.off('pageerror', onPageError);
  page.off('console', onConsole);
  console.log(`PASS: cartridge kept running across MODELS (${before.frames} -> ${after.frames} frames, same emulator ${after.emulatorId}) and model-bay care updated the shared beast.`);
}

async function main() {
  const rom = join(root, 'arcade', 'lost-cosmos', 'rom', 'lost-cosmos.gba');
  await readFile(rom);
  const server = createServer(async (req, res) => {
    try {
      const url = new URL(req.url || '/', 'http://127.0.0.1');
      const rel = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, '');
      const path = join(root, rel);
      if (!path.startsWith(root)) {
        res.writeHead(403).end();
        return;
      }
      const body = await readFile(path);
      res.writeHead(200, {
        'content-type': TYPES[extname(path)] || 'application/octet-stream',
        'cache-control': 'no-store',
      });
      res.end(body);
    } catch {
      res.writeHead(404).end('missing');
    }
  });
  const port = await listen(server);
  const misses = [];
  const cdn = [];
  let browser;
  try {
    const { chromium } = await import('playwright');
    browser = await chromium.launch({
      headless: true,
      args: [
        '--use-gl=angle',
        '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader',
        '--enable-webgl',
        '--ignore-gpu-blocklist',
      ],
    });
    const page = await browser.newPage({ viewport: { width: 960, height: 800 } });
    page.on('response', (response) => {
      const url = response.url();
      if (url.includes('cdn.emulatorjs.org')) cdn.push(`${response.status()} ${url}`);
      if (response.status() === 404) misses.push(url);
    });
    await page.route('https://cdn.emulatorjs.org/**', (route) => route.abort());
    await page.goto(`http://127.0.0.1:${port}/arcade/lost-cosmos/index.html`, { waitUntil: 'domcontentloaded' });
    await page.locator('#play').click();
    const start = page.getByText(/^start game$/i);
    await start.waitFor({ timeout: 30000 });
    await start.click();
    await page.locator('#status').filter({ hasText: 'title screen' }).waitFor({ timeout: 90000 });
    await page.waitForTimeout(1500);
    const bodyText = await page.locator('body').innerText();
    if (/Network Error/i.test(bodyText)) throw new Error(`Emulator reported a network error:\n${bodyText.slice(0, 500)}`);
    const box = await page.locator('#game canvas').first().boundingBox();
    if (!box || box.width < 32 || box.height < 32) throw new Error('GBA canvas did not appear');
    const png = await page.locator('#game canvas').first().screenshot({ type: 'png' });
    const { writeFile, mkdir } = await import('node:fs/promises');
    await mkdir('/tmp/lost-cosmos-emulator', { recursive: true });
    await writeFile('/tmp/lost-cosmos-emulator/title-screen.png', png);
    const pixels = decodePng(png);
    const ratio = pixels.opaque ? pixels.colored / pixels.opaque : 0;
    if (pixels.colored < 80 || ratio < 0.01) {
      throw new Error(`Title screen looks blank (${pixels.colored} colored / ${pixels.opaque} opaque, ${pixels.width}x${pixels.height})`);
    }
    if (misses.length) throw new Error(`404 responses:\n${misses.join('\n')}`);
    if (cdn.length) throw new Error(`CDN was contacted even though cores are vendored:\n${cdn.join('\n')}`);
    console.log(`PASS: Lost Cosmos title screen ${pixels.width}x${pixels.height}, ${pixels.colored} colored pixels, no 404s. Screenshot /tmp/lost-cosmos-emulator/title-screen.png`);
    await bootFromSite(page, port);
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

main().catch((error) => {
  console.error(error?.stack || error);
  process.exit(1);
});
