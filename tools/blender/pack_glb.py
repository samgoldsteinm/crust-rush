"""Pack a Blender-built room model (GLB) into the game's prop format and put it into crust-rush.html.
usage: py.cmd tools/blender/pack_glb.py <name> [<name> ...]     reads D:/crust-rush/blender/<name>/<name>.glb

The pack is called toy_<name>_hq. The "_hq" ending makes the build ship it as a file that downloads after the menu
is up, so nobody waits for room models at start-up; until it arrives the room uses its code-built model.
One mesh per material: its name is "<name>|<material>", and the material name is the key the room code maps to a
game material. Positions are scaled from metres to game units (347 per metre). UVs are stored 0..1 with their offset
and span in metres in the header (uo, us), because the pack format keeps UVs as 16-bit fractions. Vertex colours hold
the baked soft shading.
"""
import json, struct, sys, base64
import numpy as np

SRC = 'D:/crust-rush/source/crust-rush.html'
BL = 'D:/crust-rush/blender'
UNITS = 347.0
CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def load_glb(path):
    b = open(path, 'rb').read()
    magic, ver, length = struct.unpack_from('<4sII', b, 0)
    assert magic == b'glTF', path
    off = 12; js = None; bn = b''
    while off < length:
        clen, ctype = struct.unpack_from('<I4s', b, off)
        data = b[off + 8:off + 8 + clen]; off += 8 + clen
        if ctype == b'JSON': js = json.loads(data)
        else: bn = data
    return js, bn


def accessor(js, bn, i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]
    dt = np.dtype(CT[a['componentType']]); n = NC[a['type']]; cnt = a['count']
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); stride = bv.get('byteStride') or dt.itemsize * n
    if stride == dt.itemsize * n:
        arr = np.frombuffer(bn, dt, cnt * n, off).reshape(cnt, n)
    else:
        raw = np.frombuffer(bn, np.uint8, cnt * stride, off).reshape(cnt, stride)[:, :dt.itemsize * n]
        arr = np.frombuffer(raw.tobytes(), dt).reshape(cnt, n)
    arr = arr.astype(np.float64 if dt.kind == 'f' else arr.dtype)
    if a.get('normalized') and dt.kind != 'f':
        arr = arr.astype(np.float64) / np.iinfo(dt).max
    return arr


def node_matrix(nd):
    if 'matrix' in nd: return np.array(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    t = nd.get('translation', [0, 0, 0]); q = nd.get('rotation', [0, 0, 0, 1]); s = nd.get('scale', [1, 1, 1])
    x, y, z, w = q
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t
    return M


def gather(js, bn):
    """-> {material name: dict(pos, nrm, uv, col, idx)} with every node's transform applied"""
    out = {}

    def walk(ni, parent):
        nd = js['nodes'][ni]; M = parent @ node_matrix(nd)
        if 'mesh' in nd:
            N = np.linalg.inv(M[:3, :3]).T
            for pr in js['meshes'][nd['mesh']]['primitives']:
                at = pr['attributes']; mname = js['materials'][pr['material']]['name'] if 'material' in pr else 'none'
                pos = accessor(js, bn, at['POSITION'])[:, :3] @ M[:3, :3].T + M[:3, 3]
                nrm = accessor(js, bn, at['NORMAL'])[:, :3] @ N.T
                nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
                uv = accessor(js, bn, at['TEXCOORD_0'])[:, :2].astype(np.float64) if 'TEXCOORD_0' in at else np.zeros((len(pos), 2))
                col = accessor(js, bn, at['COLOR_0'])[:, :3].astype(np.float64) if 'COLOR_0' in at else np.ones((len(pos), 3))
                idx = accessor(js, bn, pr['indices']).ravel().astype(np.int64) if 'indices' in pr else np.arange(len(pos))
                g = out.setdefault(mname, dict(pos=[], nrm=[], uv=[], col=[], idx=[], n=0))
                g['pos'].append(pos); g['nrm'].append(nrm); g['uv'].append(uv); g['col'].append(col); g['idx'].append(idx + g['n']); g['n'] += len(pos)
        for c in nd.get('children', []): walk(c, M)

    for ni in js['scenes'][js.get('scene', 0)]['nodes']: walk(ni, np.eye(4))
    return {k: {a: np.concatenate(v[a]) for a in ('pos', 'nrm', 'uv', 'col', 'idx')} for k, v in out.items()}


def weld(g):
    """merge vertices that are the same in every attribute (the exporter splits them freely)"""
    key = np.concatenate([np.round(g['pos'] * 2e4), np.round(g['nrm'] * 60), np.round(g['uv'] * 2e4), np.round(g['col'] * 64)], axis=1)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return {a: g[a][first] for a in ('pos', 'nrm', 'uv', 'col')} | {'idx': inv.ravel()[g['idx']]}


def pack(name):
    js, bn = load_glb(f'{BL}/{name}/{name}.glb')
    heads = []; blob = bytearray()
    for mname, g in sorted(gather(js, bn).items()):
        g = weld(g)
        pos = g['pos'] * UNITS; v = len(pos)
        lo, hi = pos.min(0), pos.max(0); o = (lo + hi) / 2; s = float(max((hi - lo).max() / 2, 1e-6))
        uv = g['uv'].copy(); uv[:, 1] = 1 - uv[:, 1]                    # glTF's v runs downwards; the game's runs up
        u0 = uv.min(0); us = float(max((uv.max(0) - u0).max(), 1e-6))
        col = np.clip(.3 + .7 * g['col'], 0, 1)                         # baked shade, kept gentle
        blob += np.round((pos - o) / s * 32767).astype('<i2').tobytes()
        blob += np.round(np.clip(g['nrm'], -1, 1) * 127).astype(np.int8).tobytes()
        blob += np.round(col * 255).astype(np.uint8).tobytes()
        if len(blob) % 2: blob += b'\0'
        blob += np.round((uv - u0) / us * 65535).astype('<u2').tobytes()
        while len(blob) % 4: blob += b'\0'
        i32 = v > 65535
        blob += g['idx'].astype('<u4' if i32 else '<u2').tobytes()
        while len(blob) % 4: blob += b'\0'
        heads.append({'n': f'{name}|{mname}', 'v': v, 'i': int(len(g['idx'])), 'c': 1, 'uv': 1, 'i32': 1 if i32 else 0,
                      'o': [round(float(x), 4) for x in o], 's': round(s, 5), 'uo': [round(float(x), 5) for x in u0], 'us': round(us, 5)})
        print(f'  {name}|{mname}: {v} verts, {len(g["idx"]) // 3} tris')
    return {'h': heads, 'd': base64.b64encode(bytes(blob)).decode()}, len(blob)


def main(names):
    s = open(SRC, encoding='utf-8', newline='').read()
    a = s.index('const PROP_PACKS=') + len('const PROP_PACKS='); e = s.index('\n', a)
    lit = s[a:e].rstrip(); assert lit.endswith(';'); lit = lit[:-1]
    D = json.loads(lit)
    assert json.dumps(D, separators=(',', ':')) == lit, 'the PROP_PACKS line would not survive a rewrite unchanged'
    for n in names:
        D[f'toy_{n}_hq'], size = pack(n)
        print(f'toy_{n}_hq: {size / 1024:.0f} KB')
    s = s[:a] + json.dumps(D, separators=(',', ':')) + ';' + s[e:]
    open(SRC, 'w', encoding='utf-8', newline='').write(s)


if __name__ == '__main__':
    main(sys.argv[1:])
