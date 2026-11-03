// Crust Rush service worker: installs the game as an app and keeps every file for offline play.
// Game files have their content hash in the name, so a saved copy never goes stale; only the page itself is re-checked.
const VERSION = 'crust-rush-v48';
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
  "./assets/shots/grid-h.c38df1173a.jpg",
  "./assets/shots/grid-m.937c71e878.jpg",
  "./assets/shots/grid-a.bbfac8514d.jpg",
  "./assets/shots/margherita-h.6ce3ada66e.jpg",
  "./assets/shots/margherita-m.b4a457a59e.jpg",
  "./assets/shots/margherita-a.63fa4045d9.jpg",
  "./assets/shots/bay-h.5c6925bf30.jpg",
  "./assets/shots/bay-m.f78814aad2.jpg",
  "./assets/shots/bay-a.e8b4db14ba.jpg",
  "./assets/shots/peaks-h.cb9a6599d0.jpg",
  "./assets/shots/peaks-m.4671308761.jpg",
  "./assets/shots/peaks-a.1d210edbf1.jpg",
  "./assets/shots/frosty-h.6471d76ac7.jpg",
  "./assets/shots/frosty-m.a7ad14050c.jpg",
  "./assets/shots/frosty-a.7008fa84b6.jpg",
  "./assets/shots/basil-h.191aa8d2b4.jpg",
  "./assets/shots/basil-m.48f2a902c0.jpg",
  "./assets/shots/basil-a.3df943014b.jpg",
  "./assets/shots/lagoon-h.81d45edf5e.jpg",
  "./assets/shots/lagoon-m.14563e7ab0.jpg",
  "./assets/shots/lagoon-a.37dbae5165.jpg",
  "./assets/shots/mozz-h.ba70f9f0d3.jpg",
  "./assets/shots/mozz-m.5d83dc561b.jpg",
  "./assets/shots/mozz-a.67273baaec.jpg",
  "./assets/shots/burn-h.f6dabab80e.jpg",
  "./assets/shots/burn-m.4f65928d9c.jpg",
  "./assets/shots/burn-a.92f7910956.jpg",
  "./assets/shots/oven-h.2077fa2220.jpg",
  "./assets/shots/oven-m.039387c5be.jpg",
  "./assets/shots/oven-a.2ca3d2d284.jpg",
  "./assets/shots/calzone-h.e5d49dacb8.jpg",
  "./assets/shots/calzone-m.4954e29f9e.jpg",
  "./assets/shots/calzone-a.3c215fa317.jpg",
  "./assets/shots/napoli-h.1b8256ba7e.jpg",
  "./assets/shots/napoli-m.2db935db3e.jpg",
  "./assets/shots/napoli-a.697c353c0c.jpg",
  "./assets/shots/glacier-h.d4a319f7d7.jpg",
  "./assets/shots/glacier-m.749ed07a41.jpg",
  "./assets/shots/glacier-a.18530639c1.jpg",
  "./assets/shots/spiral-h.333d0a8af9.jpg",
  "./assets/shots/spiral-m.7aa3bf22d4.jpg",
  "./assets/shots/spiral-a.0b498fc09c.jpg",
  "./assets/shots/tour-h.e063e40ed0.jpg",
  "./assets/shots/tour-m.10faa0decc.jpg",
  "./assets/shots/tour-a.dfebfdcb40.jpg",
  "./assets/shots/moon-h.7f7974a10f.jpg",
  "./assets/shots/moon-m.bcd1682a6c.jpg",
  "./assets/shots/moon-a.87128032f5.jpg",
  "./assets/shots/peak-h.186d4aea66.jpg",
  "./assets/shots/peak-m.4003974e0a.jpg",
  "./assets/shots/peak-a.d8b995f958.jpg",
  "./css/style.5ac9056e35.css",
  "./js/game.efc89d3d5e.js",
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
      fetch(req)
        .then((res) => { if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put('./index.html', copy)); } return res; })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

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
