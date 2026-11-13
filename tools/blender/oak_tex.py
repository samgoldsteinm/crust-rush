"""Oak floorboards as a tiling texture pair (colour and surface relief) for the toy-track rooms.
usage: py.cmd tools/blender/oak_tex.py      -> D:/crust-rush/blender/oak/oak_c.jpg, oak_n.jpg and a preview
One tile is 1.92 m square: 16 boards 12 cm wide running along U, each cut to its own length, with its own tone, its own
growth rings (arched "cathedral" figure where the cut passes near the heart, straight lines where it does not), fine
streaks and open pores along the grain, a small bevel at every edge and a dark gap between boards.
Everything is built from noise shaped in frequency space, which repeats exactly at the tile's edges, so the floor tiles
without a seam. No Blender needed (numpy and Pillow).
"""
import os
import numpy as np
from PIL import Image

OUT = 'D:/crust-rush/blender/oak'
os.makedirs(OUT, exist_ok=True)
S = 1536                      # pixels per tile
ROWS = 16; PH = S // ROWS      # boards across the tile, pixels per board
rs = np.random.RandomState(20261112)


def fnoise(sx, sy, seed):
    """noise that repeats at the tile's edges, smooth over about sx pixels along the grain and sy across it; 0..1"""
    r = np.random.RandomState(seed); w = r.randn(S, S)
    fy = np.fft.fftfreq(S)[:, None]; fx = np.fft.fftfreq(S)[None, :]
    f = np.fft.ifft2(np.fft.fft2(w) * np.exp(-(fx * sx * 2.2) ** 2 - (fy * sy * 2.2) ** 2)).real
    f = (f - f.mean()) / (f.std() + 1e-9)
    return np.clip(.5 + f * .22, 0, 1)


Y, X = np.mgrid[0:S, 0:S]
row = Y // PH; yl = Y % PH
# ---- boards: each row is cut into two or three lengths; every board gets its own numbers
pid = np.zeros((S, S), dtype=np.int32); joint = np.full((S, S), 1e9)
n = 0
for r in range(ROWS):
    c0 = rs.randint(0, S); cuts = np.sort(np.array([c0, c0 + rs.randint(int(S * .38), int(S * .62))]) % S)   # two boards a row, neither under 70 cm
    for i, c in enumerate(cuts):
        c2 = cuts[(i + 1) % len(cuts)]; m = (row == r) & (((X >= c) & (X < c2)) if c2 > c else ((X >= c) | (X < c2)))
        pid[m] = n; n += 1
    for c in cuts:
        d = np.minimum((X - c) % S, (c - X) % S).astype(float); joint = np.where(row == r, np.minimum(joint, d), joint)
P = lambda lo, hi: lo + rs.rand(n) * (hi - lo)
tone = P(.5, .86); warm = P(-.04, .06); sx = rs.randint(0, S, n); sy = rs.randint(0, S, n)
heart = P(-.9, 1.9) * PH        # where the heart of the tree lies across the board (often off the board: straight grain)
lam = P(13, 26); warp = P(14, 40); pick = rs.randint(0, 3, n)
# ---- noise fields, looked up with each board's own offset so no two boards match
low = [fnoise(260, 30, s) for s in (1, 2, 3)]
streak = fnoise(90, .9, 4); fine = fnoise(26, .55, 5); pore = fnoise(7, .5, 6); blot = fnoise(120, 60, 7)
yy = (Y + sy[pid]) % S; xx = (X + sx[pid]) % S
L = np.choose(pick[pid], [f[yy, xx] for f in low])
d = np.abs(yl - heart[pid] + (L - .5) * 2 * warp[pid]) + 1.5
ring = .5 + .5 * np.sin(2 * np.pi * d ** .9 / lam[pid] + L * 5)
late = ring ** 5                                              # the dark, dense part of each growth ring: thin lines
st = streak[yy, xx]; fi = fine[yy, xx]; po = np.clip((pore[yy, xx] - .66) * 6, 0, 1); bl = blot[yy, xx]
t = tone[pid] + (st - .5) * .16 + (fi - .5) * .08 + (bl - .5) * .12 - late * .3 - po * .13
t = np.clip(t, 0, 1)
dark = np.array([128, 86, 50]) / 255; light = np.array([226, 190, 142]) / 255
col = dark + (light - dark) * t[..., None] ** 1.1
col[..., 0] *= 1 + warm[pid]; col[..., 2] *= 1 - warm[pid] * 1.4
# ---- edges: a bevel, then the gap
edge = np.minimum(np.minimum(yl, PH - 1 - yl).astype(float), joint)
bev = np.clip((3.2 - edge) / 3.2, 0, 1)
col *= (1 - .16 * bev ** 2)[..., None]; col *= np.where(edge < 1, .55, 1)[..., None]
Image.fromarray((np.clip(col, 0, 1) * 255 + .5).astype(np.uint8)).save(f'{OUT}/oak_c.jpg', quality=86, optimize=True)
# ---- relief: grain you can feel, pores sunk in, boards slightly cupped, bevelled edges, gaps
cup = ((yl - PH / 2) / (PH / 2)) ** 2
h = .5 + (st - .5) * .4 + (fi - .5) * .18 - po * .4 - late * .22 + cup * .25 - bev ** 1.5 * 1.5 - np.where(edge < 1, 1.0, 0)
gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)); gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0))
K = 2.4
nx, ny, nz = -gx * K, gy * K, np.ones_like(h)                  # the picture's rows run downwards, the texture's v upwards
ln = np.sqrt(nx * nx + ny * ny + nz * nz)
nrm = np.stack([nx / ln, ny / ln, nz / ln], -1) * .5 + .5
Image.fromarray((nrm * 255 + .5).astype(np.uint8)).save(f'{OUT}/oak_n.jpg', quality=88, optimize=True)
# ---- a preview: two tiles each way with a low light across the grain, to check the seams and the relief
c2 = np.tile(np.clip(col, 0, 1), (2, 2, 1)); n2 = np.tile(nrm * 2 - 1, (2, 2, 1))
lt = np.array([-.35, .55, .76]); sh = np.clip((n2 * lt).sum(-1) / lt[2], 0, 1.6)
Image.fromarray((np.clip(c2 * sh[..., None], 0, 1) * 255).astype(np.uint8)).resize((1536, 1536), Image.LANCZOS).save(f'{OUT}/oak_preview.jpg', quality=88)
print('oak', n, 'boards;', os.path.getsize(f'{OUT}/oak_c.jpg') // 1024, 'KB colour,', os.path.getsize(f'{OUT}/oak_n.jpg') // 1024, 'KB relief')
