"""What each material of a downloaded car model becomes in the game (read by car_convert.py).
A rule is (pattern, target); the pattern is searched, without regard to case, in "<material>@<object>"; the first match wins.
Targets:  paint | glass | tail | light | drop | <a trim class of the game> | int:<class> (the cabin, a small budget of its own)
          | wheel:<class> (a part of a wheel: only what lies inside a tyre is taken; wheel:rubber is the tyre, which is
            only measured and then rebuilt round) | wheel:auto (tyre and rim share one material: what lies beyond
            `rim_ratio` of the radius is the tyre)
          | a function (centres of the triangles in the car's frame, their UV centres) -> one target per triangle.
The car's frame: x across, y along with the FRONT AT -Y, z up, 12.2 long.
Badges, plates, stickers and displays are always dropped: no maker's marks in the game. No texture is used at all.
Per car: src (under scratch/cars_in), front (-1: the model's front is at -Y; 1: at +Y), rules, and optionally
len (length as a multiple of 12.2), rim_ratio, rim (class of a wheel:auto rim), small / small_int (loose pieces under
this size are cleared from the trim / the cabin).
"""
import numpy as np

IN = 'D:/crust-rush/scratch/cars_in'
# one material holds the head lamps and the tail lamps: the front half is 'light', the rear half 'tail'
lights = lambda c, uv: np.where(c[:, 1] < 0, 'light', 'tail')


def by_texture(path, thresh, below, above):
    """split a material by a grey texture (an opacity map: the see-through part is the glass)"""
    cache = {}
    def f(c, uv):
        import bpy
        if 'px' not in cache:
            im = bpy.data.images.load(f'{IN}/{path}'); w, h = im.size; px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px); cache['px'] = px.reshape(h, w, 4)[:, :, 0]
        px = cache['px']; h, w = px.shape; x = np.clip((np.mod(uv[:, 0], 1) * w).astype(int), 0, w - 1); y = np.clip((np.mod(uv[:, 1], 1) * h).astype(int), 0, h - 1)
        return np.where(px[y, x] < thresh, below, above)
    return f


# (2026-11-17) the four new karts built in karts_new.py: every material named for what it becomes
K_RULES = [(r'^K_PAINT', 'paint'), (r'^K_DARK', 'dark'), (r'^K_STRIPE', 'stripe'), (r'^K_CHROME', 'chrome'), (r'^K_METAL', 'steel'),
           (r'^K_GLASS', 'glass'), (r'^K_LIGHT', 'light'), (r'^K_TAIL', 'tail'), (r'^K_SEAT', 'seat'), (r'^K_WOOD', 'wood'),
           (r'^K_RED', 'red'), (r'^K_WHITE', 'white'), (r'^K_TYRE', 'wheel:rubber'), (r'^K_RIM', 'wheel:steel')]
# (2026-11-19) the e-tron's maker's rings: raised parts in the middle of the nose and the tail; dropped from whatever they are part of
# (2026-11-19) the hub centres of a car's own wheels, where makers put their emblems: (wheel y in the car frame list, centre height, track
# half-width, how far out to cut, radius) -> cut boxes
def hubs(ys, z, x0, x1, r=.17):
    return [(sx * x0 if sx > 0 else -x1, sx * x1 if sx > 0 else -x0, y - r, y + r, z - r, z + r, 'wheel:dark') for y in ys for sx in (1, -1)]   # (one flat colour: the emblem's relief disappears)


def no_rings(t):
    return lambda c, uv: np.where(((np.abs(c[:, 0]) < .38) & (c[:, 1] < -5.55) & (c[:, 2] > .84) & (c[:, 2] < 1.19)) | ((np.abs(c[:, 0]) < .3) & (c[:, 1] > 5.0) & (c[:, 1] < 5.22) & (c[:, 2] > 1.69) & (c[:, 2] < 1.92)), 'drop', t)   # (measured: scratch/ringprobe.py)


