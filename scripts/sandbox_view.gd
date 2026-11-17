extends Node3D
## What Sandbox draws in a place (web tools/mini/sandbox.js: sbCoins, sbFlag, sbGates, sbWarpMat, sbRender):
##   the coins     gold discs turning on the spot (one batch), and the hidden pepperoni coins, bigger, red, with a gold rim
##   the flag      a chequered ring on the road at the start line and a small chequered flag turning above it
##   the passages  an arch on the wall (or in the crust, or over the left-hand lane of a road in the sky) whose face is
##                 the warp picture (streaks flying out of its middle), and a board above it with the name of where it
##                 leads. The tunnel behind an arch is not drawn here: there is one tunnel for the whole game, which
##                 belongs to no place (scripts/sandbox_warp.gd), so that it is still there when this place is not.
## Everything is made here from the numbers in scripts/sandbox.gd (which come from the web's export): no picture files.
## A place travelled to is made on another thread (scripts/world_build.gd): setup() and everything it calls must not
## need the scene tree.
## Loaded by its path from main.gd (no class name: a fresh checkout has no class list yet).

const WARP := """
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, shadows_disabled;
// web sbWarpMat: u_tube 0 a flat face (streaks fly out from the point u_c of its own uv, u_s the size of the picture,
// u_core a bright middle); 1 the inside of a tunnel (uv.x round it, uv.y along it: the streaks run toward the mouth)
uniform float u_t = 0.0;
uniform float u_tube = 0.0;
uniform float u_rep = 1.0;
uniform float u_core = 0.0;
uniform vec2 u_c = vec2(0.5, 0.5);
uniform float u_s = 1.0;
float h1(float n) { return fract(sin(n * 91.345) * 47453.5453); }
vec3 lay(float a, float r, float n, float sd) {
	float b = floor(a * n);
	float f = fract(a * n);
	float id = b + sd * 1000.0;
	float on = step(0.5, h1(id));
	float sp = 0.55 + h1(id + 7.0) * 1.5;
	float ph = fract(r * (1.1 + sd * 0.45) - u_t * sp + h1(id + 3.0));
	float len = 0.22 + 0.5 * h1(id + 11.0);
	float s = smoothstep(0.0, 0.07, ph) * smoothstep(len, len * 0.25, ph);
	float w = smoothstep(0.42, 0.05, abs(f - 0.5));
	float t = h1(id + 5.0);
	vec3 col = t < 0.45 ? vec3(1.0, 0.97, 1.0) : (t < 0.72 ? vec3(0.62, 0.45, 1.0) : (t < 0.9 ? vec3(0.4, 0.6, 1.0) : vec3(0.45, 1.0, 0.7)));
	return col * on * s * w * (0.5 + 0.5 * h1(id + 13.0));
}
void fragment() {
	float a;
	float r;
	float d = 0.0;
	if (u_tube > 0.5) {
		a = UV.x;
		r = UV.y * u_rep;
	} else {
		vec2 p = (UV - u_c) / u_s;
		d = length(p) * 2.0;
		a = atan(p.y, p.x) / 6.2831853 + 0.5;
		r = log(d + 0.03) * 0.6;
	}
	vec3 c = lay(a, r, 70.0, 0.0) + lay(a, r, 120.0, 1.0) + lay(a, r, 190.0, 2.0) * 0.8;
	if (u_tube < 0.5) {
		c *= smoothstep(0.02, 0.3, d);
		c += vec3(0.86, 0.8, 1.0) * u_core * exp(-d * d * 10.0);
	} else {
		c *= 1.15;
	}
	ALBEDO = c + vec3(0.012, 0.006, 0.03);
}
"""

var sb                      # the Sandbox (scripts/sandbox.gd)
var T: TrackData
var time := 0.0
static var _warp: Shader = null     # one for the whole game (made once: a new Shader would be compiled again for every place)
var _face_mats: Array = []          # the mouths' materials: one clock (web SB_WU)
var _wu := 0.0
var _mm: MultiMesh
var _plain: PackedInt32Array = PackedInt32Array()     # the plain coins' numbers in sb's columns
var _rare: Array = []               # [[coin number, its node]]
var _flag: Node3D
const SandboxClock := preload("res://scripts/sandbox_clock.gd")
var clock: SandboxClock = null      # the day and night of this place (scripts/sandbox_clock.gd)
const SandboxNight := preload("res://scripts/sandbox_night.gd")
var night: Node3D = null            # LED strips, street lamps, headlights (scripts/sandbox_night.gd; web v206 / v210)
var _clk_acc := 1.0
var _flag_mats: Array = []          # the start flag's unlit materials: at night they keep half their brightness (web v199)


func _exit_tree() -> void:
	if clock != null:
		clock.off()
		clock = null
	if night != null:
		night.off()
		night = null


## the warp picture's shader (the arches' faces here, and the tunnel's bright end in scripts/sandbox_warp.gd)
static func face_shader() -> Shader:
	if _warp == null:
		var sh := Shader.new()
		sh.code = WARP
		_warp = sh
	return _warp


func setup(sb_, track: TrackData, maps: Array) -> void:
	sb = sb_
	T = track
	face_shader()
	_build_coins()
	if sb.has_flag:
		_build_flag()
	var names := {}
	for m in maps:
		names[String(m["id"])] = String(m.get("name", m["id"]))
	for g in sb.gates:
		_build_gate(g, names)
	if sb.acts != null:
		_build_acts()
	if String(sb.id) == String(sb.SHOP["id"]):
		_build_shop()


# ---------------------------------------------------------------- small helpers

