/** Speech-bubble text. A line is never cleared to empty once the beast has spoken. */

export function nonempty(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

export function resolveBubble(primary, secondary, fallback = '...') {
  return nonempty(primary) || nonempty(secondary) || nonempty(fallback) || '...';
}

/**
 * Habit and hiccup lines used to call the bubble hook without extending the
 * timer. The same frame then saw an expired timer and wrote an empty string,
 * so the bubble flashed blank. Holding the last real line removes that path.
 */
export function holdBubble(previous, incoming, now = 0) {
  if (incoming) {
    const text = resolveBubble(incoming.text, incoming.line, previous?.text || '...');
    return {
      text,
      line: nonempty(incoming.line),
      until: now + Math.max(0.8, Number(incoming.dur) || 2.2),
    };
  }
  const kept = nonempty(previous?.text);
  if (kept) return { text: kept, line: nonempty(previous.line), until: previous.until };
  return { text: '...', line: '', until: now + 2 };
}
