"""The PC side of web patches 71-72 (v222): the underglow remade (from the owner's photos), in the garage too, and the garage's floor.
    py.cmd tools/mini/pc71.py      (once; edits D:/crust-rush/godot/scripts)
- view.gd: View.ug_tex(lr, wf, wr, rr) the web's ugTex (footprint L x W, the wheels' x and radius, in units of W): a bright fall past the
  sill plus a soft ambient one, cut beside each tyre into front, back and side sections. View.ug_plane(g, col, alpha, src) sizes it to the
  model's own bounds and wheels (the nodes wheel_FL / wheel_RL). Under racing karts it replaces the old pool; in races it shows only in the
  dark (the owner: "the race glow should only show when its supposed to" and "some of the light is super bright still on the pc version":
  the released lights were energy 2 in daylight with range 95, a big bright disc on pale ground): lights 4.5 x darkness, range 40,
  attenuation 1.2; the picture's alpha .1 + .6 x darkness.
- menu.gd: the garage's preview gets the picture and one soft light under the car (the released PC garage had no underglow at all), a
  rainbow glow cycling, and a dark showroom floor in place of the brown disc (web patch 72).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('view.gd', """		L.omni_range = 95.0
		L.omni_attenuation = 0.45
""", """		L.omni_range = 40.0
		L.omni_attenuation = 1.2
""")
rep('view.gd', """	var q := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2((axf - axr) * 1.9 + 6.0, float(meta.get("axW", 5.0)) / sc * 3.4 + 3.0)
	q.mesh = pm
	var hm := StandardMaterial3D.new()
	hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	hm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	hm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	hm.albedo_texture = _ug_tex()
	hm.albedo_color = Color(col.r, col.g, col.b, 0.3)
	hm.disable_fog = true
	q.material_override = hm
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.position = Vector3((axf + axr) / 2.0, 0.2, 0.0)
	g.add_child(q)
	v["ug_haze"] = hm
""", """	v["ug_haze"] = ug_plane(g, col, 0.1, v["model"])   # (web patch 71: the picture from the body and its wheels)


const UG_M := 0.75
static var _ugv_t := {}


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


## web ugSat: the glow's colour a little more saturated
static func ug_sat(c: Color) -> Color:
	return Color.from_hsv(c.h, minf(1.0, c.s * 1.15 + 0.05), c.v)


## an additive plane under g with the underglow's picture, sized to src's bounds and wheels; returns its material
static func ug_plane(g: Node3D, col: Color, alpha: float, src: Node3D) -> StandardMaterial3D:
	var bb := _box_in(g, src)
	var bL := maxf(1.0, bb.size.x * 0.9)
	var bW := maxf(1.0, bb.size.z * 0.86)
	var cx := bb.position.x + bb.size.x / 2.0
	var wf := bL * 0.32
	var wr := -bL * 0.32
	var rr := bW * 0.17
	var nf := src.find_child("wheel_FL", true, false) as Node3D
	var nr := src.find_child("wheel_RL", true, false) as Node3D
	if nf != null and nr != null:
		var bf := _box_in(g, nf)
		var br := _box_in(g, nr)
		if bf.size.y > 0.0 and br.size.y > 0.0:
			wf = bf.position.x + bf.size.x / 2.0 - cx
			wr = br.position.x + br.size.x / 2.0 - cx
			rr = maxf(0.1, bf.size.y / 2.0)
	var q := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(bL + 2.0 * UG_M * bW, bW * (1.0 + 2.0 * UG_M))
	q.mesh = pm
	var hm := StandardMaterial3D.new()
	hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	hm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	hm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	hm.albedo_texture = ug_tex(bL / bW, wf / bW, wr / bW, rr / bW)
	var cs := ug_sat(col)
	hm.albedo_color = Color(cs.r, cs.g, cs.b, alpha)
	hm.disable_fog = true
	q.material_override = hm
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.position = Vector3(cx, 0.2, bb.position.z + bb.size.z / 2.0)
	g.add_child(q)
	return hm


