const CACHE = 'rss-reader-v1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(clients.claim()));

// Network-first for feed JSON; let everything else pass through.
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.match(/\/feed-[^/]+\.json$/)) {
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
  }
});
