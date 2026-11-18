"""PC: web patch 91 (v228): the Rims colour on each wheel's real spokes and hub; calipers only from Calipers; Gold, Silver, Bronze paints.
    py.cmd tools/mini/pc87.py      (once, after pc86; edits kart_builder.gd, menu.gd)
- WHEEL_SPOKES as the web's (measured on the rolling part: not the caliper's class).
- hold_cols: a held part's caliper classes are 13, the pack's own (HOLD_K: now also each wheel set's 16 / 17 / 18) and the wheel's
  calipers; no longer its spoke classes.
- PAINT_MET: paints 24..26 (gold, silver, bronze; from the export's paint list) are metallic under the clear coat; their swatches
  show a sheen. The wheel sets' facing, the Monster wheel per side and the brake discs labelled 12 come with the export.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


K = 'kart_builder.gd'
rep(K, '''const WHEEL_SPOKES := {"suv": [10], "retrogt": [10], "concept": [1], "chariot": [1], "skywing": [6], "bike_mx": [10], "bike_moto": [10],
	"rollpin": [21], "grater": [21], "comet": [21], "oilcan": [21], "redline": [17], "emerald": [16], "stealth": [16], "turbo": [18], "forged": [19]}''',
    '''const WHEEL_SPOKES := {"suv": [10], "retrogt": [10, 15], "concept": [1, 2], "chariot": [1, 6, 2, 0], "tourer": [11, 10, 7], "onyx": [11, 6], "skywing": [6],
	"bike_mx": [10], "bike_moto": [10], "rollpin": [21], "grater": [21], "comet": [21], "oilcan": [21],
	"redline": [1, 6, 17], "emerald": [6, 15, 16], "stealth": [6, 15, 16], "turbo": [1, 18, 15], "forged": [19]}   # (pc87, web patch 91: measured on the rolling part)
## (pc87, web patch 91 PAINT_MET) the metal paints: [metalness, roughness]
const PAINT_MET := {24: [0.85, 0.26], 25: [0.85, 0.22], 26: [0.85, 0.3]}''')
rep(K, '''const HOLD_K := {"monster": [12, 11], "muscle": [12], "retrogt": [7], "hatch": [9]}''',
    '''const HOLD_K := {"monster": [12, 11], "muscle": [12], "retrogt": [7], "hatch": [9], "redline": [16, 17, 18], "emerald": [16, 17, 18], "stealth": [16, 17, 18],
	"turbo": [16, 17, 18], "forged": [16, 17, 18]}   # (pc87: the wheel sets' calipers)''')
rep(K, '''		for ci in HOLD_K.get(hid, []) + WHEEL_CAL.get(hid, []) + WHEEL_SPOKES.get(hid, [11]):''',
    '''		for ci in HOLD_K.get(hid, []) + WHEEL_CAL.get(hid, []):   # (pc87: not the spoke classes)''')
rep(K, '''	return {"acc": acc_c, "accm": accm, "paint": col,''',
    '''	return {"pmet": PAINT_MET.get(p, []) if lv.is_empty() else [], "acc": acc_c, "accm": accm, "paint": col,''')
rep(K, '''					pm.metallic = minf(float(lv.get("m", 0.14)), 0.62) if not lv.is_empty() else 0.0''',
    '''					pm.metallic = minf(float(lv.get("m", 0.14)), 0.62) if not lv.is_empty() else 0.0
					var pmet: Array = cols.get("pmet", [])
					if not pmet.is_empty():
						pm.metallic = float(pmet[0])   # (pc87, web patch 91: gold, silver, bronze)
						pm.roughness = float(pmet[1])
						pm.clearcoat_roughness = 0.04''')
rep('menu.gd', '''				var st := box([col], 180.0, 32.0, CHEESE if on else Color(1, 0.957, 0.863, 0.3), 3.0 if on else 1.5)''',
    '''				var st := box([Color("#ffffff"), col, Color("#2a2420")] if KartBuilder.PAINT_MET.has(i) else [col], 135.0 if KartBuilder.PAINT_MET.has(i) else 180.0, 32.0, CHEESE if on else Color(1, 0.957, 0.863, 0.3), 3.0 if on else 1.5)   # (pc87: a metal sheen)''')
print('pc87 applied')
