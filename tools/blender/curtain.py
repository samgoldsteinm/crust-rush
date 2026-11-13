"""A pair of curtain panels for the toy-track rooms: 58 cm wide when drawn back, 159 cm long, hung as cloth.
Each panel is a 1.25 m wide sheet gathered into seven pleats along its pinned top edge and left to hang, so the folds
open out and wander towards the hem the way real curtains do. The two panels (materials curtainL and curtainR) hang
differently; the room uses one on each side of the window.
The origin is the TOP MIDDLE of a panel (it hangs down from there); +Y is the wall behind it, 7 cm away.
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/curtain.py
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from crlib import *

NAME = 'curtain'
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
W, H, FLAT, PLEATS, AMP = .58, 1.59, 1.25, 7, .036


def panel(tag, x0, seed):
    m = mat('curtain' + tag, hexcol('#c9bfae'), .9, sheen=.4)
    o = grid('panel' + tag, FLAT, H, 64, 70, (0, 0, 0), m)      # UVs: the flat sheet, in metres
    rs = np.random.RandomState(seed); ph, a1, a2, a3 = rs.rand(4) * 6.283
    pin = o.vertex_groups.new(name='pin')
    for v in o.data.vertices:
        u, t = v.co.x, v.co.y                                    # across the flat sheet, and from the hem (-H/2) to the top (+H/2)
        f = u / FLAT + .5                                        # 0..1 across the sheet
        # pleats of uneven width and depth, as a hand-drawn curtain has; towards the hem they loosen, drift and flare
        k = 2 * math.pi * PLEATS * (f + .035 * math.sin(f * 9 + a1) + .02 * math.sin(f * 21 + a2)) + ph
        down = (H / 2 - t) / H                                   # 0 at the top, 1 at the hem
        amp = AMP * (.75 + .35 * math.sin(f * 7 + a3)) * (1 - .25 * down)
        drift = down * down * (.03 * math.sin(f * 5 + a2) + .018 * math.sin(f * 13 + a1))
        v.co = (x0 + u * W / FLAT * (1 + .16 * down) + drift, amp * math.sin(k + down * 1.1 * math.sin(f * 6 + a3)) + .012 * down * math.sin(f * 17 + a1), t - H / 2)
        if t > H / 2 - 1e-4: pin.add([v.index], 1.0, 'REPLACE')
    cm = cloth(o, mass=.25, tension=18, bending=.12, self_col=True, dist=.004, quality=10, damp=6)
    cm.settings.vertex_group_mass = 'pin'
    return o


L = panel('L', -1.0, 3); R = panel('R', 1.0, 8)
wall = box('wall', (4.0, .02, H + .4), (0, .075, -H / 2), mat('_wall', (.8, .8, .8)), 0); collider(wall, .004)
simulate(120)
for o, x0 in ((L, -1.0), (R, 1.0)):
    freeze(o); relax(o, .4, 1); smooth(o)
    for v in o.data.vertices: v.co.x -= x0
bpy.data.objects.remove(wall)
bake_ao([L, R])
for o in (L, R): soften_ao(o, 3, .45)   # tight pleats: the raw shade is far too dark and streaky
# check picture: the two panels side by side
for o, dx in ((L, -.4), (R, .4)): o.location = (dx, 0, H + .02)   # lifted for the picture: the studio floor is at z=0
bpy.context.view_layer.update()
print('CHECK', check_render(NAME, [L, R], views=((20, 8), (155, 10)), dist=4.2))
for o in (L, R): o.location = (0, 0, 0)
bpy.context.view_layer.update()
export(NAME, [L, R])
