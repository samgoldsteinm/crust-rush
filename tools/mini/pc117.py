"""PC: the look past the web game (the owner: "lets do 1-6", from the list of what Godot could still add):
 1. Bounced light becomes Off / Baked / Live. Baked (the default on Ultra): a VoxelGI over the whole track baked while the
    race loads (HdLook.bake_gi, about 5 s on a big track), light off the road, hills and walls onto the karts and scenery.
    Live is pc116's SDFGI. A saved "on" from pc116 reads as Live.
 2. Fog and light rays: volumetric fog in each theme's air colour, the sun and the headlights shining through it. Ultra.
 3. Screen reflections: SSR on glossy surfaces. Ultra.
 4. Tyre marks: dark marks left on the road by drifting and hard launches (fx.gd Marks, view.gd _marks). All qualities.
 5. Film grade: a split-tone per theme on top of the web's grade (post.gdshader split/sh_col/hi_col).
 6. Road detail: grain, darker worn patches and varied gloss on the road surfaces (HdLook.road), with Finished models.
New file: godot/scripts/hd_look.gd (HdLook).
    python tools/mini/pc117.py      (once, after pc116)"""
G = 'D:/crust-rush/godot/'


def patch(path, pairs):
    p = G + path
    s = open(p, encoding='utf-8', newline='').read()
    assert 'pc117' not in s, path
    for a, b, *n in pairs:
        n = n[0] if n else 1
        assert s.count(a) == n, (path, s.count(a), a[:90])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---- main.gd
patch('scripts/main.gd', [
    ("""var gi_on := false      # (pc116) Settings > Bounced light (SDFGI), Ultra only, off by default
""", """var gi_on := false      # (pc116) Settings > Bounced light (SDFGI), Ultra only, off by default; (pc117) only read from old settings
var light_mode := "baked"   # (pc117) Settings > Bounced light: off | baked (VoxelGI, baked at load) | live (SDFGI)
var fog_on := true          # (pc117) Settings > Fog and light rays (Ultra)
var ssr_on := true          # (pc117) Settings > Screen reflections (Ultra)
var marks_on := true        # (pc117) Settings > Tyre marks
var grade_on := true        # (pc117) Settings > Film grade
var baked_gi: VoxelGI = null
"""),
    ("""				["Bounced light", "Sunlight bounces off the ground, walls and buildings onto everything near them, so shade picks up the colour around it, the way real light does. The most realistic lighting, and the heaviest: try it on a fast graphics card. Ultra only.", "gi", on_off, "1" if gi_on else "0"],
""", """				["Bounced light", "Light bounces off the road, the hills and the walls onto everything near them, so shade picks up the colour around it, the way real light does. Baked: worked out while the race loads (a few seconds), light on the frame rate. Live: worked out every frame round the camera, the heaviest. Ultra only; Baked applies from the next race.", "gi", [["off", "Off"], ["baked", "Baked"], ["live", "Live"]], light_mode],
				["Fog and light rays", "Real air: a light haze in each track's colour that the sun and the headlights shine through, with rays where trees and buildings break the light. Ultra only.", "fog", on_off, "1" if fog_on else "0"],
				["Screen reflections", "Glossy surfaces (toy-track plastic, water, polished floors, the road's worn patches) reflect the karts and scenery on screen. Ultra only.", "ssr", on_off, "1" if ssr_on else "0"],
				["Tyre marks", "Drifts and hard launches leave dark rubber marks on the road.", "marks", on_off, "1" if marks_on else "0"],
				["Film grade", "A colour grade for each kind of track, like a film's: cool shade and warm light, deep blue nights. Off is the web game's colours.", "grade", on_off, "1" if grade_on else "0"],
"""),
    ("""		"gi":
			gi_on = val == "1"
			_apply_quality()
""", """		"gi":
			light_mode = val
			_apply_quality()
		"fog":
			fog_on = val == "1"
			_apply_quality()
		"ssr":
			ssr_on = val == "1"
			_apply_quality()
		"marks":
			marks_on = val == "1"
			if fx != null:
				fx.marks_on = marks_on
		"grade":
			grade_on = val == "1"
			_apply_quality()
"""),
    ("""	var gi := gi_on and quality >= 2 and not is_phone
""", """	var ultra := quality >= 2 and not is_phone
	var gi := light_mode == "live" and ultra
	# (pc117) the baked bounce light, fog and light rays, screen reflections, the film grade
	if baked_gi != null and is_instance_valid(baked_gi):
		baked_gi.visible = light_mode == "baked" and ultra
	if T != null:
		HdLook.fog(env, T, fog_on and ultra)
		HdLook.ssr(env, ssr_on and ultra)
		HdLook.grade(post_mat, T, grade_on)
"""),
    ('"ao_on", "gi_on", "sharpen_on"', '"ao_on", "light_mode", "fog_on", "ssr_on", "marks_on", "grade_on", "sharpen_on"', 2),
    ("""	KartBuilder.stats_on = bool(cf.get_value("opt", "stats_on", true))
""", """	KartBuilder.stats_on = bool(cf.get_value("opt", "stats_on", true))
	if bool(cf.get_value("opt", "gi_on", false)) and not cf.has_section_key("opt", "light_mode"):
		light_mode = "live"   # (pc117) pc116's Bounced light "On"
"""),
    ("""		print("ground: %d finished" % HdGround.upgrade(track, String(_map_info(map_id)["dir"]).path_join(map_id + "_hd.json")))
""", """		print("ground: %d finished" % HdGround.upgrade(track, String(_map_info(map_id)["dir"]).path_join(map_id + "_hd.json")))
		print("road: %d finished" % HdLook.road(track, T))   # (pc117)
"""),
    ("""	env.glow_intensity = float(G.get("bloom", 0.3))
	env.glow_hdr_threshold = 1.6 * float(G.get("thr", 0.94)) / 0.94
	_apply_quality()
""", """	env.glow_intensity = float(G.get("bloom", 0.3))
	env.glow_hdr_threshold = 1.6 * float(G.get("thr", 0.94)) / 0.94
	# (pc117) the baked bounce light, last: everything on the track is in place
	baked_gi = null
	if light_mode == "baked" and quality >= 2 and not is_phone and OS.get_environment("CR_NOGI") != "1":
		baked_gi = HdLook.bake_gi(world, T)
	if fx != null:
		fx.marks_on = marks_on
	_apply_quality()
"""),
])

