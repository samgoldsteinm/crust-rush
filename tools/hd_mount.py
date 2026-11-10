"""The sculpted background mountain for the PC build, from the user's own upload (free-textured-mountain-blender_1.zip,
the same model the web game scatters, decimated there to 3.5k vertices). Writes to assets/hd/:
  mount_h.png    the full model's height field at 1024 x 1024, 16 bits packed in red (high) and green (low): the PC
                 rebuilds each mountain from it with ~20x the web's triangles
  mount_nrm.jpg  its surface direction at 2048 x 2048, in the model's own frame (x along u, z along the web's v, y up)
  mount_col.jpg  its colour, 4096 x 4096 (the web uses the same picture at 2048)
Usage: python3 tools/hd_mount.py <path to free-textured-mountain-blender_1.zip>"""
import io, json, os, struct, sys, zipfile
import numpy as np
from PIL import Image

src = sys.argv[1]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'hd')
z = zipfile.ZipFile(src)
inner = zipfile.ZipFile(io.BytesIO(z.read('source/000_Free_Mountain.zip')))
glb = inner.read('000_Free_Mountain.glb')
L = struct.unpack('<I', glb[12:16])[0]
js = json.loads(glb[20:20 + L])
boff = 20 + L + 8


def acc(i):
    a = js['accessors'][i]
    bv = js['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    dt = {5126: 'f4', 5125: 'u4', 5123: 'u2'}[a['componentType']]
    return np.frombuffer(glb, dtype=dt, count=a['count'] * n, offset=boff + bv.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(-1, n)


P = acc(0).astype(np.float64)
UV = acc(2).astype(np.float64)
top = P[:, 1].max()
N = 2048
# splat every vertex into the grid (the model is a regular grid, ~1023 x 1023), then fill and smooth the gaps
H = np.zeros((N, N))
W = np.zeros((N, N))
ix = np.clip(np.round(UV[:, 0] * (N - 1)).astype(int), 0, N - 1)
iy = np.clip(np.round(UV[:, 1] * (N - 1)).astype(int), 0, N - 1)
np.add.at(H, (iy, ix), P[:, 1])
np.add.at(W, (iy, ix), 1.0)
for it in range(6):
    m = W > 0
    if m.all():
        break
    Hs = H.copy()
    Ws = W.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            Hs += np.roll(np.roll(H, dy, 0), dx, 1)
            Ws += np.roll(np.roll(W, dy, 0), dx, 1)
    H = np.where(m, H, Hs)
    W = np.where(m, W, Ws)
h = H / np.maximum(W, 1e-9)
h = np.clip(h / top, 0, 1)
# the web's copy of the model (and so the PC's) has v the other way up: rows here follow the web's v
h = h[::-1].copy()
# a light smoothing pass evens out the splat
k = np.array([1, 4, 6, 4, 1], float) / 16
hs = h.copy()
for ax in (0, 1):
    hs = sum(np.roll(hs, i - 2, ax) * k[i] for i in range(5))
h = hs
# 1024 x 1024, 16 bits packed into two 8-bit channels
h1 = np.asarray(Image.fromarray(h.astype(np.float32), 'F').resize((1024, 1024), Image.BILINEAR))
q = np.clip(np.round(h1 * 65535), 0, 65535).astype(np.uint32)
rgb = np.zeros((1024, 1024, 3), np.uint8)
rgb[:, :, 0] = q >> 8
rgb[:, :, 1] = q & 255
Image.fromarray(rgb, 'RGB').save(os.path.join(out, 'mount_h.png'))
# surface direction in the model's frame: x = 2000u - 1000, z = 2000v - 1000, y = h * top
sp = 2000.0 / (N - 1)
hy = h * top
gx = (np.roll(hy, -1, 1) - np.roll(hy, 1, 1)) / (2 * sp)
gz = (np.roll(hy, -1, 0) - np.roll(hy, 1, 0)) / (2 * sp)
gx[:, 0] = gx[:, 1]; gx[:, -1] = gx[:, -2]; gz[0, :] = gz[1, :]; gz[-1, :] = gz[-2, :]
n = np.stack([-gx, np.ones_like(gx), -gz], -1)
n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8), 'RGB').save(os.path.join(out, 'mount_nrm.jpg'), quality=94)
col = Image.open(io.BytesIO(inner.read('textures/BaseColor_4K.jpg'))).convert('RGB')
col.save(os.path.join(out, 'mount_col.jpg'), quality=90)
print('mountain: top %.2f, grid %d, heights %.3f..%.3f' % (top, N, h.min(), h.max()))
