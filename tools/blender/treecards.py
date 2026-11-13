"""Pictures of a real tree for the game: the photo-scanned jacaranda from Poly Haven (CC0; ph_model.py jacaranda_tree --res 2k).
Run: blender --background --python treecards.py
Out, in D:/crust-rush/blender/treecards/:
  far.png     the whole tree seen from the south (left half) and from the east (right half), clear background: each tree
              beyond the garden's fences is two such cards crossed. Lit as the garden is (the game's sun, behind the tree
              from the garden's side, so the leaves glow), because these cards are shown as they are.
  sprays.png  four sprays of its leaves and twigs (2 x 2), each a slice of the crown's face 2.5 m across and 64 cm deep seen from outside,
              evenly lit: the garden tree's own boughs carry these as cut-out cards, and the game lights them.
then: py.cmd tools/blender/put_tex.py tex_toy_treefar D:/crust-rush/blender/treecards/far.png 1024
      py.cmd tools/blender/put_tex.py tex_toy_sprays D:/crust-rush/blender/treecards/sprays.png 1024
"""
import bpy, sys, os, glob, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from crlib import *

D = f'{OUT}/treecards'; os.makedirs(D, exist_ok=True)
s = reset()
bpy.ops.import_scene.gltf(filepath=glob.glob('D:/crust-rush/scratch/ph/models/jacaranda_tree/*.gltf')[0])
tree = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = tree.data
active(tree); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
n = len(me.vertices); co = np.zeros(n * 3, dtype=np.float32); me.vertices.foreach_get('co', co); co = co.reshape(n, 3)
lo, hi = co.min(0), co.max(0); H = float(hi[2]); cx, cy = float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2)
print('TREE box', lo.round(2), hi.round(2))
# leaves let light through: lit from behind they glow
lm = next(m for m in me.materials if 'leaves' in m.name); nt = lm.node_tree; bs = next(nd for nd in nt.nodes if nd.type == 'BSDF_PRINCIPLED'); out = next(nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL')
tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value = .5
src = bs.inputs['Base Color'].links[0].from_socket; gain = nt.nodes.new('ShaderNodeMix'); gain.data_type = 'RGBA'; gain.blend_type = 'MULTIPLY'; gain.inputs[0].default_value = 1; gain.inputs[7].default_value = (1.5, 1.7, .9, 1)
nt.links.new(src, gain.inputs[6]); nt.links.new(gain.outputs[2], tr.inputs['Color'])
# the leaf picture's holes must cut the glow as well: mix by the same alpha through a transparent shader
tp = nt.nodes.new('ShaderNodeBsdfTransparent'); cut = nt.nodes.new('ShaderNodeMixShader'); al = bs.inputs['Alpha'].links[0].from_socket if bs.inputs['Alpha'].links else None
nt.links.new(bs.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
if al: nt.links.new(al, cut.inputs[0]); nt.links.new(tp.outputs[0], cut.inputs[1]); nt.links.new(mix.outputs[0], cut.inputs[2]); nt.links.new(cut.outputs[0], out.inputs['Surface'])
else: nt.links.new(mix.outputs[0], out.inputs['Surface'])

TO_SUN = Vector((-.1, .82, .56)).normalized()
w = bpy.data.worlds.new('sky'); s.world = w
try: w.use_nodes = True
except Exception: pass
wt = w.node_tree; bg = wt.nodes['Background']
sky = wt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_disc = False; sky.sun_elevation = math.asin(TO_SUN.z); sky.sun_rotation = math.atan2(TO_SUN.x, TO_SUN.y)
wt.links.new(sky.outputs[0], bg.inputs[0])
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 11; sun.angle = math.radians(1.2); sun.color = (1, .93, .82)
so = bpy.data.objects.new('sun', sun); s.collection.objects.link(so); so.rotation_euler = TO_SUN.to_track_quat('Z', 'Y').to_euler()
cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cob = bpy.data.objects.new('cam', cam); s.collection.objects.link(cob); s.camera = cob
s.render.film_transparent = True; s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
for vt in ('AgX', 'Filmic', 'Standard'):
    try: s.view_settings.view_transform = vt; break
    except Exception: pass
s.view_settings.exposure = -1.5
S = float(max(hi[0] - lo[0], hi[1] - lo[1], H)) * 1.02
cam.ortho_scale = S; cam.clip_start = .1; cam.clip_end = 200
s.render.resolution_x = s.render.resolution_y = 512; s.cycles.samples = 96; s.cycles.use_denoising = True
SKIP_FAR = '--sprays' in sys.argv
for name, pos in () if SKIP_FAR else (('far_s', (cx, cy - 60, S / 2)), ('far_e', (cx + 60, cy, S / 2))):                       # the picture's bottom edge is the ground
    cob.location = pos; cob.rotation_euler = (Vector((cx, cy, S / 2)) - cob.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = f'{D}/{name}.png'; bpy.ops.render.render(write_still=True)
print('CARD square side', round(S, 3), 'm; the tree stands', round(H, 2), 'm; its trunk is', round(cx - 0.0, 2), 'm from the middle of the south card and', round(cy, 2), 'of the east card')

# ---- sprays: balls of the crown, each cut out as its own mesh and looked at from outside
loops = np.zeros(len(me.loops), dtype=np.int32); me.loops.foreach_get('vertex_index', loops)
ls = np.zeros(len(me.polygons), dtype=np.int32); me.polygons.foreach_get('loop_start', ls); lt = np.zeros(len(me.polygons), dtype=np.int32); me.polygons.foreach_get('loop_total', lt)
cen = co[loops[ls]]                                                                                         # one corner stands for the face
mi = np.zeros(len(me.polygons), dtype=np.int32); me.polygons.foreach_get('material_index', mi); leafi = list(me.materials).index(lm)
C = np.array([cx, cy, H * .62]); R = 1.25; rs = np.random.RandomState(4); leafc = cen[mi == leafi]; picks = []
for dirn in ((-.5, -.7, .5), (.6, -.6, .5), (0, -.3, .95), (.8, .3, .5)):
    d = np.array(dirn) / np.linalg.norm(dirn); proj = (leafc - C) @ d; side = np.linalg.norm((leafc - C) - np.outer(proj, d), axis=1)
    cand = leafc[(side < 2.5)]; pc = (cand - C) @ d; far_pt = cand[np.argsort(pc)[int(len(pc) * .975)]]    # at the crown's face on that side
    picks.append((far_pt - d * .15, d))
so.hide_render = True                                                                                      # plain white light from all round and no tone curve: the picture is the leaves' own colour, for the game to light
for l in list(bg.inputs[0].links): wt.links.remove(l)
bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 1.0; s.view_settings.view_transform = 'Standard'; s.view_settings.exposure = 0
try: s.view_settings.look = 'None'
except Exception: pass
cam.ortho_scale = 2 * R; SLAB = .32                                                                      # a thin slice: single fronds with sky between them. A thick one is a solid pad of green
for i, (p, d) in enumerate(picks):
    # the whole tree stays; the camera only sees a slab of it 2R deep (its near and far limits), which is the spray
    dv = Vector(d.tolist()); cob.location = Vector(p.tolist()) + dv * 10; cob.rotation_euler = (-dv).to_track_quat('-Z', 'Z').to_euler()
    cam.clip_start = 10 - SLAB; cam.clip_end = 10 + SLAB
    s.render.filepath = f'{D}/spray{i}.png'; bpy.ops.render.render(write_still=True)
print('DONE')