# ---- post.gdshader: the split-tone
patch('shaders/post.gdshader', [
    ("""uniform float rbw = 0.0;  // Neon Cup tracks: the boost streaks are rainbow (web v168)
""", """uniform float rbw = 0.0;  // Neon Cup tracks: the boost streaks are rainbow (web v168)
uniform float split = 0.0;    // (pc117) Settings > Film grade: the theme's split-tone, shade toward sh_col, light toward hi_col
uniform vec3 sh_col = vec3(1.0);
uniform vec3 hi_col = vec3(1.0);
"""),
    ("""	c = mix(vec3(l), c, sat);
""", """	c = mix(vec3(l), c, sat);
	if (split > 0.001) {
		vec3 tt = mix(sh_col, hi_col, smoothstep(0.03, 0.45, l));
		tt /= max(0.2, dot(tt, vec3(0.2126, 0.7152, 0.0722)));
		c = clamp(c * mix(vec3(1.0), tt, split), 0.0, 1.0);
	}
"""),
])

# ---- fx.gd: tyre marks
patch('scripts/fx.gd', [
    ("""var lite := false
""", """var lite := false
# (pc117) tyre marks: flat dark strips on the road, oldest overwritten first, fading out as they age
const MARKS := 1600
var marks_on := true
var mk_mm: MultiMesh
var mk_node: MultiMeshInstance3D
var mk_next := 0
var mk_n := 0
var mk_t := 0.0
var mk_born := PackedFloat32Array()
var mk_clock := 0.0
"""),
    ("""		rings.append({"m": m, "mat": mat, "t": 0.0, "life": 1.0, "size": 1.0, "flat": true})
""", """		rings.append({"m": m, "mat": mat, "t": 0.0, "life": 1.0, "size": 1.0, "flat": true})
	_marks_init()


func _marks_init() -> void:
	mk_mm = MultiMesh.new()
	mk_mm.transform_format = MultiMesh.TRANSFORM_3D
	mk_mm.use_colors = true
	var pm := PlaneMesh.new()
	pm.size = Vector2(1, 1)
	mk_mm.mesh = pm
	mk_mm.instance_count = MARKS
	mk_mm.visible_instance_count = 0
	mk_born.resize(MARKS)
	mk_node = MultiMeshInstance3D.new()
	mk_node.multimesh = mk_mm
	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = Color(1, 1, 1, 1)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.roughness = 0.75
	mat.render_priority = -1
	mk_node.material_override = mat
	mk_node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mk_node.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	mk_node.extra_cull_margin = 16384.0
	mk_node.custom_aabb = AABB(Vector3(-1e5, -1e5, -1e5), Vector3(2e5, 2e5, 2e5))
	add_child(mk_node)


## one strip of tyre mark from a to b (world), lying on the surface whose up is `up`, `w` wide
func mark(a: Vector3, b: Vector3, up: Vector3, w: float, strength := 1.0) -> void:
	if not marks_on or mk_mm == null:
		return
	var d := b - a
	var ln := d.length()
	if ln < 0.05:
		return
	var u := up.normalized()
	var side := u.cross(d).normalized() * w
	var xf := Transform3D(Basis(d, u, side), (a + b) * 0.5 + u * 0.12)
	var i := mk_next
	mk_next = (mk_next + 1) % MARKS
	mk_n = mini(MARKS, mk_n + 1)
	mk_mm.visible_instance_count = mk_n
	mk_mm.set_instance_transform(i, xf)
	mk_mm.set_instance_color(i, Color(0.05, 0.045, 0.04, 0.55 * strength))
	mk_born[i] = mk_clock


func _marks_fade() -> void:
	# the oldest third fades away before it is overwritten; anything over 40 s old goes too
	for i in mk_n:
		var age := (mk_next - 1 - i + MARKS) % MARKS
		var f := clampf((MARKS - age) / (MARKS * 0.33), 0.0, 1.0) * clampf((40.0 - (mk_clock - mk_born[i])) / 10.0, 0.0, 1.0)
		var c := mk_mm.get_instance_color(i)
		var a0 := minf(c.a, 0.55 * f)
		if a0 != c.a:
			c.a = a0
			mk_mm.set_instance_color(i, c)
"""),
    ("""func step(dt: float) -> void:
	fxa.update(dt)
	fxn.update(dt)
""", """func step(dt: float) -> void:
	fxa.update(dt)
	fxn.update(dt)
	mk_clock += dt
	mk_t += dt
	if mk_t > 0.5 and mk_n > 0:
		mk_t = 0.0
		_marks_fade()
"""),
    ("""	for r in rings:
		var mi: MeshInstance3D = r["m"]
		if mi.visible:
			mi.position = m * mi.position
""", """	for r in rings:
		var mi: MeshInstance3D = r["m"]
		if mi.visible:
			mi.position = m * mi.position
	for i in mk_n:
		mk_mm.set_instance_transform(i, m * mk_mm.get_instance_transform(i))
"""),
    ("""	fxa.clear()
	fxn.clear()
	for r in rings:
		(r["m"] as MeshInstance3D).visible = false
""", """	fxa.clear()
	fxn.clear()
	for r in rings:
		(r["m"] as MeshInstance3D).visible = false
	mk_n = 0
	mk_next = 0
	if mk_mm != null:
		mk_mm.visible_instance_count = 0
"""),
])

