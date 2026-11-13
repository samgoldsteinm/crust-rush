"""Turn a photo-scanned model from Poly Haven (CC0; fetched with ph_model.py) into a game model.
Run: blender --background --python scan.py -- <poly haven id> <game name> [key=value ...]
  objs=a,b      keep only objects whose name contains one of these (default: every mesh)
  height=0.33   scale so the kept model is this tall in metres (or scale=0.5)
  tris=3000     thin the mesh down to about this many triangles (the textures carry the detail)
  turn=180      turn about the vertical, degrees (a model's front should be -Y, as crlib says)
  wall=1        keep the model's own back plane where it is (a thing that hangs on a wall); otherwise it is centred
  tex=1024      the size its colour and relief pictures are stored at
  alpha=1       the colour picture has holes (grass, leaves): it is stored with them and the game cuts them out
Out, in D:/crust-rush/blender/<name>/: <name>.glb (one material, called s_<name>), <name>_d.jpg or .png, <name>_n.jpg,
<name>_check0.png (rendered with the scan's own materials: what it should look like in the game).
Then: py.cmd tools/blender/pack_glb.py <name>
      py.cmd tools/blender/put_tex.py tex_toy_s_<name> D:/crust-rush/blender/<name>/<name>_d.jpg 1024 84    (the script prints both lines)
The game: `sMat(name)` in tools/mini/models.js makes the material from those two pictures; the pack's texture coordinates
are the scan's own (tile 100 in pk leaves them alone).
"""
import bpy, sys, os, glob, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix
from crlib import *

a = sys.argv[sys.argv.index('--') + 1:]; PID, NAME = a[0], a[1]; O = dict(x.split('=', 1) for x in a[2:])
reset()
bpy.ops.import_scene.gltf(filepath=glob.glob(f'D:/crust-rush/scratch/ph/models/{PID}/*.gltf')[0])
keep = [k for k in O.get('objs', '').split(',') if k]
objs = [o for o in bpy.data.objects if o.type == 'MESH' and (not keep or any(k in o.name for k in keep))]
for o in list(bpy.data.objects):
    if o not in objs: bpy.data.objects.remove(o)
assert objs, 'nothing kept'
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
if len(objs) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active; o.name = NAME
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
lo, hi = bounds(o)
sc = float(O['scale']) if 'scale' in O else float(O['height']) / (hi.z - lo.z) if 'height' in O else 1.0
cx, cy = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2) if not O.get('wall') else (0.0, 0.0)
o.matrix_world = Matrix.Rotation(math.radians(float(O.get('turn', 0))), 4, 'Z') @ Matrix.Diagonal((sc, sc, sc, 1)) @ Matrix.Translation((-cx, -cy, -lo.z if not O.get('wall') else 0))
active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
n0 = sum(len(p.vertices) - 2 for p in o.data.polygons)
if 'tris' in O and n0 > int(O['tris']):
    d = o.modifiers.new('thin', 'DECIMATE'); d.ratio = int(O['tris']) / n0; d.use_collapse_triangulate = True; freeze(o)
smooth(o)
lo, hi = bounds(o); print('SIZE', NAME, [round(v, 3) for v in lo], [round(v, 3) for v in hi], 'tris', n0, '->', sum(len(p.vertices) - 2 for p in o.data.polygons))
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
print('CHECK', check_render(NAME, [o], views=((-30, 15),), dist=None))
# the pictures: colour (with its holes if it has them) and relief, at the size asked for
S = int(O.get('tex', 1024)); cmds = []
m = o.data.materials[0]
for nd in m.node_tree.nodes:
    if nd.type != 'TEX_IMAGE' or not nd.image: continue
    nm = nd.image.name.lower(); kind = 'd' if 'diff' in nm else 'n' if 'nor' in nm else None
    if not kind: continue
    im = nd.image.copy(); im.scale(S, S); png = kind == 'd' and bool(O.get('alpha'))
    p = f'{OUT}/{NAME}/{NAME}_{kind}.{"png" if png else "jpg"}'
    s = bpy.context.scene; s.render.image_settings.file_format = 'PNG' if png else 'JPEG'; s.render.image_settings.color_mode = 'RGBA' if png else 'RGB'; s.render.image_settings.quality = 92
    s.view_settings.view_transform = 'Standard'; im.save_render(p, scene=s) if kind == 'd' else None
    if kind == 'n': im.filepath_raw = p; im.file_format = 'JPEG'; im.save()                # as stored: a relief picture must not go through the colour pipeline
    cmds.append(f'py.cmd tools/blender/put_tex.py tex_toy_s_{NAME}{"_n" if kind == "n" else ""} {p} {S} {86 if kind == "n" else 84}')
# one material, named for the game; export
for mt in list(o.data.materials)[1:]: pass
m.name = f's_{NAME}'
export(NAME, [o])
print('NEXT  py.cmd tools/blender/pack_glb.py', NAME)
for c in cmds: print('NEXT ', c)
