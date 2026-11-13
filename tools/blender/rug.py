"""The rug for the toy-track rooms: 110 x 150 cm, 1.2 cm thick. A woven mat that does not lie perfectly flat (shallow
dips, one corner curling up), with a knotted fringe along both short ends.
Materials: rug (the pattern: its UVs run 0..1.10 m across and 0..1.50 m along, so the game maps one picture over the
whole mat) and fringe. Nothing rises above 1.2 cm except the curled corner (things stand on this rug).
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/rug.py
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from crlib import *

NAME = 'rug'
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
W, L, T = 1.10, 1.50, .012
rugm = mat('rug', hexcol('#d9cfbf'), 1.0, sheen=.3); fr = mat('fringe', hexcol('#e9e0cf'), 1.0, sheen=.3)

top = grid('rug', W, L, 44, 60, (0, 0, T), rugm)
rs = np.random.RandomState(4); ph = rs.rand(4) * 6.283
CX, CY, R = W / 2, L / 2, .26                                   # the corner that curls
for v in top.data.vertices:
    x, y = v.co.x, v.co.y
    dip = .0016 * (1 + math.sin(x * 9 + ph[0]) * math.cos(y * 7 + ph[1])) + .0008 * (1 + math.sin(x * 23 + y * 17 + ph[2]))
    v.co.z -= dip                                              # shallow dips only: never above the mat's thickness
    d = math.hypot(x - CX, y - CY)
    if d < R:
        k = (1 - d / R) ** 2
        v.co.z += .034 * k; v.co.x -= .012 * k; v.co.y -= .012 * k
solidify(top, T - .001, -1.0); freeze(top)
active(top)
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
except Exception: smooth(top)

# the fringe: short strands lying on the floor past each short end, each a little askew
bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); r = np.random.RandomState(9)
for sy in (-1, 1):
    x = -W / 2 + .004
    while x < W / 2 - .004:
        ln = .055 + r.rand() * .025; dx = (r.rand() - .5) * .022; w = .0034
        y0 = sy * (L / 2 - .004); y1 = sy * (L / 2 + ln)
        vs = [bm.verts.new((x - w, y0, .007)), bm.verts.new((x + w, y0, .007)), bm.verts.new((x + w + dx, y1, .0015)), bm.verts.new((x - w + dx, y1, .0015))]
        f = bm.faces.new(vs if sy > 0 else vs[::-1])
        for lp, uv in zip(f.loops, ((0, 0), (.01, 0), (.01, ln), (0, ln))): lp[uvl].uv = uv
        x += .0085 + r.rand() * .003
me = bpy.data.meshes.new('fringe'); bm.normal_update(); bm.to_mesh(me); bm.free()
fringe = bpy.data.objects.new('fringe', me); bpy.context.collection.objects.link(fringe); me.materials.append(fr); smooth(fringe)

allo = [top, fringe]
# a floor under it while the shade is baked, so the underside and the edges are shaded as on a real floor
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -.0005)); floor = bpy.context.object; floor.data.materials.append(mat('_floor', (.5, .5, .5)))
bake_ao(allo); bpy.data.objects.remove(floor)
for o in allo: soften_ao(o, 1, .3)
print('CHECK', check_render(NAME, allo, views=((35, 28), (-140, 12)), dist=2.6))
export(NAME, allo)
