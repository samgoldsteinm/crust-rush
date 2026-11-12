// Crust Rush service worker: installs the game as an app and keeps every file for offline play.
// Game files have their content hash in the name, so a saved copy never goes stale; only the page itself is re-checked.
const VERSION = 'crust-rush-v153';
const SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-64.png",
  "./assets/geo/formula.a2521243d2.bin",
  "./assets/geo/gt.0614da9ec6.bin",
  "./assets/geo/hyper.6b7da65a37.bin",
  "./assets/geo/roadster.b954c55e8a.bin",
  "./assets/geo/tourer.10219a867b.bin",
  "./assets/geo/concept.4896a96dc6.bin",
  "./assets/geo/interceptor.1da367a926.bin",
  "./assets/geo/monster.c1c7d0aa59.bin",
  "./assets/geo/muscle.c6a8fa4e96.bin",
  "./assets/geo/wheelset.01d35e5074.bin",
  "./assets/geo/gokart.baf72d914c.bin",
  "./assets/geo/chariot.1fb96afc85.bin",
  "./assets/geo/hatch.db29691d7a.bin",
  "./assets/geo/coupe.ed9b78f64b.bin",
  "./assets/geo/scissor.641b1efa5f.bin",
  "./assets/geo/suv.a3c94fb4a4.bin",
  "./assets/geo/formula_hq.3b711f9dbc.bin",
  "./assets/geo/gt_hq.843754961c.bin",
  "./assets/geo/hyper_hq.eaafa35d8f.bin",
  "./assets/geo/tourer_hq.6a5a22f4db.bin",
  "./assets/geo/concept_hq.702ecf66ed.bin",
  "./assets/geo/interceptor_hq.c61f046b3c.bin",
  "./assets/geo/gokart_hq.8abaeecd3e.bin",
  "./assets/geo/hatch_hq.682ec32c9c.bin",
  "./assets/geo/scissor_hq.cfb581826d.bin",
  "./assets/geo/suv_hq.eea66bc13f.bin",
  "./assets/geo/onyx.bd5e8ef3d3.bin",
  "./assets/geo/bike_moto.6d0d279356.bin",
  "./assets/geo/bike_mx.d260f3fac9.bin",
  "./assets/geo/bike_neutron.33a8caa28c.bin",
  "./assets/geo/bike_rocket.c1d0ba014a.bin",
  "./assets/geo/bike_june.a357af641e.bin",
  "./assets/geo/tree_pine1.55f1df225a.bin",
  "./assets/geo/tree_pine2.51237a24e1.bin",
  "./assets/geo/tree_round1.cc883fdab7.bin",
  "./assets/geo/tree_round2.be26072d49.bin",
  "./assets/geo/tree_shrub.0ddbd87366.bin",
  "./assets/geo/skyline.f6c0aa9c1a.bin",
  "./assets/geo/mount.5104833cac.bin",
  "./assets/geo/tunnel.975467a68d.bin",
  "./assets/geo/city.bce45a74fe.bin",
  "./assets/geo/tree_pine1_lo.c9c9061205.bin",
  "./assets/geo/tree_pine2_lo.0f99873fb2.bin",
  "./assets/geo/tree_round1_lo.3d6fd5a921.bin",
  "./assets/geo/tree_round2_lo.1c0ead0363.bin",
  "./assets/geo/waterfall.efc038e2cf.bin",
  "./assets/geo/riverbed.6009bf3d95.bin",
  "./assets/geo/pond.1dafdeeb39.bin",
  "./assets/tex/tex_ar_arena.f7dc7fc88b.jpg",
  "./assets/tex/tex_ar_track.579b73460a.jpg",
  "./assets/tex/tex_ar_glow.67ce84a9df.jpg",
  "./assets/tex/tex_wrap.0418d23b18.jpg",
  "./assets/tex/tex_skyline.457a6fecf7.jpg",
  "./assets/tex/tex_skyline_e.30cb2dfa85.jpg",
  "./assets/tex/tex_mount.b8a1c13020.jpg",
  "./assets/tex/tex_space.98cb95ba4c.jpg",
  "./assets/tex/tex_wf0.76f8455401.jpg",
  "./assets/tex/tex_wf1.8327e7fb03.jpg",
  "./assets/tex/tex_wf2.b9baa7fcb6.jpg",
  "./assets/tex/tex_wf3.1339551440.jpg",
  "./assets/tex/tex_wf4.5a24678b6c.jpg",
  "./assets/tex/tex_wf5.c7c965caa0.jpg",
  "./assets/tex/tex_wf6.2c65d0bc3f.jpg",
  "./assets/tex/tex_wf7.6ffe181e72.jpg",
  "./assets/tex/tex_wf8.735a884f42.jpg",
  "./assets/tex/tex_wf9.c0a2dc9c2d.jpg",
  "./assets/tex/tex_riverbed.0b4642c165.jpg",
  "./assets/tex/sky_anime.590aabd5d9.jpg",
  "./assets/tex/sky_beach.d899e80210.jpg",
  "./assets/tex/sky_mc.e744b96a84.jpg",
  "./assets/tex/sky_cave.7ed938e790.jpg",
  "./assets/tex/sky_nebula.f4e8c6c9bb.jpg",
  "./assets/tex/tex_pond.8f551e9556.jpg",
  "./assets/tex/tex_pondgrass.ea3a48c6f8.jpg",
  "./assets/shots/margherita-h.3e4a083708.jpg",
  "./assets/shots/margherita-m.15a3940147.jpg",
  "./assets/shots/margherita-a.04a971fcaf.jpg",
  "./assets/shots/bay-h.70de7c4f1b.jpg",
  "./assets/shots/bay-m.0a596b5f3f.jpg",
  "./assets/shots/bay-a.f50b1f7212.jpg",
  "./assets/shots/peaks-h.8fe9ab6669.jpg",
  "./assets/shots/peaks-m.af3185d303.jpg",
  "./assets/shots/peaks-a.2858e28fd4.jpg",
  "./assets/shots/frosty-h.b7998b7897.jpg",
  "./assets/shots/frosty-m.f51533d319.jpg",
  "./assets/shots/frosty-a.056d66d184.jpg",
  "./assets/shots/basil-h.b3ea150372.jpg",
  "./assets/shots/basil-m.2df9f767a6.jpg",
  "./assets/shots/basil-a.69466899c4.jpg",
  "./assets/shots/lagoon-h.ad7aec11ef.jpg",
  "./assets/shots/lagoon-m.1357c9c3ed.jpg",
  "./assets/shots/lagoon-a.0b1219d96d.jpg",
  "./assets/shots/mozz-h.f538d7ca40.jpg",
  "./assets/shots/mozz-m.c118b15808.jpg",
  "./assets/shots/mozz-a.9e53da4963.jpg",
  "./assets/shots/burn-h.625d53ad01.jpg",
  "./assets/shots/burn-m.dc88d4067c.jpg",
  "./assets/shots/burn-a.1d6712b800.jpg",
  "./assets/shots/oven-h.08bbae318d.jpg",
  "./assets/shots/oven-m.357fd1ac89.jpg",
  "./assets/shots/oven-a.98375bd2f2.jpg",
  "./assets/shots/calzone-h.24ab9561aa.jpg",
  "./assets/shots/calzone-m.c2bfb31d8e.jpg",
  "./assets/shots/calzone-a.24d1e02f98.jpg",
  "./assets/shots/napoli-h.45c22e65c8.jpg",
  "./assets/shots/napoli-m.5ab090553f.jpg",
  "./assets/shots/napoli-a.f1a62ff48e.jpg",
  "./assets/shots/glacier-h.183d6663fa.jpg",
  "./assets/shots/glacier-m.f64e168e66.jpg",
  "./assets/shots/glacier-a.34d6c6d329.jpg",
  "./assets/shots/spiral-h.627f7be3fa.jpg",
  "./assets/shots/spiral-m.2462d9b32f.jpg",
  "./assets/shots/spiral-a.3aff3c723e.jpg",
  "./assets/shots/tour-h.ba27e35168.jpg",
  "./assets/shots/tour-m.9dafc15de3.jpg",
  "./assets/shots/tour-a.d7323180ea.jpg",
  "./assets/shots/moon-h.b45142e46e.jpg",
  "./assets/shots/moon-m.9d4cf94a3c.jpg",
  "./assets/shots/moon-a.0123de80e9.jpg",
  "./assets/shots/peak-h.8ab9de0c73.jpg",
  "./assets/shots/peak-m.d99684e38a.jpg",
  "./assets/shots/peak-a.4bb350175e.jpg",
  "./assets/shots/grid-h.6c586748d8.jpg",
  "./assets/shots/grid-m.2e43e63f50.jpg",
  "./assets/shots/grid-a.830a3e08e6.jpg",
  "./assets/shots/holo-h.c491ee40fe.jpg",
  "./assets/shots/holo-m.5359c8c9a0.jpg",
  "./assets/shots/holo-a.40fc34a978.jpg",
  "./assets/shots/laser-h.c2ba6ec1cb.jpg",
  "./assets/shots/laser-m.ef4bd9b8d3.jpg",
  "./assets/shots/laser-a.4d762e950a.jpg",
  "./assets/shots/synth-h.41729b54f1.jpg",
  "./assets/shots/synth-m.f94348a683.jpg",
  "./assets/shots/synth-a.99c3b6fb96.jpg",
  "./assets/shots/bedroom-h.9131c26320.jpg",
  "./assets/shots/bedroom-m.731b08b6d4.jpg",
  "./assets/shots/bedroom-a.021ce52f70.jpg",
  "./css/style.28ec637177.css",
  "./js/game.b053e8aaf5.js",
  "./vendor/three-0.149.0.min.js"
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then(async (c) => {
    // fetch what this browser doesn't already hold, a few at a time
    const todo = [];
    for (const u of SHELL) if (!(await caches.match(u))) todo.push(u);
    let i = 0;
    const worker = async () => { while (i < todo.length) { const u = todo[i++]; try { await c.add(u); } catch (e) {} } };
    await Promise.all([worker(), worker()]);
  }).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    // carry files from older caches into the new one, then drop the old caches
    const keep = new Set(SHELL.map((u) => new URL(u, self.location).href));
    const cur = await caches.open(VERSION);
    for (const k of await caches.keys()) {
      if (k === VERSION) continue;
      const old = await caches.open(k);
      for (const req of await old.keys()) if (keep.has(req.url) && !(await cur.match(req))) { const r = await old.match(req); if (r) await cur.put(req, r); }
      await caches.delete(k);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // The page: network first so updates show up, saved copy when offline.
  if (req.mode === 'navigate' || (url.origin === location.origin && (url.pathname.endsWith('.html') || url.pathname.endsWith('/')))) {
    event.respondWith(
      fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' })
        .then((res) => { if (res.ok && (url.pathname.endsWith('/') || url.pathname.endsWith('/index.html'))) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put('./index.html', copy)); } return res; })
        .catch(() => caches.match(url.pathname.endsWith('/') || url.pathname.endsWith('/index.html') ? './index.html' : req))
    );
    return;
  }

  if (url.pathname.endsWith('/version.json')) { event.respondWith(fetch(req.url, { cache: 'no-store' })); return; }

  // Hashed game files never change: saved copy first.
  if (url.origin === location.origin && /\.[0-9a-f]{10}\.(js|css|bin|jpg)$/.test(url.pathname)) {
    event.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    })));
    return;
  }

  // Everything else (fonts, icons, engine): saved copy, refreshed in the background.
  event.respondWith(
    caches.open(VERSION).then((cache) =>
      cache.match(req).then((hit) => {
        const net = fetch(req)
          .then((res) => { if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone()); return res; })
          .catch(() => hit);
        return hit || net;
      })
    )
  );
});
