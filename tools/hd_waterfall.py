"""The waterfall on Hawaiian Bay and Calzone Coast at full detail for the PC build.

The web game draws "WATERFALL MOUNTAIN River" by Nikitos & 3130 (Sketchfab, CC BY 4.0) cut down to about 5% of its
triangles with its pictures shrunk to fit a phone, in its own frame (turned and re-centred from the original's). This
takes the original GLB, turns it into the web's frame exactly (the transform is fitted from the web's own copy by
matching texture coordinates), keeps every triangle, makes the surfaces lit and two-sided, and halves the 4K pictures
to 2K. Writes assets/hd/waterfall/waterfall.glb.

Usage: python3 tools/hd_waterfall.py <original .glb> <web game .html>"""
import base64, io, json, re, struct, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

src, web = sys.argv[1], sys.argv[2]
out = 'assets/hd/waterfall/waterfall.glb'
f = open(src, 'rb').read()
jl = struct.unpack('<I', f[12:16])[0]
j = json.loads(f[20:20 + jl])
B = 20 + jl + 8


def acc(i):
    a = j['accessors'][i]
    bv = j['bufferViews'][a['bufferView']]
    n = {'VEC3': 3, 'VEC2': 2, 'SCALAR': 1}[a['type']]
    dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a['componentType']]
    off = B + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    r = np.frombuffer(f, dtype=dt, count=a['count'] * n, offset=off)
    return r.reshape(-1, n) if n > 1 else r


# the web's copy: PROP_PACKS.waterfall (int16 positions over o/s, uint16 uvs), same decoder as the game's propGeos
# (since November 2026 the web source keeps each model as files: source/data/geo/<id>.json and .bin, beside crust-rush.html)
import os
_geo = os.path.join(os.path.dirname(os.path.abspath(web)), 'data', 'geo')
hdr = json.load(open(os.path.join(_geo, 'waterfall.json')))['h']
blob = open(os.path.join(_geo, 'waterfall.bin'), 'rb').read()
o = 0
webt = []
for m in hdr:
    v = m['v']
    pos = np.frombuffer(blob, dtype=np.int16, count=v * 3, offset=o).reshape(-1, 3)
    o += v * 6 + v * 3 + (v * 3 if m['c'] else 0)
    o += o % 2
    uv = np.frombuffer(blob, dtype=np.uint16, count=v * 2, offset=o).reshape(-1, 2) / 65535.0
    o += v * 4
    while o % 4:
        o += 1
    o += m['i'] * (4 if m['i32'] else 2)
    while o % 4:
        o += 1
    webt.append((pos / 32767.0 * m['s'] + np.array(m['o']), uv))

# fit web = [x y z 1] @ X over every tile, matching vertices by texture coordinate
rows, rhs = [], []
for t, mesh in enumerate(j['meshes']):
    pr = mesh['primitives'][0]
    P = acc(pr['attributes']['POSITION']).astype(np.float64)
    UV = acc(pr['attributes']['TEXCOORD_0']).astype(np.float64)
    wp, wuv = webt[t]
    dist, idx = cKDTree(UV).query(wuv)
    ok = dist < 2e-4
    rows.append(np.hstack([P[idx[ok]], np.ones((ok.sum(), 1))]))
    rhs.append(wp[ok])
A = np.vstack(rows)
X = np.linalg.lstsq(A, np.vstack(rhs), rcond=None)[0]
err = np.abs(A @ X - np.vstack(rhs)).max()
R = X[:3]
print('fit: max error %.5f, det %.4f' % (err, np.linalg.det(R)))
assert err < 0.01

# a new GLB: positions and normals in the web's frame, uvs as they are, pictures at 2K, lit two-sided materials
bin_ = bytearray()
views, accs, meshes, mats, imgs, texs = [], [], [], [], [], []


def view(data, target=None):
    while len(bin_) % 4:
        bin_.append(0)
    v = {'buffer': 0, 'byteOffset': len(bin_), 'byteLength': len(data)}
    if target:
        v['target'] = target
    bin_.extend(data)
    views.append(v)
    return len(views) - 1


def accessor(arr, typ, ct, target, mm=False):
    a = {'bufferView': view(arr.tobytes(), target), 'componentType': ct, 'count': len(arr), 'type': typ}
    if mm:
        a['min'] = arr.min(0).tolist()
        a['max'] = arr.max(0).tolist()
    accs.append(a)
    return len(accs) - 1


