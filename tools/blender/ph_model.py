"""Download a scanned model from Poly Haven (polyhaven.com: every asset is CC0, free for any use, no attribution needed)
as glTF with its textures, into D:/crust-rush/scratch/ph/models/<id>/ (one folder per model; nothing is run from there).
usage: py.cmd tools/blender/ph_model.py <id> [<id> ...] [--res 1k|2k]
Nothing of the game or its owner is sent: plain downloads of public files. scan.py turns a download into a game model.
"""
import json, os, sys, urllib.request
UA = {'User-Agent': 'asset-fetch/1.0'}
ROOT = 'D:/crust-rush/scratch/ph/models'


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(path, 'wb') as f: f.write(r.read())


def fetch(pid, res='1k'):
    info = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/files/{pid}', headers=UA), timeout=60).read())
    g = info['gltf'][res]['gltf']; d = f'{ROOT}/{pid}'
    name = os.path.basename(g['url']); get(g['url'], f'{d}/{name}'); total = g.get('size', 0)
    for rel, inc in g.get('include', {}).items():
        assert '..' not in rel and not os.path.isabs(rel), rel
        get(inc['url'], f'{d}/{rel}'); total += inc.get('size', 0)
    print(pid, res, f'{total / 1e6:.1f} MB', '->', f'{d}/{name}')


if __name__ == '__main__':
    a = sys.argv[1:]; res = '1k'
    if '--res' in a: i = a.index('--res'); res = a[i + 1]; del a[i:i + 2]
    for pid in a: fetch(pid, res)
