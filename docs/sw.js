/* sw.js — Service Worker NetMikuji */

const CACHE = 'net-mikuji-v1';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './data/loto6.json',
  './data/loto7.json',
  './data/miniloto.json',
];

/* Instalação: pré-carrega assets principais */
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache =>
      Promise.allSettled(ASSETS.map(url => cache.add(url)))
    ).then(() => self.skipWaiting())
  );
});

/* Ativação: remove caches antigos */
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* Fetch: cache-first para assets estáticos, network-first para dados */
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  /* Dados JSON — network-first: tenta buscar atualizado, fallback no cache */
  if (url.pathname.endsWith('.json')) {
    e.respondWith(
      fetch(e.request)
        .then(resp => {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  /* Resto — cache-first */
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
