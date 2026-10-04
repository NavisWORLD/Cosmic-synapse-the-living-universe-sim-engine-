/**
 * Draws a QR symbol for a share link. The encoder is the MIT Nayuki library.
 * The link itself is the trade ticket. The symbol does not hold a secret.
 */
import { qrcodegen } from './qrcodegen.mjs';

export function qrMatrix(text) {
  const Qr = qrcodegen.QrCode;
  const Seg = qrcodegen.QrSegment;
  const bytes = new TextEncoder().encode(String(text));
  if (bytes.length > 700) throw new Error('That share link is too long for a QR symbol. Download the .qbeast file instead.');
  const seg = Seg.makeBytes(bytes);
  const qr = Qr.encodeSegments([seg], Qr.Ecc.MEDIUM);
  const rows = [];
  for (let y = 0; y < qr.size; y++) {
    let row = '';
    for (let x = 0; x < qr.size; x++) row += qr.getModule(x, y) ? '1' : '0';
    rows.push(row);
  }
  return rows;
}

export function drawQr(canvas, text) {
  const rows = qrMatrix(text);
  const n = rows.length;
  const scale = Math.max(2, Math.floor(300 / (n + 8)));
  const quiet = 4;
  const size = (n + quiet * 2) * scale;
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#f4fffd';
  ctx.fillRect(0, 0, size, size);
  ctx.fillStyle = '#071018';
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      if (rows[y][x] === '1') ctx.fillRect((x + quiet) * scale, (y + quiet) * scale, scale, scale);
    }
  }
  return rows;
}
