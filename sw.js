const CACHE = 'rss-reader-v2';
const FEED_TTL = 30 * 60 * 1000; // 30 minutes

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => clients.claim())
));

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (!url.pathname.match(/\/feed-[^/]+\.json$/)) return;

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(e.request);

    if (cached) {
      const age = Date.now() - new Date(cached.headers.get('sw-cached-at') || 0).getTime();
      if (age < FEED_TTL) return cached;
    }

    try {
      const fresh = await fetch(e.request);
      if (fresh.ok) {
        // Clone and inject a timestamp header so we can measure age
        const headers = new Headers(fresh.headers);
        headers.set('sw-cached-at', new Date().toISOString());
        const stamped = new Response(await fresh.clone().blob(), { status: fresh.status, statusText: fresh.statusText, headers });
        cache.put(e.request, stamped);
      }
      return fresh;
    } catch {
      return cached || Response.error();
    }
  })());
});
