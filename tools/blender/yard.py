"""The Backyard Mega Circuit's models, one GLB each (the models themselves are in yardlib.py, which outside.py also uses).
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/yard.py [-- name ...]
then py.cmd tools/blender/pack_glb.py <name ...>
  yfence, yfenceb   one bay of close-board fence, 2.125 m (two that differ, so a run of them does not repeat)
  yshed             the shed, 2.4 x 1.9 m
  ygoal             the football goal
  ywash             the washing line with four things on it, 4.8 m between its posts
  yhouse            the back of the house: eaves, gutter, downpipes, roof slope, back door, lamp (in garden coordinates)
  yneigh            the neighbour's house, 10 x 7 m
  ypot1..3          flowerpots with plants; ywcan, yhose, ygnome, ypipe, yball, ytuft: the small things
  ytree             the tree by the back fence, 6.2 m (the track spirals round its trunk); ytreef: a 10 m tree for beyond the fences
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crlib import *
import yardlib as Y

ONLY = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []
# name: (builder, camera distance, views (turn, height in degrees), lift of the baked shade, floor under it for the bake)
MODELS = {
    'yfence': (lambda: Y.fence(1), 5.5, ((-25, 12),), .3, True),
    'yfenceb': (lambda: Y.fence(7), 5.5, ((-25, 12),), .3, True),
    'yshed': (Y.shed, 7.5, ((-32, 14), (150, 16)), .3, True),
    'ygoal': (Y.goal, 5.0, ((-30, 14), (160, 20)), .4, True),
    'ywash': (Y.washing, 8.5, ((-20, 8),), .45, True),
    'ytree': (lambda: Y.tree(6.2, 2.5, 3, 5000, .20, .15), 15, ((-25, 8), (60, -12)), .35, True),
    'ytreef': (lambda: Y.tree(10.0, 4.3, 9, 2000, .50, .22), 24, ((-25, 8),), .35, True),
    'yhouse': (Y.house, 16, ((-160, 10), (-200, 4)), .4, True),
    'yneigh': (Y.neighbour, 22, ((-30, 12),), .35, True),
    'ypot1': (lambda: Y.pot(1, 5), 1.5, ((-30, 18),), .4, True),
    'ypot2': (lambda: Y.pot(2, 8), 1.7, ((-30, 18),), .4, True),
    'ypot3': (lambda: Y.pot(3, 3), 1.5, ((-30, 18),), .4, True),
    'ywcan': (Y.wcan, 1.3, ((-30, 18),), .4, True),
    'yhose': (Y.hose, 1.8, ((150, 22),), .4, True),
    'ygnome': (Y.gnome, 1.0, ((-25, 12),), .4, True),
    'ypipe': (Y.pipe, 4.0, ((-35, 14),), .4, True),
    'yball': (Y.football, .8, ((-30, 18),), .5, True),
    'ytuft': (lambda: Y.tuft(2, 18), .5, ((-30, 18),), .6, True),
}
for name, (fn, dist, views, lift, floor) in MODELS.items():
    if ONLY and name not in ONLY: continue
    reset(); parts = fn()
    finish_model(name, parts, dist, lift=lift, views=views, floor=floor, after=lambda ps: [Y.leaf_normals(o) for o in ps])