for t, mesh in enumerate(j['meshes']):
    pr = mesh['primitives'][0]
    P = acc(pr['attributes']['POSITION']).astype(np.float64)
    N = acc(pr['attributes']['NORMAL']).astype(np.float64)
    UV = acc(pr['attributes']['TEXCOORD_0']).astype(np.float32)
    I = acc(pr['indices']).astype(np.uint32)
    P2 = (np.hstack([P, np.ones((len(P), 1))]) @ X).astype(np.float32)
    N2 = N @ R
    N2 /= np.maximum(1e-9, np.linalg.norm(N2, axis=1, keepdims=True))
    if np.linalg.det(R) < 0:
        I = I.reshape(-1, 3)[:, [0, 2, 1]].reshape(-1)
    att = {'POSITION': accessor(P2, 'VEC3', 5126, 34962, True), 'NORMAL': accessor(N2.astype(np.float32), 'VEC3', 5126, 34962),
           'TEXCOORD_0': accessor(UV, 'VEC2', 5126, 34962)}
    ia = accessor(I, 'SCALAR', 5125, 34963)
    mat = j['materials'][pr['material']]
    ti = mat['pbrMetallicRoughness']['baseColorTexture']['index']
    im = j['images'][j['textures'][ti]['source']]
    bv = j['bufferViews'][im['bufferView']]
    raw = f[B + bv.get('byteOffset', 0):B + bv.get('byteOffset', 0) + bv['byteLength']]
    pic = Image.open(io.BytesIO(raw)).convert('RGB').resize((2048, 2048), Image.LANCZOS)
    jb = io.BytesIO()
    pic.save(jb, 'JPEG', quality=88, optimize=True)
    imgs.append({'bufferView': view(jb.getvalue()), 'mimeType': 'image/jpeg', 'name': 'waterfall_%d' % t})
    texs.append({'source': len(imgs) - 1, 'sampler': 0})
    mats.append({'name': 'waterfall_%d' % t, 'doubleSided': True,
                 'pbrMetallicRoughness': {'baseColorTexture': {'index': len(texs) - 1}, 'metallicFactor': 0.0, 'roughnessFactor': 0.92}})
    meshes.append({'name': 'waterfall_%d' % t, 'primitives': [{'attributes': att, 'indices': ia, 'material': len(mats) - 1}]})
    print('tile', t, len(P), 'points', len(I) // 3, 'triangles')

nodes = [{'name': 'waterfall', 'children': list(range(1, len(meshes) + 1))}] + [{'name': 'waterfall_%d' % t, 'mesh': t} for t in range(len(meshes))]
g = {'asset': {'version': '2.0', 'generator': 'Crust Rush tools/hd_waterfall.py',
               'extras': {'title': 'WATERFALL MOUNTAIN River', 'author': 'Nikitos & 3130 (https://sketchfab.com/vrcityphoto)',
                          'license': 'CC-BY-4.0', 'source': 'https://sketchfab.com/3d-models/waterfall-mountain-river-446f36f2ccb54cf1bc090cd5bc25dce1'}},
     'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': nodes, 'meshes': meshes, 'materials': mats, 'textures': texs, 'images': imgs,
     'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071}],
     'accessors': accs, 'bufferViews': views, 'buffers': [{'byteLength': len(bin_)}]}
js = json.dumps(g, separators=(',', ':')).encode()
js += b' ' * ((4 - len(js) % 4) % 4)
while len(bin_) % 4:
    bin_.append(0)
total = 12 + 8 + len(js) + 8 + len(bin_)
import os
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'wb') as w:
    w.write(struct.pack('<III', 0x46546C67, 2, total))
    w.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
    w.write(struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_))
open(os.path.join(os.path.dirname(out), 'credits.txt'), 'w').write(
    'WATERFALL MOUNTAIN River by Nikitos & 3130 (https://sketchfab.com/vrcityphoto)\n'
    'https://sketchfab.com/3d-models/waterfall-mountain-river-446f36f2ccb54cf1bc090cd5bc25dce1\n'
    'Licensed under Creative Commons Attribution 4.0 (http://creativecommons.org/licenses/by/4.0/).\n'
    'Changed for Crust Rush: turned into the game\'s frame, surfaces made lit and two-sided, pictures halved to 2048.\n')
print('wrote', out, total // 1024, 'KB')
