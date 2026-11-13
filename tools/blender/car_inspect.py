"""List what a downloaded car model is made of, before converting it for the game (tools/blender/car_convert.py).
usage: blender --background --python car_inspect.py -- <model.glb|.fbx> [more ...]
Prints the model's size, and every material with how much surface it covers, its colour and where it sits (which tells
paint from glass from tyres). The model files are other people's data: this only reads them.
"""
import sys, bpy, math
from mathutils import Vector

for path in sys.argv[sys.argv.index('--') + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.lower().endswith('.fbx'): bpy.ops.import_scene.fbx(filepath=path)
    else: bpy.ops.import_scene.gltf(filepath=path)
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3); mats = {}
    for o in obs:
        mw = o.matrix_world; me = o.data
        for p in me.polygons:
            c = mw @ p.center; lo = Vector(map(min, lo, c)); hi = Vector(map(max, hi, c))
            m = me.materials[p.material_index] if me.materials and p.material_index < len(me.materials) else None
            d = mats.setdefault(m.name if m else '(none)', dict(a=0.0, n=0, lo=Vector((1e9,) * 3), hi=Vector((-1e9,) * 3), m=m, objs=set()))
            sc = mw.to_scale(); d['a'] += p.area * abs(sc.x * sc.y * sc.z) ** (2 / 3); d['n'] += 1; d['lo'] = Vector(map(min, d['lo'], c)); d['hi'] = Vector(map(max, d['hi'], c)); d['objs'].add(o.name)
    size = hi - lo
    print('CAR', path.split('/')[-1], '| objects', len(obs), '| tris', sum(len(p.vertices) - 2 for o in obs for p in o.data.polygons), '| size x %.2f y %.2f z %.2f' % tuple(size), '| low', tuple(round(v, 2) for v in lo))
    for nm, d in sorted(mats.items(), key=lambda kv: -kv[1]['a']):
        m = d['m']; col = ''; al = ''
        if m and m.node_tree:
            b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if b:
                c = b.inputs['Base Color'].default_value; tex = bool(b.inputs['Base Color'].links)
                col = 'rgb %.2f %.2f %.2f%s metal %.1f rough %.1f' % (c[0], c[1], c[2], ' +tex' if tex else '', b.inputs['Metallic'].default_value, b.inputs['Roughness'].default_value)
                al = ' alpha %.2f' % b.inputs['Alpha'].default_value if b.inputs['Alpha'].default_value < .99 or b.inputs['Alpha'].links else ''
                tr = b.inputs.get('Transmission Weight'); al += ' transm' if tr and tr.default_value > .3 else ''
        rel_lo = tuple(round((d['lo'][i] - lo[i]) / max(size[i], 1e-6), 2) for i in range(3)); rel_hi = tuple(round((d['hi'][i] - lo[i]) / max(size[i], 1e-6), 2) for i in range(3))
        tot = sum(x['a'] for x in mats.values()) or 1
        print('  MAT %-52s %5.1f%% faces %6d box %s..%s %s%s objs %d %s' % (nm[:52], 100 * d['a'] / tot, d['n'], rel_lo, rel_hi, col, al, len(d['objs']), sorted(d['objs'])[0][:28]))
