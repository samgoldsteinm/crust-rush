"""Download the free (CC0) Poly Haven textures the PC build's finished scenery uses, at 1k or 2k, as JPG colour,
OpenGL normal and roughness maps. Writes OUT/<id>_{col,nrm,rgh}.jpg and OUT/credits.txt.
Usage: OUT=hd python3 tools/hd_fetch.py   (needs internet; runs in GitHub Actions)"""
import json, os, urllib.request

API = 'https://api.polyhaven.com'
UA = {'User-Agent': 'CrustRush-PC-build/1.0 (github.com/samgoldsteinm/crust-rush)'}
OUT = os.environ.get('OUT', 'hd')
# id, resolution
WANT = [('bark_brown_02', '1k'), ('bark_willow', '1k'), ('rock_boulder_dry', '2k'), ('rock_face', '2k'), ('cliff_side', '2k'),
        ('snow_02', '1k'), ('rock_06', '1k'), ('gray_rocks', '1k')]


def get(url, raw=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        b = r.read()
    return b if raw else json.loads(b.decode())


os.makedirs(OUT, exist_ok=True)
cred = ['Textures from Poly Haven (polyhaven.com), CC0 (public domain). Powered by Poly Haven.', '']
for aid, res in WANT:
    f = get('%s/files/%s' % (API, aid))
    print('FILES', aid, sorted(f.keys()))
    pick = {'col': ['Diffuse', 'diffuse', 'diff'], 'nrm': ['nor_gl', 'Normal'], 'rgh': ['Rough', 'rough']}
    for short, keys in pick.items():
        ent = None
        for k in keys:
            if k in f:
                ent = f[k]
                break
        if ent is None:
            print('  missing', short)
            continue
        r = ent.get(res) or ent.get('1k')
        fmt = r.get('jpg') or r.get('png')
        data = get(fmt['url'], True)
        ext = 'jpg' if 'jpg' in r else 'png'
        open(os.path.join(OUT, '%s_%s.%s' % (aid, short, ext)), 'wb').write(data)
        print('  got', short, len(data) // 1024, 'KB')
    info = get('%s/info/%s' % (API, aid))
    cred.append('%s: %s, by %s' % (aid, info.get('name', aid), ', '.join(info.get('authors', {}).keys())))
open(os.path.join(OUT, 'credits.txt'), 'w').write('\n'.join(cred) + '\n')
print('\n'.join(cred))
