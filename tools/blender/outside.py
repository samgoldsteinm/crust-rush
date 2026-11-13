"""The whole back garden as ONE Blender scene, built from the same models the Backyard Mega Circuit shows (yardlib.py),
standing where the track's garden has them (toyYard in tools/mini/mini.js; the numbers here and there must agree).
Rendered from it:
  (no argument)  the view out of the bedroom window   -> blender/outside/outside.jpg   (tex_toy_outside)
  -- k           out of the kitchen window, 7 m west   -> outsidek.jpg                  (tex_toy_outsidek)
  -- g           out of the garage window, 7.5 m east  -> outsideg.jpg                  (tex_toy_outsideg)
  -- sky         the sky alone, all round, for the dome over the Backyard track -> sky.jpg (tex_toy_sky, 4096 wide)
  -- top         a check picture of the garden from above the house             -> top.jpg
Each window picture covers a 3.9 x 2.75 m plane seen from 3.1 m inside the room (the game hangs it a little way beyond the
glass). The sun is where the game's sun is (ahead and a little to the left, 34 degrees up), so the trees are lit from
behind the way the rooms' sunlight says. Original scene: no real place, no brands.
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/outside.py [-- k|g|sky|top]
then: py.cmd tools/blender/put_tex.py tex_toy_outside<view> D:/crust-rush/blender/outside/outside<view>.jpg 1792 82
      py.cmd tools/blender/put_tex.py tex_toy_sky D:/crust-rush/blender/outside/sky.jpg 4096 80
Garden coordinates, metres: x east with the bedroom window at 0, y north from the house wall (0) to the back fence (7).
The rooms' floors are 35 cm above the lawn: GROUND.
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
from crlib import *
import yardlib as Y

NAME = 'outside'
VIEW = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv and len(sys.argv) > sys.argv.index('--') + 1 else ''
DX = -7.0 if VIEW == 'k' else 8.0 if VIEW == 'g' else 0.0
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
GROUND = -.35
TO_SUN = Vector((-.1, .82, .56)).normalized()          # the game's sun (-.1, .56, -.82) in Blender axes: +Y is out of the window
if VIEW == 'g': TO_SUN = Vector((.2, -.8, .52)).normalized()   # the garage is lit through its big door, in the south wall: there the sun stands in the south, and the garden out of its north window is lit from the front
TEX = f'{OUT}/tex'
W0, W1 = Y.W0, Y.W1


def nodes(m):
    try: m.use_nodes = True
    except Exception: pass
    return m.node_tree


def stand(parts, x, y, deg=0.0, scale=1.0, sink=0.0):
    """stand a model (as yardlib built it at the origin) in the garden at (x, y), turned and scaled"""
    bpy.context.view_layer.update()
    T = Matrix.Translation((x, y, GROUND - sink)) @ Matrix.Rotation(math.radians(deg), 4, 'Z') @ Matrix.Diagonal((scale if not isinstance(scale, tuple) else scale[0], scale if not isinstance(scale, tuple) else scale[1], scale if not isinstance(scale, tuple) else scale[2], 1))
    for o in parts:
        o.matrix_world = T @ o.matrix_world
        if not o.get('keep_uv') and not o.data.uv_layers: uv_box(o)
    return parts


def picture(m, file, tile=1.0, tint=(1, 1, 1), rough=.9, attr=None):
    """dress a material for the render: a tiling picture from blender/tex laid by the model's own texture coordinates
    (metres), multiplied by a colour, and by the vertices' own tones where a model has them"""
    nt = nodes(m); bs = nt.nodes['Principled BSDF']; im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(f'{TEX}/{file}', check_existing=True)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / tile, 1 / tile, 1)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], im.inputs['Vector'])
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1; mul.inputs[7].default_value = (*tint, 1)
    nt.links.new(im.outputs['Color'], mul.inputs[6]); nt.links.new(mul.outputs[2], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = rough


def leaf_material(m):
    """leaves let the light through: lit from behind, they glow. Each leaf's own green comes from the 'Tint' layer."""
    nt = nodes(m); nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); mix = nt.nodes.new('ShaderNodeMixShader'); d = nt.nodes.new('ShaderNodeBsdfDiffuse'); t = nt.nodes.new('ShaderNodeBsdfTranslucent')
    col = nt.nodes.new('ShaderNodeVertexColor'); col.layer_name = 'Tint'
    for sh, hx in ((d, '#5f9a3c'), (t, '#c4e25a')):
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
        mul.inputs[6].default_value = (*hexcol(hx), 1); nt.links.new(col.outputs['Color'], mul.inputs[7]); nt.links.new(mul.outputs[2], sh.inputs['Color'])
    mix.inputs[0].default_value = .6
    nt.links.new(d.outputs[0], mix.inputs[1]); nt.links.new(t.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])


