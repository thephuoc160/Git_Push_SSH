const CACHE_NAME = 'appquiz-cache-v1';
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.ico',
  './icons/app-icon-192.png',
  './icons/app-icon-512.png'
];
const EXTERNAL_ASSETS = [
  'https://unpkg.com/xlsx@0.18.5/dist/xlsx.full.min.js'
];
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async cache => {
      await cache.addAll(CORE_ASSETS);
      await Promise.all(
        EXTERNAL_ASSETS.map(url => cache.add(url).catch(() => undefined))
      );
    }).then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(key => key === CACHE_NAME ? Promise.resolve() : caches.delete(key)))).then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') {
    return;
  }
  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) {
        return cached;
      }
      return fetch(request).then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          const sameOrigin = request.url.startsWith(self.location.origin);
          if (sameOrigin || EXTERNAL_ASSETS.includes(request.url)) {
            cache.put(request, copy);
          }
        });
        return response;
      }).catch(() => {
        if (request.mode === 'navigate') {
          return caches.match('./index.html');
        }
        return caches.match('./favicon.ico');
      });
    })
  );
});
