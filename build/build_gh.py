"""Build the GitHub Pages version of Crust Rush from the single-file source.

Output layout (in D:/crust-rush/app):
  index.html                 page markup + small boot data
  css/style.<hash>.css       all styles
  js/game.<hash>.js          the game
  vendor/three-0.149.0.min.js
  assets/geo/<id>.<hash>.bin one file per car and prop model
  assets/tex/<name>.<hash>.jpg   skies and prop textures
  assets/shots/<id>-<k>.<hash>.jpg track photos
  sw.js                      offline cache with the full file list
Hashed names mean a changed file always gets a new URL, so a cached old copy can never be mixed with new code.
"""
import json, re, os, shutil, hashlib, base64, subprocess, sys
SRC = 'D:/crust-rush/source/crust-rush.html'
APP = 'D:/crust-rush/app'
GH = 'D:/crust-rush/source/build'
HQ = GH + '/hq'           # higher-quality replacements: hq/tex/<name>.jpg, hq/shots/<id>-<k>.jpg
SWVER = sys.argv[1] if len(sys.argv) > 1 else 'crust-rush-v32'

s = open(SRC).read()
subprocess.run(['node', GH + '/extract.js', SRC], check=True, cwd=GH, stdout=subprocess.DEVNULL)
spans = json.load(open(GH + '/spans.json'))
D = {k: json.load(open(f'{GH}/{k}.json')) for k in spans}

h8 = lambda b: hashlib.sha1(b).hexdigest()[:10]
for d in ['assets', 'js', 'css', 'vendor']:
    shutil.rmtree(f'{APP}/{d}', ignore_errors=True)
os.makedirs(f'{APP}/assets/tex'); os.makedirs(f'{APP}/assets/geo'); os.makedirs(f'{APP}/assets/shots'); os.makedirs(f'{APP}/js'); os.makedirs(f'{APP}/css'); os.makedirs(f'{APP}/vendor')
files = []
def put(rel, data):
    open(f'{APP}/{rel}', 'wb').write(data); files.append(rel); return rel
def hashed(dirn, stem, ext, data):
    return put(f'{dirn}/{stem}.{h8(data)}.{ext}', data)

# ---- models: one file per model, so an update only re-downloads the models that changed; high-detail bodies load after the menu
items = []; geo_total = 0
os.makedirs(f'{APP}/assets/geo', exist_ok=True)
for kind, key in (('c', 'CAR_PACKS'), ('p', 'PROP_PACKS')):
    for id_, v in D[key].items():
        b = base64.b64decode(v['d']); rel = hashed('assets/geo', id_, 'bin', b); geo_total += len(b)
        items.append([kind, id_, rel, len(b), 1 if id_.endswith('_hq') else 0])
geo = b''

def img(dirn, stem, b64, hq):
    p = f'{HQ}/{hq}'
    data = open(p, 'rb').read() if os.path.exists(p) else base64.b64decode(b64)
    return hashed(dirn, stem, 'png' if data[:4] == b'\x89PNG' else 'jpg', data)   # (a texture with holes in it is a PNG: put_tex.py)
tex = {n: img('assets/tex', n, v, f'tex/{n}.jpg') for n, v in D['PROP_TEX'].items()}
shots = {}
for id_, v in D['MAP_SHOTS'].items():
    e = {k: img('assets/shots', f'{id_}-{k}', v[k], f'shots/{id_}-{k}.jpg') for k in ('h', 'm', 'a')}
    e['i'] = v['i']; shots[id_] = e

js = lambda o: json.dumps(o, separators=(',', ':'))
repl = {
    'CAR_PACKS': js({k: {'h': v['h']} for k, v in D['CAR_PACKS'].items()}),
    'PROP_PACKS': js({k: {'h': v['h']} for k, v in D['PROP_PACKS'].items()}),
    'PROP_TEX': js(tex),
    'MAP_SHOTS': js(shots),
}
out = s
for k in sorted(spans, key=lambda k: -spans[k]['start']):
    a, b = spans[k]['start'], spans[k]['end']; out = out[:a] + repl[k] + out[b:]

