"""One-off (web v173): the six new car bodies' definitions. Run once, after tools/blender/car_pack.py has put their packs in.
    py.cmd tools/cars/patch_cars.py
To change a car's numbers afterwards, edit CARS here and run it again: it replaces what it wrote before (each piece it
writes is one line between /*cars6...*/ and /*:cars6*/).
A body's id must not be the id of anything else in the game: 'retro' is a livery and 'wedge' is a kart, and a first
version of this script that cleared its old lines by id deleted that livery (caught by reading the diff).
Every number is in the car's own space (x forward, y up, z to the right; about 12.2 long):
  roof/belt  the cabin's ceiling and the bottom of its side glass (the driver is scaled and seated to show between them)
  drv        the seat: x, the cabin floor's height, z      lean  how far the driver leans back
  pipes      where the boost flames come out               top / bubY / glY  body top, shield bubble, glider height
rw and fw (wheel x, half track, radius) are read from the pack, so they always match the model.
"""
import json, re

SRC = 'D:/crust-rush/source/crust-rush.html'; BL = 'D:/crust-rush/blender/cars'
CARS = [
    dict(id='skywing', sf=1.08, name='Skywing', eng='race', st=[2, 0, 1, -1, -2],
         desc='A track-bred hypercar under a huge top-mounted wing. Enormous downforce and top speed; stiff, low and useless off the road.',
         roof=3.0, belt=2.2, lean=.35, smax=.27, drv=[.6, .6, -.75], pipes=[[-6.15, 1.55, 0]], numPos=[.2, 1.1], bubY=2.5, glY=8.2, top=3.3),
    dict(id='megagt', sf=1.1, name='Mega GT', eng='race', st=[1, 1, -1, 1, -2],
         desc='A four-seat hyper grand tourer. Three motors and an engine launch its bulk hard and it runs fast and steady; long and heavy in tight turns.',
         roof=3.1, belt=2.1, lean=.25, smax=.28, drv=[.9, .7, -.75], pipes=[[-6.1, 1.0, .9], [-6.1, 1.0, -.9]], numPos=[.2, 1.2], bubY=2.6, glY=8.2, top=3.25),
    dict(id='megawatt', sf=1.08, name='Megawatt', eng='race', st=[2, 2, -1, -1, -2],
         desc='One megawatt for barely more than a ton: a hypercar with as much power as it has weight. Ferocious launch and top speed; light, nervous and stuck to the tarmac.',
         roof=2.75, belt=1.9, lean=.4, smax=.27, drv=[.5, .5, -.75], pipes=[[-6.15, 1.0, 0]], numPos=[.2, 1.0], bubY=2.4, glY=8.0, top=3.05),
    dict(id='endur', sf=1.08, name='Endurance GT', eng='race', st=[1, 0, 2, -1, -2],
         desc='A widebody GT racer built for twenty-four-hour races. Slick tyres and a big wing make it superb in the turns; not the fastest in a straight line, and lost off the tarmac.',
         roof=2.85, belt=2.1, lean=.3, smax=.28, drv=[.4, .6, -.8], pipes=[[-6.1, .9, .7], [-6.1, .9, -.7]], numPos=[.2, 1.2], bubY=2.5, glY=8.6, top=3.1),
    dict(id='slip', sf=1.08, name='Slipstream', eng='race', st=[2, 1, 0, -1, -2],
         desc='A concept racer from the future whose driver lies flat under a glass canopy. Slippery, fast and quick to launch; feather-light, and it cannot leave the road.',
         roof=2.4, belt=1.6, lean=.5, smax=.26, drv=[1.6, .6, 0], pipes=[[-6.2, 1.3, 0]], numPos=[.2, 1.0], bubY=2.3, glY=7.8, top=2.9),
    dict(id='retrogt', sf=1.08, name='Retro Racer', eng='race', st=[1, -1, 1, 0, -1],
         desc='A wedge-shaped endurance racer from the late seventies. A big flat twelve and a long tail: fast and steady, honest in the turns, slow to wind up.',
         roof=2.65, belt=1.9, lean=.3, smax=.27, drv=[.2, .55, -.7], pipes=[[-5.95, .55, .5], [-5.95, .55, -.5]], numPos=[.2, 1.0], bubY=2.3, glY=7.7, top=2.85),
]
f = lambda v: re.sub(r'(?<![0-9])0\.', '.', json.dumps(v, separators=(',', ':')))


