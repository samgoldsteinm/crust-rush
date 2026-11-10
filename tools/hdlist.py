"""List the free (CC0) Poly Haven models and textures that could replace the PC build's scenery: trees, plants,
rocks and ground surfaces. Prints one line per asset (id, categories, tags, size) so the right ones can be picked.
Usage: python3 tools/hdlist.py   (needs internet; run in GitHub Actions)"""
import json, urllib.request

API = 'https://api.polyhaven.com'
UA = {'User-Agent': 'CrustRush-PC-build/1.0 (github.com/samgoldsteinm/crust-rush)'}


def get(path):
    with urllib.request.urlopen(urllib.request.Request(API + path, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode())


print('CATS models', json.dumps(get('/categories/models')))
print('CATS textures', json.dumps(get('/categories/textures')))
for t in ['models', 'textures']:
    a = get('/assets?type=' + t)
    keep = 0
    for k, v in sorted(a.items()):
        cats = v.get('categories', [])
        tags = v.get('tags', [])
        words = set(c.lower() for c in cats) | set(x.lower() for x in tags)
        want = {'nature', 'plants', 'trees', 'tree', 'rocks', 'rock', 'ground', 'sand', 'grass', 'bark', 'terrain', 'snow', 'ice', 'shrub', 'bush', 'palm', 'leaves', 'flowers', 'moss', 'gravel', 'dirt', 'soil', 'cliff', 'stone', 'wood', 'plaster', 'brick', 'fabric', 'roofing', 'asphalt', 'concrete'}
        if not (words & want):
            continue
        keep += 1
        extra = ''
        if t == 'models':
            extra = ' poly=%s dims=%s' % (v.get('polycount', '?'), v.get('dimensions', '?'))
        print('ASSET %s %s | cats=%s | tags=%s%s' % (t, k, ','.join(cats), ','.join(tags[:12]), extra))
    print('KEPT', t, keep, 'of', len(a))