# ---- sky and sun (the same sky the dome over the Backyard track is rendered from)
w = bpy.data.worlds.new('sky'); s.world = w; wt = nodes(w); bg = wt.nodes['Background']
sky = wt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_disc = False
sky.sun_elevation = math.asin(TO_SUN.z); sky.sun_rotation = math.atan2(TO_SUN.x, TO_SUN.y)
tc = wt.nodes.new('ShaderNodeTexCoord'); cn = wt.nodes.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value = 2.2; cn.inputs['Detail'].default_value = 6
mp = wt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 3.2)
cr = wt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = .6; cr.color_ramp.elements[1].position = .78   # scattered fair-weather clouds, mostly blue sky
mixc = wt.nodes.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.inputs[7].default_value = (4.2, 4.2, 4.3, 1)
wt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); wt.links.new(mp.outputs[0], cn.inputs['Vector']); wt.links.new(cn.outputs[0], cr.inputs[0])
wt.links.new(cr.outputs[0], mixc.inputs[0]); wt.links.new(sky.outputs[0], mixc.inputs[6]); wt.links.new(mixc.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 11; sun.angle = math.radians(1.2); sun.color = (1, .93, .82)
so = bpy.data.objects.new('sun', sun); s.collection.objects.link(so); so.rotation_euler = TO_SUN.to_track_quat('Z', 'Y').to_euler()
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); s.collection.objects.link(co); s.camera = co
for vt in ('AgX', 'Filmic', 'Standard'):
    try: s.view_settings.view_transform = vt; break
    except Exception: pass
s.view_settings.exposure = -2.45
try: s.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
s.render.image_settings.file_format = 'JPEG'; s.render.image_settings.quality = 90

if VIEW == 'sky':
    # all round and overhead, as one long picture: its middle column looks north, its top row straight up
    cam.type = 'PANO'
    try: cam.panorama_type = 'EQUIRECTANGULAR'
    except Exception: cam.cycles.panorama_type = 'EQUIRECTANGULAR'
    co.location = (0, 3.5, GROUND + .3); co.rotation_euler = (math.pi / 2, 0, 0)
    s.render.resolution_x, s.render.resolution_y = 4096, 2048; s.cycles.samples = 24; s.cycles.use_denoising = True
    s.render.filepath = f'{OUT}/{NAME}/sky_full.jpg'; bpy.ops.render.render(write_still=True)
    print('RENDERED', s.render.filepath)
    sys.exit(0)

# ---- the ground: lawn far past the fences, the patio along the house, the bed of earth under the back fence
def ground(name, x0, x1, y0, y1, z, file, tile, tint=(1, 1, 1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, GROUND + z)); o = bpy.context.object; o.name = name; o.scale = (x1 - x0, y1 - y0, 1); apply_scale(o); uv_box(o)
    m = bpy.data.materials.new(name); o.data.materials.append(m); picture(m, file, tile, tint, .95); return o
ground('lawn', -80, 80, -1, 150, 0, 'lawn.jpg', .7, (1.7, 1.7, 1.6));   # (the picture is darkened for the game, where a pale lawn blooms: here it wants its own colour back)
ground('patio', W0, W1, 0, 1.6, .004, 'paving.jpg', 1.5); ground('bed', -7.4, -.6, 6.25, 6.98, .006, 'soil.jpg', .6)

# ---- everything that stands in the garden, as toyYard has it
B = 2.125
for i in range(12): stand(Y.fence(1 + 6 * (i % 2) + 20 * i), W0 + B * (i + .5), 7.0)
for i in range(3):
    stand(Y.fence(101 + i), W0, 7 * (i + .5) / 3, 90, (7 / (3 * B), 1, 1)); stand(Y.fence(201 + i), W1, 7 * (i + .5) / 3, -90, (7 / (3 * B), 1, 1))
stand(Y.shed(), -11.2, 5.4); stand(Y.washing(), -5.8, 4.2); stand(Y.goal(), 9.6, 5.6); stand(Y.football(), 7.4, 3.9, 63)
# the trees are a real one: the photo-scanned jacaranda (Poly Haven, CC0: ph_model.py jacaranda_tree --res 2k), 19.3 m as scanned,
# stood at each tree's height. The Backyard track shows the same tree: the garden's own carries cards of its leaf sprays, the
# ones beyond the fences are pictures of it (treecards.py).
import glob
bpy.ops.import_scene.gltf(filepath=glob.glob('D:/crust-rush/scratch/ph/models/jacaranda_tree/*.gltf')[0])
JAC = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
for m_ in JAC.data.materials:
    if 'leaves' not in m_.name: continue
    nt = m_.node_tree; bs = next(nd for nd in nt.nodes if nd.type == 'BSDF_PRINCIPLED'); out = next(nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL')   # leaves let the light through: lit from behind, they glow
    tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value = .75   # seen against the sun, as every window sees them: most of what reaches the eye has come through the leaf
    src = bs.inputs['Base Color'].links[0].from_socket; gain = nt.nodes.new('ShaderNodeMix'); gain.data_type = 'RGBA'; gain.blend_type = 'MULTIPLY'; gain.inputs[0].default_value = 1; gain.inputs[7].default_value = (3.2, 3.6, 1.6, 1)
    nt.links.new(src, gain.inputs[6]); nt.links.new(gain.outputs[2], tr.inputs['Color'])
    tp = nt.nodes.new('ShaderNodeBsdfTransparent'); cut = nt.nodes.new('ShaderNodeMixShader'); al = bs.inputs['Alpha'].links[0].from_socket
    nt.links.new(bs.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2]); nt.links.new(al, cut.inputs[0]); nt.links.new(tp.outputs[0], cut.inputs[1]); nt.links.new(mix.outputs[0], cut.inputs[2]); nt.links.new(cut.outputs[0], out.inputs['Surface'])
