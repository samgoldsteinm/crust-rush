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
	# the plain ones: one batch of gold discs standing on edge
	var disc := CylinderMesh.new()
	disc.top_radius = 4.2
	disc.bottom_radius = 4.2
	disc.height = 0.9
	disc.radial_segments = 22
	disc.rings = 1
	_mm = MultiMesh.new()
	_mm.transform_format = MultiMesh.TRANSFORM_3D
	_mm.mesh = disc
	_mm.instance_count = maxi(1, _plain.size())
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _mm
	mmi.material_override = _std("#ffc93a", 0.28, 0.85, "#a86a00", 0.9)
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# (the batch is spread over the whole place: never culled as one box round the first coin)
	mmi.custom_aabb = AABB(Vector3(-20000, -2000, -20000), Vector3(40000, 6000, 40000))
	add_child(mmi)
	if _plain.is_empty():
		_mm.set_instance_transform(0, Transform3D(Basis.from_scale(Vector3.ZERO), Vector3.ZERO))
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
	for i in sb.coin_n:
		if sb.coin_rare[i] == 0:
			continue
		var g := Node3D.new()
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
	_mesh(g, _cheq(quads), _vcol_mat(), Vector3(0, 0.55, 0))
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
	_mesh(_flag, _cheq(cloth), _vcol_mat())


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
		# (the disc lies flat as made: stood on edge, then turned about the upright)
		var b := Basis(Vector3.UP, a) * Basis(Vector3.RIGHT, PI / 2.0)
		_mm.set_instance_transform(q, Transform3D(b.scaled(Vector3(s, s, s)), Vector3(cx[i], cy[i], cz[i])))
	for r in _rare:
		var i2: int = r[0]
		var n: Node3D = r[1]
		var vis: bool = sb.coin_t[i2] >= 0.0
		if n.visible != vis:
			n.visible = vis
		if vis:
			n.rotation.y = time * 2.6 + float(i2) * 0.37
			n.position.y = sb.coin_y[i2] + sin(time * 2.0 + float(i2) * 0.37) * 0.8
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