CARS = {
    'rollpin': dict(src='karts/rollpin.glb', front=-1, rules=K_RULES, tub=False, len=0.62),
    'grater': dict(src='karts/grater.glb', front=-1, rules=K_RULES, tub=False),
    'comet': dict(src='karts/comet.glb', front=-1, rules=K_RULES, tub=False),
    'oilcan': dict(src='karts/oilcan.glb', front=-1, rules=K_RULES, tub=False, len=0.88),
    # a widebody endurance GT racer
    'endur': dict(src='c3/source/mclaren_650s_gt3.glb', front=-1, rules=[
        (r'^INT_(VELLUTO|Cintura|Impugnatura|PROTEZIONI|Details_CINTURE)', 'int:dark'), (r'^INT_Sedile', 'int:seat'),   # (2026-11-18) the interior colour: seats and console only
        (r'^Carpaint', 'paint'), (r'^INT_Glass|^Glass_Wind_noTrasp|^DAMAGE_GLASS|DISPLAY|LEDS', 'drop'), (r'^Glass_Windows', 'glass'),
        (r'^Glass_Clear', lights), (r'^Front_Light', 'light'), (r'^Rear_Light', 'tail'),
        (r'^Rim', 'wheel:rim'), (r'^Tyre', 'wheel:rubber'), (r'^Brake_Disk', 'wheel:disc'), (r'^Brake_Caliper', 'caliper'),
        (r'^Matte_Black|^Plastic|^Carplastic|^Details', 'dark'), (r'^Carbon_Mult|^Grid_', 'carbon'), (r'^Mechanics', 'gunmetal'), (r'^Alluminio', 'metal'), (r'^MIRROR', 'chrome'),
        (r'^INT_(Sedile|VELLUTO|Cintura|Impugnatura|PROTEZIONI)', 'int:seat'), (r'^INT_.*(METAL|ALLUMINIO|Tubi|Tube|Pistoni)', 'int:metal'), (r'^INT_CARPAINT_COLOR', 'int:red'), (r'^INT_', 'int:dark'),
    ]),
    # a track hypercar with a huge top-mounted wing
    'skywing': dict(src='c1/source/inner/Final_Model.fbx', front=-1, rules=[
        (r'^Tela_Int@.*(DOOR|STEERING)', 'int:dark'), (r'^Tela_Int@.*INT_INTERIOR_mm_mat0[24]', 'int:seat'),   # (2026-11-18) the interior colour: seats and console only
        (r'badges|LOD_B|INT_GLASS|Glass_Blask@.*INT_BODY', 'drop'), (r'mm_ext1', 'paint'), (r'MIRROR_GLASS', 'chrome'), (r'BRAKE_CALIPER', 'caliper'),
        (r'^CARBON@LOD_A_WHEEL|^CARBON@jesko:LOD_A_WHEEL|mm_wheel1', 'wheel:carbon'), (r'mm_tyre1', 'wheel:rubber'), (r'mm_rotor1', 'wheel:disc'),
        (r'^Tela_Int', 'int:seat'), (r'_INT_|^Int@|mm_cab1|PLASTICO|INTERIOR', 'int:dark'),
        (r'^CARBON', 'carbon'), (r'mm_chassis1', 'dark'), (r'mm_misc1', 'dark'), (r'mm_windows1', 'glass'), (r'^Glass_Blask', 'glass'), (r'mm_lights1', lights), (r'^phong', 'dark'),
    ]),
    # a four-seat hyper grand tourer
    'megagt': dict(src='c2/source/inner/FINAL_MODEL_G.fbx', front=-1, rim_ratio=.72, rules=[
        (r'SeatBelt', 'int:dark'),   # (2026-11-18) the interior colour: seats and console only
        (r'Badge|ManufacturerPlate|interior_glass', 'drop'), (r'^Light_glass', lambda c, uv: np.where((c[:, 1] > 2.0) & (c[:, 2] > 1.9), 'glass', 'drop')),
        (r'SeatBelt|InteriorColourZone', 'int:seat'), (r'2025Paint', 'paint'), (r'2025Coloured', 'paint'), (r'2025Carbon', 'carbon'), (r'2025Base', 'dark'),
        (r'_Wheel1A', 'wheel:auto'), (r'Calliper|caliper_color', 'caliper'), (r'2025Engine', 'int:gunmetal'), (r'2025Window|^d_glass', 'glass'), (r'^red_glass', 'tail'), (r'2025Light', lights),
        (r'2025Grille', 'dark'), (r'^int_color_1', 'int:seat'), (r'2025Interior|^int_color_2', 'int:dark'),
    ]),
    # a one-megawatt hypercar
    'megawatt': dict(src='c5/source/Koenigsegg_OnePlus.fbx', front=-1, rules=[
        (r'^KOP_Body', 'paint'), (r'^KOP_Base', 'dark'), (r'^KOP_Cockpit', by_texture('c5/textures/KOP_Cockpit_Shd_Opacity.jpg', .8, 'glass', 'int:dark')),
        (r'^KOP_OutCarbon', 'carbon'), (r'^KOP_InCarbon', 'int:dark'), (r'^KOP_Seats', 'int:seat'), (r'^KOP_Tyre', 'wheel:rubber'), (r'^KOP_Rims', 'wheel:rim'), (r'^KOP_DiskBrake', 'wheel:disc'),
        (r'^KOP_Steel', 'metal'), (r'^KOP_Grills', 'dark'), (r'^KOP_Emissive', lambda c, uv: np.where(c[:, 1] < -3, 'light', np.where(c[:, 1] > 3, 'tail', 'drop'))),   # the cabin's lit displays are in this material too
    ]),
    # a concept racer whose driver lies flat
    'slip': dict(src='c4/source/mclaren_ultimate_vision_gt__updated__texture.glb', front=-1, rules=[
        (r'^sm_48@', 'int:seat'),   # (2026-11-18) the interior colour: seats and console only
        (r'^INT_DISPLAY|^win_int|^sm_16_T|^sm_158|^sm_72|^material@|^sm_110|^sm_100|^sm_71', 'drop'),
        (r'^body_1|^body_2|^sm_152_T', 'paint'), (r'^carbon_1', 'carbon'), (r'^black1|^sm_115|^sm_129|^wiper', 'dark'), (r'^glass', 'glass'),
        (r'^EXT_WHEEL', 'wheel:rubber'), (r'^rim_ao', 'wheel:rim'), (r'^color_rims', 'wheel:red'), (r'^white_center_rim', 'wheel:white'), (r'^EXT_BRAKEDISC', 'wheel:disc'),
        (r'^rear_lights|^sm_31_T', 'tail'), (r'^headlights', 'light'), (r'^metall1', 'chrome'), (r'^metal_red', 'red'), (r'^sm_55_T', 'white'),
        (r'^carbon_int|^carbon_steer|^sm_48|^Material_3|^sm_6|^sm_69|^sm_43_T|^plastic_gloss', 'int:dark'),
        (r'^sm_', 'dark'),
    ]),
    # a late-seventies endurance wedge
    'retrogt': dict(src='c6/source/Sketchfab_2026_11_04_10_34_31.glb', front=-1, rules=[
        (r'^INTSTEER_FABRIC|^INT2_FABRIC|SEATBELT', 'int:dark'), (r'centerconsolestructure|^INT_FABRIC', 'int:seat'),   # (2026-11-18) the interior colour: seats and console only
        (r'STICKER|weld|int_gauges|STITCH', 'drop'), (r'^EXT_BODY|^carPaint', 'paint'), (r'^EXT_WINDOWS|^EXT_BLACKGLASS', 'glass'),
        (r'^EXT_tyre', 'wheel:rubber'), (r'^RIM_CHROME', 'wheel:chrome'), (r'^RIM_GUNMETAL|^inner_rim', 'wheel:gunmetal'), (r'^rotor_', 'wheel:disc'), (r'^hub|^steel', 'wheel:metal'),
        (r'^EXT_FLATGLASS|^EXT_HEADLIGHTCHROME|^EXT_LIGHT', 'light'), (r'^TAILGLASS', lambda c, uv: np.where(c[:, 1] > 3, 'tail', 'drop')), (r'^BULB', lights), (r'^MAIN_CIRCLE', 'white'),
        (r'^ENG_ALU|^SUSP_ALU', 'metal'), (r'^ENG_CHROME|^EXH_CHROME|^EXT_CHROME|^MIRRORS', 'chrome'), (r'^ENG_RED', 'red'), (r'^ENG_BLUE', 'bluem'), (r'^ENG_|^SUSP_|^EXT_DARKALLOY', 'gunmetal'),
        (r'^BLACK|^DARK|^EXT_GRILLE|^EXT_PLASTIC|^rubbertrim|^frame', 'dark'),
        (r'badge|gauge_needle|reflector', 'drop'), (r'^EXT_RIVET|^aluminum|^chrome@|^screw', 'metal'), (r'^MISC_RED', 'red'), (r'^zeroblack|^EXT_DETAILS', 'dark'),
        (r'FABRIC|SEATBELT', 'int:seat'), (r'^INT_ALU|^INT_DARKALU|^INT2_ALU|^INTSTEER_ALU', 'int:metal'), (r'^INT|^blkplastic|^metalpainted|^plastic_|^rubber_', 'int:dark'),
    ]),
# (2026-11-19) an organic concept car on glowing wheels
    'biome': dict(src='c7/source/source/Mercedes AVTR.fbx', front=-1, rim_ratio=.72, cut=hubs((-4.49, 3.98), .974, 2.2, 2.95), rules=[
        (r'logo', 'drop'), (r'^avtr_primary', 'paint'), (r'^avtr_glass\.001', 'light'), (r'^avtr_glass', 'glass'),
        (r'^avtr_black@avtr_rim', 'wheel:auto'), (r'^avtr_left_front_light@avtr_rim', 'wheel:bluem'), (r'^avtr_chrome@avtr_rim', 'drop'),   # (hub caps: the maker's emblem)
        (r'^avtr_left_front_light', lights), (r'^avtr_right_rear_light|^avtr_taillight', 'tail'),
        (r'^avtr_koja', 'int:seat'), (r'^avtr_wood', 'int:wood'), (r'^avtr_body\.2|^avtr_dash', 'int:dark'), (r'^avtr_secondary', 'int:dark'),
        (r'^avtr_chassis_ok\.0', 'gunmetal'), (r'^avtr_chassis|^avtr_black', 'dark'),
    ]),
    # (2026-11-19) an electric Gran Turismo concept (an OBJ lying along X; its material names do not describe the parts)
    'surge': dict(src='c8/source/source/inner/Audi E-Tron Vision Gran Turismo.obj', front=1, rot90=1,
                  cut=[(-.38, .38, -6.2, -5.55, .84, 1.19, 'paint'), (-.3, .3, 5.0, 5.22, 1.69, 1.92, 'paint')] + hubs((-3.67, 2.97), .873, 2.3, 2.9),   # (the maker's rings, nose and tail: scratch/ringprobe.py)
                  rules=[
        (r'_HEADLIGHT(_GLASS)?_[BCD](\.\d+)?$', 'drop'), (r'BADGING|^BOTTOM_@', 'drop'),   # (four identical copies of some parts: kit variants; the tyres are all '_D')
        (r'SKIN2', 'paint'), (r'^RUBBER_TIRE', 'wheel:rubber'), (r'HEADLIGHTGLASS_RIM@', 'wheel:rim'),
        (r'@KIT00_FRONT_WINDOW', 'glass'), (r'^INTERIOR', 'int:dark'), (r'SIDELIGHT', lambda c, uv: np.where((np.abs(c[:, 0]) < .38) & (np.abs(c[:, 1]) > 5.0) & (c[:, 2] > .84), 'drop', np.where(c[:, 1] < 0, 'light', 'tail'))),   # (the maker's rings sit in the middle of both lamp bands) (r'^CHROME', no_rings('chrome')),
        (r'HEADLIGHTGLASS_TREAD', no_rings('carbon')), (r'HEADLIGHTGLASS_@BASE', no_rings('dark')), (r'^DULLPLASTIC', no_rings('dark')), (r'HEADLIGHTGLASS_@KIT00_RIGHT_HEADLIGHT_A', no_rings('dark')), (r'^ALUMINUM_MISC', 'drop'), (r'^ALUMINUM', 'paint'),   # (the owner: no grey patches; the door / bonnet plate is a separate square on top of the body: dropped)
    ]),
    # (2026-11-19) a V12 track concept
    'vortex': dict(src='c9/source/lambo_v12_vgt.glb', front=-1, paint_near=1, cut=hubs((-3.26, 3.87), .93, 2.42, 2.95), rules=[
        (r'badge|logo|dials|anniu|yibiao', 'drop'), (r'^Matte__FFFFFFFF__prim', 'paint'), (r'^barbon', 'carbon'),
        (r'^glass1', 'int:dark'), (r'^glass_.*trans', 'glass'), (r'^glass_.*spec_001@', 'tail'),
        (r'^tyre', 'wheel:rubber'), (r'^rotor', 'wheel:disc'), (r'^dz00.*@Object_2[12]$', 'wheel:rim'),
        (r'^jin.*@Object_3[67]$', 'wheel:gunmetal'),   # (centre-lock hubs, not calipers)
        (r'^jin.*@Object_35$', 'drop'),   # (hair-thin red pinlines: simplified into long spikes) (r'^vehiclelights128__spec_FR', 'light'), (r'^vehiclelights128__spec_RR', 'tail'),
        (r'^leather', 'int:seat'), (r'^int_belt|^plastic_blcarp', 'int:dark'), (r'^jin', 'red'), (r'^grey', 'gunmetal'),
        (r'^dz00.*@Object_27$', 'paint'),
        (r'^dz00', lambda c, uv: np.where((np.abs(c[:, 0]) > 1.5) & (np.abs(c[:, 0]) < 2.15) & (c[:, 1] > .55) & (c[:, 1] < 1.65) & (c[:, 2] > .25) & (c[:, 2] < .92), 'drop', 'dark')),   # (the 'GT' lettering on both flanks: scratch/pieceprobe.py)
    ]),
    # (2026-11-19) a red front-engined Vision GT concept
    'scarlet': dict(src='c10/source/ferrari_vgt.glb', front=-1, cut=[(-9, 9, 6.35, 99, -9, 99)] + hubs((-3.37,), .912, 2.5, 3.1) + hubs((3.87,), 1.004, 2.5, 3.1), rules=[
        (r'^logo|^badge|^INT_TEXT|^track@|^material@|^Material_25|^Glass_rim', 'drop'), (r'^Body', 'paint'), (r'^carbon', 'carbon'),
        (r'^EXT_Tyre', 'wheel:rubber'), (r'^Rim_[12]', 'wheel:rim'), (r'^Rim_3', 'wheel:red'), (r'^EXT_Disk', 'wheel:disc'),
        (r'^black_shiny@Object_4[2-6]$', 'caliper'), (r'^d_glass', 'glass'), (r'^glass@', 'drop'),   # ('glass' at 11% opacity: lamp covers and a see-through sheet over the tail)
        (r'^r_glass|^r_lights', lambda c, uv: np.where((c[:, 1] > 4.2) & (c[:, 1] < 6.3), 'tail', 'drop')),   # (the red-glass material also holds cabin bits) (r'^lights', 'light'),
        (r'^INT1|^INT3', 'int:seat'), (r'^INT|^STEER|^Material_26|^Material_0', 'int:dark'), (r'^material_37', 'red'),
        (r'^silver_d|^silver|^chrome', 'metal'), (r'^white', 'white'), (r'^EXT_Chassis', 'dark'), (r'^black', 'dark'),
    ]),
    # (2026-11-19) the owner's armoured night tank (CC BY: "Batmobile-The Dark Knight Tumbler" by Gravity Jack, credited in the game);
    # one material for everything: parts by object name; the jet, fins, fans and front struts sit apart from the body in the file
    'nighttank': dict(src='c11/source/source/Batmobile.fbx', front=-1, rim_ratio=.62, tub=False,
                      move={r'@(jet|struts|Spoiler\d|boostfan|FrontStrut)': (5.886, 0, 0)}, rules=[
        (r'@FrontStrut', 'drop'), (r'@Frontbody|@Hatch', 'paint'), (r'@Window', 'glass'), (r'tire|wheel', 'wheel:auto'),
        (r'@jet', 'gunmetal'), (r'@boostfan', 'metal'), (r'@', 'dark'),
    ]),
}