for k, (x, y, h, sd) in enumerate(((3.1, 5.2, 6.2, 1), (-4.6, 11.5, 8.5, 5), (6.5, 15, 9.5, 7), (-10.5, 17, 9.0, 9), (12.5, 26, 11, 12), (3.5, 31, 12, 14), (-15, 33, 12, 17), (16.2, 6.2, 9, 23), (18.5, 12.5, 10.5, 27), (-18.6, 9.5, 9.5, 31), (-21, 15, 11, 35), (20, 19, 11.5, 39))):
    o = JAC.copy(); s.collection.objects.link(o); sc = h / 19.32                                              # the same mesh each time: only the first costs memory
    o.matrix_world = Matrix.Translation((x, y, GROUND - .05)) @ Matrix.Rotation(sd * 1.0, 4, 'Z') @ Matrix.Diagonal((sc, sc, sc, 1))
JAC.hide_render = True
stand(Y.neighbour(), -2.5, 23.0); stand(Y.neighbour(), 21.5, 2.6, -90); stand(Y.neighbour(), -24.5, 4.4, 90)
for (rc, sd, x, y, sink) in ((15, 5, 5.0, .5, 0), (13, 8, -1.2, .3, 0), (17, 3, 1.4, .32, 0), (14, 12, 6.3, .3, 0), (16, 21, -8.6, .34, 0)) + tuple((13 + sd % 5, sd, gx, 6.62, .10) for gx, sd in ((-6.9, 2), (-5.9, 6), (-4.9, 9), (-2.6, 13), (-1.5, 17))):
    stand(Y.pot(sd % 3 + 1, sd), x, y, -math.degrees(sd), rc / 10.8, sink)
stand(Y.pipe(), -3.6, 5.71); stand(Y.gnome(), 2.2, 4.3, -math.degrees(2.6)); stand(Y.wcan(), 4.5, 1.72, -math.degrees(2.4)); stand(Y.hose(), -2.4, .35)
# (the game turns things by an angle about its up axis, which runs the other way from Blender's Z seen from above: hence the minus signs)

# ---- dress the materials for a still picture
M = bpy.data.materials
for k, (file, tint) in {'yfence': ('planks.jpg', hexcol('#f2e6d6')), 'yshed': ('planks.jpg', hexcol('#c2ad98')), 'ysheddoor': ('planks.jpg', hexcol('#9a8876')), 'ybark': ('bark.jpg', (1, 1, 1)),
                        'ybrick': ('brick.jpg', (1, 1, 1)), 'yslate': ('slate.jpg', (1, 1, 1)), 'ysoil': ('soil.jpg', (1, 1, 1)), 'yconc': ('concrete.jpg', (1, 1, 1))}.items():
    if k in M: picture(M[k], file, 1.5 if k == 'yslate' else 1.4 if k == 'ybrick' else 1.1 if k == 'yconc' else 1.0, tint)
if 'yleaf' in M: leaf_material(M['yleaf'])

# ---- the camera
if VIEW == 'top':
    co.location = (-1, -9, 13); co.rotation_euler = (Vector((-1, 5, 0)) - co.location).to_track_quat('-Z', 'Y').to_euler(); cam.lens = 20; cam.clip_end = 500
    s.render.resolution_x, s.render.resolution_y = 2200, 1100; s.cycles.samples = 48; s.cycles.use_denoising = True
else:
    # from inside the room, through the 3.9 x 2.75 m plane 3.1 m ahead whose middle is 1.64 m up
    co.location = (DX, -3.1, 1.25 if VIEW in ('k', 'g') else 1.0); co.rotation_euler = (Vector((DX + (.5 if VIEW == 'k' else -.4 if VIEW == 'g' else 0), 0, 1.64)) - co.location).to_track_quat('-Z', 'Y').to_euler()
    cam.sensor_fit = 'HORIZONTAL'; cam.angle = 2 * math.atan(1.95 / 3.17); cam.clip_end = 500
    s.render.resolution_x, s.render.resolution_y = 2048, 1444; s.cycles.samples = 160; s.cycles.use_denoising = True
s.render.filepath = f'{OUT}/{NAME}/' + ('top.jpg' if VIEW == 'top' else f'outside{VIEW}.jpg')
bpy.ops.render.render(write_still=True)
if VIEW == '': bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/{NAME}/garden.blend')
print('RENDERED', s.render.filepath, s.view_settings.view_transform)
