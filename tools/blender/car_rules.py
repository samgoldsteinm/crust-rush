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


CARS = {
    # a widebody endurance GT racer
    'endur': dict(src='c3/source/mclaren_650s_gt3.glb', front=-1, rules=[
        (r'^Carpaint', 'paint'), (r'^INT_Glass|^Glass_Wind_noTrasp|^DAMAGE_GLASS|DISPLAY|LEDS', 'drop'), (r'^Glass_Windows', 'glass'),
        (r'^Glass_Clear', lights), (r'^Front_Light', 'light'), (r'^Rear_Light', 'tail'),
        (r'^Rim', 'wheel:rim'), (r'^Tyre', 'wheel:rubber'), (r'^Brake_Disk', 'wheel:disc'), (r'^Brake_Caliper', 'caliper'),
        (r'^Matte_Black|^Plastic|^Carplastic|^Details', 'dark'), (r'^Carbon_Mult|^Grid_', 'carbon'), (r'^Mechanics', 'gunmetal'), (r'^Alluminio', 'metal'), (r'^MIRROR', 'chrome'),
        (r'^INT_(Sedile|VELLUTO|Cintura|Impugnatura|PROTEZIONI)', 'int:seat'), (r'^INT_.*(METAL|ALLUMINIO|Tubi|Tube|Pistoni)', 'int:metal'), (r'^INT_CARPAINT_COLOR', 'int:red'), (r'^INT_', 'int:dark'),
    ]),
    # a track hypercar with a huge top-mounted wing
    'skywing': dict(src='c1/source/inner/Final_Model.fbx', front=-1, rules=[
        (r'badges|LOD_B|INT_GLASS|Glass_Blask@.*INT_BODY', 'drop'), (r'mm_ext1', 'paint'), (r'MIRROR_GLASS', 'chrome'), (r'BRAKE_CALIPER', 'caliper'),
        (r'^CARBON@LOD_A_WHEEL|^CARBON@jesko:LOD_A_WHEEL|mm_wheel1', 'wheel:carbon'), (r'mm_tyre1', 'wheel:rubber'), (r'mm_rotor1', 'wheel:disc'),
        (r'^Tela_Int', 'int:seat'), (r'_INT_|^Int@|mm_cab1|PLASTICO|INTERIOR', 'int:dark'),
        (r'^CARBON', 'carbon'), (r'mm_chassis1', 'dark'), (r'mm_misc1', 'dark'), (r'mm_windows1', 'glass'), (r'^Glass_Blask', 'glass'), (r'mm_lights1', lights), (r'^phong', 'dark'),
    ]),
    # a four-seat hyper grand tourer
    'megagt': dict(src='c2/source/inner/FINAL_MODEL_G.fbx', front=-1, rim_ratio=.72, rules=[
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
        (r'^INT_DISPLAY|^win_int|^sm_16_T|^sm_158|^sm_72|^material@|^sm_110|^sm_100|^sm_71', 'drop'),
        (r'^body_1|^body_2|^sm_152_T', 'paint'), (r'^carbon_1', 'carbon'), (r'^black1|^sm_115|^sm_129|^wiper', 'dark'), (r'^glass', 'glass'),
        (r'^EXT_WHEEL', 'wheel:rubber'), (r'^rim_ao', 'wheel:rim'), (r'^color_rims', 'wheel:red'), (r'^white_center_rim', 'wheel:white'), (r'^EXT_BRAKEDISC', 'wheel:disc'),
        (r'^rear_lights|^sm_31_T', 'tail'), (r'^headlights', 'light'), (r'^metall1', 'chrome'), (r'^metal_red', 'red'), (r'^sm_55_T', 'white'),
        (r'^carbon_int|^carbon_steer|^sm_48|^Material_3|^sm_6|^sm_69|^sm_43_T|^plastic_gloss', 'int:dark'),
        (r'^sm_', 'dark'),
    ]),
    # a late-seventies endurance wedge
    'retrogt': dict(src='c6/source/Sketchfab_2026_11_04_10_34_31.glb', front=-1, rules=[
        (r'STICKER|weld|int_gauges|STITCH', 'drop'), (r'^EXT_BODY|^carPaint', 'paint'), (r'^EXT_WINDOWS|^EXT_BLACKGLASS', 'glass'),
        (r'^EXT_tyre', 'wheel:rubber'), (r'^RIM_CHROME', 'wheel:chrome'), (r'^RIM_GUNMETAL|^inner_rim', 'wheel:gunmetal'), (r'^rotor_', 'wheel:disc'), (r'^hub|^steel', 'wheel:metal'),
        (r'^EXT_FLATGLASS|^EXT_HEADLIGHTCHROME|^EXT_LIGHT', 'light'), (r'^TAILGLASS', lambda c, uv: np.where(c[:, 1] > 3, 'tail', 'drop')), (r'^BULB', lights), (r'^MAIN_CIRCLE', 'white'),
        (r'^ENG_ALU|^SUSP_ALU', 'metal'), (r'^ENG_CHROME|^EXH_CHROME|^EXT_CHROME|^MIRRORS', 'chrome'), (r'^ENG_RED', 'red'), (r'^ENG_BLUE', 'bluem'), (r'^ENG_|^SUSP_|^EXT_DARKALLOY', 'gunmetal'),
        (r'^BLACK|^DARK|^EXT_GRILLE|^EXT_PLASTIC|^rubbertrim|^frame', 'dark'),
        (r'badge|gauge_needle|reflector', 'drop'), (r'^EXT_RIVET|^aluminum|^chrome@|^screw', 'metal'), (r'^MISC_RED', 'red'), (r'^zeroblack|^EXT_DETAILS', 'dark'),
        (r'FABRIC|SEATBELT', 'int:seat'), (r'^INT_ALU|^INT_DARKALU|^INT2_ALU|^INTSTEER_ALU', 'int:metal'), (r'^INT|^blkplastic|^metalpainted|^plastic_|^rubber_', 'int:dark'),
    ]),
}
