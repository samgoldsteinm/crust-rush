"""The four concept cars of 2026-11-19 (web v239): their definitions, signature themes and signature colour combos.
    py.cmd tools/cars/patch_cars2.py      (after tools/blender/car_pack.py has put their packs in; running it again replaces what it wrote)
Same scheme as patch_cars.py (read its notes): each piece is one line between /*cars7...*/ and /*:cars7*/ marks; new bodies go after
every existing one (after the cars6 block), because a build holds a body's INDEX. Made-up names, no maker's marks (badges, rings and
lettering were dropped in tools/blender/car_rules.py).
  biome    Biome      an organic electric concept on glowing wheels
  surge    Surge      an electric Gran Turismo racer with a huge wing
  vortex   Vortex     a V12 single-seat track concept
  scarlet  Scarlet    a red front-engined concept racer
Signature themes go into LIVERIES (only:'<id>'); signature combos are appended to COMBOS (KEEP THE ORDER: the PC's style.gd gets the
same lines from tools/mini/pc95.py).
"""
import json, re

SRC = 'D:/crust-rush/source/crust-rush.html'; BL = 'D:/crust-rush/blender/cars'
CARS = [
    dict(id='biome', sf=1.08, name='Biome', eng='jet', st=[0, 2, 0, 0, -2],
         desc='An organic electric concept that seems to grow rather than be built: a glass bubble on four glowing wheels. Silent, instant launch and smooth in the turns; it hates rough ground.',
         roof=2.9, belt=2.4, lean=.25, smax=.28, drv=[1.0, .85, -.8], pipes=[[-6.1, 1.3, .8], [-6.1, 1.3, -.8]], numPos=[.2, 1.4], bubY=2.7, glY=8.3, top=3.1),
    dict(id='surge', sf=1.08, name='Surge', eng='jet', st=[1, 2, 0, -1, -2],
         desc='An electric Gran Turismo racer with a huge rear wing. Fierce off the line and fast; light, and lost off the tarmac.',
         roof=2.5, belt=1.95, lean=.3, smax=.27, drv=[.4, .55, -.8], pipes=[[-6.0, 1.0, .9], [-6.0, 1.0, -.9]], numPos=[.2, 1.1], bubY=2.4, glY=8.1, top=2.85),
    dict(id='vortex', sf=1.08, name='Vortex', eng='race', st=[2, 1, 1, -2, -2],
         desc='A V12 single-seater for the track: the driver sits dead centre under a canopy. Huge speed and grip, feather-light, and useless off the road.',
         roof=2.35, belt=1.7, lean=.4, smax=.26, drv=[1.3, .55, 0], pipes=[[-6.1, 1.2, .5], [-6.1, 1.2, -.5]], numPos=[.2, 1.0], bubY=2.3, glY=7.9, top=2.55),
    dict(id='scarlet', sf=1.08, name='Scarlet', eng='race', st=[2, 0, 2, -2, -2],
         desc='A long red concept racer with its engine up front and a cockpit pushed far back. Fast and beautifully balanced; light, low and never meant for gravel.',
         roof=2.4, belt=1.95, lean=.35, smax=.26, drv=[.8, .45, 0], pipes=[[-6.1, .9, .7], [-6.1, .9, -.7]], numPos=[.2, 1.0], bubY=2.4, glY=7.9, top=2.65),
    # (web v241) the owner's armoured night tank: CC BY 'Batmobile-The Dark Knight Tumbler' by Gravity Jack (credited in Settings > More)
    dict(id='nighttank', sf=1.08, name='Night Tank', eng='jet', st=[0, -1, -1, 1, 1],
         desc='An armoured night tank on huge rear tyres, with a jet in its tail. Heavy, unstoppable and at home off the road; slow to turn.',
         roof=3.6, belt=2.5, lean=.25, smax=.3, drv=[1.6, 1.5, -.75], pipes=[[-6.0, 2.15, 0]], numPos=[.2, 1.8], bubY=3.3, bubS=1.3, glY=9.5, top=4.4),
]
# three signature themes each (pat, A main, B second, C third, m metal, r roughness, dec decal, word, num)
LIV = [
    "{id:'bi_reef',name:'Coral Reef',only:'biome',pat:25,A:'#0e6f78',B:'#3fe0c8',C:'#ff7a5c',m:.55,r:.22,dec:-1,word:-1}",
    "{id:'bi_moss',name:'Living Moss',only:'biome',pat:4,A:'#2e5a2a',B:'#8fd14f',C:'#e9e2c4',m:.2,r:.4,dec:-1,word:-1}",
    "{id:'bi_glow',name:'Bioluminescence',only:'biome',pat:2,A:'#0b1228',B:'#2ae8ff',C:'#a040ff',m:.6,r:.2,dec:7,word:-1}",
    "{id:'su_volt',name:'High Voltage',only:'surge',pat:9,A:'#f2f2f0',B:'#1b1d22',C:'#ff2c2c',m:.3,r:.28,dec:2,word:-1,num:1}",
    "{id:'su_neon',name:'Neon Circuit',only:'surge',pat:16,A:'#14161c',B:'#7dff2a',C:'#2ae8ff',m:.45,r:.24,dec:5,word:-1,num:1}",
    "{id:'su_sunset',name:'Grid Sunset',only:'surge',pat:2,A:'#ff6a1a',B:'#2a1150',C:'#ffd21a',m:.35,r:.26,dec:-1,word:-1,num:1}",
    "{id:'vo_venom',name:'Venom',only:'vortex',pat:16,A:'#86c916',B:'#111214',C:'#f2f2f0',m:.5,r:.22,dec:1,word:-1}",
    "{id:'vo_storm',name:'Thunderhead',only:'vortex',pat:25,A:'#22262e',B:'#ffc400',C:'#c9ccd2',m:.75,r:.2,dec:6,word:-1}",
    "{id:'vo_ice',name:'Polar Strike',only:'vortex',pat:9,A:'#e9eef4',B:'#0b49c9',C:'#111214',m:.4,r:.24,dec:3,word:-1,num:1}",
    "{id:'sc_classic',name:'Rosso Classico',only:'scarlet',pat:2,A:'#b0060f',B:'#f2f2f0',C:'#111214',m:.3,r:.24,dec:-1,word:-1,num:1}",
    "{id:'sc_giallo',name:'Giallo Sun',only:'scarlet',pat:9,A:'#ffc400',B:'#111214',C:'#c40c0c',m:.3,r:.26,dec:2,word:-1,num:1}",
    "{id:'sc_night',name:'Midnight Flame',only:'scarlet',pat:4,A:'#0d0e12',B:'#ff3a12',C:'#ffd23a',m:.55,r:.22,dec:1,word:-1}",
    "{id:'nt_knight',name:'Dark Knight',only:'nighttank',pat:7,A:'#1b1c1f',B:'#2b2d31',C:'#3d4046',m:.15,r:.72,dec:-1,word:-1}",
]
# one signature combo each, then one shared by the two electric cars (paint index, style; $ price)
COMBOS = [
    "{n:'Glowroot',p:14,st:{tr:1,ac:13,in:7,rm:2,cl:13,gl:1,hl:2,sm:2},$:450,only:['biome']}",
    "{n:'Plug In',p:22,st:{tr:1,ac:4,in:1,rm:1,cl:4,gl:0,hl:1,sm:0},$:400,only:['surge']}",
    "{n:'Acid Strike',p:12,st:{tr:1,ac:1,in:12,rm:1,cl:12,gl:4,hl:5,sm:5},$:550,only:['vortex']}",
    "{n:'Grand Prix Red',p:10,st:{tr:1,ac:16,in:11,rm:16,cl:16,gl:0,hl:0,sm:0},$:500,only:['scarlet']}",
    "{n:'Static Charge',p:17,st:{tr:1,ac:13,in:1,rm:14,cl:13,gl:1,hl:2,sm:2},$:450,only:['biome','surge']}",
    "{n:'Dark Knight',p:23,st:{tr:1,ac:14,in:1,rm:14,cl:1,gl:0,hl:2,sm:1},$:500,only:['nighttank']}",
]
f = lambda v: re.sub(r'(?<![0-9])0\.', '.', json.dumps(v, separators=(',', ':')))


