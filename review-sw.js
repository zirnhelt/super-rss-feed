// Service worker for the review web app. Network-first for the page and the day's batch (a
// stale batch would be rated against a fresh `_batch` key), cache-first for static assets.
// Cross-origin requests (the GitHub Contents API save) are never touched.
const CACHE = 'review-app-v1';
const SHELL = ['review.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png',
               'icons/apple-touch-icon.png'];

self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

async function networkFirst(request) {
    const cache = await caches.open(CACHE);
    try {
        const fresh = await fetch(request);
        if (fresh.ok) await cache.put(request.url.split('?')[0], fresh.clone());
        return fresh;
    } catch (err) {
        const cached = await cache.match(request.url.split('?')[0]);
        if (cached) return cached;
        throw err;
    }
}

async function cacheFirst(request) {
    const cached = await caches.match(request);
    return cached || fetch(request);
}

self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    if (request.method !== 'GET' || url.origin !== self.location.origin) return;

    const path = url.pathname;
    if (path.endsWith('/review.html') || path.endsWith('/feed-review.json')) {
        event.respondWith(networkFirst(request));
    } else if (path.includes('/icons/') || path.endsWith('/manifest.webmanifest')) {
        event.respondWith(cacheFirst(request));
    }
});