def main():
    s = open(SRC, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s[:20000] else '\n'
    ids = [c['id'] for c in CARS]
    # what an earlier run wrote is taken out first: each piece sits on one line of its own between a pair of marks
    s = re.sub(r'/\*cars6[a-z]*\*/[^\n]*?/\*:cars6\*/\r?\n', '', s)
    for c in CARS: assert f"id:'{c['id']}'" not in s and f"\n  {c['id']}(S,M" not in s, c['id'] + ' is already the id of something else'
    # --- BODIES: a build saved on a phone or sent over the network holds a body's INDEX, so new bodies go after every
    #     existing one: after the block that pushes the last four karts, never into the middle
    a = s.index("BODIES.push("); a = s.index("{id:'tomato'", a); e = s.index('\n', a) + 1
    assert s[a:e].rstrip().endswith('});'), 'the last BODIES.push is not where it was'
    rows = ','.join(f"{{id:'{c['id']}',sf:{c['sf']},name:'{c['name']}',desc:'{c['desc']}',st:{f(c['st'])}}}" for c in CARS)
    s = s[:e] + f'/*cars6*/BODIES.push({rows});/*:cars6*/{nl}' + s[e:]
    # --- BODY_FN: a statement of its own after the cars' block
    a = s.index("  gt(S,M,rc,idx,B){carBody('gt',M,B);"); e = s.index('\n', a) + 1
    assert s[a:e].rstrip().endswith('}});'), 'the end of the BODY_FN block is not where it was'
    fn = []
    for c in CARS:
        w = json.load(open(f"{BL}/{c['id']}/{c['id']}.json"))['info']['wheels']; r = next(q for q in w if not q['f'] and q['c'][2] > 0); fr = next(q for q in w if q['f'] and q['c'][2] > 0)
        fn.append(f"{c['id']}(S,M,rc,idx,B){{carBody('{c['id']}',M,B);return {{car:'{c['id']}',fit:{{roof:{c['roof']},belt:{c['belt']},lean:{c['lean']},smax:{c['smax']}}},belt:{c['belt']},numPos:{f(c['numPos'])},"
                  f"rw:{f([r['c'][0], r['c'][2], r['r']])},fw:{f([fr['c'][0], fr['c'][2], fr['r']])},wz:1.3,drv:{f(c['drv'])},drvS:{c['smax']},noCockpit:1,pipes:{f(c['pipes'])},bubY:{c['bubY']},bubS:1.1,glY:{c['glY']},top:{c['top']}}};}}")
    s = s[:e] + '/*cars6fn*/Object.assign(BODY_FN,{' + ','.join(fn) + f'}});/*:cars6*/{nl}' + s[e:]
    # --- the garage's Cars tab, the engine sounds (both rebuilt without these ids, then with them)
    a = s.index("const CAR_BODIES=["); e = s.index(']', a); cur = [x for x in json.loads(s[a + 17:e + 1].replace("'", '"')) if x not in ids]
    s = s[:a + 17] + json.dumps(cur + ids, separators=(',', ':')).replace('"', "'") + s[e + 1:]
    a = s.index("ENG_BODY={"); e = s.index('}', a); cur = s[a + 10:e]
    cur = ','.join(p for p in cur.split(',') if p.split(':')[0] not in ids)
    s = s[:a + 10] + cur + ''.join(f",{c['id']}:'{c['eng']}'" for c in CARS) + s[e:]
    open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('six cars defined')


if __name__ == '__main__':
    main()
