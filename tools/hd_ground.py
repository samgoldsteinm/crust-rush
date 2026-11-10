"""The PC build's finished ground, made from each track's own ground picture (cheese on most tracks, frost on the
frozen ones): a relief map where the light flecks stand up, browned blisters swell and dark specks sink in, with a
slow melted ripple, and a gloss map (fresh light cheese shinier, browned spots dull). Writes next to the picture:
<name>_hdn.png (normal, OpenGL) and <name>_hdr.png (roughness in green), and <track>_hd.json listing them by material.
Usage: python3 tools/hd_ground.py maps   (every track folder under it)"""
import json, os, sys
import numpy as np
from PIL import Image


def tile_blur(a, r):
    """a soft (gaussian, sigma r/2) blur that wraps around, so the picture still tiles"""
    h, w = a.shape
    sg = r / 2.0
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    k = np.exp(-2.0 * (np.pi * sg) ** 2 * (fx * fx + fy * fy))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * k)).astype(np.float32)


def ripple(h, w, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = 1.0
    for o in range(3):
        n = 4 * 2 ** o
        g = rng.random((n, n)).astype(np.float32)
        g = np.pad(g, 1, mode='wrap')
        im = Image.fromarray(g, 'F').resize((w + w // n * 2, h + h // n * 2), Image.BICUBIC)
        a = np.asarray(im, np.float32)
        out += a[h // n:h // n + h, w // n:w // n + w] * amp
        amp *= 0.5
    return (out - out.mean()) / (out.std() + 1e-6)


def one(path):
    img = np.asarray(Image.open(path).convert('RGB'), np.float32) / 255.0
    h, w, _ = img.shape
    lum = img[:, :, 0] * 0.3 + img[:, :, 1] * 0.55 + img[:, :, 2] * 0.15
    base = tile_blur(lum, max(8, w // 24))
    d = np.clip((lum - base) * 3.2, -1, 1)
    hgt = tile_blur(d, 2) * 0.55 + ripple(h, w, 7) * 0.12
    # normal from height, wrapping at the edges
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) * 0.5
    gy = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) * 0.5
    s = 9.0
    nx, ny, nz = -gx * s, gy * s, np.ones_like(hgt)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / l, ny / l, nz / l], -1)
    stem = os.path.splitext(path)[0]
    Image.fromarray(((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8), 'RGB').save(stem + '_hdn.png')
    r = np.clip(0.6 - (lum - lum.mean()) * 1.5 + np.abs(tile_blur(d, 3)) * 0.1, 0.3, 0.85)
    rg = np.zeros((h, w, 3), np.uint8)
    rg[:, :, 0] = 255
    rg[:, :, 1] = (r * 255).astype(np.uint8)
    Image.fromarray(rg, 'RGB').save(stem + '_hdr.png')
    print('ground', path, w, h)
    return os.path.basename(stem)


root = sys.argv[1] if len(sys.argv) > 1 else 'maps'
for d in sorted(os.listdir(root)):
    g = os.path.join(root, d, d + '.gltf')
    if not os.path.exists(g):
        continue
    j = json.load(open(g))
    idx = {}
    for m in j.get('materials', []):
        if not str(m.get('name', '')).startswith('terrain'):
            continue
        t = m.get('pbrMetallicRoughness', {}).get('baseColorTexture')
        if not t:
            continue
        uri = j['images'][j['textures'][t['index']]['source']]['uri']
        st = one(os.path.join(root, d, uri))
        sub = os.path.dirname(uri)
        idx[m['name']] = {'n': os.path.join(sub, st + '_hdn.png'), 'r': os.path.join(sub, st + '_hdr.png')}
    if idx:
        json.dump(idx, open(os.path.join(root, d, d + '_hd.json'), 'w'))
