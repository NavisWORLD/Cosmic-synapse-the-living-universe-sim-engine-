const VERSION = 'sim-earth-7-08-lost-cosmos-11-1';
const CORE = ['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./apple-touch-icon.png','./offline.html'];
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