static func _sm(a: float, b: float, v: float) -> float:
	var t := clampf((v - a) / (b - a), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


## web ugTex
static func ug_tex(lr: float, wf: float, wr: float, rr: float) -> ImageTexture:
	lr = snappedf(lr, 0.01)
	wf = snappedf(wf, 0.01)
	wr = snappedf(wr, 0.01)
	rr = snappedf(rr, 0.01)
	var key := "%.2f:%.2f:%.2f:%.2f" % [lr, wf, wr, rr]
	if _ugv_t.has(key):
		return _ugv_t[key]
	var m := UG_M
	var PL := lr + 2.0 * m
	var PW := 1.0 + 2.0 * m
	var W := 256
	var H := maxi(64, int(round(256.0 * PW / PL / 8.0)) * 8)
	var rc := 0.28
	var bx := lr / 2.0
	var bz := 0.5
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	for z in H:
		for x in W:
			var xs := ((x + 0.5) / W - 0.5) * PL
			var X := absf(xs)
			var Z := absf((z + 0.5) / H - 0.5) * PW
			var qx := X - (bx - rc)
			var qz := Z - (bz - rc)
			var sd := Vector2(maxf(qx, 0.0), maxf(qz, 0.0)).length() + minf(maxf(qx, qz), 0.0) - rc
			var o := maxf(0.0, sd)
			var fz := 1.0 - _sm(0.0, m, o)
			var a := 1.0 if sd <= 0.0 else (0.62 * exp(-o / 0.09) + 0.38 * exp(-o / 0.3)) * fz
			if Z > bz - 0.14:
				for xw in [wf, wr]:
					var outw := maxf(0.0, Z - bz)
					var hw := rr * (1.05 + 1.5 * outw)
					var dx := absf(xs - float(xw))
					a *= 1.0 - 0.92 * _sm(hw, hw * 0.5, dx) * _sm(bz - 0.14, bz - 0.02, Z)
			if qx > 0.0 and qx > qz:
				a *= 0.85
			img.set_pixel(x, z, Color(1, 1, 1, clampf(a, 0.0, 1.0)))
	var tex := ImageTexture.create_from_image(img)
	_ugv_t[key] = tex
	return tex
""")
rep('view.gd', """		(L as OmniLight3D).light_energy = (2.0 + 6.0 * dark) * (1.2 if k.boost > 0.0 else 1.0)""",
    """		(L as OmniLight3D).light_energy = 4.5 * dark * (1.2 if k.boost > 0.0 else 1.0)   # (pc71: only in the dark, as the web)""")
rep('view.gd', """		hm.albedo_color = Color(c.r, c.g, c.b, 0.05 + 0.07 * dark)   # (a faint haze only: the lights do the work)""",
    """		var cs := ug_sat(c)
		hm.albedo_color = Color(cs.r, cs.g, cs.b, 0.1 + 0.6 * dark)   # (pc71: faint by day, the glow at night)""")
# the garage: the floor and the glow
rep('menu.gd', """	var fm := StandardMaterial3D.new()
	fm.albedo_color = Color("#3a2216")
	fm.roughness = 0.85
""", """	var fm := StandardMaterial3D.new()
	fm.albedo_texture = _floor_tex()   # (pc71: a dark showroom floor, web patch 72)
	fm.roughness = 0.42
	fm.metallic = 0.15
""")
rep('menu.gd', """## a node's transform relative to an ancestor""", """## web gFloorTex: dark polished charcoal, a lighter spot under the car, fine circular brushing, darker to the edge
static var _floor_t: ImageTexture = null
static func _floor_tex() -> ImageTexture:
	if _floor_t != null:
		return _floor_t
	var N := 512
	var img := Image.create(N, N, false, Image.FORMAT_RGBA8)
	var c0 := Color("#3a3c44")
	var c1 := Color("#26272d")
	var c2 := Color("#121317")
	for y in N:
		for x in N:
			var r := Vector2(x - N / 2.0, y - N / 2.0).length() / (N / 2.0)
			var c := c0.lerp(c1, clampf(r / 0.45, 0.0, 1.0)) if r < 0.45 else c1.lerp(c2, clampf((r - 0.45) / 0.55, 0.0, 1.0))
			img.set_pixel(x, y, c)
	img.generate_mipmaps()
	_floor_t = ImageTexture.create_from_image(img)
	return _floor_t


## a node's transform relative to an ancestor""")
rep('menu.gd', """			_grad = bb.size.length() * 0.5
			_gcy = bb.position.y + bb.size.y * 0.5
	_frame_garage_cam()
""", """			_grad = bb.size.length() * 0.5
			_gcy = bb.position.y + bb.size.y * 0.5
		# (pc71) the underglow under the preview (after the camera's bounds): the picture and one soft light under the middle
		var S := preload("res://scripts/style.gd")
		var gl: Dictionary = S.pick(build, "gl")
		_gug = null
		if gl["h"] != null:
			var gc := Color("#ff3030") if String(gl["h"]) == "rainbow" else Color(String(gl["h"]))
			_gug = View.ug_plane(_gkart, gc, 0.75, _gkart)
			_gug_rb = String(gl["h"]) == "rainbow"
			var L := OmniLight3D.new()
			L.light_color = gc
			L.omni_range = 14.0
			L.omni_attenuation = 1.4
			L.light_energy = 2.5
			L.shadow_enabled = false
			L.position = Vector3(0, 0.6, 0)
			_gkart.add_child(L)
			_gugl = L
	_frame_garage_cam()
""")
# the garage's rainbow glow cycles (web patch 72)
rep('menu.gd', """		_gturn.rotation.y = _grot
""", """		_gturn.rotation.y = _grot
		if _gug_rb and _gug != null and is_instance_valid(_gugl):
			var rc := Color.from_hsv(fmod(Time.get_ticks_msec() / 1000.0 * 0.12, 1.0), 1.0, 1.0)
			_gug.albedo_color = Color(rc.r, rc.g, rc.b, _gug.albedo_color.a)
			_gugl.light_color = rc
""")
rep('menu.gd', "var _grot := 0.6\n", "var _grot := 0.6\nvar _gug: StandardMaterial3D = null   # (pc71) the garage's underglow picture, its light, rainbow or not\nvar _gugl: OmniLight3D = null\nvar _gug_rb := false\n")
print('pc71 applied')
