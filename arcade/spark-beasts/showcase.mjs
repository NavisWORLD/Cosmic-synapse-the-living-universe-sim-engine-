/**
 * Rare-spark showcase catalog.
 * The manifest lists every clip, including ones another copy of the tree
 * may not have yet. The gallery only shows a clip when its video file exists.
 */

export const SHOWCASE_SCHEMA = 'spark-beasts-rare-showcase-v1';

const BARE = /^[\w.-]+$/;
const RARE = /^rare\/[\w.-]+$/;

export function safeMediaPath(file) {
  if (typeof file !== 'string' || !file || file.includes('..') || file.includes('\\') || file.startsWith('/')) return null;
  if (file === 'montage.mp4') return file;
  if (RARE.test(file)) return file;
  if (BARE.test(file)) return `rare/${file}`;
  return null;
}

export async function presentClips(manifest, exists) {
  if (!manifest || manifest.schema !== SHOWCASE_SCHEMA || !Array.isArray(manifest.clips)) {
    throw new Error('Unexpected rare spark manifest');
  }
  const clips = [];
  for (const clip of manifest.clips) {
    const video = safeMediaPath(clip?.video);
    if (!video || !(await exists(video))) continue;
    const log = safeMediaPath(clip.audioLog);
    const audioLog = log && await exists(log) ? log : null;
    clips.push({
      name: String(clip.name || 'Rare spark'),
      seconds: Number(clip.seconds) > 0 ? Number(clip.seconds) : 18,
      video,
      audioLog,
    });
  }
  return clips;
}
