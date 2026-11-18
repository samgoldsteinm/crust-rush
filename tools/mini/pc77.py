"""The PC side of web patch 77 (v222): the underglow as LED strips, the same light as the web's.
    py.cmd tools/mini/pc77.py      (once, after pc71-pc76; edits D:/crust-rush/godot/scripts; reads source/tools/neon/ug_params.json,
                                    made by tools/neon/ugtable.py from the web build)
- shaders/underglow.gdshaderinc: the web's ugLs line for line (four strips under the sills and bumpers, each a continuous line of
  light, blocked by the tyres; a little light bounced out from under the body; smooth-limited, ending with the margin), worked out
  for each pixel (the web bakes it into a picture once per car).
- view.gd: UG_P, the web's ugParams for every body (so both draw from the same numbers), ug_params (the table, or the model's
  bounds and wheels for a body not in it), ug_comp (the colour evened out by its brightness), ug_sat (the web's, in HSL),
  ug_plane: the race's sheet (shaders/ug_sheet.gdshader). The two lights under a racing kart low and short (2.4 x the half-width;
  they reached 40 units, two bright pools), tinting its lowest panels; in the dark only, as before.
- menu.gd: the garage floor (shaders/garage_floor.gdshader) is lit by the glow (floor colour x light, so it keeps its look) in
  place of the sheet over it; one short light under the car for its panels and tyres; the rainbow cycling.
- kart_builder.gd: the body's id in the model's meta (for the table).
"""
import json
G = 'D:/crust-rush/godot/scripts/'
T = json.load(open('D:/crust-rush/source/tools/neon/ug_params.json', encoding='utf-8'))


def rd(f):
    return open(G + f, encoding='utf-8', newline='').read()


def wr(f, s):
    open(G + f, 'w', encoding='utf-8', newline='').write(s)


def rep(f, a, b, n=1):
    s = rd(f)
    assert s.count(a) == n, (f, s.count(a), a[:80])
    wr(f, s.replace(a, b))


def cut(f, a, z, b):
    """replace from a up to (not including) z"""
    s = rd(f)
    assert s.count(a) == 1, (f, 'start', a[:80])
    i = s.find(a)
    j = s.find(z, i)
    assert j > i, (f, 'end', z[:80])
    wr(f, s[:i] + b + s[j:])


rep('kart_builder.gd', 'var meta := {"scale": 1.76 * sf, "sf": sf, ', 'var meta := {"scale": 1.76 * sf, "sf": sf, "id": String(bd["id"]), ', 2)

# racing karts: the lights and the sheet from the body's numbers
cut('view.gd', "	var sc: float = g.scale.x if g.scale.x > 0.0 else 1.0\n	var axf := float(meta.get(\"axF\", 6.0)) / sc\n",
    "	v[\"ug_haze\"] = ug_plane(g, col, 0.1, v[\"model\"])",
    """	var P := ug_params(String(meta.get("id", "")), g, v["model"])
	var cs := ug_sat(col)
	v["ug_cp"] = ug_comp(cs.srgb_to_linear())
	for i in 2:
		# (pc77) low under the car and short: they tint its lowest panels and tyres (the sheet lights the ground)
		var L := OmniLight3D.new()
		L.light_color = cs
		L.omni_range = float(P["b"]) * 2.4
		L.omni_attenuation = 2.0
		L.light_energy = 0.0
		L.shadow_enabled = false
		L.position = Vector3(float(P["cx"]) + float(P["wf"] if i == 0 else P["wr"]) * 0.5, float(P["h"]) * 0.55, float(P["cz"]))
		g.add_child(L)
		(v["ug"] as Array).append(L)
""")
s = rd('view.gd')
assert s.count("""	v["ug_haze"] = ug_plane(g, col, 0.1, v["model"])   # (web patch 71: the picture from the body and its wheels)""") == 1
s = s.replace("""	v["ug_haze"] = ug_plane(g, col, 0.1, v["model"])   # (web patch 71: the picture from the body and its wheels)""",
              """	v["ug_haze"] = ug_plane(g, col, 0.1, v["model"], P)   # (pc77: the LED strips' light from the body and its wheels)""")
