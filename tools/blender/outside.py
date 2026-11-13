"""The view out of the bedroom window, rendered as one picture (the game hangs it a little way beyond the glass).
A back garden seen from inside: lawn, a board fence, a tree close by and more beyond the fence, a neighbour's house,
and a sky with the sun where the game's sun is (ahead and a little to the left, 34 degrees up), so the trees are lit
from behind the way the room's sunlight says they should be. Original scene: no real place, no brands.
The picture covers a 3.9 x 2.75 m plane seen from 3.1 m inside the room (what the code-built backdrop covered).
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/outside.py   -> blender/outside/outside.jpg
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
from crlib import *

NAME = 'outside'
# which window the garden is seen from: '' the bedroom's; 'k' the kitchen's, 7 m further west along the same wall. Run with:  ... --python outside.py -- k
VIEW = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv and len(sys.argv) > sys.argv.index('--') + 1 else ''
DX = -7.0 if VIEW == 'k' else 0.0
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
rs = np.random.RandomState(11)
GROUND = -.35
TO_SUN = Vector((-.1, .82, .56)).normalized()          # the game's sun (-.1, .56, -.82) in Blender axes: +Y is out of the window


def nodes(m):
    try: m.use_nodes = True
    except Exception: pass
    return m.node_tree


def leaf_material():
    m = bpy.data.materials.new('leaf'); nt = nodes(m); nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); mix = nt.nodes.new('ShaderNodeMixShader'); d = nt.nodes.new('ShaderNodeBsdfDiffuse'); t = nt.nodes.new('ShaderNodeBsdfTranslucent')
    col = nt.nodes.new('ShaderNodeVertexColor'); col.layer_name = 'Col'
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
    mul.inputs[6].default_value = (*hexcol('#5f9a3c'), 1); nt.links.new(col.outputs['Color'], mul.inputs[7])
    nt.links.new(mul.outputs[2], d.inputs['Color'])
    mul2 = nt.nodes.new('ShaderNodeMix'); mul2.data_type = 'RGBA'; mul2.blend_type = 'MULTIPLY'; mul2.inputs[0].default_value = 1
    mul2.inputs[6].default_value = (*hexcol('#c4e25a'), 1); nt.links.new(col.outputs['Color'], mul2.inputs[7]); nt.links.new(mul2.outputs[2], t.inputs['Color'])
    mix.inputs[0].default_value = .6;   # lit from behind, leaves glow: more of the light passes through than bounces back
    nt.links.new(d.outputs[0], mix.inputs[1]); nt.links.new(t.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m


LEAF = leaf_material(); BARK = mat('bark', hexcol('#5a4636'), .95)


def tree(x, y, height, crown, seed, leaf=.085, n_leaf=9000):
    """a broadleaf tree: a trunk, a handful of boughs, and a crown made of thousands of small leaves in clumps"""
    r = np.random.RandomState(seed); parts = []
    th = height * .42
    bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=height * .028, radius2=height * .014, depth=th, location=(x, y, GROUND + th / 2)); tr = bpy.context.object; tr.data.materials.append(BARK); smooth(tr); parts.append(tr)
    clumps = []
    top = Vector((x, y, GROUND + th))
    for i in range(9):
        a = i / 9 * 6.283 + r.rand(); up = .35 + r.rand() * .55; ln = crown * (.55 + r.rand() * .5)
        d = Vector((math.cos(a) * (1 - up * .6), math.sin(a) * (1 - up * .6), up)).normalized(); end = top + d * ln
        mid = (top + end) / 2
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=height * .012, radius2=height * .004, depth=ln, location=mid); b = bpy.context.object
        b.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); b.data.materials.append(BARK); smooth(b); parts.append(b)
        for k in range(4):
            c = top + d * ln * (.45 + .2 * k) + Vector(r.randn(3)) * crown * .16
            clumps.append((c, crown * (.3 + r.rand() * .22)))
    clumps.append((top + Vector((0, 0, crown * .75)), crown * .5))
    # leaves: small quads scattered through each clump, denser towards its outside, facing every way
    V = []; F = []; C = []
    per = n_leaf // len(clumps)
    for c, rad in clumps:
        p = r.randn(per, 3); p /= np.linalg.norm(p, axis=1, keepdims=True); p *= (rad * (.55 + .45 * r.rand(per, 1) ** .5)); p[:, 2] *= .8
        for q in p:
            ctr = c + Vector(q); n = Vector(r.randn(3)).normalized(); t = n.orthogonal().normalized(); b2 = n.cross(t)
            sz = leaf * (.7 + r.rand() * .6); i0 = len(V)
            V += [ctr - t * sz, ctr - b2 * sz * .42, ctr + t * sz, ctr + b2 * sz * .42]            # a pointed leaf, not a square
            F.append((i0, i0 + 1, i0 + 2, i0 + 3)); sh = .55 + r.rand() * .6; C += [(sh * (.9 + r.rand() * .2), sh, sh * (.8 + r.rand() * .3), 1)] * 4
    me = bpy.data.meshes.new('leaves'); me.from_pydata([tuple(v) for v in V], [], F); me.update()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', np.array(C, dtype=np.float32).ravel())
    o = bpy.data.objects.new('leaves', me); bpy.context.collection.objects.link(o); me.materials.append(LEAF)
    return parts + [o]


# ---- the garden
bpy.ops.mesh.primitive_plane_add(size=160, location=(0, 60, GROUND)); lawn = bpy.context.object
gm = bpy.data.materials.new('grass'); nt = nodes(gm); bs = nt.nodes['Principled BSDF']; nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.6
ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*hexcol('#3f7a2c'), 1); ramp.color_ramp.elements[1].color = (*hexcol('#7fb24a'), 1)
nt.links.new(nz.outputs[0], ramp.inputs[0]); nt.links.new(ramp.outputs[0], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .9
lawn.data.materials.append(gm)
# a board fence across the back of the garden
fw = mat('fencewood', hexcol('#9a7650'), .85); fws = [fw, mat('fencewood2', hexcol('#8a6844'), .9), mat('fencewood3', hexcol('#a9855c'), .85)]
for i in range(-150, 71):    # far enough left for the kitchen's view too
    h = 1.78 + rs.rand() * .05
    box(f'board{i}', (.118, .02, h), (i * .125, 7.0 + rs.rand() * .006, GROUND + h / 2), fws[rs.randint(3)], .003, 1)
for z in (.45, 1.45): box(f'rail{z}', (27.8, .04, .09), (-5.0, 7.035, GROUND + z), fw, 0)
for i in range(-4, 5): box(f'post{i}', (.09, .09, 1.9), (i * 2.2, 7.06, GROUND + .95), fw, .004, 1)
# a neighbour's house beyond it
wallm = mat('siding', hexcol('#e6dcc8'), .8); roofm = mat('roof', hexcol('#5d6470'), .7); glassm = mat('pane', (.03, .05, .08), .08)
HX, HY = -2.5, 23.0
box('house', (10, 7, 3.2), (HX, HY, GROUND + 1.6), wallm, 0)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=7.6, radius2=0, depth=2.6, location=(HX, HY, GROUND + 3.2 + 1.3), rotation=(0, 0, math.radians(45))); rf = bpy.context.object; rf.scale = (1, .72, 1); rf.data.materials.append(roofm)
for wx in (-2.6, 0.2, 2.9):
    box(f'win{wx}', (1.1, .06, 1.25), (HX + wx, HY - 3.52, GROUND + 1.75), glassm, 0)
    box(f'winf{wx}', (1.26, .04, 1.41), (HX + wx, HY - 3.5, GROUND + 1.75), mat('trim', (.9, .9, .88), .5), 0)
# trees: one close to the window on the right, others beyond the fence, a line of them far off
for (x, y, h, cr, sd, lf, n) in ((3.1, 5.2, 6.2, 2.5, 3, .06, 42000), (-4.6, 11.5, 8.5, 3.4, 5, .075, 40000), (6.5, 15, 9.5, 3.8, 7, .085, 36000), (-10.5, 17, 9, 3.6, 9, .09, 28000),
                             (12.5, 26, 11, 4.4, 12, .11, 24000), (3.5, 31, 12, 4.8, 14, .12, 24000), (-15, 33, 12, 5, 17, .13, 20000)):
    tree(x, y, h, cr, sd, lf, n)
# ---- sky and sun
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

# ---- the camera: from inside the room, through the 3.9 x 2.75 m plane 3.1 m ahead whose middle is 1.64 m up
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); s.collection.objects.link(co); s.camera = co
# ONE garden for the whole house: every room's window looks onto this same scene from its own place along the north wall, so the
# rooms agree about what is outside (the shed, the washing line, the fence, the neighbour's house, the trees). The bedroom's window
# is at x = 0, the kitchen's 7 m to the west (x = -7). The Backyard track is to be built as this garden.
if True:
    shm = mat('shed', hexcol('#7a5b3c'), .85); box('shed', (2.4, 1.9, 2.0), (-11.2, 5.4, GROUND + 1.0), shm, .01, 1)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.95, radius2=0, depth=.8, location=(-11.2, 5.4, GROUND + 2.4), rotation=(0, 0, math.radians(45))); rf2 = bpy.context.object; rf2.scale = (1.05, .82, 1); rf2.data.materials.append(roofm)
    box('sheddoor', (.8, .04, 1.7), (-11.2, 4.44, GROUND + .85), mat('sheddoor', hexcol('#5c4630'), .8), .01, 1)
    for px in (-8.2, -3.4): box(f'pole{px}', (.05, .05, 2.0), (px, 4.2, GROUND + 1.0), mat('pole', (.75, .75, .75), .5), 0)
    box('line', (4.8, .01, .01), (-5.8, 4.2, GROUND + 1.95), mat('pole', (.75, .75, .75), .5), 0)
    for k, (px, cc) in enumerate(((-7.2, '#d9534f'), (-6.3, '#f4f1ea'), (-5.3, '#4f86c6'), (-4.4, '#f0c040'))):
        box(f'cloth{k}', (.62, .012, .62 + .1 * (k % 2)), (px, 4.2, GROUND + 1.6 - .05 * (k % 2)), mat(f'cloth{k}', hexcol(cc), .9), 0)
co.location = (DX, -3.1, 1.25 if VIEW == 'k' else 1.0); co.rotation_euler = (Vector((DX + (.5 if VIEW == 'k' else 0), 0, 1.64)) - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.sensor_fit = 'HORIZONTAL'; cam.angle = 2 * math.atan(1.95 / 3.17); cam.clip_end = 500
s.render.resolution_x, s.render.resolution_y = 2048, 1444
s.cycles.samples = 160; s.cycles.use_denoising = True
for vt in ('AgX', 'Filmic', 'Standard'):
    try: s.view_settings.view_transform = vt; break
    except Exception: pass
s.view_settings.exposure = -2.75
try: s.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
s.render.image_settings.file_format = 'JPEG'; s.render.image_settings.quality = 88
s.render.filepath = f'{OUT}/{NAME}/outside{VIEW}.jpg'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/{NAME}/outside{VIEW}.blend')
print('RENDERED', s.render.filepath, s.view_settings.view_transform)
