"""List what a downloaded Poly Haven model holds: objects, sizes, triangle counts, materials and their pictures.
Run: blender --background --python scan_inspect.py -- <id> [<id> ...]      (after ph_model.py <id>)"""
import bpy, sys, glob
from mathutils import Vector
for pid in sys.argv[sys.argv.index('--') + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    f = glob.glob(f'D:/crust-rush/scratch/ph/models/{pid}/*.gltf')[0]; bpy.ops.import_scene.gltf(filepath=f)
    print('==', pid)
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        vs = [o.matrix_world @ Vector(c) for c in o.bound_box]; lo = [min(v[i] for v in vs) for i in range(3)]; hi = [max(v[i] for v in vs) for i in range(3)]
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        print('  obj', o.name, 'tris', tris, 'box', [round(x, 2) for x in lo], [round(x, 2) for x in hi], 'mats', [m.name for m in o.data.materials])
    for m in bpy.data.materials:
        if not m.node_tree: continue
        print('  mat', m.name, 'blend', getattr(m, 'blend_method', ''), [(n.image.name, tuple(n.image.size)) for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image])
