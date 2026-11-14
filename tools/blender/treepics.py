"""Pictures of real trees and shrubs for the pizza tracks (web v194; the owner: "update all the maps with the new trees ... some of
the older maps still have the old blocky trees and shrubs"). Each is a photo-scanned model from Poly Haven (CC0; download with
ph_model.py <id> --res 1k), drawn twice from the side: from the south (the left half of the picture) and from the east (the right half),
on a clear background, the ground at the picture's bottom edge and the trunk in the middle of each half. The game stands such a picture
up as crossed cards (forest() in the engine: three cards near the track, two further out) and lights it itself, so the light here is
plain: white from all round with a little from above for the crown's shape, no tone curve.
Run: blender --background --python treepics.py -- <poly haven id> <name> [width of each half in px, default 512]
Out: D:/crust-rush/blender/treepics/<name>.png and a line `TREEPIC <name> <height m> <card side m>` (the card is square: its side is the
     larger of the tree's height and spread).
then: py.cmd tools/blender/put_tex.py tex_tree_<name> D:/crust-rush/blender/treepics/<name>.png 1024
"""
import bpy, sys, os, glob, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from crlib import *

args = sys.argv[sys.argv.index('--') + 1:]
PID, NAME = args[0], args[1]; nums = [q for q in args[2:] if q.isdigit()]; PX = int(nums[0]) if nums else 512
D = f'{OUT}/treepics'; os.makedirs(D, exist_ok=True)
s = reset()
if '--cpu' in args: s.cycles.device = 'CPU'      # (the fir and the pine are too big for this PC's graphics memory)
bpy.ops.import_scene.gltf(filepath=glob.glob(f'D:/crust-rush/scratch/ph/models/{PID}/*.gltf')[0])
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
lo = np.array([1e9] * 3); hi = -lo
for o in meshes:
    active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    n = len(o.data.vertices); co = np.zeros(n * 3, dtype=np.float32); o.data.vertices.foreach_get('co', co); co = co.reshape(n, 3)
    lo = np.minimum(lo, co.min(0)); hi = np.maximum(hi, co.max(0))
H = float(hi[2] - lo[2])
# the trunk: where the model meets the ground (the lowest tenth of it), which is where the card is centred
low = []
for o in meshes:
    n = len(o.data.vertices); co = np.zeros(n * 3, dtype=np.float32); o.data.vertices.foreach_get('co', co); co = co.reshape(n, 3)
    low.append(co[co[:, 2] < lo[2] + (hi[2] - lo[2]) * .08])
low = np.concatenate(low); tx, ty = (float(low[:, 0].mean()), float(low[:, 1].mean())) if len(low) else (float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2))
spread = 2 * float(max(hi[0] - tx, tx - lo[0], hi[1] - ty, ty - lo[1]))
S = max(H, spread) * 1.03
print('TREE box', lo.round(2), hi.round(2), 'trunk', round(tx, 2), round(ty, 2))
w = bpy.data.worlds.new('sky'); s.world = w
try: w.use_nodes = True
except Exception: pass
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = .85
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 2.2; sun.angle = math.radians(25)
so = bpy.data.objects.new('sun', sun); s.collection.objects.link(so); so.rotation_euler = Vector((-.25, -.35, .9)).normalized().to_track_quat('Z', 'Y').to_euler()
cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cob = bpy.data.objects.new('cam', cam); s.collection.objects.link(cob); s.camera = cob
s.render.film_transparent = True; s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
s.view_settings.view_transform = 'Standard'; s.view_settings.exposure = 0.9          # the scans' leaf colours are dark: the game's light multiplies them again
try: s.view_settings.look = 'None'
except Exception: pass
cam.ortho_scale = S; cam.clip_start = .1; cam.clip_end = 400
s.render.resolution_x = s.render.resolution_y = PX; s.cycles.samples = 64; s.cycles.use_denoising = True
zc = float(lo[2]) + S / 2                      # the picture's bottom edge is the model's foot
for view, pos in (('s', (tx, ty - 120, zc)), ('e', (tx + 120, ty, zc))):
    cob.location = pos; cob.rotation_euler = (Vector((tx, ty, zc)) - cob.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = f'{D}/{NAME}_{view}.png'; bpy.ops.render.render(write_still=True)
# the two halves side by side
a = bpy.data.images.load(f'{D}/{NAME}_s.png'); b = bpy.data.images.load(f'{D}/{NAME}_e.png')
pa = np.array(a.pixels[:], dtype=np.float32).reshape(PX, PX, 4); pb = np.array(b.pixels[:], dtype=np.float32).reshape(PX, PX, 4)
out = bpy.data.images.new('sheet', PX * 2, PX, alpha=True); out.pixels = np.concatenate([pa, pb], axis=1).ravel(); out.filepath_raw = f'{D}/{NAME}.png'; out.file_format = 'PNG'; out.save()
print('TREEPIC', NAME, round(H, 2), round(S, 2), 'filled', round(float((pa[..., 3] > .5).mean()), 3))
