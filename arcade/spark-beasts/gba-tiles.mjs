/**
 * Spark sprites become GBA 4bpp 32x32 OBJ tiles.
 * Index 0 is transparent. Colours are BGR555. Recorded sprites only.
 */

function dist2(a, b) {
  const dr = a[0] - b[0];
  const dg = a[1] - b[1];
  const db = a[2] - b[2];
  return dr * dr + dg * dg + db * db;
}

function channelRange(box, channel) {
  let lo = 255;
  let hi = 0;
  for (const pixel of box) {
    const value = pixel[channel];
    if (value < lo) lo = value;
    if (value > hi) hi = value;
  }
  return hi - lo;
}

function splitBox(box) {
  let channel = 0;
  let spread = channelRange(box, 0);
  for (let i = 1; i < 3; i++) {
    const next = channelRange(box, i);
    if (next > spread) {
      spread = next;
      channel = i;
    }
  }
  box.sort((a, b) => a[channel] - b[channel]);
  const mid = Math.max(1, Math.floor(box.length / 2));
  return [box.slice(0, mid), box.slice(mid)];
}

function average(box) {
  let r = 0;
  let g = 0;
  let b = 0;
  for (const pixel of box) {
    r += pixel[0];
    g += pixel[1];
    b += pixel[2];
  }
  const n = box.length || 1;
  return [Math.round(r / n), Math.round(g / n), Math.round(b / n)];
}

export function quantizeColors(samples, count = 15) {
  const opaque = samples.filter((pixel) => pixel);
  if (!opaque.length) return [[0, 0, 0]];
  let boxes = [opaque.slice()];
  while (boxes.length < count) {
    let index = 0;
    let largest = 0;
    for (let i = 0; i < boxes.length; i++) {
      if (boxes[i].length > largest) {
        largest = boxes[i].length;
        index = i;
      }
    }
    if (largest < 2) break;
    const [left, right] = splitBox(boxes[index]);
    boxes.splice(index, 1, left, right);
  }
  return boxes.map(average);
}

export function bgr555(r, g, b) {
  return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10);
}

export function downscaleNearest(rgba, srcSize, dstSize) {
  const out = new Uint8ClampedArray(dstSize * dstSize * 4);
  const step = srcSize / dstSize;
  for (let y = 0; y < dstSize; y++) {
    const sy = Math.min(srcSize - 1, Math.floor(y * step));
    for (let x = 0; x < dstSize; x++) {
      const sx = Math.min(srcSize - 1, Math.floor(x * step));
      const s = (sy * srcSize + sx) * 4;
      const d = (y * dstSize + x) * 4;
      out[d] = rgba[s];
      out[d + 1] = rgba[s + 1];
      out[d + 2] = rgba[s + 2];
      out[d + 3] = rgba[s + 3];
    }
  }
  return out;
}

function pixelsOf(rgba, size) {
  const pixels = [];
  for (let i = 0; i < size * size; i++) {
    const o = i * 4;
    if (rgba[o + 3] < 128) pixels.push(null);
    else pixels.push([rgba[o], rgba[o + 1], rgba[o + 2]]);
  }
  return pixels;
}

export function indexPixels(pixels, colors) {
  const indexed = new Uint8Array(pixels.length);
  for (let i = 0; i < pixels.length; i++) {
    if (!pixels[i]) continue;
    let best = 1;
    let score = dist2(pixels[i], colors[0]);
    for (let c = 1; c < colors.length; c++) {
      const next = dist2(pixels[i], colors[c]);
      if (next < score) {
        score = next;
        best = c + 1;
      }
    }
    indexed[i] = best;
  }
  return indexed;
}

/** GBA 4bpp OBJ tiles. `size` is 32 or 64. Index 0 stays transparent. */
export function packTiles(indexed, size) {
  const tilesPerRow = size >> 3;
  const out = new Uint8Array(tilesPerRow * tilesPerRow * 32);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x += 2) {
      const lo = indexed[y * size + x] & 15;
      const hi = indexed[y * size + x + 1] & 15;
      const at = ((y >> 3) * tilesPerRow + (x >> 3)) * 32 + (y & 7) * 4 + ((x & 7) >> 1);
      out[at] = lo | (hi << 4);
    }
  }
  return out;
}

export function packTiles32(indexed) {
  return packTiles(indexed, 32);
}

/**
 * A second walk frame from the same render: the body bobs down and the
 * legs step apart. Field sprites alternate this with the standing frame.
 */
export function walkFrame(sprite) {
  const size = sprite.width;
  const out = new Uint8ClampedArray(sprite.rgba.length);
  const bob = 2;
  const split = Math.floor(size * 0.62);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let sx = x;
      const sy = y - bob;
      if (y > split) sx += x < size / 2 ? 2 : -2;
      if (sx < 0 || sy < 0 || sx >= size || sy >= size) continue;
      const s = (sy * size + sx) * 4;
      const d = (y * size + x) * 4;
      out[d] = sprite.rgba[s];
      out[d + 1] = sprite.rgba[s + 1];
      out[d + 2] = sprite.rgba[s + 2];
      out[d + 3] = sprite.rgba[s + 3];
    }
  }
  return { width: size, height: size, rgba: out };
}

export function paletteWords(colors) {
  const words = [0];
  for (const [r, g, b] of colors) words.push(bgr555(r, g, b));
  while (words.length < 16) words.push(0);
  return words.slice(0, 16);
}

/** One sprite, its own 15-colour palette, at 32 or 64 pixels. */
export function spriteToGbaSize(sprite, size) {
  const rgba = sprite.width === size ? sprite.rgba : downscaleNearest(sprite.rgba, sprite.width, size);
  const pixels = pixelsOf(rgba, size);
  const colors = quantizeColors(pixels.filter(Boolean), 15);
  return {
    palette: paletteWords(colors),
    tiles: packTiles(indexPixels(pixels, colors), size),
  };
}

/** One sprite, its own 15-colour palette. */
export function spriteToGba(sprite) {
  return spriteToGbaSize(sprite, 32);
}

/** Several sprites share one 15-colour palette so they can use one OBJ bank. */
export function spritesToSharedGba(sprites) {
  const frames = sprites.map((sprite) => pixelsOf(downscaleNearest(sprite.rgba, sprite.width, 32), 32));
  const samples = [];
  for (const frame of frames) for (const pixel of frame) if (pixel) samples.push(pixel);
  const colors = quantizeColors(samples, 15);
  return {
    palette: paletteWords(colors),
    tiles: frames.map((frame) => packTiles32(indexPixels(frame, colors))),
  };
}