wr('view.gd', s)

TABLE = ',\n'.join('\t"%s": [%s]' % (k, ', '.join(repr(float(x)) for x in v)) for k, v in sorted(T.items()))
cut('view.gd', "const UG_M := 0.75\n", "## each frame: the glow brighter in the dark",
    """## (pc77, web ugParams via tools/neon/ugtable.py) each body's underglow numbers in the kart's own units: the body's half-length and
## half-width, its centre (x, z), the strips' height (the sill), the axles' x, the wheels' radius (front, rear), their z, a tyre's width
const UG_KEYS := ["a", "b", "cx", "cz", "h", "wf", "wr", "rf", "rr", "wz", "tw"]
const UG_P := {
""" + TABLE + """
}
const UG_GAIN := 1.0       # (web UG_GAIN) the garage floor's light
const UG_TONE := 1.4      # Godot's ACES (white 8) compresses more than three.js's: the same glow on screen as the web
const UG_BOUNCE := 0.35    # the light under the car in the garage
const UG_BOUNCE_R := 1.6   # the lights under a racing kart, x the dark
const UG_SHEET := preload("res://shaders/ug_sheet.gdshader")


## the meshes' bounds (src's) in g's own space
static func _box_in(g: Node3D, src: Node3D) -> AABB:
	var bb := AABB()
	var first := true
	for mi in src.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null:
			continue
		var xf := Transform3D.IDENTITY
		var c: Node = m
		while c != null and c != g:
			if c is Node3D:
				xf = (c as Node3D).transform * xf
			c = c.get_parent()
		var ab := xf * m.mesh.get_aabb()
		bb = ab if first else bb.merge(ab)
		first = false
	return bb


## web ugParams: the body's numbers (the table; for a body not in it, src's bounds and its wheels), with kT and M (web ugDerive)
static func ug_params(id: String, g: Node3D, src: Node3D) -> Dictionary:
	var P := {}
	if UG_P.has(id):
		var q: Array = UG_P[id]
		for i in UG_KEYS.size():
			P[UG_KEYS[i]] = float(q[i])
	else:
		var bb := _box_in(g, src)
		var cx := bb.position.x + bb.size.x / 2.0
		var cz := bb.position.z + bb.size.z / 2.0
		P = {"a": bb.size.x * 0.45, "b": bb.size.z * 0.42, "cx": cx, "cz": cz, "h": 0.5, "wf": bb.size.x * 0.3, "wr": -bb.size.x * 0.3, "rf": 0.0, "rr": 0.0, "wz": 0.0, "tw": 0.0}
		var nf := src.find_child("wheel_FL", true, false) as Node3D
		var nr := src.find_child("wheel_RL", true, false) as Node3D
		if nf != null and nr != null:
			var bf := _box_in(g, nf)
			var br := _box_in(g, nr)
			if bf.size.y > 0.0 and br.size.y > 0.0:
				P["wf"] = bf.get_center().x - cx
				P["wr"] = br.get_center().x - cx
				P["rf"] = bf.size.y / 2.0
				P["rr"] = br.size.y / 2.0
				P["wz"] = absf(bf.get_center().z - cz)
				P["tw"] = bf.size.z
				P["h"] = 0.45 * (float(P["rf"]) + float(P["rr"])) / 2.0
	var tw := float(P["tw"])
	var rA := (float(P["rf"]) + float(P["rr"])) / 2.0
	P["kT"] = 5.0 / maxf(0.2, minf(tw if tw > 0.0 else 1.0, rA if rA > 0.0 else 1.0))
	P["M"] = 0.45 * float(P["b"]) + 1.5 * float(P["h"])
	return P


## the body's numbers into a material using shaders/underglow.gdshaderinc
static func ug_apply(m: ShaderMaterial, P: Dictionary) -> void:
	m.set_shader_parameter("ug_p0", Vector4(P["a"], P["b"], P["h"], P["kT"]))
	m.set_shader_parameter("ug_p1", Vector4(P["wf"], P["wr"], P["wz"], P["tw"]))
	m.set_shader_parameter("ug_p2", Vector4(P["rf"], P["rr"], P["M"], 0.0))


## web ugSat: the glow's colour a little more saturated (in HSL, on the colour as picked)
static func ug_sat(c: Color) -> Color:
	var mx := maxf(c.r, maxf(c.g, c.b))
	var mn := minf(c.r, minf(c.g, c.b))
	var l := (mx + mn) / 2.0
	var s := 0.0 if mx <= mn else (mx - mn) / (1.0 - absf(2.0 * l - 1.0))
	s = minf(1.0, s * 1.15 + 0.05)
	l *= 0.96
	var h := c.h * 6.0
	var C := (1.0 - absf(2.0 * l - 1.0)) * s
	var X := C * (1.0 - absf(fmod(h, 2.0) - 1.0))
	var o := l - C / 2.0
	var rgb := Vector3(C, X, 0) if h < 1.0 else Vector3(X, C, 0) if h < 2.0 else Vector3(0, C, X) if h < 3.0 else Vector3(0, X, C) if h < 4.0 else Vector3(X, 0, C) if h < 5.0 else Vector3(C, 0, X)
	return Color(rgb.x + o, rgb.y + o, rgb.z + o, c.a)


## web ugComp: the colour (linear) evened out by its brightness, the colour itself kept: a dark blue lifted, a pale cyan brought down
static func ug_comp(c: Color) -> float:
	var Y := 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
	return clampf(pow(0.25 / maxf(Y, 0.01), 0.3), 0.8, 1.6)


## the race's colour on a sheet (col as picked)
static func ug_colour(m: ShaderMaterial, col: Color) -> void:
	var cl := ug_sat(col).srgb_to_linear()
	m.set_shader_parameter("ug_col", Vector3(cl.r, cl.g, cl.b) * ug_comp(cl) * 0.75 * UG_TONE)


## web patch 77's sheets: an additive sheet under g with the LED strips' light (shaders/ug_sheet.gdshader); returns its material
static func ug_plane(g: Node3D, col: Color, alpha: float, src: Node3D, P := {}) -> ShaderMaterial:
	if P.is_empty():
		P = ug_params("", g, src)
	var W := 2.0 * (float(P["a"]) + float(P["M"]))
	var H := 2.0 * (float(P["b"]) + float(P["M"]))
	var q := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(W, H)
	q.mesh = pm
	var m := ShaderMaterial.new()
	m.shader = UG_SHEET
	ug_apply(m, P)
	ug_colour(m, col)
	m.set_shader_parameter("ug_alpha", alpha)
	m.set_shader_parameter("ug_size", Vector2(W, H))
	q.material_override = m
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.position = Vector3(float(P["cx"]), 0.2, float(P["cz"]))
	g.add_child(q)
	return m


""")
cut('view.gd', "func _style_frame(k: Kart, v: Dictionary, time: float, dark: float) -> void:\n", "func smoke_col(",
    """func _style_frame(k: Kart, v: Dictionary, time: float, dark: float) -> void:
	var ug: Array = v.get("ug", [])
	if ug.is_empty():
		return
	var rb := bool(v.get("ug_rb", false))
	var rc := Color.from_hsv(fmod(time * 0.12 + k.ri * 0.13, 1.0), 1.0, 1.0) if rb else Color(0, 0, 0, 0)
	var cp := float(v.get("ug_cp", 1.0))
	for L in ug:
		(L as OmniLight3D).light_energy = UG_BOUNCE_R * cp * dark * (1.2 if k.boost > 0.0 else 1.0)   # (only in the dark, as the web)
		if rb:
			(L as OmniLight3D).light_color = ug_sat(rc)
	var hm: ShaderMaterial = v.get("ug_haze")
	if hm != null:
		hm.set_shader_parameter("ug_alpha", 0.1 + 0.6 * dark)   # (faint by day, the glow at night)
		if rb:
			ug_colour(hm, rc)


""")

