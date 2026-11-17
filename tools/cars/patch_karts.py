"""(web v217) Four new karts built in Blender (tools/blender/karts_new.py -> car_convert.py -> car_pack.py), as bodies of the game.
    py.cmd tools/cars/patch_karts.py      (run again after changing KARTS: it replaces what it wrote, between /*karts4...*/ marks)
They are packed like the cars (carBody) but are KARTS: not in CAR_BODIES (so the garage shows them on the Karts tab), an open seat
with the driver in full view like the bikes (drvS, no cabin fit). New bodies go after EVERY existing one (a saved or networked build
holds a body's index). Seat, flames, number, bubble and glider are given in the MODEL's metres (karts_new.py) and turned into the
game's units here from each pack's measured wheels (s: game units a metre, yc: the model's y that is the game's x = 0).
"""
import json, re

SRC = 'D:/crust-rush/source/crust-rush.html'; BL = 'D:/crust-rush/blender/cars'
KARTS = [
    dict(id='rollpin', name='Rolling Pin', st=[1, 0, 1, -1, -1], wr=(0.31, 0.74), wf=(0.25, -0.78),
         desc='A retro open-wheel racer turned from one long rolling pin, a pizza peel for a wing. Quick and nimble; light, and it hates the rough.',
         seat=(0.2, 0.73), pipes=[(0, 1.72, 0.46)], top=1.12, num=(-0.55, 0.5), drvS=.5, lean=.2),
    dict(id='grater', name='Grater', st=[-1, -1, 0, 1, 1], wr=(0.36, 0.68), wf=(0.34, -0.72),
         desc='A chunky utility kart hauling a giant cheese grater. Heavy, tough and at home off the road; slow to wind up.',
         seat=(-0.16, 0.74), pipes=[(0.38, 1.18, 0.42), (-0.38, 1.18, 0.42)], top=1.72, num=(0.3, 0.42), drvS=.5, lean=.15),
    dict(id='comet', name='Calzone Comet', st=[1, 1, 0, -1, -1], wr=(0.23, 0.8), wf=(0.2, -0.78),
         desc='A folded-dough streamliner under a bubble canopy, its edge crimped shut. Slippery and quick off the line; light and twitchy.',
         seat=(0.1, 0.52), pipes=[(0.2, 1.38, 0.38), (-0.2, 1.38, 0.38)], top=1.1, num=(-0.6, 0.38), drvS=.34, lean=.3),
    dict(id='oilcan', name='Oil Can', st=[2, 1, -2, 0, -1], wr=(0.44, 0.55), wf=(0.15, -1.45),
         desc='A drag racer built round a can of olive oil, spout first. Blistering in a straight line, clumsy in the turns.',
         seat=(0.56, 0.55), pipes=[(0.55, 0.05, 1.08), (-0.55, 0.05, 1.08)], top=1.38, num=(-0.15, 0.7), drvS=.5, lean=.25),
]
f = lambda v: re.sub(r'(?<![0-9])0\.', '.', json.dumps([round(x, 3) if isinstance(x, float) else x for x in v] if isinstance(v, list) else v, separators=(',', ':')))


def frame(k):
    """s (game units a metre) and yc (model y at the game's x = 0), from the pack's wheels"""
    w = json.load(open(f"{BL}/{k['id']}/{k['id']}.json"))['info']['wheels']
    fr = next(q for q in w if q['f'] and q['c'][2] > 0); r = next(q for q in w if not q['f'] and q['c'][2] > 0)
    s = (fr['r'] / k['wf'][0] + r['r'] / k['wr'][0]) / 2
    yc = k['wf'][1] + fr['c'][0] / s
    return s, yc, fr, r


def main():
    s = open(SRC, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s[:20000] else '\n'
    ids = [k['id'] for k in KARTS]
    s = re.sub(r'/\*karts4[a-z]*\*/[^\n]*?/\*:karts4\*/\r?\n', '', s)
    for k in KARTS:
        assert f"id:'{k['id']}'" not in s and f"{k['id']}(S,M" not in s, k['id'] + ' is already the id of something else'
    # BODIES: after the last push of all (the six cars'): a build holds a body's index
    a = s.index('/*cars6*/BODIES.push('); e = s.index('\n', a) + 1
    assert s.count('BODIES.push(', e) == 0, 'a BODIES.push after the cars: put these after it'
    rows = ','.join(f"{{id:'{k['id']}',name:'{k['name']}',desc:'{k['desc']}',st:{f(k['st'])}}}" for k in KARTS)
    s = s[:e] + f'/*karts4*/BODIES.push({rows});/*:karts4*/{nl}' + s[e:]
    # BODY_FN: after the cars' block
    a = s.index('/*cars6fn*/'); e = s.index('\n', a) + 1
    fn = []
    for k in KARTS:
        sc, yc, fr, r = frame(k)
        X = lambda y: -(y - yc) * sc
        drv = [X(k['seat'][0]), k['seat'][1] * sc, 0]
        pipes = [[X(p[1]), p[2] * sc, p[0] * sc] for p in k['pipes']]
        top = k['top'] * sc
        print('%-8s %.2f units a metre, x=0 at model y %.3f: seat %s, top %.2f' % (k['id'], sc, yc, [round(v, 2) for v in drv], top))
        fn.append(f"{k['id']}(S,M,rc,idx,B){{carBody('{k['id']}',M,B);return {{car:'{k['id']}',belt:{round(k['seat'][1] * sc + .6, 2)},numPos:{f([X(k['num'][0]), k['num'][1] * sc])},"
                  f"rw:{f([r['c'][0], r['c'][2], r['r']])},fw:{f([fr['c'][0], fr['c'][2], fr['r']])},wz:1.3,drv:{f(drv)},drvS:{k['drvS']},lean:{k['lean']},noCockpit:1,"
                  f"pipes:{f(pipes)},bubY:{round(top * .62, 2)},bubS:1.15,glY:{round(top + 4.5, 2)},top:{round(top, 2)}}};}}")
    s = s[:e] + '/*karts4fn*/Object.assign(BODY_FN,{' + ','.join(fn) + f'}});/*:karts4*/{nl}' + s[e:]
    open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('four karts defined')


if __name__ == '__main__':
    main()
