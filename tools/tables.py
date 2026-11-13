"""The game's four big asset tables, kept as ordinary files instead of as text inside crust-rush.html.

Until web v181 the source file carried every model, texture and track picture as base64 text: 73 MB in one file, against
GitHub's limit of 100 MB for a file, and every small change pushed the whole thing again. Now (owner's instruction,
2026-11-13: "Do what you have to do to be able to make the files fit") each asset is its own file under source/data/:

  CAR_PACKS   data/cars/<id>.json (the header: meta, wheels)  + data/cars/<id>.bin (the geometry, byte for byte)
  PROP_PACKS  data/geo/<id>.json  (the header)                + data/geo/<id>.bin
  PROP_TEX    data/tex/<name>.jpg or .png                       (the picture file itself)
  MAP_SHOTS   data/shots/<id>-<k>.jpg                           (each track's pictures: k is the picture's key, h m ...;
              the few plain facts kept with them are in MAP_SHOTS.order.json)
and data/<TABLE>.order.json keeps each table's entries in their order (the game lists some of them in that order).

Nothing is recompressed or changed: load() gives back exactly the table that used to be written in the source file
(same keys, same order, the same base64 text), and the build puts the tables into the game exactly as before.
In crust-rush.html each table is now declared empty: `const PROP_TEX={};`.

  from tables import load, save
  D = load('PROP_TEX'); D['tex_toy_x'] = b64; save('PROP_TEX', D)      # writes only what changed, removes what is gone
"""
import base64, json, os

DATA = 'D:/crust-rush/source/data'
DIRS = {'CAR_PACKS': 'cars', 'PROP_PACKS': 'geo', 'PROP_TEX': 'tex', 'MAP_SHOTS': 'shots'}
NAMES = tuple(DIRS)


def _ext(b):
    return 'png' if b[:4] == b'\x89PNG' else 'jpg'


def _is_pic(x):
    """a track's entry holds pictures (long base64 text) and a few plain facts (anything else): only pictures become files"""
    return isinstance(x, str) and len(x) > 400


def _num(x):
    """numbers as JavaScript writes them (1.0 -> 1): the tables used to pass through JavaScript on their way into the build, and a
    header written by Python must come out the same text, or re-storing an unchanged model would change the built game's file"""
    if isinstance(x, float) and x.is_integer(): return int(x)
    if isinstance(x, list): return [_num(v) for v in x]
    if isinstance(x, dict): return {k: _num(v) for k, v in x.items()}
    return x


def _write(path, data):
    """write only if the file is not already exactly this (so git and file times show real changes only)"""
    if os.path.exists(path) and os.path.getsize(path) == len(data) and open(path, 'rb').read() == data: return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data); return True


def _files(name, D):
    """every file the table D should be stored as: {relative path: bytes}"""
    d = DIRS[name]; out = {}
    if name == 'PROP_TEX':
        for k, v in D.items(): b = base64.b64decode(v); out[f'{d}/{k}.{_ext(b)}'] = b
    elif name == 'MAP_SHOTS':
        for k, v in D.items():
            for q, x in v.items():
                if _is_pic(x): b = base64.b64decode(x); out[f'{d}/{k}-{q}.{_ext(b)}'] = b
    else:
        for k, v in D.items():
            out[f'{d}/{k}.bin'] = base64.b64decode(v['d'])
            out[f'{d}/{k}.json'] = json.dumps(_num({q: x for q, x in v.items() if q != 'd'}), separators=(',', ':')).encode()
    return out


def save(name, D):
    files = _files(name, D); d = DIRS[name]; n = 0
    for rel, b in files.items(): n += _write(f'{DATA}/{rel}', b)
    order = [[k, [[q, None] if _is_pic(x) else [q, _num(x)] for q, x in v.items()]] for k, v in D.items()] if name == 'MAP_SHOTS' else list(D)   # (a picture is a file: null here; a plain fact is kept here)
    n += _write(f'{DATA}/{name}.order.json', json.dumps(order, separators=(',', ':')).encode())
    if os.path.isdir(f'{DATA}/{d}'):
        for f in os.listdir(f'{DATA}/{d}'):
            if f'{d}/{f}' not in files: os.remove(f'{DATA}/{d}/{f}'); n += 1
    return n


def load(name):
    d = DIRS[name]; order = json.load(open(f'{DATA}/{name}.order.json')); D = {}
    b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
    pic = lambda stem: next(f'{DATA}/{d}/{stem}.{e}' for e in ('jpg', 'png') if os.path.exists(f'{DATA}/{d}/{stem}.{e}'))
    if name == 'PROP_TEX':
        for k in order: D[k] = b64(pic(k))
    elif name == 'MAP_SHOTS':
        for k, qs in order: D[k] = {q: b64(pic(f'{k}-{q}')) if x is None else x for q, x in qs}
    else:
        for k in order:
            h = json.load(open(f'{DATA}/{d}/{k}.json')); D[k] = dict(h); D[k]['d'] = b64(f'{DATA}/{d}/{k}.bin')
            # keep the header's keys and the data in the order the table had them: h first, d last
    return D


if __name__ == '__main__':
    for n in NAMES:
        D = load(n); print(n, len(D), 'entries')
