const VERSION = 'cute-beast-pocket-reality-v11-spark-beastboy39';
const CORE = ['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./apple-touch-icon.png','./offline.html',
  './arcade/spark-beasts/index.html','./arcade/spark-beasts/app.mjs','./arcade/spark-beasts/draw.mjs',
  './arcade/spark-beasts/engine.mjs','./arcade/spark-beasts/explore.mjs','./arcade/spark-beasts/genome.mjs',
  './arcade/spark-beasts/hash.mjs','./arcade/spark-beasts/live.mjs','./arcade/spark-beasts/render.mjs',
  './arcade/spark-beasts/runs.mjs','./arcade/spark-beasts/sensors.mjs','./arcade/spark-beasts/showcase.mjs',
  './arcade/spark-beasts/signal.mjs','./arcade/spark-beasts/store.mjs','./arcade/spark-beasts/trade.mjs',
  './arcade/spark-beasts/voice.mjs','./arcade/spark-beasts/voice-synth.mjs',
  './arcade/spark-beasts/data/quantum-runs.json','./arcade/spark-beasts/media/rare/manifest.json',
  './arcade/lost-cosmos/muse.mjs','./arcade/lost-cosmos/mailbox.mjs','./arcade/lost-cosmos/qbeast.mjs',
  './arcade/lost-cosmos/synapse-os.mjs','./arcade/lost-cosmos/qr.mjs','./arcade/lost-cosmos/qrcodegen.mjs'];
self.addEventListener('install', event => event.waitUntil(caches.open(VERSION).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).then(resp => {
    if (resp.ok) {
      const copy = resp.clone(); event.waitUntil(caches.open(VERSION).then(c=>c.put(event.request, copy)));
    }
    return resp;
  }).catch(async()=>{
    const cached = await caches.match(event.request);
    if (cached) return cached;
    if (event.request.mode === 'navigate') return caches.match('./offline.html');
    return Response.error();
  }));
});