func _std(col: String, rough := 0.7, metal := 0.0, emis := "", e_i := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(col)
	m.roughness = rough
	m.metallic = metal
	if emis != "":
		m.emission_enabled = true
		m.emission = Color(emis)
		m.emission_energy_multiplier = e_i
	return m


func _flat(col: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = col
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m


func _mesh(parent: Node3D, mesh: Mesh, mat: Material, pos := Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
	return mi


func _warp_mat(c := Vector2(0.5, 0.5), s := 1.0, core := 0.0) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = _warp
	m.set_shader_parameter("u_tube", 0.0)
	m.set_shader_parameter("u_c", c)
	m.set_shader_parameter("u_s", s)
	m.set_shader_parameter("u_core", core)
	m.set_shader_parameter("u_rep", 1.0)
	_face_mats.append(m)
	return m


## the outline of an arch: straight sides and a round top (web arch(w, h): the top's middle is at h + .45 w)
func _arch(w: float, h: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var yc := h - w * 0.55
	pts.append(Vector2(-w, 0.0))
	for i in 15:
		var a := PI - PI * float(i) / 14.0
		pts.append(Vector2(cos(a) * w, yc + sin(a) * w))
	pts.append(Vector2(w, 0.0))
	return pts


## a flat mesh filling an outline (its uv is its own x and y, as the web's ShapeGeometry has it)
func _fill(pts: PackedVector2Array) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(1, pts.size() - 1):
		for q in [pts[0], pts[i], pts[i + 1]]:
			st.set_uv(q)
			st.set_normal(Vector3(0, 0, 1))
			st.add_vertex(Vector3(q.x, q.y, 0.0))
	return st.commit()


## the band between two outlines of the same number of points (an arch's frame)
func _band(inner: PackedVector2Array, outer: PackedVector2Array) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in inner.size() - 1:
		for q in [inner[i], outer[i], outer[i + 1], inner[i], outer[i + 1], inner[i + 1]]:
			st.set_normal(Vector3(0, 0, 1))
			st.add_vertex(Vector3(q.x, q.y, 0.0))
	return st.commit()


## flat squares in two colours (the flag's cloth, the ring on the road): each [corner a, b, c, d, dark?]
func _cheq(quads: Array) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for q in quads:
		var col := Color("#141210") if bool(q[4]) else Color("#fbf6ea")
		for v in [q[0], q[1], q[2], q[0], q[2], q[3]]:
			st.set_color(col)
			st.add_vertex(v)
	return st.commit()


func _vcol_mat() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.vertex_color_use_as_albedo = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m


# ---------------------------------------------------------------- the coins (web sbCoins)

func _build_coins() -> void:
	for i in sb.coin_n:
		if sb.coin_rare[i] == 0:
			_plain.append(i)
	# the plain ones: one batch of the detailed coin (web patch 61: rim, reeded edge, a pizza slice on each face), its face along z
	_mm = MultiMesh.new()
	_mm.transform_format = MultiMesh.TRANSFORM_3D
	_mm.mesh = _coin_mesh()
	_mm.instance_count = maxi(1, _plain.size())
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _mm
	var cm := _std("#ffffff", 0.3, 0.85, "#8a5800", 0.45)
	cm.vertex_color_use_as_albedo = true
	mmi.material_override = cm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# (the batch is spread over the whole place: never culled as one box round the first coin)
	mmi.custom_aabb = AABB(Vector3(-20000, -2000, -20000), Vector3(40000, 6000, 40000))
	add_child(mmi)
	if _plain.is_empty():
		_mm.set_instance_transform(0, Transform3D(Basis.from_scale(Vector3.ZERO), Vector3.ZERO))
	_build_coin_shadows()
	# the hidden ones: bigger, a pepperoni face, a gold rim
	var rg := CylinderMesh.new()
	rg.top_radius = 6.4
	rg.bottom_radius = 6.4
	rg.height = 1.2
	rg.radial_segments = 28
	rg.rings = 1
	var rim := TorusMesh.new()
	rim.inner_radius = 5.7
	rim.outer_radius = 7.1
	rim.rings = 28
	rim.ring_segments = 8
	var dot := CylinderMesh.new()
	dot.top_radius = 1.5
	dot.bottom_radius = 1.5
	dot.height = 1.45
	dot.radial_segments = 12
	dot.rings = 1
	var rm := _std("#d8402a", 0.35, 0.35, "#6a1408", 0.7)
	var em := _std("#ffd65a", 0.25, 0.9, "#7a4a00", 0.6)
	var dm := _std("#8f1d10", 0.5)
	var pep_mesh: Mesh = _coin_mesh("coin_pep") if FileAccess.file_exists("res://assets/sandbox/coin_pep.json") else null
	var pep_mat := _std("#ffffff", 0.3, 0.45, "#5a1206", 0.35)
	pep_mat.vertex_color_use_as_albedo = true
	for i in sb.coin_n:
		if sb.coin_rare[i] == 0:
			continue
		var g := Node3D.new()
		# the web's pepperoni coin (patch 63: a gold rim round a pepperoni face, raised slices); the old parts if the file is missing
		if pep_mesh != null:
			_mesh(g, pep_mesh, pep_mat)
		else:
			# (the meshes lie flat; `tip` stands them on edge, so the coin's face looks along its own z)
			var tip := Node3D.new()
			tip.rotation.x = PI / 2.0
			g.add_child(tip)
			_mesh(tip, rg, rm)
			_mesh(tip, rim, em)
			for p in [[-2.0, 1.7], [2.2, 1.2], [0.0, -2.3], [-2.4, -1.5], [2.4, -1.8], [0.3, 3.0]]:
				_mesh(tip, dot, dm, Vector3(float(p[0]), 0.0, -float(p[1])))
		g.position = Vector3(sb.coin_x[i], sb.coin_y[i], sb.coin_z[i])
		add_child(g)
		_rare.append([i, g])


## the coin's shape, the web's own triangles (tools/neon/coinexport.py from sbCoinGeo); a plain disc if the file is missing
func _coin_mesh(file := "coin") -> Mesh:
	var f := FileAccess.open("res://assets/sandbox/%s.json" % file, FileAccess.READ)
	if f == null:
		var disc := CylinderMesh.new()
		disc.top_radius = 4.2
		disc.bottom_radius = 4.2
		disc.height = 0.9
		disc.radial_segments = 22
		var am0 := ArrayMesh.new()
		var a0 := disc.get_mesh_arrays()
		# (stood on edge, the face along z, as the file's coin)
		var pv: PackedVector3Array = a0[Mesh.ARRAY_VERTEX]
		var nv: PackedVector3Array = a0[Mesh.ARRAY_NORMAL]
		var tip := Basis(Vector3.RIGHT, PI / 2.0)
		for i in pv.size():
			pv[i] = tip * pv[i]
			nv[i] = tip * nv[i]
		a0[Mesh.ARRAY_VERTEX] = pv
		a0[Mesh.ARRAY_NORMAL] = nv
		var cv := PackedColorArray()
		cv.resize(pv.size())
		cv.fill(Color("#ffc93a"))
		a0[Mesh.ARRAY_COLOR] = cv
		am0.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, a0)
		return am0
	var d: Dictionary = JSON.parse_string(f.get_as_text())
	var p: Array = d["p"]
	var n: Array = d["n"]
	var c: Array = d["c"]
	var pv2 := PackedVector3Array()
	var nv2 := PackedVector3Array()
	var cv2 := PackedColorArray()
	var k := 0
	while k < p.size():
		# (the web winds counter-clockwise from outside, Godot clockwise: each triangle's last two corners swap)
		for o in [0, 6, 3]:
			pv2.append(Vector3(p[k + o], p[k + o + 1], p[k + o + 2]))
			nv2.append(Vector3(n[k + o], n[k + o + 1], n[k + o + 2]))
			cv2.append(Color(c[k + o], c[k + o + 1], c[k + o + 2]))
		k += 9
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = pv2
	arr[Mesh.ARRAY_NORMAL] = nv2
	arr[Mesh.ARRAY_COLOR] = cv2
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return am


## a soft shadow flat on the ground under each coin, turning with it (web sbCoinShadows): one batch
var _shm: MultiMesh = null
var _sh_of: PackedInt32Array = PackedInt32Array()    # coin number -> its shadow's number, or -1


var _sh_tex: ImageTexture = null
var _meds: Array = []      # [medallion, its shadow] of each mission marker


## the coins' soft shadow (web sbShadowTex): .85 dark at the middle, .55 half way, nothing at the edge
func _shadow_tex() -> ImageTexture:
	if _sh_tex != null:
		return _sh_tex
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in 64:
		for x in 64:
			var r := Vector2(x - 31.5, y - 31.5).length() / 31.0
			var a := 0.0 if r >= 1.0 else (lerpf(0.85, 0.55, r / 0.55) if r < 0.55 else lerpf(0.55, 0.0, (r - 0.55) / 0.45))
			img.set_pixel(x, y, Color(0, 0, 0, a))
	_sh_tex = ImageTexture.create_from_image(img)
	return _sh_tex


func _build_coin_shadows() -> void:
	_sh_of.resize(sb.coin_n)
	var cnt := 0
	for i in sb.coin_n:
		if is_nan(sb.coin_gy[i]):
			_sh_of[i] = -1
		else:
			_sh_of[i] = cnt
			cnt += 1
	if cnt == 0:
		return
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_texture = _shadow_tex()
	m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	m.render_priority = 1
	var q := PlaneMesh.new()
	q.size = Vector2(1, 1)
	_shm = MultiMesh.new()
	_shm.transform_format = MultiMesh.TRANSFORM_3D
	_shm.mesh = q
	_shm.instance_count = cnt
	var mi := MultiMeshInstance3D.new()
	mi.multimesh = _shm
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.custom_aabb = AABB(Vector3(-20000, -2000, -20000), Vector3(40000, 6000, 40000))
	add_child(mi)


# ---------------------------------------------------------------- the start line's marker (web sbFlag)

func _build_flag() -> void:
	var g := Node3D.new()
	g.position = Vector3(float(sb.flag[0]), float(sb.flag[1]), float(sb.flag[2]))
	add_child(g)
	# a chequered ring flat on the road: two bands of 24 squares
	var quads: Array = []
	for i in 24:
		var a0 := float(i) / 24.0 * TAU
		var a1 := float(i + 1) / 24.0 * TAU
		for b in 2:
			var r0 := 11.5 + b * 2.0
			var r1 := r0 + 2.0
			quads.append([Vector3(cos(a0) * r0, 0, sin(a0) * r0), Vector3(cos(a0) * r1, 0, sin(a0) * r1), Vector3(cos(a1) * r1, 0, sin(a1) * r1), Vector3(cos(a1) * r0, 0, sin(a1) * r0), (i + b) % 2 == 0])
	var rm := _vcol_mat()
	_flag_mats.append(rm)
	_mesh(g, _cheq(quads), rm, Vector3(0, 0.55, 0))
	# the flag on its pole, turning
	_flag = Node3D.new()
	_flag.position.y = 12.0
	g.add_child(_flag)
	var pole := CylinderMesh.new()
	pole.top_radius = 0.45
	pole.bottom_radius = 0.45
	pole.height = 17.0
	pole.radial_segments = 8
	_mesh(_flag, pole, _std("#e9e4d8", 0.5, 0.3), Vector3(0, 8.5, 0))
	var cloth: Array = []
	for i in 6:
		for j in 4:
			var x0 := float(i) * 10.0 / 6.0
			var y0 := 13.6 - 3.3 + float(j) * 6.6 / 4.0
			cloth.append([Vector3(x0, y0, 0), Vector3(x0 + 10.0 / 6.0, y0, 0), Vector3(x0 + 10.0 / 6.0, y0 + 6.6 / 4.0, 0), Vector3(x0, y0 + 6.6 / 4.0, 0), (i + j) % 2 == 0])
	var cm := _vcol_mat()
	_flag_mats.append(cm)
	_mesh(_flag, _cheq(cloth), cm)


# ---------------------------------------------------------------- things to do and the Easter egg (web activities.js)

var _egg: Node3D = null
var _egg_y := 0.0
var _signs: Array = []


func _build_acts() -> void:
	for m in sb.acts.marks:
		var kind := String(m["a"]["kind"])
		var col := Color("#e8542f") if kind == "deliver" else (Color("#2fa6e8") if kind == "drift" else Color("#7bd14a"))
		var g := Node3D.new()
		g.position = Vector3(float(m["x"]), float(m["y"]), float(m["z"]))
		add_child(g)
		var tm := TorusMesh.new()
		tm.inner_radius = 13.0
		tm.outer_radius = 16.5
		tm.rings = 40
		var ring := _mesh(g, tm, _flat(col), Vector3(0, 0.6, 0))
		ring.scale = Vector3(1, 0.08, 1)
		# the gold medallion with the mission's icon on both faces, turning and bobbing, with a shadow (web patch 63)
		if FileAccess.file_exists("res://assets/sandbox/coin_act.json"):
			var med := Node3D.new()
			med.position = Vector3(0, 17, 0)
			g.add_child(med)
			var mm := _std("#ffffff", 0.3, 0.85, "#8a5800", 0.4)
			mm.vertex_color_use_as_albedo = true
			_mesh(med, _coin_mesh("coin_act"), mm)
			var ip := "res://assets/sandbox/act_%s.png" % kind
			if FileAccess.file_exists(ip):
				var im := StandardMaterial3D.new()
				im.albedo_texture = ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(ip)))
				im.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
				im.alpha_scissor_threshold = 0.5
				im.roughness = 0.45
				im.metallic = 0.05
				im.emission_enabled = true
				im.emission_texture = im.albedo_texture
				im.emission_energy_multiplier = 0.3
				var q := QuadMesh.new()
				q.size = Vector2(9.6, 9.6)
				for sd in [1.0, -1.0]:
					var d := _mesh(med, q, im, Vector3(0, 0, sd * (0.3 * 1.25 + 0.03)))
					if sd < 0.0:
						d.rotation.y = PI
			var sh := QuadMesh.new()
			sh.size = Vector2(1, 1)
			sh.orientation = PlaneMesh.FACE_Y
			var sm := StandardMaterial3D.new()
			sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			sm.albedo_texture = _shadow_tex()
			sm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
			sm.render_priority = 1
			var shm := _mesh(g, sh, sm, Vector3(0, 0.8, 0))
			shm.scale = Vector3(15, 1, 6)
			_meds.append([med, shm])
		var l := Label3D.new()
		l.text = {"deliver": "PIZZA
DELIVERY", "drift": "DRIFT", "air": "JUMP"}[kind]
		l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		l.font_size = 96
		l.outline_size = 24
		l.modulate = Color("#fff4dc")
		l.outline_modulate = col.darkened(0.35)
		l.pixel_size = 0.05
		l.position = Vector3(0, 27 if FileAccess.file_exists("res://assets/sandbox/coin_act.json") else 17, 0)   # (over the medallion)
		l.no_depth_test = false
		g.add_child(l)
		_signs.append(l)
	if not sb.acts.egg.is_empty():
		var e: Dictionary = sb.acts.egg
		_egg = _egg_model(String(e["id"]))
		_egg.position = Vector3(float(e["x"]), float(e["y"]), float(e["z"]))
		_egg.rotation.y = float(e["ry"])
		_egg_y = float(e["y"])
		add_child(_egg)


## the mechanic's shop: a toy garage playset (web sbShopBuild): base, red walls with a yellow band, blue roof, the sign, tyres, a
## toolbox and a lift inside
## the mechanic's shop: the web's Blender-built workshop (web v205 patch 41, exported by tools/shopexport.py to assets/shop/mshop.glb:
## the building, and the roll-up door at its hinge), a light inside, and the door rolling up as the kart comes at it (_shop_frame).
## Without the file, the old code-built shop (_build_shop_old). Its walls for the kart are sandbox.gd's either way.
var shop_door: Node3D = null
var shop_open := 0.0
var shop_lamp: OmniLight3D = null
var shop_meta := {}


func _build_shop() -> void:
	var S: Dictionary = sb.SHOP
	var ps = load("res://assets/shop/mshop.glb") if ResourceLoader.exists("res://assets/shop/mshop.glb") else null
	if ps == null:
		_build_shop_old()
		return
	var f := FileAccess.open("res://assets/shop/mshop.json", FileAccess.READ)
	shop_meta = JSON.parse_string(f.get_as_text()) if f != null else {}
	var root: Node3D = (ps as PackedScene).instantiate()
	root.position = Vector3(float(S["x"]), 0.0, float(S["z"]))
	add_child(root)
	shop_door = root.find_child("door", true, false) as Node3D
	if shop_door != null:
		var dp: Array = shop_meta.get("door", [0.0, 0.8, 44.0])
		shop_door.position = Vector3(float(dp[0]), float(dp[1]), float(dp[2]))
	shop_lamp = OmniLight3D.new()
	shop_lamp.light_color = Color("#ffe2b8")
	shop_lamp.omni_range = 90.0
	shop_lamp.light_energy = 0.0
	shop_lamp.position = Vector3(float(S["x"]), 34.0, float(S["z"]))
	add_child(shop_lamp)


## each frame: the door rolls up while the kart is at it (or inside), and down once it is away; the light inside comes on with it
func _shop_frame(dt: float, k) -> void:
	if shop_door == null or k == null:
		return
	var S: Dictionary = sb.SHOP
	var fx: float = float(S["x"])
	var fz: float = float(S["z"]) + float(S["d"]) / 2.0
	var near: bool = absf(k.x - fx) < 60.0 and k.y > float(S["z"]) - float(S["d"]) / 2.0 and k.y < fz + 80.0
	shop_open = move_toward(shop_open, 1.0 if near else 0.0, dt / 0.9)
	var e := shop_open * shop_open * (3.0 - 2.0 * shop_open)
	var dh: float = float(shop_meta.get("dh", 30.0))
	var dp: Array = shop_meta.get("door", [0.0, 0.8, 44.0])
	shop_door.position.y = float(dp[1]) + e * dh * 0.92
	shop_door.scale = Vector3(1.0, maxf(0.08, 1.0 - e * 0.92), 1.0)
	shop_lamp.light_energy = 2.2 * e


func _build_shop_old() -> void:
	var S: Dictionary = sb.SHOP
	var G := Node3D.new()
	add_child(G)
	var sx: float = S["x"]
	var sz: float = S["z"]
	var w: float = S["w"]
	var d: float = S["d"]
	var H: float = S["h"]
	var x0 := sx - w / 2.0
	var x1 := sx + w / 2.0
	var z0 := sz - d / 2.0
	var z1 := sz + d / 2.0
	var bx := func(sz3: Vector3, mat: Material, p: Vector3) -> void:
		var bm := BoxMesh.new()
		bm.size = sz3
		var mi := MeshInstance3D.new()
		mi.mesh = bm
		mi.material_override = mat
		mi.position = p
		G.add_child(mi)
	var red := _std("#d8342a", 0.38)
	var yel := _std("#f5c21b", 0.38)
	var blu := _std("#2a5bd7", 0.38)
	var gry := _std("#8d949c", 0.6)
	var flr := _std("#5d636b", 0.55)
	var drk := _std("#2b2f35", 0.7)
	bx.call(Vector3(w + 8.0, 2.0, d + 8.0), gry, Vector3(sx, 1.0, sz))
	bx.call(Vector3(w - 8.0, 0.1, d - 4.0), flr, Vector3(sx, 2.05, sz - 2.0))
	bx.call(Vector3(w, H, 4.0), red, Vector3(sx, H / 2.0 + 2.0, z0 + 2.0))
	for xx in [x0 + 2.0, x1 - 2.0]:
		bx.call(Vector3(4.0, H, d), red, Vector3(xx, H / 2.0 + 2.0, sz))
		bx.call(Vector3(4.6, 5.0, d + 0.6), yel, Vector3(xx, H * 0.62 + 2.0, sz))
	bx.call(Vector3(w + 0.6, 5.0, 4.6), yel, Vector3(sx, H * 0.62 + 2.0, z0 + 2.0))
	bx.call(Vector3(w + 10.0, 4.0, d + 16.0), blu, Vector3(sx, H + 4.0, sz + 4.0))
	bx.call(Vector3(w * 0.88, w * 0.88 / 4.0 + 2.0, 1.2), drk, Vector3(sx, H + 14.0, z1 + 11.4))
	var sgn := Label3D.new()
	sgn.text = "MECHANIC"
	sgn.font_size = 140
	sgn.outline_size = 0
	sgn.modulate = Color("#1b1f26")
	sgn.pixel_size = 0.045
	sgn.position = Vector3(sx, H + 14.0, z1 + 12.2)
	var back := _std("#fbf3df", 0.6)
	bx.call(Vector3(w * 0.84, w * 0.84 / 4.0, 0.4), back, Vector3(sx, H + 14.0, z1 + 12.05))
	G.add_child(sgn)
	var tm := TorusMesh.new()
	tm.inner_radius = 2.6
	tm.outer_radius = 7.4
	for i in 3:
		var t := MeshInstance3D.new()
		t.mesh = tm
		t.material_override = drk
		t.position = Vector3(x0 + 14.0, 4.5 + i * 4.6, z0 + 14.0)
		t.scale = Vector3(1, 0.65, 1)
		G.add_child(t)
	bx.call(Vector3(16, 12, 9), red, Vector3(x1 - 16.0, 8.0, z0 + 10.0))
	bx.call(Vector3(16.4, 2, 9.4), gry, Vector3(x1 - 16.0, 14.6, z0 + 10.0))
	for xx in [sx - 24.0, sx + 24.0]:
		bx.call(Vector3(3, 30, 3), yel, Vector3(xx, 17.0, sz - 14.0))
	bx.call(Vector3(52, 2.4, 3), yel, Vector3(sx, 30.0, sz - 14.0))


## the eggs, as the web builds them (sbEggModel): spheres, cones, boxes and rings in plain materials
func _egg_model(eid: String) -> Node3D:
	var G := Node3D.new()
	var sph := SphereMesh.new()
	sph.radius = 1.0
	sph.height = 2.0
	var add := func(mesh: Mesh, mat: Material, p: Vector3, sc := Vector3.ONE) -> MeshInstance3D:
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.material_override = mat
		mi.position = p
		mi.scale = sc
		G.add_child(mi)
		return mi
	var cone := func(r: float, h: float) -> CylinderMesh:
		var c := CylinderMesh.new()
		c.top_radius = 0.0
		c.bottom_radius = r
		c.height = h
		return c
	var cyl := func(r0: float, r1: float, h: float) -> CylinderMesh:
		var c := CylinderMesh.new()
		c.top_radius = r0
		c.bottom_radius = r1
		c.height = h
		return c
	var box := func(x: float, y: float, z: float) -> BoxMesh:
		var b := BoxMesh.new()
		b.size = Vector3(x, y, z)
		return b
	match eid:
		"duck":
			var y := _std("#ffcf1f", 0.22)
			add.call(sph, y, Vector3(0, 4, 0), Vector3(6, 4.4, 5))
			add.call(sph, y, Vector3(3.6, 8.6, 0), Vector3(3.3, 3.3, 3.3))
			add.call(sph, _std("#ff7a1a", 0.3), Vector3(6.6, 8.3, 0), Vector3(1.8, 0.8, 1.5))
			add.call(sph, y, Vector3(-5, 6, 0), Vector3(2, 2.6, 2.4))
			for sd in [-1.0, 1.0]:
				add.call(sph, _std("#111111", 0.2), Vector3(5.4, 9.6, sd * 1.8), Vector3(0.45, 0.45, 0.45))
		"cat":
			var f := _std("#d98a3c", 0.85)
			add.call(sph, f, Vector3(0, 3.2, 0), Vector3(7, 3.4, 4.6))
			add.call(sph, f, Vector3(6.2, 4.2, 1), Vector3(3.3, 3, 3.2))
			for sd in [-1.0, 1.0]:
				add.call(cone.call(1.2, 2.4), f, Vector3(6.6, 7, 1 + sd * 1.8))
			add.call(sph, _std("#f4e4cc", 0.85), Vector3(8.7, 3.6, 1), Vector3(1.4, 1.1, 1.5))
			var tor := TorusMesh.new()
			tor.inner_radius = 4.0
			tor.outer_radius = 6.0
			var t := add.call(tor, f, Vector3(-2, 1.4, -2.6), Vector3(1, 0.5, 1)) as MeshInstance3D
		"shell":
			var m := _std("#f2c4a8", 0.45)
			for i in 11:
				var r := add.call(cyl.call(0.9, 0.2, 9.0), m, Vector3(sin((i - 5) * 0.27) * 4.5, 1.2, cos((i - 5) * 0.27) * 4.5 - 3)) as MeshInstance3D
				r.rotation = Vector3(PI / 2.0 - 0.25, (i - 5) * 0.27, 0)
			add.call(sph, m, Vector3(0, 1.2, -3.2), Vector3(2.2, 1.2, 1.6))
		"snowman":
			var w := _std("#f7f9ff", 0.9)
			add.call(sph, w, Vector3(0, 4, 0), Vector3(4, 4, 4))
			add.call(sph, w, Vector3(0, 10, 0), Vector3(3, 3, 3))
			add.call(sph, w, Vector3(0, 14.6, 0), Vector3(2.1, 2.1, 2.1))
			var n := add.call(cone.call(0.5, 3.0), _std("#ff7a1a"), Vector3(0, 14.6, 2.6)) as MeshInstance3D
			n.rotation.x = PI / 2.0
			for x in [-0.8, 0.8]:
				add.call(sph, _std("#111111"), Vector3(x, 15.3, 1.8), Vector3(0.32, 0.32, 0.32))
			add.call(cyl.call(2.3, 2.3, 0.5), _std("#222222"), Vector3(0, 16.4, 0))
			add.call(cyl.call(1.5, 1.5, 2.4), _std("#222222"), Vector3(0, 17.8, 0))
		"robot":
			var b := _std("#9aa3ad", 0.35, 0.7)
			add.call(box.call(6, 6, 4.4), b, Vector3(0, 6, 0))
			add.call(box.call(4.6, 3.6, 3.6), b, Vector3(0, 11, 0))
			for x in [-1.1, 1.1]:
				add.call(sph, _std("#111111", 0.5, 0.0, "#39d0ff", 2.2), Vector3(x, 11.3, 1.85), Vector3(0.6, 0.6, 0.3))
			add.call(cyl.call(0.18, 0.18, 2.4), b, Vector3(0, 14, 0))
			add.call(sph, _std("#ff4b6e", 0.5, 0.0, "#ff4b6e", 2.0), Vector3(0, 15.3, 0), Vector3(0.55, 0.55, 0.55))
			for x in [-1.6, 1.6]:
				add.call(box.call(1.4, 3, 2), b, Vector3(x, 1.5, 0))
		"meatball":
			add.call(sph, _std("#6e3420", 0.95), Vector3(0, 5, 0), Vector3(5, 5, 5))
			for i in 6:
				add.call(sph, _std("#3f8a2e"), Vector3(cos(i) * 3.6, 7.4 + sin(i * 3) * 1.2, sin(i) * 3.6), Vector3(0.9, 0.25, 0.6))
		"wrench":
			var st := _std("#c9ced4", 0.25, 0.9)
			add.call(box.call(16, 0.9, 2.2), st, Vector3(0, 0.6, 0))
			for x in [-8.6, 8.6]:
				var tor2 := TorusMesh.new()
				tor2.inner_radius = 1.2
				tor2.outer_radius = 3.0
				add.call(tor2, st, Vector3(x, 0.6, 0), Vector3(1, 0.4, 1))
		"gnome":
			add.call(sph, _std("#2f5fb0"), Vector3(0, 4, 0), Vector3(3.4, 4, 3.4))
			add.call(sph, _std("#f1c7a0"), Vector3(0, 9, 0), Vector3(2.4, 2.4, 2.4))
			add.call(cone.call(2.6, 7.0), _std("#d6302a"), Vector3(0, 13.6, 0))
			var bd := add.call(cone.call(2.3, 4.0), _std("#f4f4f0", 0.9), Vector3(0, 6.6, 1.7)) as MeshInstance3D
			bd.rotation.x = PI
			add.call(sph, _std("#e88c7a"), Vector3(0, 8.6, 2.3), Vector3(0.8, 0.8, 0.8))
			for x in [-1.6, 1.6]:
				add.call(box.call(1.8, 1.2, 3), _std("#4a2c18"), Vector3(x, 0.6, 0.6))
	return G


# ---------------------------------------------------------------- the passages (web sbGates, the drawing half)

func _sign(parent: Node3D, text: String, bw: float, bh: float, neon: bool, wood: String, pos: Vector3) -> void:
	var b := Node3D.new()
	b.position = pos
	parent.add_child(b)
	var back := BoxMesh.new()
	back.size = Vector3(bw + 2.4, bh + 2.4, 1.6)
	_mesh(b, back, _std("#0c1822", 0.4, 0.0, "#39d0ff", 0.9) if neon else _std(wood, 0.75))
	var font: Font = ThemeDB.fallback_font
	for s in [1.0, -1.0]:
		# (its face is not shaded: a sign in a dark corner of a room reads as well as one in the sun)
		var side := Node3D.new()
		side.position.z = s * 0.9
		if s < 0.0:
			side.rotation.y = PI
		b.add_child(side)
		var edge := QuadMesh.new()
		edge.size = Vector2(bw, bh)
		_mesh(side, edge, _flat(Color("#39d0ff") if neon else Color("#5a3d22")))
		var face := QuadMesh.new()
		face.size = Vector2(bw * 0.965, bh * 0.86)
		_mesh(side, face, _flat(Color("#06121c") if neon else Color("#f6ecd4")), Vector3(0, 0, 0.05))
		# the name, as large as fits between the two arrows
		var lab := Label3D.new()
		lab.text = text
		lab.font_size = 96
		lab.outline_size = 0
		lab.shaded = false
		lab.double_sided = false
		lab.modulate = Color("#bff1ff") if neon else Color("#3a2513")
		var tw := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 96).x
		lab.pixel_size = minf(bw * 0.78 / maxf(1.0, tw), bh * 0.58 / 96.0)
		lab.position = Vector3(0, 0, 0.12)
		side.add_child(lab)
		for sd in [-1.0, 1.0]:
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			var ax: float = sd * bw * 0.451
			var ah := bh * 0.165
			for v in [Vector3(ax, ah, 0), Vector3(ax + bw * 0.025, -ah, 0), Vector3(ax - bw * 0.025, -ah, 0)]:
				st.add_vertex(v)
			_mesh(side, st.commit(), _flat(Color("#39d0ff") if neon else Color("#b4472a")), Vector3(0, 0, 0.1))


func _build_gate(g: Dictionary, names: Dictionary) -> void:
	var road: bool = g["road"]
	var room: bool = sb.toy and sb.id != "backyard"   # one of the three rooms (web R.room): its wall has a skirting board the arch stands proud of
	var proud := 6.0 if room else 0.0
	var G := Node3D.new()
	G.position = Vector3(float(g["x"]), float(g["y"]), float(g["z"]))
	G.rotation.y = atan2(-float(g["nx"]), -float(g["nz"]))   # its face looks back at whoever drives up to it
	add_child(G)
	var W: float = float(g["hw"]) + 1.0
	var H := 31.0 if road else 27.0
	var neon := road and T.neon
	var wood := "#7a5636" if room else ("#a9743c" if sb.kind == "open" else "#5d5148")
	var label := String(g.get("label", String(names.get(String(g["to"]), g["to"])).to_upper()))
	if bool(g["plain"]):
		# the garage's open door: a gantry you drive out under
		var bw := 150.0
		var bh := 37.5
		_sign(G, label, bw, bh, neon, wood, Vector3(0, 66, -14))
		for s in [-1.0, 1.0]:
			var post := CylinderMesh.new()
			post.top_radius = 2.2
			post.bottom_radius = 2.6
			post.height = 84.0
			post.radial_segments = 10
			_mesh(G, post, _std("#4a4d52", 0.5, 0.4), Vector3(s * (bw / 2.0 + 4.0), 42, -14))
	else:
		var inner := _arch(W, H)
		_mesh(G, _fill(inner), _warp_mat(Vector2(0.0, H * 0.46), H * 1.05, 0.5), Vector3(0, 0, proud + (1.2 if room else 0.9)))
		var fm: StandardMaterial3D = _std("#12202c", 0.4, 0.0, "#39d0ff", 1.6) if neon else _std(wood, 0.7)
		fm.cull_mode = BaseMaterial3D.CULL_DISABLED
		_mesh(G, _band(inner, _arch(W + 3.4, H + 3.4)), fm, Vector3(0, 0, proud + 0.2))
		# the board stands on two posts well above the arch and in front of it, where neither the arch's own rim nor the
		# kart in front of the camera is across it
		var bw2 := maxf(2.0 * W + 40.0, 84.0)
		var bh2 := bw2 / 4.0
		var by := H + 17.0 + bh2 / 2.0
		var bz := proud + 5.0
		_sign(G, label, bw2, bh2, neon, wood, Vector3(0, by, bz))
		for sd in [-1.0, 1.0]:
			var pm := BoxMesh.new()
			pm.size = Vector3(2.2, by - H + 2.0, 2.2)
			_mesh(G, pm, _std("#12202c", 0.4, 0.0, "#39d0ff", 1.2) if neon else _std(wood, 0.75), Vector3(sd * (W + 1.5), (by + H - 2.0) / 2.0, bz - 1.3))


# ---------------------------------------------------------------- each frame (web sbRender, sbWarpTick)

func _process(dt: float) -> void:
	if sb == null:
		return
	var mn := get_parent()
	if mn != null and bool(mn.get("paused")):
		return
	time += dt
	var ct: PackedFloat32Array = sb.coin_t
	var cx: PackedFloat32Array = sb.coin_x
	var cy: PackedFloat32Array = sb.coin_y
	var cz: PackedFloat32Array = sb.coin_z
	# the coins turn; a taken one is not drawn until it is back
	for q in _plain.size():
		var i := _plain[q]
		var a := time * 2.6 + float(i) * 0.37
		var s := 0.0 if ct[i] > 0.0 else 1.0
		# (the coin stands on edge as made, its face along z: turned about the upright)
		var b := Basis(Vector3.UP, a)
		_mm.set_instance_transform(q, Transform3D(b.scaled(Vector3(s, s, s)), Vector3(cx[i], cy[i], cz[i])))
	# the mission medallions turn and bob, their shadows with them (web patch 63)
	for md in _meds:
		(md[0] as Node3D).rotation.y = time * 1.4
		(md[0] as Node3D).position.y = 17.0 + sin(time * 2.0) * 0.8
		(md[1] as Node3D).rotation.y = time * 1.4
	# the shadows turn with their coins; gone while the coin is (web patch 61)
	if _shm != null:
		var gy: PackedFloat32Array = sb.coin_gy
		for i3 in sb.coin_n:
			var si := _sh_of[i3]
			if si < 0:
				continue
			var a3 := time * 2.6 + float(i3) * 0.37
			var big := 1.5 if sb.coin_rare[i3] != 0 else 1.0
			var bob := 1.0 - sin(time * 2.0 + float(i3) * 0.37) * 0.04 if sb.coin_rare[i3] != 0 else 1.0
			var on := 1.0 if ct[i3] == 0.0 else 0.0
			# (scaled in its own frame, long across the coin's face, so it turns with the coin)
			var sb3 := Basis(Vector3.UP, a3) * Basis.from_scale(Vector3(9.5 * big * bob * on, 1.0, 3.8 * big * bob * on))
			_shm.set_instance_transform(si, Transform3D(sb3, Vector3(cx[i3], gy[i3] + 0.3, cz[i3])))
	for r in _rare:
		var i2: int = r[0]
		var n: Node3D = r[1]
		var vis: bool = sb.coin_t[i2] >= 0.0
		if n.visible != vis:
			n.visible = vis
		if vis:
			n.rotation.y = time * 2.6 + float(i2) * 0.37
			n.position.y = sb.coin_y[i2] + sin(time * 2.0 + float(i2) * 0.37) * 0.8
	# the clock's light, ten times a second, once the place is the one being driven and the kart is out of any tunnel
	_clk_acc += dt
	if _clk_acc >= 0.1 and mn != null and is_inside_tree():
		_clk_acc = 0.0
		var kk = mn.get("kart")
		if kk != null and kk.tun == null and mn.get("env") != null:
			if clock == null:
				clock = SandboxClock.new()
				clock.arm(mn, T, String(sb.id))
			if night == null:
				night = SandboxNight.new()
				add_child(night)
				night.arm(mn, T, String(sb.id), clock.kind)
			clock.apply(float(sb.save.get("t", 0.4)))
			if _flag_mats.size() > 0:
				var Fd: Dictionary = SandboxClock.f(float(sb.save.get("t", 0.4)))
				var kf := 0.5 + 0.5 * float(Fd["D"])
				for m in _flag_mats:
					(m as BaseMaterial3D).albedo_color = Color(kf, kf, kf)
	# the night's lights follow the kart every frame (the clock sets their level)
	if night != null and mn != null:
		night.frame(dt, float(SandboxClock.f(float(sb.save.get("t", 0.4)))["L"]), mn.get("kart"))
	if shop_door != null and mn != null:
		_shop_frame(dt, mn.get("kart"))
	# the egg hops when found
	if _egg != null and sb.acts != null and not sb.acts.egg.is_empty():
		var hop := float(sb.acts.egg["hop"])
		_egg.position.y = _egg_y + sin((1.0 - hop / 0.8) * PI) * 7.0 if hop > 0.0 else _egg_y
		if hop > 0.0:
			_egg.rotation.y += dt * 9.0
	if _flag != null:
		_flag.rotation.y = time * 1.6
		_flag.position.y = 12.0 + sin(time * 2.2) * 1.2
	# the arches' faces: their clock
	_wu = fmod(_wu + dt * 0.5, 1000.0)
	for m in _face_mats:
		(m as ShaderMaterial).set_shader_parameter("u_t", _wu)


# ---------------------------------------------------------------- the cover over a load (web sbCover, #sbDuct)

## The cover over fast travel from the map: dark, with light streaks flying out of its middle. The next place is built
## on another thread, so the streaks keep moving for the whole of the load; then the cover fades over the new place.
## (A journey through a gate has no cover at all: the kart drives the tunnel, scripts/sandbox_warp.gd.)
class Cover extends Control:
	var t := 0.0
	var a := 0.0            # how solid it is: 1 while it covers, fading to 0
	var fading := false
	var c := Vector2(0.5, 0.46)
	var _st: Array = []     # the streaks: [angle, r0, r1, colour, width, phase]

	func _init() -> void:
		var rng := RandomNumberGenerator.new()
		rng.seed = 4711
		var cols := [Color(1, 0.97, 1), Color(0.63, 0.46, 1), Color(0.43, 0.63, 1), Color(0.47, 1, 0.73)]
		for i in 220:
			var tt := rng.randf()
			var r0 := 0.1 + rng.randf() * 0.5
			_st.append([rng.randf() * TAU, r0, minf(1.0, r0 + 0.08 + rng.randf() * 0.34), cols[0 if tt < 0.45 else (1 if tt < 0.72 else (2 if tt < 0.9 else 3))], 0.8 + rng.randf() * 2.4, rng.randf()])
		visible = false
		process_mode = Node.PROCESS_MODE_ALWAYS

	func show_at(at: Vector2) -> void:
		c = at
		a = 1.0
		fading = false
		visible = true
		queue_redraw()

	func fade() -> void:
		fading = true

	func _process(dt: float) -> void:
		if not visible:
			return
		t += dt
		if fading:
			a -= dt / 0.5
			if a <= 0.0:
				a = 0.0
				visible = false
		queue_redraw()

	func _draw() -> void:
		var sz := size
		draw_rect(Rect2(Vector2.ZERO, sz), Color(0.02, 0.012, 0.04, a))
		var m := maxf(sz.x, sz.y)
		var o := Vector2(c.x * sz.x, c.y * sz.y)
		for s in _st:
			# each streak flies outward and grows, then starts again (web @keyframes sbwarp: scale .18 to 4.2 in 1.05 s)
			var ph := fposmod(t / 1.05 + float(s[5]), 1.0)
			var sc := lerpf(0.18, 4.2, ph) * m * 0.5
			var op := (ph / 0.14) if ph < 0.14 else (1.0 - 0.15 * (ph - 0.14) / 0.61 if ph < 0.75 else 0.85 * (1.0 - (ph - 0.75) / 0.25))
			var d := Vector2(cos(float(s[0])), sin(float(s[0])))
			var col: Color = s[3]
			var p0 := o + d * float(s[1]) * sc
			var p1 := o + d * float(s[2]) * sc
			var al := clampf(op, 0.0, 1.0) * a * 0.9
			# (faint at both ends, brightest most of the way out, as the web's streaks are painted)
			draw_polyline_colors(PackedVector2Array([p0, p0.lerp(p1, 0.7), p1]), PackedColorArray([Color(col.r, col.g, col.b, 0.0), Color(col.r, col.g, col.b, al), Color(col.r, col.g, col.b, 0.0)]), float(s[4]) * (1.0 + ph * 2.0), true)
