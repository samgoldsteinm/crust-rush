"""Render the web game's soundtrack for the PC build: every track's song and the four menu songs.

The web game builds its music in the browser, section by section (intro, verse, pre-chorus, chorus, bridge,
final chorus), and plays them in the order intro, verse, pre, chorus, verse, pre, chorus, bridge, chorusX, then
loops back to the first verse. Here each section is rendered the same way (OfflineAudioContext, 32 kHz), laid
end to end with their tails overlapping exactly as the web schedules them, and the body's last tail is wrapped
onto its start so the loop is seamless. Each song becomes one Ogg Vorbis file with its loop point and where the
chorus starts (the final lap jumps there). Writes OUT/<key>.ogg and OUT/music.json.
Usage: WEB=web OUT=music [ONLY=key,key] python3 tools/cimusic.py   (needs ffmpeg)
"""
import asyncio, base64, functools, http.server, json, os, re, subprocess, sys, threading, time, wave
import numpy as np
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
OUT = os.environ.get('OUT', 'music')
ONLY = [k for k in os.environ.get('ONLY', '').split(',') if k]
PORT = 8811
PLAN = ['intro', 'verse', 'pre', 'chorus', 'verse', 'pre', 'chorus', 'bridge', 'chorusX']
LOOP = 1


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()

RENDER = r'''async ([key, id]) => {
  const S = SONGS2[key]; if (!S) return null;
  const r = await musRender(S, id, 32000);
  const b = r.buf, n = b.length, ch = b.numberOfChannels, out = [];
  for (let c = 0; c < Math.min(2, ch); c++) {
    const d = b.getChannelData(c), q = new Int16Array(n);
    for (let i = 0; i < n; i++) { const v = Math.max(-1, Math.min(1, d[i])); q[i] = v < 0 ? v * 32768 : v * 32767; }
    let s = ''; const u = new Uint8Array(q.buffer); const C = 0x8000;
    for (let i = 0; i < u.length; i += C) s += String.fromCharCode.apply(null, u.subarray(i, i + C));
    out.push(btoa(s));
  }
  return {sr: b.sampleRate, dur: r.dur, ch: out};
}'''


async def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 640, 'height': 360}, service_workers='block')
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            u = r.request.url
            if re.search(r'/js/game\.[0-9a-f]+\.js', u):
                resp = await r.fetch()
                body = await resp.text()
                body = body.replace('requestAnimationFrame(frame);\n})();', 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();')
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            else:
                await r.continue_()
        await pg.route('**/*', route)
        await pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='domcontentloaded', timeout=300000)
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=900000)
        # hand the page's render function out of its closure
        await pg.evaluate("__ev(`window.__musR=" + RENDER.replace('`', '\\`') + ";1`)")
        keys = json.loads(await pg.evaluate("__ev(`JSON.stringify(Object.keys(SONGS2))`)"))
        maps = json.loads(await pg.evaluate("__ev(`JSON.stringify(MAPS.map(m=>[m.id,SONGS2[m.id]?m.id:SONGS2[m.song]?m.song:'margherita']))`)"))
        menu = json.loads(await pg.evaluate("__ev(`JSON.stringify(MENU_SONGS)`)"))
        print('booted', round(time.time() - t0), 's;', len(keys), 'songs', flush=True)
        info = {'songs': {}, 'maps': {m: k for m, k in maps}, 'menu': menu, 'vol': {'race': 0.62, 'menu': 0.95, 'paused': 0.3, 'loading': 0.55, 'music': 0.45}}
        for key in keys:
            if ONLY and key not in ONLY:
                continue
            secs = {}
            for sid in dict.fromkeys(PLAN):
                r = await pg.evaluate("a=>window.__musR(a)", [key, sid])
                if not r:
                    continue
                chans = [np.frombuffer(base64.b64decode(c), dtype=np.int16).astype(np.float32) / 32768.0 for c in r['ch']]
                if len(chans) == 1:
                    chans.append(chans[0])
                secs[sid] = {'sr': r['sr'], 'dur': r['dur'], 'a': np.stack(chans)}
            if 'verse' not in secs:
                print('skip', key, flush=True)
                continue
            sr = secs['verse']['sr']
            # lay the sections end to end as the web schedules them: each starts when the one before has
            # played its bars (dur); its sound runs on past that (reverb, decays), overlapping the next
            def place(seq, start):
                t = start
                items = []
                for sid in seq:
                    s = secs.get(sid) or secs['verse']
                    items.append((int(round(t * sr)), s['a']))
                    t += s['dur']
                return items, t
            intro_items, t_body = place(PLAN[:LOOP], 0.0)
            body_items, t_end = place(PLAN[LOOP:], t_body)
            n_end = int(round(t_end * sr))
            n_body = int(round(t_body * sr))
            mix = np.zeros((2, n_end), dtype=np.float32)
            for off, a in intro_items + body_items:
                n = a.shape[1]
                stop = min(n_end, off + n)
                mix[:, off:stop] += a[:, :stop - off]
                # the body's last sounds ring on past its end: wrap them onto the start of the loop
                if off + n > n_end:
                    over = a[:, n_end - off:]
                    k = 0
                    while k < over.shape[1]:
                        seg = over[:, k:k + (n_end - n_body)]
                        mix[:, n_body:n_body + seg.shape[1]] += seg
                        k += seg.shape[1]
            peak = float(np.max(np.abs(mix))) or 1.0
            if peak > 0.99:
                mix *= 0.99 / peak
            wav = os.path.join(OUT, key + '.wav')
            with wave.open(wav, 'wb') as w:
                w.setnchannels(2)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
            ogg = os.path.join(OUT, key + '.ogg')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-c:a', 'libvorbis', '-q:a', '3', ogg], check=True)
            os.remove(wav)
            chorus = t_body + sum((secs.get(s) or secs['verse'])['dur'] for s in PLAN[LOOP:PLAN.index('chorus')])
            info['songs'][key] = {'file': key + '.ogg', 'loop': round(t_body, 4), 'len': round(t_end, 4), 'chorus': round(chorus, 4), 'menu': bool(key in menu)}
            print('song', key, 'loop at %.2f s, %.1f s long, chorus at %.2f s, %d KB' % (t_body, t_end, chorus, os.path.getsize(ogg) // 1024), round(time.time() - t0), flush=True)
        json.dump(info, open(os.path.join(OUT, 'music.json'), 'w'), indent=1)
        print('done', round(time.time() - t0), 's, errors', errs[:5], flush=True)
        await b.close()

asyncio.run(main())