def main():
    s = open(SRC, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s[:20000] else '\n'
    ids = [c['id'] for c in CARS]
    s = re.sub(r'/\*cars7[a-z]*\*/[^\n]*?/\*:cars7\*/\r?\n', '', s)
    s = re.sub(r',/\*cars7c\*/.*?/\*:cars7\*/', '', s)
    for c in CARS: assert f"id:'{c['id']}'" not in s and f"{c['id']}(S,M" not in s, c['id'] + ' is already the id of something else'
    # --- BODIES: after the cars6 block (the last bodies)
    a = s.index('/*cars6*/BODIES.push('); e = s.index('\n', a) + 1
    rows = ','.join(f"{{id:'{c['id']}',sf:{c['sf']},name:'{c['name']}',desc:'{c['desc']}',st:{f(c['st'])}}}" for c in CARS)
    s = s[:e] + f'/*cars7*/BODIES.push({rows});/*:cars7*/{nl}' + s[e:]
    # --- BODY_FN: after the cars6 definitions
    a = s.index('/*cars6fn*/'); e = s.index('\n', a) + 1
    fn = []
    for c in CARS:
        w = json.load(open(f"{BL}/{c['id']}/{c['id']}.json"))['info']['wheels']; r = next(q for q in w if not q['f'] and q['c'][2] > 0); fr = next(q for q in w if q['f'] and q['c'][2] > 0)
        fn.append(f"{c['id']}(S,M,rc,idx,B){{carBody('{c['id']}',M,B);return {{car:'{c['id']}',fit:{{roof:{c['roof']},belt:{c['belt']},lean:{c['lean']},smax:{c['smax']}}},belt:{c['belt']},numPos:{f(c['numPos'])},"
                  f"rw:{f([r['c'][0], r['c'][2], r['r']])},fw:{f([fr['c'][0], fr['c'][2], fr['r']])},wz:1.3,drv:{f(c['drv'])},drvS:{c['smax']},noCockpit:1,pipes:{f(c['pipes'])},bubY:{c['bubY']},bubS:{c.get('bubS',1.1)},glY:{c['glY']},top:{c['top']}}};}}")
    s = s[:e] + '/*cars7fn*/Object.assign(BODY_FN,{' + ','.join(fn) + f'}});/*:cars7*/{nl}' + s[e:]
    # --- the Cars tab and the engine sounds
    a = s.index("const CAR_BODIES=["); e = s.index(']', a); cur = [x for x in json.loads(s[a + 17:e + 1].replace("'", '"')) if x not in ids]
    s = s[:a + 17] + json.dumps(cur + ids, separators=(',', ':')).replace('"', "'") + s[e + 1:]
    a = s.index("ENG_BODY={"); e = s.index('}', a); cur = ','.join(p for p in s[a + 10:e].split(',') if p.split(':')[0] not in ids)
    s = s[:a + 10] + cur + ''.join(f",{c['id']}:'{c['eng']}'" for c in CARS) + s[e:]
    # --- signature themes: after the Onyx's wrap
    a = s.index("  {id:'onyxwrap',"); e = s.index('\n', a) + 1
    s = s[:e] + '/*cars7liv*/  ' + ','.join(LIV) + f',/*:cars7*/{nl}' + s[e:]
    # --- signature combos: appended to COMBOS (the end of its list)
    a = s.index("const COMBOS=["); e = s.index("}];", a) + 1
    s = s[:e] + ',/*cars7c*/' + ','.join(COMBOS) + '/*:cars7*/' + s[e:]
    open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('four cars defined')


if __name__ == '__main__':
    main()