# the garage: the floor lit by the glow
cut('menu.gd', "	var fm := StandardMaterial3D.new()\n	fm.albedo_texture = _floor_tex()", "	fl.material_override = fm\n",
    """	var fm := ShaderMaterial.new()
	fm.shader = load("res://shaders/garage_floor.gdshader")   # (pc77: the dark showroom floor, lit by the car's underglow)
	fm.set_shader_parameter("albedo_tex", _floor_tex())
	fm.set_shader_parameter("albedo_col", Color(0.17, 0.17, 0.18))   # (darker under the showroom's lights)
	_gfloor = fm
""")
cut('menu.gd', "		_gug = null\n		if gl[\"h\"] != null:", "	_frame_garage_cam()\n",
    """		_gug_P = {}
		if _gfloor != null:
			_gfloor.set_shader_parameter("ug_on", 0.0)
		if gl["h"] != null:
			# (pc77) the floor lit by the LED strips (shaders/garage_floor.gdshader), one short light under the car for its panels
			var gc := Color("#ff3030") if String(gl["h"]) == "rainbow" else Color(String(gl["h"]))
			_gug_rb = String(gl["h"]) == "rainbow"
			_gug_P = View.ug_params(String((built["meta"] as Dictionary).get("id", "")), _gkart, _gkart)
			if _gfloor != null:
				View.ug_apply(_gfloor, _gug_P)
			var L := OmniLight3D.new()
			L.omni_range = float(_gug_P["b"]) * 2.4
			L.omni_attenuation = 2.0
			L.shadow_enabled = false
			L.position = Vector3(float(_gug_P["cx"]), float(_gug_P["h"]) * 0.55, float(_gug_P["cz"]))
			_gkart.add_child(L)
			_gugl = L
			_gug_colour(gc)
""")
rep('menu.gd', """## web gFloorTex: dark polished charcoal""", """## (pc77) the garage glow's colour: the floor's light (colour x brightness / the floor's own colour at the middle) and the light's
func _gug_colour(c: Color) -> void:
	var cs := View.ug_sat(c)
	var cl := cs.srgb_to_linear()
	var cp := View.ug_comp(cl)
	var f0 := Color("#3a3c44").srgb_to_linear()
	var f1 := Color(0.17, 0.17, 0.18).srgb_to_linear()
	var ref := (f0.r * f1.r + f0.g * f1.g + f0.b * f1.b) / 3.0
	if _gfloor != null:
		_gfloor.set_shader_parameter("ug_col", Vector3(cl.r, cl.g, cl.b) * cp * View.UG_GAIN * View.UG_TONE / ref)
	if is_instance_valid(_gugl):
		_gugl.light_color = cs
		_gugl.light_energy = View.UG_BOUNCE * cp


## web gFloorTex: dark polished charcoal""")
rep('menu.gd', """		if _gug_rb and _gug != null and is_instance_valid(_gugl):
			var rc := Color.from_hsv(fmod(Time.get_ticks_msec() / 1000.0 * 0.12, 1.0), 1.0, 1.0)
			_gug.albedo_color = Color(rc.r, rc.g, rc.b, _gug.albedo_color.a)
			_gugl.light_color = rc
""", """		if not _gug_P.is_empty() and _gfloor != null and is_instance_valid(_gkart):
			# (pc77) the floor's light follows the turning car
			var xf := _gkart.global_transform * Transform3D(Basis(), Vector3(float(_gug_P["cx"]), 0.0, float(_gug_P["cz"])))
			_gfloor.set_shader_parameter("ug_inv", Projection(xf.affine_inverse()))
			_gfloor.set_shader_parameter("ug_on", 1.0)
			if _gug_rb:
				_gug_colour(Color.from_hsv(fmod(Time.get_ticks_msec() / 1000.0 * 0.12, 1.0), 1.0, 1.0))
""")
rep('menu.gd', "var _gug: StandardMaterial3D = null   # (pc71) the garage's underglow picture, its light, rainbow or not\n",
    "var _gfloor: ShaderMaterial = null   # (pc77) the garage floor, lit by the underglow; the body's numbers; its light, rainbow or not\nvar _gug_P := {}\n")
print('pc77 applied')
