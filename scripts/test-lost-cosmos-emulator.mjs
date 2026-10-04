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
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

main().catch((error) => {
  console.error(error?.stack || error);
  process.exit(1);
});
