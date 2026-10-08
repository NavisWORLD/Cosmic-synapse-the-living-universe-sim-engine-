/**
 * Read a bounded optical summary of the ACTUAL native display canvas.
 * This is screen observation, not an object detector or full visual understanding.
 * Nothing runs continuously and no frame/image leaves this game document.
 */
let previous = null;
export function observeGameFrame(canvas, doc = globalThis.document) {
  if (!canvas || canvas.width < 8 || canvas.height < 8) return { status: 'unavailable', reason: 'No native game frame is ready.' };
  try {
    const scratch = doc.createElement('canvas');
    scratch.width = 32; scratch.height = 24;
    const ctx = scratch.getContext('2d', { willReadFrequently: true });
    if (!ctx) return { status: 'unavailable', reason: 'Screen pixel readback is unsupported.' };
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(canvas, 0, 0, 32, 24);
    const rgba = ctx.getImageData(0, 0, 32, 24).data;
    let light = 0, reds = 0, greens = 0, blues = 0, min = 255, max = 0, delta = 0;
    const luminance = new Uint8Array(32 * 24);
    for (let i = 0; i < luminance.length; i++) {
      const n = i * 4, r = rgba[n], g = rgba[n+1], b = rgba[n+2];
      const l = Math.round((r * 54 + g * 183 + b * 19) / 256);
      luminance[i] = l; light += l; reds += r; greens += g; blues += b;
      min = Math.min(min, l); max = Math.max(max, l);
      if (previous) delta += Math.abs(l - previous[i]);
    }
    if (max === 0) return { status: 'unavailable', reason: 'The display returned a blank frame; Safari may block framebuffer readback.' };
    previous = luminance;
    const count = luminance.length;
    const dominant = reds > greens * 1.15 && reds > blues * 1.15 ? 'red'
      : greens > reds * 1.15 && greens > blues * 1.15 ? 'green'
      : blues > reds * 1.15 && blues > greens * 1.15 ? 'blue' : 'mixed';
    return {
      status: 'observed', source: 'native-emulator-display', width: canvas.width, height: canvas.height,
      brightness: Math.round(light / count / 255 * 100),
      contrast: Math.round((max - min) / 255 * 100),
      dominant, frameChange: previous && delta ? Math.round(delta / count / 255 * 100) : 0,
      // Frame change is temporal optical difference, never proof of movement or an enemy.
      limits: 'Pixel statistics only; no object or map identification.'
    };
  } catch {
    return { status: 'unavailable', reason: 'The emulator framebuffer is not readable by this browser.' };
  }
}
