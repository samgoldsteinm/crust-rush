"""The PC side of web patch 71 (v222): the underglow's styles, and the underglow in the garage's preview.
    py.cmd tools/mini/pc71.py      (once; edits D:/crust-rush/godot/scripts)
- view.gd: View.UGV (1-4; 0 the old pool; CR_UGV for pictures), View.ug_tex(v, lr) the same picture as the web's ugVarT (from the body's
  footprint L x W and a margin of ground), View.ug_plane() an additive plane sized to the body's own box (_body_box: the meshes' bounds),
  used under racing karts (the haze, now the main glow: alpha .55 + .2 dark with a style, the old faint .05 + .07 without) and in the garage.
- menu.gd: the garage's preview gets the plane and one soft light under the car (it had no underglow).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


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
""", """	if UGV > 0:
		v["ug_haze"] = ug_plane(g, col, 0.6, v["model"])   # (web patch 71: the soft picture, sized to the body)
		return
	var q := MeshInstance3D.new()
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


## (web patch 71) the underglow's style: 1 soft pool, 2 core and halo, 3 side strips, 4 wide and faint (0: the old pool)
static var UGV := int(OS.get_environment("CR_UGV")) if OS.get_environment("CR_UGV") != "" else 1
const UG_M := [0.0, 0.8, 0.9, 0.7, 1.1]
static var _ugv_t := {}


## the meshes' bounds (src's, the kart's model) in g's own space: the body's footprint
static func _body_box(g: Node3D, src: Node3D) -> AABB:
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


## an additive plane under g with the style's picture; returns its material (alpha set each frame by _style_frame)
static func ug_plane(g: Node3D, col: Color, alpha := 0.6, src: Node3D = null) -> StandardMaterial3D:
	var bb := _body_box(g, src if src != null else g)
	var bL := maxf(1.0, bb.size.x * 0.94)
	var bW := maxf(1.0, bb.size.z * 0.94)
	var m: float = UG_M[UGV]
	var q := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(bL + 2.0 * m * bW, bW * (1.0 + 2.0 * m))
	q.mesh = pm
	var hm := StandardMaterial3D.new()
	hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	hm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	hm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	hm.albedo_texture = ug_tex(UGV, bL / bW)
	hm.albedo_color = Color(col.r, col.g, col.b, alpha)
	hm.disable_fog = true
	q.material_override = hm
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.position = Vector3(bb.position.x + bb.size.x / 2.0, 0.2, bb.position.z + bb.size.z / 2.0)
	g.add_child(q)
	return hm


## web ugVarT: under the body brightest in the middle; past its (rounded) edge a soft fall like light's, to nothing at the plane's edge
static func ug_tex(v: int, lr: float) -> ImageTexture:
	lr = snappedf(lr, 0.1)
	var key := "%d:%.1f" % [v, lr]
	if _ugv_t.has(key):
		return _ugv_t[key]
	var m: float = UG_M[v]
	var PL := lr + 2.0 * m
	var PW := 1.0 + 2.0 * m
	var W := 256
	var H := maxi(64, int(round(256.0 * PW / PL / 8.0)) * 8)
	var rc := 0.3
	var bx := lr / 2.0
	var bz := 0.5
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	for z in H:
		for x in W:
			var X := absf((x + 0.5) / W - 0.5) * PL
			var Z := absf((z + 0.5) / H - 0.5) * PW
			var qx := X - (bx - rc)
			var qz := Z - (bz - rc)
			var sd := Vector2(maxf(qx, 0.0), maxf(qz, 0.0)).length() + minf(maxf(qx, qz), 0.0) - rc
			var o := maxf(0.0, sd)
			var t := minf(1.0, o / m)
			var fz := 1.0 - t * t * (3.0 - 2.0 * t)
			var r := pow(pow(X / bx, 4.0) + pow(Z / bz, 4.0), 0.25)
			var k := maxf(0.0, 1.0 - r * r)
			var side := 0.4 + 0.6 * clampf(1.0 - (X - bx) / 0.5, 0.0, 1.0)
			var a: float
			if v == 2:
				a = (0.6 + 0.4 * k * k) if sd <= 0.0 else 0.6 * (0.55 / (1.0 + (o / 0.1) * (o / 0.1)) + 0.45 * exp(-(o / 0.45) * (o / 0.45))) * fz
			elif v == 3:
				a = 0.8 if sd <= 0.0 else 0.8 / (1.0 + (o / 0.14) * (o / 0.14)) * side * fz
			elif v == 4:
				a = (0.45 + 0.15 * k) if sd <= 0.0 else 0.45 / (1.0 + (o / 0.35) * (o / 0.35)) * fz
			else:
				a = (0.75 + 0.25 * k) if sd <= 0.0 else 0.75 / (1.0 + (o / 0.16) * (o / 0.16)) * fz
			img.set_pixel(x, z, Color(1, 1, 1, clampf(a, 0.0, 1.0)))
	var tex := ImageTexture.create_from_image(img)
	_ugv_t[key] = tex
	return tex
""")
rep('view.gd', """		hm.albedo_color = Color(c.r, c.g, c.b, 0.05 + 0.07 * dark)   # (a faint haze only: the lights do the work)""",
    """		hm.albedo_color = Color(c.r, c.g, c.b, (0.55 + 0.2 * dark) if UGV > 0 else 0.05 + 0.07 * dark)   # (web patch 71: with a style the picture is the glow; the old pool a faint haze only)""")
# the garage's preview
rep('menu.gd', """			_grad = bb.size.length() * 0.5
			_gcy = bb.position.y + bb.size.y * 0.5
	_frame_garage_cam()
""", """			_grad = bb.size.length() * 0.5
			_gcy = bb.position.y + bb.size.y * 0.5
		# (web patch 71) the underglow under the preview (after the camera's bounds): the soft picture and one light under the middle
		var S := preload("res://scripts/style.gd")
		var gl: Dictionary = S.pick(build, "gl")
		if gl["h"] != null:
			var gc := Color("#ff3030") if String(gl["h"]) == "rainbow" else Color(String(gl["h"]))
			View.ug_plane(_gkart, gc, 0.95)
			var L := OmniLight3D.new()
			L.light_color = gc
			L.omni_range = 14.0
			L.omni_attenuation = 1.2
			L.light_energy = 4.0
			L.shadow_enabled = false
			L.position = Vector3(0, 0.6, 0)
			_gkart.add_child(L)
	_frame_garage_cam()
""")
print('pc71 applied')