# ---- split page into css / markup / game script
st0 = out.index('<style>'); st1 = out.index('</style>')
css = out[st0 + 7:st1]
sc0 = out.index('<script src="https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"></script>')
g0 = out.index('<script>', sc0); g1 = out.rindex('</script>')
game = out[g0 + 8:g1]
markup = out[st1 + 8:sc0]
headx = out[:st0]
headx = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', '', headx).replace('<title>Crust Rush</title>\n', '').replace('<title>Crust Rush</title>', '')
assert 'CAR_PACKS={formula:' not in game and 'base64,/9j' not in game

css_rel = hashed('css', 'style', 'css', css.encode())
game_rel = hashed('js', 'game', 'js', game.encode())
three_rel = put('vendor/three-0.149.0.min.js', open(GH + '/vendor/three-0.149.0.min.js', 'rb').read())
# newer three.js (r187) for the WebGPU work: the engine check page uses it now; the game itself still loads r149
os.makedirs(f'{APP}/vendor/three-0.187.0', exist_ok=True)
for fn in ('three.core.js', 'three.module.js', 'three.webgpu.js', 'three.tsl.js'):
    put(f'vendor/three-0.187.0/{fn}', open(f'{GH}/vendor/three-0.187.0/{fn}', 'rb').read())
shutil.copy(GH + '/gpu-check.html', f'{APP}/gpu-check.html')
shutil.copy(GH + '/gpu-check.html', f'{APP}/engine-check.html')

ext = {'items': items}
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="description" content="Crust Rush: a 3D kart racer on giant pizzas. Drift, boost, and loop your way to first.">
<meta name="theme-color" content="#160c09">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Crust Rush">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/favicon-64.png">
<title>Crust Rush</title>
{headx.strip()}
<link rel="preload" href="{three_rel}" as="script">
<link rel="stylesheet" href="{css_rel}">
</head>
<body>
{markup.strip()}
<script>window.CR_EXT={js(ext)};window.CR_BUILD={js(SWVER)};</script>
<script src="{three_rel}"></script>
<script src="{game_rel}"></script>
<script>
if('serviceWorker' in navigator){{let done=false;const reg=()=>{{if(done)return;done=true;navigator.serviceWorker.register('sw.js').catch(()=>{{}});}};addEventListener('cr-booted',reg);setTimeout(reg,90000);}}
/* stale-page guard: after a crash the browser may reload an old copy of this page from its cache; ask the server which build is current
   and, if this copy is older, reload once (cache-busting) while still on the menu. */
(()=>{{const K='cr-stale-reload';const check=()=>fetch('version.json?t='+Date.now(),{{cache:'no-store'}}).then(r=>r.json()).then(v=>{{if(!v||!v.build||v.build===window.CR_BUILD)return;if(sessionStorage.getItem(K)===v.build){{if(window.showBanner)showBanner('A newer version is online: close and reopen the app',3,'sm');return;}}sessionStorage.setItem(K,v.build);if(typeof state==='undefined'||state==='menu')location.replace(location.pathname+'?v='+encodeURIComponent(v.build));else window.__crStale=v.build;}}).catch(()=>{{}});
addEventListener('cr-booted',()=>setTimeout(check,1500));document.addEventListener('visibilitychange',()=>{{if(!document.hidden)check();}});}})();
</script>
</body>
</html>
'''
open(f'{APP}/index.html', 'w').write(page)
open(f'{APP}/version.json', 'w').write(json.dumps({'build': SWVER}))

shell = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png', './icons/favicon-64.png'] + ['./' + f for f in files if not f.startswith('vendor/three-0.187.0')]
sw = open(GH + '/sw_tmpl.js').read().replace('__VERSION__', SWVER).replace('__SHELL__', ',\n  '.join(json.dumps(x) for x in shell))
open(f'{APP}/sw.js', 'w').write(sw)
tot = sum(os.path.getsize(f'{APP}/{f}') for f in files)
print('page', len(page), 'game.js', len(game), 'geo', geo_total, 'files', len(files), 'total MB', round(tot / 1e6, 2))
