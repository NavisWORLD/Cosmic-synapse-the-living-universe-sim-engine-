/** The pinned native core requests an optional screen lock without awaiting it.
 * Browsers may deny that request even after a play gesture. Keep that denial
 * local to this handheld, without changing permissions or the vendored core.
 */
export function handleOptionalWakeLock(wakeLock) {
  if (!wakeLock?.request) return;
  const request = wakeLock.request.bind(wakeLock);
  wakeLock.request = async (...args) => {
    try { return await request(...args); }
    catch (error) {
      if (['NotAllowedError', 'SecurityError', 'AbortError'].includes(error?.name)) return null;
      throw error;
    }
  };
}