# ---- view.gd: lay the marks
patch('scripts/view.gd', [
    ("""	var fxl: Array = v["fxL"]
	var lat := absf(T.lateral(k.idx, k.x, k.y))
""", """	var fxl: Array = v["fxL"]
	_marks(k, v, gt, fxl)   # (pc117)
	var lat := absf(T.lateral(k.idx, k.x, k.y))
"""),
    ("""func _drift_light(k: Kart, v: Dictionary, tier: int) -> void:""", """## (pc117) tyre marks: while a kart drifts or launches hard on the ground, each rear tyre draws a strip from where it was
func _marks(k: Kart, v: Dictionary, gt: Transform3D, fxl: Array) -> void:
	var on := fx.marks_on and not k.air and fxl.size() > 0 and k.z < 0.4 and ((k.drift != 0 and absf(k.speed) > 18.0) or (k.drift == 0 and k.speed > 3.0 and k.speed < 48.0 and k.acc > 30.0))
	if not on:
		v["mk"] = null
		return
	var up := gt.basis.y.normalized()
	var pts: Array = []
	for lv in fxl:
		pts.append(gt * (lv as Vector3))
	var last = v.get("mk")
	if last is Array and (last as Array).size() == pts.size():
		var far := false
		for i in pts.size():
			var dd := ((pts[i] as Vector3) - (last[i] as Vector3)).length()
			if dd > 12.0:
				far = true
		if far:
			v["mk"] = pts
			return
		if ((pts[0] as Vector3) - (last[0] as Vector3)).length() < 1.2:
			return
		for i in pts.size():
			fx.mark(last[i], pts[i], up, 0.9 * KS, 1.0 if k.drift != 0 else 0.7)
	v["mk"] = pts


func _drift_light(k: Kart, v: Dictionary, tier: int) -> void:"""),
])
print('pc117 applied')
