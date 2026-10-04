import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../standalone/SIM_EARTH_7_08_REALITY_BODY.html', import.meta.url), 'utf8');

test('the digital cosmic theme and persistent GBA player are present', () => {
  assert.match(html, /id="cosmic-sky"/);
  assert.match(html, /id="cosmic-theme"/);
  assert.match(html, /prefers-reduced-motion:\s*reduce/);
  assert.match(html, /id="gba-player"/);
  assert.match(html, /id="gba-slot"/);
  assert.match(html, /id="gba-expand"/);
  assert.match(html, /id="gba-collapse"/);
  assert.match(html, /id="gba-mute"/);
  assert.match(html, /id="lc-arcade-frame"/);
  assert.match(html, /placeGbaPlayer/);
  assert.match(html, /data-mode="parked"/);
  assert.match(html, /class="tab-ico"/);
  assert.match(html, /PLAY GBA/);
  assert.match(html, /MODELS/);
  assert.doesNotMatch(html, /src="https?:/);
});
