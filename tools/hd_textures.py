"""Textures for the PC build's finished trees, palms and bushes, drawn from scratch (no outside images):
leaf clusters, a palm frond, a pine bough and two barks, each with a matching relief (normal) map.
Writes assets/hd/*.png. Usage: python3 tools/hd_textures.py"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'hd')
os.makedirs(OUT, exist_ok=True)
R = random.Random(20261110)


def normal_from_height(h, strength):
    """height (0..1 float array) -> RGB normal map (OpenGL convention, +Y up)"""
    gx = np.zeros_like(h)
    gy = np.zeros_like(h)
    gx[:, 1:-1] = (h[:, 2:] - h[:, :-2]) * 0.5
    gy[1:-1, :] = (h[2:, :] - h[:-2, :]) * 0.5
    nx = -gx * strength
    ny = gy * strength
    nz = np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / l, ny / l, nz / l], -1)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8), 'RGB')


def save(img, name):
    img.save(os.path.join(OUT, name), optimize=True)
    print('wrote', name, img.size)


def fbm(w, h, scale, octaves, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = 1.0
    tot = 0.0
    for o in range(octaves):
        gw = max(2, int(w / scale * 2 ** o))
        gh = max(2, int(h / scale * 2 ** o))
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255.0 * amp
        tot += amp
        amp *= 0.5
    return out / tot


# ------------------------------------------------------------------ broadleaf cluster (round trees, bushes, shrubs)
def leaf_shape(d, hd, cx, cy, ln, wd, ang, col, shade):
    """one leaf: a pointed ellipse with a midrib, drawn into colour (d) and height (hd)"""
    pts = []
    n = 18
    for i in range(n + 1):
        t = i / n
        r = math.sin(math.pi * t) ** 0.8 * wd
        pts.append((t * ln, r))
    for i in range(n, -1, -1):
        t = i / n
        r = math.sin(math.pi * t) ** 0.8 * wd
        pts.append((t * ln, -r))
    ca, sa = math.cos(ang), math.sin(ang)
    poly = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]
    c = tuple(int(max(0, min(255, v * shade))) for v in col)
    d.polygon(poly, fill=c + (255,))
    hd.polygon(poly, fill=int(150 + 60 * shade))
    # midrib, a little lighter, raised
    d.line([(cx, cy), (cx + ln * 0.92 * ca, cy + ln * 0.92 * sa)], fill=tuple(min(255, int(v * 1.25)) for v in c) + (255,), width=2)
    hd.line([(cx, cy), (cx + ln * 0.92 * ca, cy + ln * 0.92 * sa)], fill=255, width=2)
    # side veins
    for k in range(1, 6):
        t = k / 6.5
        bx, by = cx + t * ln * ca, cy + t * ln * sa
        for sg in (-1, 1):
            va = ang + sg * 0.75
            vl = wd * 0.8 * math.sin(math.pi * t)
            hd.line([(bx, by), (bx + vl * math.cos(va), by + vl * math.sin(va))], fill=210, width=1)


def broadleaf(name, size, n_leaves, ln_range, palette, seed):
    rnd = random.Random(seed)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    hgt = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(img)
    hd = ImageDraw.Draw(hgt)
    c = size / 2
    for i in range(n_leaves):
        # leaves fill a round blob, the outer ones pointing outwards; drawn back to front so inner leaves overlap
        r = c * 0.86 * math.sqrt(rnd.random())
        a = rnd.random() * math.tau
        x = c + math.cos(a) * r
        y = c + math.sin(a) * r * 0.92
        ln = rnd.uniform(*ln_range) * size
        ang = a + rnd.uniform(-0.9, 0.9)
        col = palette[rnd.randrange(len(palette))]
        shade = 0.72 + 0.4 * (1 - r / (c * 0.9)) * rnd.uniform(0.7, 1.0) + rnd.uniform(-0.08, 0.08)
        leaf_shape(d, hd, x - math.cos(ang) * ln * 0.1, y - math.sin(ang) * ln * 0.1, ln, ln * rnd.uniform(0.22, 0.3), ang, col, shade)
    # soften the alpha edge a touch so mipmaps don't fringe
    a = np.asarray(img)[:, :, 3]
    save(img, name + '_col.png')
    h = np.asarray(hgt.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255.0
    save(normal_from_height(h, 6.0), name + '_nrm.png')


GREENS = [(58, 128, 46), (70, 145, 52), (48, 110, 40), (86, 160, 60), (64, 136, 48), (98, 168, 70)]
broadleaf('leaves', 1024, 900, (0.07, 0.12), GREENS, 11)
broadleaf('bushleaf', 1024, 1300, (0.05, 0.085), GREENS, 12)


# ------------------------------------------------------------------ palm frond: a midrib with drooping leaflets
def frond(name, w, h, seed):
    rnd = random.Random(seed)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hgt = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    hd = ImageDraw.Draw(hgt)
    cy = h / 2
    n = 46
    for i in range(n):
        t = (i + 0.5) / n
        x = w * (0.04 + 0.94 * t)
        L = h * 0.48 * (math.sin(math.pi * min(1.0, t * 1.15)) ** 0.6) * (1.0 - 0.25 * t)
        for sg in (-1, 1):
            ang = sg * (0.95 - 0.35 * t) + rnd.uniform(-0.06, 0.06)
            # a leaflet: long and narrow, pointing towards the tip
            ln = L * rnd.uniform(0.92, 1.05)
            wd = h * 0.022
            ex = x + ln * math.sin(abs(ang)) * 0.55
            ey = cy + sg * ln * math.cos(abs(ang) * 0.6) * 0.98
            col = (int(52 + 30 * t + rnd.uniform(-8, 8)), int(122 + 30 * (1 - t) + rnd.uniform(-10, 10)), int(40 + rnd.uniform(-6, 6)))
            pts = [(x - wd, cy), (x + (ex - x) * 0.5 - wd * sg * 0.3, cy + (ey - cy) * 0.5), (ex, ey), (x + (ex - x) * 0.5 + wd * 1.4, cy + (ey - cy) * 0.5), (x + wd, cy)]
            d.polygon(pts, fill=col + (255,))
            hd.polygon(pts, fill=170)
            d.line([(x, cy), (ex, ey)], fill=tuple(min(255, int(v * 1.2)) for v in col) + (255,), width=2)
            hd.line([(x, cy), (ex, ey)], fill=230, width=2)
    # the midrib
    d.line([(0, cy), (w, cy)], fill=(140, 150, 70, 255), width=max(3, h // 40))
    hd.line([(0, cy), (w, cy)], fill=255, width=max(3, h // 40))
    save(img, name + '_col.png')
    h_ = np.asarray(hgt.filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255.0
    save(normal_from_height(h_, 5.0), name + '_nrm.png')


frond('frond', 1024, 512, 21)


# ------------------------------------------------------------------ pine bough: a twig with needles fanning out
def bough(name, w, h, seed):
    rnd = random.Random(seed)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hgt = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    hd = ImageDraw.Draw(hgt)
    cy = h / 2
    segs = []

    def twig(x0, y0, ang, ln, depth):
        x1 = x0 + math.cos(ang) * ln
        y1 = y0 + math.sin(ang) * ln
        segs.append((x0, y0, x1, y1, depth))
        if depth < 2:
            nk = 7 if depth == 0 else 3
            for k in range(nk):
                t = (k + 0.5) / nk * 0.85 + rnd.uniform(-0.04, 0.04)
                bx = x0 + (x1 - x0) * t
                by = y0 + (y1 - y0) * t
                sg = 1 if k % 2 else -1
                twig(bx, by, ang + sg * rnd.uniform(0.45, 0.8), ln * (0.42 if depth == 0 else 0.5) * (1.0 - 0.5 * t), depth + 1)

    twig(w * 0.02, cy, 0.0, w * 0.94, 0)
    # needles first (under the twigs), dark ones then light tips, so the bough reads full and soft
    for pass_ in (0, 1):
        for x0, y0, x1, y1, depth in segs:
            ln = math.hypot(x1 - x0, y1 - y0)
            ang = math.atan2(y1 - y0, x1 - x0)
            steps = int(ln / 2.2)
            for k in range(steps):
                t = k / max(1, steps)
                px = x0 + (x1 - x0) * t
                py = y0 + (y1 - y0) * t
                for sg in (-1, 1):
                    na = ang + sg * rnd.uniform(0.55, 1.05)
                    nl = rnd.uniform(16, 30) * (1.0 - 0.4 * t) * (1.0 if depth == 0 else 0.85)
                    if pass_ == 1:
                        nl *= 0.6
                    g = int(rnd.uniform(62, 100) if pass_ == 0 else rnd.uniform(100, 140))
                    col = (int(g * 0.36), g, int(g * 0.46), 255)
                    d.line([(px, py), (px + math.cos(na) * nl, py + math.sin(na) * nl)], fill=col, width=3 if pass_ == 0 else 2)
                    hd.line([(px, py), (px + math.cos(na) * nl, py + math.sin(na) * nl)], fill=140 + 40 * pass_, width=2)
    for x0, y0, x1, y1, depth in segs:
        d.line([(x0, y0), (x1, y1)], fill=(96, 68, 42, 255), width=max(2, 6 - 2 * depth))
        hd.line([(x0, y0), (x1, y1)], fill=230, width=max(2, 6 - 2 * depth))
    save(img, name + '_col.png')
    h_ = np.asarray(hgt.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255.0
    save(normal_from_height(h_, 4.0), name + '_nrm.png')


bough('bough', 1024, 512, 31)


# ------------------------------------------------------------------ barks (tile left-right and top-bottom)
def bark(name, size, base, ridges, seed):
    n = fbm(size, size, 48, 5, seed)
    v = fbm(size, size, 12, 3, seed + 1)
    x = np.linspace(0, 1, size, endpoint=False)[None, :]
    # vertical ridges, wobbling with the noise
    rid = np.abs(np.sin((x * ridges + v * 1.4) * math.pi))
    hgt = 0.55 * rid ** 0.6 + 0.45 * n
    if name == 'palmbark':
        y = np.linspace(0, 1, size, endpoint=False)[:, None]
        ring = np.abs(np.sin((y * 9 + n * 0.25) * math.pi)) ** 6
        hgt = 0.5 * hgt + 0.5 * (1 - ring)
    hgt = (hgt - hgt.min()) / (hgt.max() - hgt.min())
    col = np.stack([base[0] * (0.55 + 0.6 * hgt), base[1] * (0.55 + 0.6 * hgt), base[2] * (0.55 + 0.6 * hgt)], -1)
    col *= (0.9 + 0.2 * n)[:, :, None]
    save(Image.fromarray(col.clip(0, 255).astype(np.uint8), 'RGB'), name + '_col.png')
    save(normal_from_height(hgt.astype(np.float32), 9.0), name + '_nrm.png')


bark('bark', 512, (120, 86, 56), 9, 41)
bark('palmbark', 512, (150, 112, 74), 6, 42)
