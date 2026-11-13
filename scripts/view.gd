class_name View
extends Node3D
## Draws the race the way the web game does (its syncKart, item, item-box and trap drawing, and the
## effects its simulation fires: spin-outs, box pickups, item use, shields, explosions, wall sparks).
## Drawing only: nothing here changes the race.

const SPARKC := [Color("#fff1c8"), Color("#ffc62e"), Color("#ff1f12"), Color("#8fe0ff")]
const FLAMEC := [[Color("#ff7a1a"), Color("#fff0a0")], [Color("#ffb51a"), Color("#fff6b8")], [Color("#ff0c06"), Color("#ff5a3c")], [Color("#2f8cff"), Color("#d2f4ff")]]
const ITEM_GLOW := {"pep": Color("#ff5a2a"), "dough": Color("#ffe2a0"), "lob": Color("#c9e86a"), "oil": Color("#e8b23a"), "flour": Color("#ffffff"), "wheel": Color("#ff3b1a")}
const TRAIL := {"pep": Color("#ff7a3a"), "dough": Color("#ffe2a0"), "lob": Color("#c9e86a"), "flour": Color("#ffffff"), "torp": Color("#9fd8ff"), "meat2": Color("#c8784a"), "bomb": Color("#ffcc33"), "twist": Color("#f3dfb4")}
const ITEM_COL := {"chili": Color("#ff5a1a"), "pepperoni": Color("#ff6a3a"), "oil": Color("#e8c040"), "dough": Color("#ffe2a0"), "trio": Color("#ff6a3a"), "garlic": Color("#e8fff0"), "flour": Color("#ffffff"), "wheel": Color("#ff3b1a"), "rush": Color("#7fe8ff"), "freezer": Color("#bfe6ff")}
const FLY_SC := {"pep": 1.4, "dough": 1.25, "torp": 1.2, "lob": 1.1, "meat2": 1.0}
const HITC := {"flour": ["#ffffff", "#f6f1e6", "#e9dfc8"], "wheel": ["#ff3b1a", "#ffe066", "#ffffff"], "garlic": ["#7fe07a", "#f4ecdc", "#ffffff"], "pep": ["#ff3b1a", "#b8311c", "#ffe066", "#fff4dc"], "dough": ["#fff4dc", "#f3dfb4", "#ffe066"], "oil": ["#ffd24a", "#e0b22a", "#fff2b0"], "lob": ["#ffd24a", "#e0b22a", "#fff2b0"]}
const TRICKS := [[Vector3(0, 0, 1), 1.0], [Vector3(0, 1, 0), 1.0], [Vector3(0, 0, 1), -1.0], [Vector3(1, 0, 0), -1.0], [Vector3(1, 0, 0), 1.0]]
const PROJ_NODE := {"pep": "pep", "dough": "dough", "flour": "flour", "lob": "lob", "wheel": "wheel", "torp": "torpedo", "meat2": "meatball", "bomb": "bomb", "twist": "twister"}
## traps on the road: which model, how much bigger it is drawn, and its glow (web hazDecorate)
const TRAP := {"oil": ["oil", 1.2, "#ffd23a", 16.0, 4.5], "olive": ["oil", 1.2, "#ffd23a", 16.0, 4.5], "forks": ["forks", 1.9, "#d8ecff", 13.0, 4.5], "boxes": ["boxes", 1.3, "#ffb040", 16.0, 6.0]}
const HELD_NODE := {"pepperoni": "pep", "dough": "dough", "flour": "flour"}

var T: TrackData
var race: Race
var fx: Fx
var cam: Camera3D
var me: Kart
var items_lib: Node3D
var kart_scenes := {}
var views := {}          # Kart -> Dictionary
var box_nodes: Array = []
var proj_nodes := {}     # id -> {n, age, sp, roll, halo, type}
var pops: Array = []     # {n, t, s}
var haz_nodes := {}      # id -> {n, ring, warn}
var whaz := {"traffic": [], "rollers": [], "walk": [], "wagons": []}   # the world's moving hazards
var pad_nodes: Array = []
var ring_nodes: Array = []   # the glide's boost rings (web GLIDE.rings meshes; the track export leaves them out)
var time := 0.0
var KS := 1.76

var fan_mesh: ArrayMesh
var bubble_mat: ShaderMaterial
var rush_mat: ShaderMaterial
var glow_mats := {}
var flame_meshes: Array = []
var ring_mat_n: StandardMaterial3D
var ring_mat_d: StandardMaterial3D
var box_glow_mat: StandardMaterial3D
var warn_tex: Texture2D
var haz_ring_mat: StandardMaterial3D
var mozz_mat: StandardMaterial3D
var mozz_mesh: SphereMesh
var fire_mat: StandardMaterial3D
var fire_in_mat: StandardMaterial3D


func setup(track: TrackData, r: Race, f: Fx, camera: Camera3D, items: Node3D) -> void:
	T = track
	race = r
	fx = f
	cam = camera
	items_lib = items
	KS = T.KS
	me = race.player
	_shared()


func _shared() -> void:
	if fan_mesh != null:
		return
	# the spark fan: two crossed triangles, white at the tyre fading out at the tip (web FANG)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for tri in [[Vector3(0, -0.5, 0), Vector3(0, 0.5, 0), Vector3(1, 0, 0)], [Vector3(0, 0, -0.5), Vector3(0, 0, 0.5), Vector3(1, 0, 0)]]:
		for i in 3:
			st.set_color(Color(1, 1, 1, 0.0 if i == 2 else 1.0))
			st.add_vertex(tri[i])
	fan_mesh = st.commit()
	bubble_mat = ShaderMaterial.new()
	bubble_mat.shader = load("res://shaders/bubble.gdshader")
	bubble_mat.set_shader_parameter("c1", Color("#6fe06a"))
	bubble_mat.set_shader_parameter("c2", Color("#eaffd8"))
	rush_mat = ShaderMaterial.new()
	rush_mat.shader = bubble_mat.shader
	rush_mat.set_shader_parameter("c1", Color("#ff8a1f"))
	rush_mat.set_shader_parameter("c2", Color("#ffe39a"))
	# boost flames: open cones (web KG.flame / KG.flameIn)
	for spec in [[0.55, 2.6, 16], [0.3, 1.7, 12]]:
		var cm := CylinderMesh.new()
		cm.top_radius = 0.0
		cm.bottom_radius = spec[0]
		cm.height = spec[1]
		cm.radial_segments = spec[2]
		cm.rings = 1
		cm.cap_top = false
		cm.cap_bottom = false
		flame_meshes.append(cm)
	ring_mat_n = _basic(Color("#ffe9a0"), 0.9)
	ring_mat_d = _basic(Color("#ffd24a"), 0.95)
	box_glow_mat = _glow_mat(Color("#ffd24a"), 0.5, true)
	haz_ring_mat = _basic(Color("#ffe02a"), 0.95)
	warn_tex = _warn_texture()
	# Melt Shield: a stretchy mozzarella ball per hit it can still take (web bub.userData.mz)
	mozz_mat = StandardMaterial3D.new()
	mozz_mat.albedo_color = Color("#fbf5e6")
	mozz_mat.roughness = 0.35
	mozz_mat.emission_enabled = true
	mozz_mat.emission = Color("#fff2cf")
	mozz_mat.emission_energy_multiplier = 0.18
	mozz_mesh = SphereMesh.new()
	mozz_mesh.radius = 1.15
	mozz_mesh.height = 2.3
	mozz_mesh.radial_segments = 18
	mozz_mesh.rings = 12
	# Fire Trail flames on the road (web flameMat / flameInMat: additive, not tone mapped)
	fire_mat = _basic(Color("#ff7a1a"), 0.85)
	fire_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	fire_mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	fire_in_mat = _basic(Color("#fff0a0"), 0.95)
	fire_in_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	fire_in_mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED


static func _basic(col: Color, op: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(col.r, col.g, col.b, op)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.disable_fog = true
	return m


func _glow_mat(col: Color, op: float, flat := false) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_texture = fx.glow_tex
	m.albedo_color = Color(col.r, col.g, col.b, op)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.disable_fog = true
	if not flat:
		m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	return m


## a glowing sprite (web glowMat + Sprite), one shared material per colour
func _halo(col: Color, size: float) -> MeshInstance3D:
	var key := col.to_html()
	if not glow_mats.has(key):
		glow_mats[key] = _glow_mat(col, 0.55)
	var q := QuadMesh.new()
	q.size = Vector2(1, 1)
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.material_override = glow_mats[key]
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.scale = Vector3.ONE * size
	return mi


static func _warn_texture() -> ImageTexture:
	# the web's hazard sign: a dark-edged yellow triangle with an exclamation mark
	var S := 128
	var img := Image.create(S, S, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var dark := Color("#1a0d06")
	var yel := Color("#ffd21f")
	var tri := func(inset: float, px: float, py: float) -> bool:
		var ax := 64.0
		var ay := 10.0 + inset
		var bx := 120.0 - inset * 1.15
		var by := 112.0 - inset * 0.6
		var cx := 8.0 + inset * 1.15
		var cy := 112.0 - inset * 0.6
		var d1 := (px - bx) * (ay - by) - (ax - bx) * (py - by)
		var d2 := (px - cx) * (by - cy) - (bx - cx) * (py - cy)
		var d3 := (px - ax) * (cy - ay) - (cx - ax) * (py - ay)
		var neg := d1 < 0 or d2 < 0 or d3 < 0
		var pos := d1 > 0 or d2 > 0 or d3 > 0
		return not (neg and pos)
	for y in S:
		for x in S:
			var px := x + 0.5
			var py := y + 0.5
			var c := Color(0, 0, 0, 0)
			# outline: the triangle grown by ~5px
			var near := false
			for o in [Vector2(0, 0), Vector2(5, 0), Vector2(-5, 0), Vector2(0, 5), Vector2(0, -5), Vector2(3.5, 3.5), Vector2(-3.5, 3.5), Vector2(3.5, -3.5), Vector2(-3.5, -3.5)]:
				if tri.call(0.0, px + o.x, py + o.y):
					near = true
					break
			if near:
				c = dark
			if tri.call(10.0, px, py):
				c = yel
			if (px >= 57 and px <= 71 and py >= 42 and py <= 82) or Vector2(px - 64, py - 95).length() <= 8.0:
				if c.a > 0:
					c = dark
			img.set_pixel(x, y, c)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


## Godot's glTF import leaves vertex colours off; most paint and scenery colour lives in them
static func vertex_colours(root: Node) -> int:
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var am := (node as MeshInstance3D).mesh as ArrayMesh
		if am == null:
			continue
		for si in am.get_surface_count():
			var sm := am.surface_get_material(si) as StandardMaterial3D
			if sm != null and (am.surface_get_format(si) & Mesh.ARRAY_FORMAT_COLOR) != 0 and not sm.vertex_color_use_as_albedo:
				sm.vertex_color_use_as_albedo = true
				n += 1
	return n


func item_node(name_: String) -> Node3D:
	var n3 := Node3D.new()
	if items_lib != null:
		var src := items_lib.find_child(name_, true, false)
		if src != null:
			var c := src.duplicate() as Node3D
			c.transform = Transform3D.IDENTITY
			n3.add_child(c)
	return n3


# ---------------------------------------------------------------- karts

func add_kart(k: Kart, sc_file_loader: Callable) -> void:
	var info: Dictionary = k.info
	var meta: Dictionary = info.get("meta", {})
	var g := Node3D.new()
	add_child(g)
	var tilt := Node3D.new()
	g.add_child(tilt)
	var model: Node3D
	var glider: Node3D = null
	if info.has("spec") and KartBuilder.ready():
		# a garage build: assembled from parts, painted for its paint or livery
		var built := KartBuilder.build(info["spec"], k.ri)
		model = built["node"]
		glider = built["glider_node"]
		tilt.add_child(model)
		if glider != null:
			tilt.add_child(glider)
	else:
		var file := String(info.get("file", "player.glb"))
		var ps: PackedScene = sc_file_loader.call(file)
		model = ps.instantiate()
		tilt.add_child(model)
		vertex_colours(model)
	var sc := float(meta.get("scale", KS))
	g.scale = Vector3.ONE * sc
	var wheels: Array = []
	for w in meta.get("wheels", []):
		var wd: Dictionary = w
		var wn := model.find_child(String(wd["name"]), true, false) as Node3D
		if wn:
			wheels.append({"node": wn, "r": float(wd["r"]), "front": bool(wd["front"])})
	# flames, hidden until a boost
	var flames: Array = []
	for f in meta.get("flames", []):
		var fd: Dictionary = f
		var inner := bool(fd.get("inner", false))
		var mi := MeshInstance3D.new()
		mi.mesh = flame_meshes[1 if inner else 0]
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		m.disable_fog = true
		m.albedo_color = Color(1, 0.5, 0.1, 0.95 if inner else 0.85)
		mi.material_override = m
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.rotation = Vector3(0, 0, PI / 2.0)
		mi.position = Vector3(float(fd["x"]), float(fd["y"]), float(fd["z"]))
		mi.visible = false
		tilt.add_child(mi)
		var fl = fd.get("fl")
		flames.append({"mi": mi, "mat": m, "inner": inner, "fl": fl})
	# garlic shield / rush aura bubble, with a garlic clove per layer orbiting inside
	var bub := MeshInstance3D.new()
	var sp := SphereMesh.new()
	sp.radius = 6.4
	sp.height = 12.8
	sp.radial_segments = 28
	sp.rings = 18
	bub.mesh = sp
	bub.material_override = bubble_mat
	bub.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var bd: Dictionary = meta.get("bub", {"x": 0.0, "y": 3.5, "z": 0.0, "s": 1.0}) if meta.get("bub") != null else {"x": 0.0, "y": 3.5, "z": 0.0, "s": 1.0}
	bub.position = Vector3(float(bd["x"]), float(bd["y"]), float(bd["z"]))
	bub.scale = Vector3.ONE * float(bd["s"])
	bub.visible = false
	g.add_child(bub)
	var cloves: Array = []
	for i in 2:
		var c := item_node("clove")
		var a := float(i) / 2.0 * TAU
		c.position = Vector3(cos(a) * 5.3, sin(a * 2.0) * 1.2, sin(a) * 5.3)
		c.rotation = Vector3(0.5, a, 0.3)
		c.scale = Vector3.ONE * 1.25
		bub.add_child(c)
		cloves.append(c)
	var mz := Node3D.new()
	for i in 3:
		var am := float(i) / 3.0 * TAU
		var mb := MeshInstance3D.new()
		mb.mesh = mozz_mesh
		mb.material_override = mozz_mat
		mb.position = Vector3(cos(am) * 5.6, sin(am * 3.0) * 1.0, sin(am) * 5.6)
		mb.scale = Vector3(1.0, 0.85, 1.0)
		mb.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mz.add_child(mb)
	mz.visible = false
	bub.add_child(mz)
	# Freezer Blast: a block of ice (web m.ice)
	var ice := item_node("icebox")
	ice.position = bub.position
	ice.visible = false
	g.add_child(ice)
	# drift spark fans at the back wheels
	var fan := MultiMeshInstance3D.new()
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = fan_mesh
	mm.instance_count = 18
	mm.visible_instance_count = 0
	fan.multimesh = mm
	var fm := StandardMaterial3D.new()
	fm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	fm.vertex_color_use_as_albedo = true
	fm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	fm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	fm.cull_mode = BaseMaterial3D.CULL_DISABLED
	fm.disable_fog = true
	fm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD   # PC: added like the spark sprites, so the fan glows instead of painting over
	fan.material_override = fm
	fan.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	fan.visible = false
	g.add_child(fan)
	var fxl: Array = []
	for v in meta.get("fxL", []):
		fxl.append(Vector3(v[0], v[1], v[2]))
	var fxp: Array = []
	for v in meta.get("fxP", []):
		fxp.append(Vector3(v[0], v[1], v[2]))
	var smoke = null
	if meta.get("smoke") != null:
		var sv: Array = meta["smoke"]
		smoke = Vector3(sv[0], sv[1], sv[2])
	views[k] = {"g": g, "tilt": tilt, "model": model, "wheels": wheels, "flames": flames, "bub": bub, "cloves": cloves, "mz": mz, "sc": sc, "pop": false, "bf": 0.0, "cut_m": [], "ice": ice, "fan": fan, "fan_mat": fm,
		"fxL": fxl, "fxP": fxp, "smoke": smoke, "top": float(meta.get("top", 7.0)), "axF": float(meta.get("axF", 6.0)), "axR": float(meta.get("axR", -6.0)),
		"axW": float(meta.get("axW", 5.0)), "hover": float(meta.get("hover", 0.0)), "hglow": meta.get("hglow"), "tp": 0.0, "tr": 0.0, "fxc": 0.0, "trick_on": false, "f_ti": -1,
		"held": null, "held_it": "", "rx": k.x, "ry": k.y, "rz": k.wy, "rma": k.ma, "glider": glider, "ga": 0.0}


func clear() -> void:
	for k in views:
		var v: Dictionary = views[k]
		(v["g"] as Node).queue_free()
		for cn in v.get("cut_m", []):
			(cn as Node).queue_free()
		if v["held"] != null:
			(v["held"] as Node).queue_free()
		if v.get("dl") != null:
			(v["dl"] as Node).queue_free()
	views.clear()
	for n in box_nodes:
		(n["n"] as Node).queue_free()
	box_nodes.clear()
	for id in proj_nodes:
		(proj_nodes[id]["n"] as Node).queue_free()
	proj_nodes.clear()
	for p in pops:
		(p["n"] as Node).queue_free()
	pops.clear()
	for id in haz_nodes:
		(haz_nodes[id]["n"] as Node).queue_free()
	haz_nodes.clear()
	for n in ring_nodes:
		(n as Node).queue_free()
	ring_nodes.clear()


func _near_cam(x: float, y: float, d: float) -> bool:
	var c := cam.global_position
	return (x - c.x) * (x - c.x) + (y - c.z) * (y - c.z) <= d * d


## web syncKart: place one kart between its last two physics steps and run its effects
func draw_kart(k: Kart, al: float, dt: float, racing: bool, paused: bool) -> void:
	var v: Dictionary = views[k]
	var g: Node3D = v["g"]
	var tilt: Node3D = v["tilt"]
	var x := lerpf(k.ox, k.x, al)
	var y := lerpf(k.oy, k.y, al)
	var z := lerpf(k.owy, k.wy, al)
	var a := lerp_angle(k.oa, k.a, al)
	var lth := 0.0
	if not k.loop.is_empty():
		lth = clampf(lerpf(k.o_th if k.o_loop else 0.0, k.loop_th, al), 0.0001, TAU)
	v["rx"] = x
	v["ry"] = y
	v["rz"] = z
	v["rma"] = lerp_angle(k.oma, k.ma, al)
	var pos := Vector3(x, z, y)
	var B: float = v["sc"] * (0.62 if k.shrink_t > 0.0 else 1.0)
	var scv := Vector3.ONE * B
	if k.mega_t > 0.0:
		scv *= 1.0 + 0.45 * minf(1.0, minf((Race.MEGA_T - k.mega_t) * 4.0, k.mega_t * 4.0))
	elif k.flat_t > 0.0:
		# splat flat in a blink, jiggle like dough, then spring back up (overshoot and settle) with a puff
		var ft := Race.FLAT_T - k.flat_t
		var P := 0.32
		var sy := 1.0
		var sw := 1.0
		if ft < 0.06:
			var e0 := ft / 0.06
			sy = 1.0 - 0.86 * e0 * e0
			sw = 1.0 + 0.62 * e0 * e0
		elif k.flat_t > P:
			var j := exp(-(ft - 0.06) * 7.0)
			sy = 0.14 + 0.035 * sin(ft * 46.0) * j
			sw = 1.62 + 0.1 * sin(ft * 46.0 + 1.3) * j
		else:
			var u0 := 1.0 - k.flat_t / P
			sy = 1.0 - 0.86 * cos(u0 * PI * 2.5) * exp(-u0 * 4.0)
			sw = 1.0 + (1.0 - sy) * 0.72 if sy < 1.0 else 1.0 - (sy - 1.0) * 0.55
			if not v["pop"] and not paused:
				v["pop"] = true
				for i in 12:
					var pa := float(i) / 12.0 * TAU
					fx.spawn_n(x + cos(pa) * 5.0, z + 2.0, y + sin(pa) * 5.0, cos(pa) * 26.0, 10.0 + randf() * 8.0, sin(pa) * 26.0, Color("#efe3cb"), 5.0, 9.0, 0.45, 0.0, 3.0)
		if k.flat_t > P:
			v["pop"] = false
		scv = Vector3(B * sw, B * maxf(0.12, sy), B * sw)
	if lth == 0.0:
		var tp: float = v["tp"]
		var tr: float = v["tr"]
		if not k.air:
			var ca := cos(a)
			var sa := sin(a)
			var fF := maxf(6.0, float(v["axF"]))
			var fR := minf(-6.0, float(v["axR"]))
			var fW := maxf(5.0, float(v["axW"]))
			var hF := T.ground(x + ca * fF, y + sa * fF)
			var hB := T.ground(x + ca * fR, y + sa * fR)
			var hL := T.ground(x - sa * fW, y + ca * fW)
			var hR := T.ground(x + sa * fW, y - ca * fW)
			var sF := (hF - hB) / (fF - fR)
			var sR := (hL - hR) / (2.0 * fW)
			var ff := minf(1.0, 16.0 * dt)
			tp += (atan(sF) - tp) * ff
			tr += (-atan(sR) - tr) * ff
		else:
			tp *= 0.97
			tr *= 0.97
		v["tp"] = tp
		v["tr"] = tr
		g.transform = Transform3D(Basis(Vector3.UP, -a) * Basis(Vector3(0, 0, 1), tp) * Basis(Vector3(1, 0, 0), tr) * Basis.from_scale(scv), pos)
	else:
		g.transform = Transform3D(Basis(Vector3.UP, -a) * Basis(Vector3(0, 0, 1), lth) * Basis.from_scale(scv), pos)
	g.visible = not (k != me and _near_cam(x, y, 14.0)) and not k.elim
	# blink for three seconds after a hit
	tilt.visible = not (k.inv > 0.0 and k.spin <= 0.0 and racing and int(floor(time * 12.0)) % 2 == 1)
	var f := minf(1.0, 8.0 * dt)
	if k.trick_t > 0.0:
		var u := clampf(1.0 - k.trick_t / Kart.TRICK_T, 0.0, 1.0)
		var e := u * u * u * (u * (u * 6.0 - 15.0) + 10.0)
		var tk: Array = TRICKS[clampi(k.trick_k, 0, 4)]
		var q := Quaternion(tk[0], float(tk[1]) * e * TAU)
		var c := Vector3(0, float(v["top"]) * 0.42, 0)
		tilt.quaternion = q
		tilt.position = c - q * c
		v["trick_on"] = true
	else:
		if v["trick_on"]:
			tilt.rotation = Vector3.ZERO
			tilt.position = Vector3.ZERO
			v["trick_on"] = false
		var lean := (k.steer * 0.08 * k.d_amt if k.drift != 0 else 0.0) + k.steer * 0.04
		var rot := tilt.rotation
		rot.x += (lean - rot.x) * f
		rot.z += (clampf(k.acc * 0.0006, -0.07, 0.05) - rot.z) * f
		tilt.rotation = rot
	if float(v["hover"]) > 0.0 and not v["trick_on"]:
		tilt.position.y = sin(time * 2.4 + k.ri * 1.7) * 0.22
	if v.get("hglow") != null and is_instance_valid(v["hglow"]):
		# the underglow flickers, and burns brighter on a boost (web: opacity .55 + .12 sin(9t) + .3)
		var hm := (v["hglow"] as MeshInstance3D).material_override as StandardMaterial3D
		if hm != null:
			hm.albedo_color.a = clampf(0.55 + sin(time * 9.0 + k.ri) * 0.12 + (0.3 if k.boost > 0.0 else 0.0), 0.0, 1.0)
	if not paused:
		for w in v["wheels"]:
			var n: Node3D = w["node"]
			n.rotation.z -= k.speed * dt / (float(w["r"]) * KS)
			if w["front"]:
				n.rotation.y = -k.steer * 0.42
	# frozen in a block of ice: it grows in, wobbles, and shrinks away at the end
	var ice: Node3D = v["ice"]
	var fz := k.frozen > 0.0
	if ice.visible != fz:
		ice.visible = fz
	if fz:
		ice.scale = Vector3.ONE * float((v["bub"] as Node3D).scale.x) * minf(1.0, 0.25 + (2.8 - k.frozen) * 6.0) * (k.frozen * 4.0 if k.frozen < 0.25 else 1.0)
		ice.rotation.y = sin(time * 1.5) * 0.05
	# shield or rush bubble
	# the glider unfolds while gliding (web: ga eases to 1 at 5/s, folds away at 8/s)
	var gl = v.get("glider")
	if gl != null:
		var gt := 1.0 if k.glide else 0.0
		v["ga"] = float(v["ga"]) + (gt - float(v["ga"])) * minf(1.0, dt * (5.0 if gt > 0.0 else 8.0))
		var gv := float(v["ga"]) > 0.02
		(gl as Node3D).visible = gv
		if gv:
			(gl as Node3D).scale = Vector3.ONE * float(v["ga"])
			(gl as Node3D).rotation = Vector3(-k.steer * 0.18, 0.0, sin(time * 2.2 + k.ri) * 0.06)
	var bub: MeshInstance3D = v["bub"]
	var sh_on := (k.shield > 0.0 and (k.shield > 1.2 or int(floor(time * 10.0)) % 2 == 0)) or k.sh_l > 0
	var ru_on := k.rush > 0.0 or k.chili_t > 0.0 or k.olive_t > 0.0
	bub.visible = sh_on or ru_on
	if bub.visible:
		bub.material_override = bubble_mat if sh_on else rush_mat
		bub.rotation.y += dt * (2.0 if sh_on else 4.0)
		# pieces left = hits left
		var cl: Array = v["cloves"]
		for i in cl.size():
			(cl[i] as Node3D).visible = i < k.sh_l
		var mzn := k.mz_h if k.shield > 0.0 else 0
		var mz: Node3D = v["mz"]
		mz.visible = mzn > 0
		for i in mz.get_child_count():
			(mz.get_child(i) as Node3D).visible = i < mzn
	# boost flames, sized by the boost and coloured by the drift tier it came from
	var on := k.boost > 0.0
	var sl := 1.0
	var sw := 1.0
	if on:
		var ft := clampi(k.f_tier, 0, 3)
		var P := k.b_pk if k.b_pk > 0.0 else 1.0
		sl = clampf(0.55 + 0.42 * P, 0.75, 2.1)
		sw = 0.55 + 0.45 * sl
		if int(v["f_ti"]) != ft:
			v["f_ti"] = ft
			for fl in v["flames"]:
				var col: Color = FLAMEC[ft][1 if fl["inner"] else 0]
				(fl["mat"] as StandardMaterial3D).albedo_color = Color(col.r, col.g, col.b, 0.95 if fl["inner"] else 0.85)
	for fl in v["flames"]:
		var mi: MeshInstance3D = fl["mi"]
		mi.visible = on
		if on and not paused:
			var L := sl * (0.8 + randf() * 0.5)
			mi.scale = Vector3(sw, L, sw)
			var u2 = fl["fl"]
			if u2 != null:
				mi.position.x = float(u2[0]) + float(u2[1]) * (1.0 - L)
	if paused:
		return
	var gt := g.global_transform
	var rma: float = v["rma"]
	if k.burn_t > 0.0:
		# on fire: flames lick up off the kart and dark smoke trails behind
		v["bf"] = float(v["bf"]) + dt * 70.0 * minf(1.0, k.burn_t / 0.5 + 0.3)
		while float(v["bf"]) >= 1.0:
			v["bf"] = float(v["bf"]) - 1.0
			var bc: Color = [Color("#ff3a12"), Color("#ff8a1f"), Color("#ffd23a")][randi() % 3]
			fx.spawn_a(x + (randf() - 0.5) * 10.0, z + 3.0 + randf() * 5.0, y + (randf() - 0.5) * 10.0, (randf() - 0.5) * 8.0, 22.0 + randf() * 20.0, (randf() - 0.5) * 8.0, bc, 5.5, 1.2, 0.38 + randf() * 0.15, -25.0, 1.2)
			if randf() < 0.3:
				fx.spawn_n(x + (randf() - 0.5) * 6.0, z + 9.0 + randf() * 3.0, y + (randf() - 0.5) * 6.0, -cos(rma) * 12.0, 14.0 + randf() * 8.0, -sin(rma) * 12.0, Color("#3a2e28") if randf() < 0.5 else Color("#5a4a40"), 5.0, 13.0, 0.9, -8.0, 0.8)
	# the newer items' states (web itemsRender)
	var cm: Array = v["cut_m"]
	if k.cut_t > 0.0:
		if cm.is_empty():
			for b in 3:
				var cn := item_node("cutter")
				cn.scale = Vector3.ONE * 1.1
				add_child(cn)
				cm.append(cn)
		for b in 3:
			var ca2 := k.cut_a + b * 2.094
			var cn2: Node3D = cm[b]
			cn2.visible = true
			cn2.position = Vector3(x + cos(ca2) * 15.0, z + 5.0, y + sin(ca2) * 15.0)
			cn2.rotation = Vector3(0.0, -ca2, time * 25.0)
			if randf() < 0.4:
				fx.spawn_a(cn2.position.x, cn2.position.y, cn2.position.z, 0, 0, 0, Color("#e8f4ff"), 2.0, 0.2, 0.25)
	elif not cm.is_empty() and (cm[0] as Node3D).visible:
		for cn3 in cm:
			(cn3 as Node3D).visible = false
	if k.ghost_t > 0.0:
		tilt.visible = int(floor(time * 24.0)) % 3 != 0
		if randf() < 0.5:
			fx.spawn_a(x + (randf() - 0.5) * 10.0, z + 6.0, y + (randf() - 0.5) * 10.0, 0, 8, 0, Color("#cfe8ff"), 3.0, 0.3, 0.4)
	if k.mag_t > 0.0 and k.mag_tg != null and views.has(k.mag_tg) and randf() < 0.8:
		var tv: Dictionary = views[k.mag_tg]
		var mt := randf()
		fx.spawn_a(x + (float(tv["rx"]) - x) * mt, z + 6.0, y + (float(tv["ry"]) - y) * mt, 0, 0, 0, Color("#ff5a5a"), 2.6, 0.3, 0.2)
	if k.cannon_t > 0.0 and randf() < 0.9:
		var cna := randf() * TAU
		fx.spawn_a(x - cos(rma) * 10.0, z + 5.0, y - sin(rma) * 10.0, cos(cna) * 20.0, 10.0, sin(cna) * 20.0, Color("#ffcc33"), 5.0, 0.4, 0.4, 0.0, 1.0)
		fx.spawn_n(x - cos(rma) * 12.0, z + 4.0, y - sin(rma) * 12.0, 0, 6, 0, Color("#8a7a6a"), 5.0, 16.0, 0.8, -2.0, 1.0)
	if k.sauce_t > 0.0 and randf() < 0.3:
		fx.spawn_n(x, z + 3.0, y, (randf() - 0.5) * 10.0, 2.0, (randf() - 0.5) * 10.0, Color("#b8200e"), 2.5, 1.0, 0.6, 30.0, 1.0)
	if k.frozen > 0.0 and randf() < 0.5:
		fx.spawn_a(x + (randf() - 0.5) * 10.0, z + 8.0 * KS, y + (randf() - 0.5) * 10.0, 0, -6, 0, Color("#bfe6ff"), 2.4, 0.6, 0.5)
	if k.ab_fx > 0.0 and randf() < 0.9:
		fx.spawn_a(x - cos(rma) * 9.0 + (randf() - 0.5) * 6.0, z + 3.0 + randf() * 4.0, y - sin(rma) * 9.0 + (randf() - 0.5) * 6.0, (randf() - 0.5) * 14.0, 8.0, (randf() - 0.5) * 14.0, k.ab_col, 3.4, 0.3, 0.45, 0.0, 1.0)
	if k.spin > 0.0:
		for i in 3:
			var an := time * 9.0 + i * 2.094
			fx.spawn_a(x + cos(an) * 4.5 * KS, z + (float(v["top"]) + 2.3) * KS, y + sin(an) * 4.5 * KS, 0, 0, 0, Color("#ffe066"), 2.2, 1.2, 0.07)
	var near := _near_cam(x, y, 260.0)
	_fan(k, v, near)
	if not near:
		return
	v["fxc"] = float(v["fxc"]) + dt * 60.0
	var n2 := mini(4, int(floor(float(v["fxc"]))))
	v["fxc"] = float(v["fxc"]) - floor(float(v["fxc"]))
	var fxl: Array = v["fxL"]
	var lat := absf(T.lateral(k.idx, k.x, k.y))
	var sf_off := lat >= T.CURB
	for i in n2:
		if k.drift != 0 and k.charge > 0.3 and fxl.size() > 0:
			var tier := Kart._tier_of(k.charge)
			var sz := 1.6 + tier * 0.4 if tier > 0 else 1.1
			for lv in fxl:
				var tv: Vector3 = gt * (lv as Vector3)
				for q2 in (2 if tier > 0 else 1):
					fx.spawn_a(tv.x, tv.y + 0.3, tv.z, (randf() - 0.5) * 30.0 - cos(k.ma) * (22.0 + tier * 6.0), 10.0 + randf() * 30.0, (randf() - 0.5) * 30.0 - sin(k.ma) * (22.0 + tier * 6.0), SPARKC[tier], sz, 0.3, 0.3 + tier * 0.03, 80.0, 1.0)
				if tier > 0 and i % 2 == 0:
					fx.spawn_a(tv.x, tv.y + 0.7, tv.z, -cos(k.ma) * 8.0, 2.0, -sin(k.ma) * 8.0, SPARKC[tier], 4.5 + tier, 2.0, 0.14)
			if i % 3 == 0:
				var tv2: Vector3 = gt * (fxl[0 if randf() < 0.5 else mini(1, fxl.size() - 1)] as Vector3)
				fx.spawn_n(tv2.x, tv2.y + 0.6, tv2.z, (randf() - 0.5) * 6.0, 4.0 + randf() * 4.0, (randf() - 0.5) * 6.0, Color("#f2ebe0"), 2.5, 8.0, 0.8, -2.0, 1.5)
		if on and (k == me and i % 3 == 0 or (k != me and i == 0 and randf() < 0.5 and _near_cam(x, y, 160.0))):
			for pv in v["fxP"]:
				var tp2: Vector3 = gt * (pv as Vector3)
				fx.spawn_a(tp2.x, tp2.y, tp2.z, -cos(k.ma) * 30.0 + (randf() - 0.5) * 6.0, (randf() - 0.2) * 6.0, -sin(k.ma) * 30.0 + (randf() - 0.5) * 6.0, Color("#ff7a1a") if randf() < 0.5 else Color("#ffd36b"), 2.2, 0.4, 0.25, 0.0, 2.0)
		if v["smoke"] != null and i == 0 and randf() < 0.3:
			var sm: Vector3 = gt * (v["smoke"] as Vector3)
			fx.spawn_n(sm.x, sm.y, sm.z, (randf() - 0.5) * 4.0, 8.0 + randf() * 6.0, (randf() - 0.5) * 4.0, Color("#9a918a"), 2.5, 9.0, 1.4, -1.0, 1.5)
		if k.glide and i % 2 == 0:
			fx.spawn_a(x + (randf() - 0.5) * 14.0, z + (float(v["top"]) - 1.0) * KS * randf(), y + (randf() - 0.5) * 14.0, -cos(k.ma) * 70.0, 0.0, -sin(k.ma) * 70.0, Color("#e8f8ff"), 1.4, 0.35, 0.25)
		if sf_off and not k.air and absf(k.speed) > 60.0 and i % 3 == 0 and fxl.size() > 0:
			var tv3: Vector3 = gt * (fxl[0 if randf() < 0.5 else mini(1, fxl.size() - 1)] as Vector3)
			fx.spawn_n(tv3.x, tv3.y + 0.5, tv3.z, (randf() - 0.5) * 10.0, 5.0 + randf() * 6.0, (randf() - 0.5) * 10.0, Color("#f2cf6a"), 2.0, 7.0, 0.7, -1.0, 1.5)


## PC: the sparks light the road: a small flickering light in the drift's colour between the back wheels
func _drift_light(k: Kart, v: Dictionary, tier: int) -> void:
	var fxl: Array = v["fxL"]
	if fxl.is_empty():
		return
	var dl: OmniLight3D = v.get("dl")
	if dl == null:
		dl = OmniLight3D.new()
		dl.shadow_enabled = false
		dl.light_specular = 0.6
		dl.omni_attenuation = 1.6
		add_child(dl)
		v["dl"] = dl
	var mid := Vector3.ZERO
	for lv in fxl:
		mid += lv as Vector3
	mid /= float(fxl.size())
	dl.global_position = (v["g"] as Node3D).global_transform * Vector3(mid.x - 1.0, mid.y + 1.6, 0.0)
	dl.light_color = SPARKC[tier]
	dl.omni_range = 26.0 + 4.0 * tier
	dl.light_energy = (1.1 + 0.45 * tier) * (0.7 + 0.6 * randf())
	dl.visible = true


## web fanUpdate: a crackling fan of spark streaks at each back wheel while a drift is charged
func _fan(k: Kart, v: Dictionary, near: bool) -> void:
	var tier := 0
	if near and k.drift != 0 and not k.air and k.spin <= 0.0 and k.charge > 0.8:
		tier = 3 if k.charge > 2.6 else (2 if k.charge > 1.6 else 1)
	var fan: MultiMeshInstance3D = v["fan"]
	fan.visible = tier > 0
	if tier == 0:
		if v.get("dl") != null:
			(v["dl"] as OmniLight3D).visible = false
		return
	# the web draws these without tone mapping: lift them by the same amount as the spark sprites so they
	# come out of Godot's tone mapper at full strength
	var c: Color = SPARKC[tier].srgb_to_linear() * 1.25
	(v["fan_mat"] as StandardMaterial3D).albedo_color = Color(c.r, c.g, c.b, 1.0).linear_to_srgb()
	_drift_light(k, v, tier)
	var mm := fan.multimesh
	var n := 0
	for lv in v["fxL"]:
		var lp: Vector3 = lv
		var sz := 1.0 if lp.z >= 0.0 else -1.0
		for b in 8:
			var L := (2.2 + randf() * 3.4) * (1.0 + 0.16 * tier)
			var d := Vector3(-1.0, 0.2 + randf() * 1.25, (randf() - 0.25) * 1.1 * sz).normalized()
			var w := 0.18 + randf() * 0.16
			var q := Quaternion(Vector3(1, 0, 0), d)
			# stretch the blade along its own length first, then turn it (three.js compose: rotation x scale)
			mm.set_instance_transform(n, Transform3D(Basis(q) * Basis.from_scale(Vector3(L, w, w)), Vector3(lp.x, lp.y + 0.12, lp.z)))
			n += 1
			if n >= 18:
				break
	mm.visible_instance_count = n


## a held item rides right behind the kart, swaying a little
func _draw_held(k: Kart) -> void:
	var v: Dictionary = views[k]
	var want: String = String(k.held.get("it", "")) if not k.held.is_empty() else ""
	if want != String(v["held_it"]):
		if v["held"] != null:
			(v["held"] as Node).queue_free()
			v["held"] = null
		v["held_it"] = want
		if want != "":
			var t: String = HELD_NODE.get(want, "pep")
			var hn := item_node(t)
			if ITEM_GLOW.has(t):
				hn.add_child(_halo(ITEM_GLOW[t], 12.0))
			add_child(hn)
			v["held"] = hn
	if v["held"] == null:
		return
	var hn2: Node3D = v["held"]
	var L := 11.0 * k.sf * KS * 0.62 + 4.0
	var rma: float = v["rma"]
	var ca := cos(rma)
	var sa := sin(rma)
	var sw := sin(time * 5.0 + k.ri) * 1.2
	var hx := float(v["rx"]) - ca * L - sa * sw
	var hz := float(v["ry"]) - sa * L + ca * sw
	hn2.position = Vector3(hx, (float(v["rz"]) + 1.0 if k.air else T.ground(hx, hz)) + 2.4, hz)
	hn2.scale = Vector3.ONE * (1.15 if want == "pepperoni" or want == "dough" else 1.0)
	hn2.rotation = Vector3(0, -rma + (time * 6.0 if want == "pepperoni" else 0.0), 0)
	hn2.visible = (v["g"] as Node3D).visible


# ---------------------------------------------------------------- items, boxes, traps

func build_boxes() -> void:
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 5.8 - 0.32
	ring_mesh.outer_radius = 5.8 + 0.32
	ring_mesh.rings = 40
	ring_mesh.ring_segments = 10
	var glow_mesh := PlaneMesh.new()
	glow_mesh.size = Vector2(12, 12)
	var gi_n := 0
	var gi_a := 0
	for b in race.boxes:
		var bd: Dictionary = b
		var root := Node3D.new()
		var body := item_node("itembox2" if bool(bd["dbl"]) else "itembox")
		root.add_child(body)
		var ring := MeshInstance3D.new()
		ring.mesh = ring_mesh
		ring.material_override = ring_mat_d if bool(bd["dbl"]) else ring_mat_n
		ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		root.add_child(ring)
		add_child(root)
		var glow: MeshInstance3D = null
		if not bool(bd["air"]):
			glow = MeshInstance3D.new()
			glow.mesh = glow_mesh
			glow.material_override = box_glow_mat
			glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(glow)
			glow.position = Vector3(float(bd["x"]), float(bd["gy"]) + 0.3, float(bd["y"]))
		var sv := 0
		if bool(bd["air"]):
			sv = 90 + (gi_a / 3) * 4 + gi_a % 3
			gi_a += 1
		else:
			sv = (gi_n / 3) * 4 + gi_n % 3
			gi_n += 1
		box_nodes.append({"n": root, "body": body, "ring": ring, "glow": glow, "sv": float(sv)})


func _draw_boxes() -> void:
	box_glow_mat.albedo_color.a = 0.35 + sin(time * 4.0) * 0.15
	for i in race.boxes.size():
		var b: Dictionary = race.boxes[i]
		var bn: Dictionary = box_nodes[i]
		var root: Node3D = bn["n"]
		var br: float = b["r"]
		var vis := br <= 0.0 or br < 0.35
		var s := (1.0 - br / 0.35 if br > 0.0 else 1.0) if vis else 0.0
		root.visible = s > 0.001
		if not root.visible:
			continue
		var sv: float = bn["sv"]
		var sc := maxf(0.001, s) * (1.25 if bool(b["dbl"]) else 1.0)
		root.position = Vector3(float(b["x"]), float(b["gy"]) + 6.5 + sin(time * 3.0 + sv) * 0.8, float(b["y"]))
		root.scale = Vector3.ONE * sc
		(bn["body"] as Node3D).basis = Basis.from_euler(Vector3(0.3, time * 1.6 + sv, 0.18), EULER_ORDER_XYZ)
		# three's torus lies in its XY plane; Godot's in XZ
		(bn["ring"] as Node3D).basis = Basis.from_euler(Vector3(PI / 2.0 + sin(time * 2.0 + sv) * 0.35, 0.0, time), EULER_ORDER_XYZ) * Basis(Vector3(1, 0, 0), PI / 2.0)


func _proj_ground(x: float, y: float) -> float:
	var pg := T.ground(x, y)
	if not T.glide.is_empty():
		var gyy := T.glide_y(x, y)
		if pg < gyy - 20.0:
			pg = gyy + 6.0
	return pg


func _draw_projectiles(al: float, dt: float) -> void:
	var seen := {}
	for p in race.projectiles:
		var pd: Dictionary = p
		var id: int = pd["id"]
		seen[id] = true
		var type: String = pd["type"]
		var x := float(pd["x"])
		var y := float(pd["y"])
		if pd.has("px") and str(pd.get("ph", "")) == "":   # "ph" is a word on some items and a number on others: String() of a number is an error and stopped every thrown item being drawn
			x = lerpf(float(pd["px"]), x, al)
			y = lerpf(float(pd["py"]), y, al)
		if not proj_nodes.has(id):
			var nn := item_node(PROJ_NODE.get(type, "pep"))
			var halo: MeshInstance3D = null
			if ITEM_GLOW.has(type):
				halo = _halo(ITEM_GLOW[type], 16.0 if type == "wheel" else 12.0)
				nn.add_child(halo)
			add_child(nn)
			proj_nodes[id] = {"n": nn, "age": 0.0, "sp": 0.0, "roll": 0.0, "halo": halo, "type": type, "lf": null}
			var c: Color = ITEM_GLOW.get(type, TRAIL.get(type, Color("#ffe066")))
			var gy := _proj_ground(x, y) + 4.0
			fx.spawn_a(x, gy, y, 0, 0, 0, c, 16.0, 5.0, 0.16)
			for n in 6:
				var a := randf() * TAU
				fx.spawn_a(x, gy, y, cos(a) * 45.0, 10.0 + randf() * 25.0, sin(a) * 45.0, c, 2.2, 0.3, 0.3, 40.0, 1.0)
		else:
			proj_nodes[id]["age"] = float(proj_nodes[id]["age"]) + dt
		var pn: Dictionary = proj_nodes[id]
		pn["pop"] = pd.get("pop", false)
		var ms: Node3D = pn["n"]
		var age: float = pn["age"]
		var pg := _proj_ground(x, y)
		var pop := 0.35 + 0.65 * (1.0 - pow(1.0 - age / 0.22, 3.0)) if age < 0.22 else 1.0
		if type == "wheel":
			_draw_wheel(pd, pn, pg, x, y)
			continue
		if type == "flour":
			var ff := 1.0 - float(pd["t"]) / maxf(0.01, float(pd["t0"]))
			ms.position = Vector3(x, pg + 3.4 + sin(PI * ff) * 20.0, y)
			ms.rotation.y += dt * 6.0
			ms.rotation.z = sin(ff * TAU) * 0.5
		elif type == "lob":
			var fl := 1.0 - float(pd["t"]) / maxf(0.01, float(pd["t0"]))
			ms.position = Vector3(x, pg + 2.0 + sin(PI * fl) * 16.0, y)
			ms.rotation.z -= dt * 8.0
		elif type == "meat2":
			pn["roll"] = float(pn["roll"]) + Vector2(float(pd["vx"]), float(pd["vy"])).length() * dt / 3.0
			ms.position = Vector3(x, pg + 4.5, y)
			ms.basis = Basis.from_euler(Vector3(0.0, -atan2(float(pd["vy"]), float(pd["vx"])), -float(pn["roll"])), EULER_ORDER_XYZ)
			if dt > 0.0 and randf() < 0.5:
				fx.spawn_n(x, pg + 1.0, y, (randf() - 0.5) * 16.0, 6.0, (randf() - 0.5) * 16.0, Color("#c8a878"), 4.0, 10.0, 0.6, -2.0, 1.5)
			continue
		elif type == "bomb":
			var landed := bool(pd.get("landed", true))
			var t0b := maxf(0.01, float(pd.get("t0", 0.75)))
			var fb := 1.0 if landed else 1.0 - (float(pd["t"]) - float(pd.get("fuse", 1.1))) / t0b
			ms.position = Vector3(x, pg + 3.0 + (0.0 if landed else sin(PI * minf(1.0, fb)) * 18.0), y)
			ms.rotation.y += dt * 3.0
			var pul := 1.0 + sin(time * (8.0 + (1.6 - float(pd["t"])) * 16.0)) * 0.12 if landed else 1.0
			ms.scale = Vector3.ONE * pul
			if dt > 0.0:
				fx.spawn_a(x, ms.position.y + 5.0, y, (randf() - 0.5) * 20.0, 30.0, (randf() - 0.5) * 20.0, Color("#ffcc33"), 1.8, 0.2, 0.3, 60.0, 1.0)
			continue
		elif type == "twist":
			ms.position = Vector3(x, pg + 6.0, y)
			ms.rotation.y += dt * 14.0
			ms.scale = Vector3.ONE * (2.2 + sin(time * 7.0) * 0.15)
			if dt > 0.0:
				for n in 2:
					var ta := randf() * TAU
					fx.spawn_n(x + cos(ta) * 8.0, pg + 2.0 + randf() * 12.0, y + sin(ta) * 8.0, -sin(ta) * 40.0, 10.0, cos(ta) * 40.0, Color("#f3e6c8"), 5.0, 12.0, 0.7, 0.0, 1.0)
			continue
		elif type == "torp":
			ms.position = Vector3(x, pg + 4.0, y)
			ms.basis = Basis.from_euler(Vector3(sin(time * 20.0) * 0.15, -atan2(float(pd["vy"]), float(pd["vx"])), 0.0), EULER_ORDER_XYZ)
		elif type == "pep":
			var storm := bool(pd.get("storm", false))
			pn["sp"] = float(pn["sp"]) + dt * 17.0
			ms.position = Vector3(x, pg + (1.9 if storm else 3.3) + sin(age * 9.0) * (0.2 if storm else 0.35), y)
			var q := Quaternion(Vector3.UP, -atan2(float(pd["vy"]), float(pd["vx"]))) * Quaternion(Vector3(0, 0, 1), 0.18 if storm else 0.4) * Quaternion(Vector3(1, 0, 0), sin(age * 7.0) * 0.2) * Quaternion(Vector3.UP, float(pn["sp"]))
			ms.quaternion = q
		elif type == "dough":
			pn["roll"] = float(pn["roll"]) + Vector2(float(pd["vx"]), float(pd["vy"])).length() * dt / 2.6
			ms.position = Vector3(x, pg + 2.8 + absf(sin(age * 6.5)) * 1.6, y)
			ms.basis = Basis.from_euler(Vector3(0.0, -atan2(float(pd["vy"]), float(pd["vx"])), -float(pn["roll"])), EULER_ORDER_XYZ)
		else:
			ms.position = Vector3(x, pg + 2.7, y)
		if type != "flour":
			var bs: float = FLY_SC.get(type, 1.0)
			ms.scale = Vector3.ONE * ((pop * bs) if age < 0.25 else bs)
		# trail (web itemsRender)
		if TRAIL.has(type):
			var col: Color = TRAIL[type]
			var m := ms.position
			var sz := 3.0 if type == "flour" else 2.4
			fx.spawn_a(m.x + (randf() - 0.5) * 1.2, m.y + (randf() - 0.5) * 1.2, m.z + (randf() - 0.5) * 1.2, (randf() - 0.5) * 6.0, 2.0, (randf() - 0.5) * 6.0, col, sz, 0.2, 0.35, 0.0, 2.0)
			var lf = pn["lf"]
			if lf != null:
				var lv: Vector3 = lf
				var h := (m + lv) / 2.0
				if (m.x - lv.x) ** 2 + (m.z - lv.z) ** 2 > 9.0:
					fx.spawn_a(h.x, h.y, h.z, (randf() - 0.5) * 6.0, 2.0, (randf() - 0.5) * 6.0, col, sz * 0.85, 0.2, 0.32, 0.0, 2.0)
			pn["lf"] = m
	for id in proj_nodes.keys():
		if seen.has(id):
			continue
		var gone: Dictionary = proj_nodes[id]
		var gn: Node3D = gone["n"]
		if bool(gone.get("pop", false)) and pops.size() < 12:
			pops.append({"n": gn, "t": 0.0, "s": gn.scale.x})
		else:
			gn.queue_free()
		proj_nodes.erase(id)
	for i in range(pops.size() - 1, -1, -1):
		var q2: Dictionary = pops[i]
		q2["t"] = float(q2["t"]) + dt
		var f := float(q2["t"]) / 0.26
		var pn2: Node3D = q2["n"]
		if f >= 1.0:
			pn2.queue_free()
			pops.remove_at(i)
			continue
		var kk := 1.0 + f / 0.3 * 0.55 if f < 0.3 else 1.55 * (1.0 - (f - 0.3) / 0.7)
		pn2.scale = Vector3.ONE * float(q2["s"]) * maxf(0.01, kk)
		pn2.rotation.y += dt * 12.0


## the pizza cutter (web wheelRender)
func _draw_wheel(pd: Dictionary, pn: Dictionary, pg: float, x0: float, y0: float) -> void:
	var ms: Node3D = pn["n"]
	var tg: Kart = pd.get("target")
	var ph: String = pd.get("ph", "")
	var x := x0
	var y := pg + 7.5
	var z := y0
	var spin: float = pd.get("spin", 0.0)
	var bank := 0.42 + sin(time * 5.5) * 0.1
	var pitch := sin(time * 3.1) * 0.06
	var yaw := -float(pd.get("dir", 0.0)) + sin(time * 2.3 + spin * 0.01) * 0.5
	var sc := minf(1.0, 0.35 + float(pn["age"]) * 3.5)
	var hs := 16.0
	if ph != "" and tg != null and views.has(tg):
		var tv: Dictionary = views[tg]
		var kp := Vector3(tv["rx"], tv["rz"], tv["ry"])
		var hr: float = tv["rma"]
		x = kp.x + cos(hr) * 7.0
		z = kp.z + sin(hr) * 7.0
		yaw = -hr + PI / 2.0
		var pt: float = pd.get("pt", 0.0)
		if ph == "wind":
			var f := minf(1.0, 1.0 - maxf(0.0, pt) / 0.62)
			var e := 1.0 - pow(1.0 - minf(1.0, f * 1.7), 3.0)
			y = kp.y + 8.0 + 9.0 * e
			pitch = 1.0 * e
			bank = sin(time * 31.0) * 0.07 * e
			sc = 1.0 + 0.06 * e
			hs = 18.0 + sin(time * 28.0) * 5.0
			pn["wr"] = float(pn.get("wr", 0.0)) - get_process_delta_time()
			if float(pn["wr"]) <= 0.0:
				pn["wr"] = 0.13
				fx.ring(kp.x, kp.y + 0.5, kp.z, Color("#ff3b1a"), 22.0 + 12.0 * e, 0.22, true)
			if randf() < 0.8:
				fx.spawn_a(x + (randf() - 0.5) * 10.0, y, z + (randf() - 0.5) * 10.0, (randf() - 0.5) * 60.0, 20.0 + randf() * 30.0, (randf() - 0.5) * 60.0, Color("#ffffff") if randf() < 0.5 else Color("#ffb347"), 2.0, 0.3, 0.3, 60.0, 1.0)
		elif ph == "slice":
			var f2 := minf(1.0, 1.0 - maxf(0.0, pt) / 0.16)
			y = kp.y + 17.0 - 11.0 * f2 * f2
			pitch = 1.0 - 2.1 * f2
			sc = 1.18
			hs = 22.0
			for n in 3:
				fx.spawn_a(x + (randf() - 0.5) * 4.0, y - 4.0, z + (randf() - 0.5) * 4.0, (randf() - 0.5) * 20.0, -60.0, (randf() - 0.5) * 20.0, Color("#ffffff"), 2.6, 0.4, 0.18, 0.0, 1.0)
		else:
			var f3 := minf(1.0, 1.0 - maxf(0.0, pt) / 0.4)
			y = kp.y + 7.0 + f3 * 5.0
			pitch = -1.1
			sc = 1.18 * (1.0 - f3 * f3)
			hs = 14.0 * (1.0 - f3)
	elif randf() < 0.7:
		fx.spawn_a(x, pg + 1.0, z, (randf() - 0.5) * 30.0, 10.0 + randf() * 20.0, (randf() - 0.5) * 30.0, Color("#ffb347"), 1.6, 0.3, 0.25, 60.0, 1.0)
	ms.position = Vector3(x, y, z)
	ms.basis = Basis.from_euler(Vector3(bank, yaw, pitch), EULER_ORDER_YXZ).scaled(Vector3.ONE * maxf(0.01, sc))
	var model := ms.get_child(0) as Node3D
	if model != null and model.get_child_count() > 0:
		# the blade spins about its own axle
		model.rotation = Vector3(0, 0, 0)
	var h: MeshInstance3D = pn["halo"]
	if h != null:
		h.scale = Vector3.ONE * maxf(0.01, hs)


func _draw_hazards() -> void:
	var seen := {}
	var ring_a := 0.62 + 0.33 * sin(time * 7.0)
	haz_ring_mat.albedo_color.a = ring_a
	var bob := sin(time * 3.2) * 1.2
	for h in race.hazards:
		var hd: Dictionary = h
		var id: int = hd["id"]
		seen[id] = true
		if String(hd.get("kind", "")) == "fire":
			if not haz_nodes.has(id):
				var fr := Node3D.new()
				for i in 3:
					var c := MeshInstance3D.new()
					c.mesh = flame_meshes[0]
					c.material_override = fire_mat
					c.scale = Vector3(3.0, 3.0 + i, 3.0)
					c.position = Vector3((i - 1) * 2.5, 3.0, 0.0)
					c.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
					fr.add_child(c)
				var ci := MeshInstance3D.new()
				ci.mesh = flame_meshes[1]
				ci.material_override = fire_in_mat
				ci.scale = Vector3.ONE * 3.0
				ci.position.y = 2.0
				ci.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				fr.add_child(ci)
				add_child(fr)
				haz_nodes[id] = {"n": fr, "warn": null}
			var fn: Node3D = haz_nodes[id]["n"]
			var fxx := float(hd["x"])
			var fyy := float(hd["y"])
			var fg := race.haz_ground(hd)
			fn.position = Vector3(fxx, fg + 0.12, fyy)
			fn.rotation.y = float(hd["born"]) * 0.05
			fn.scale = Vector3.ONE * maxf(0.01, minf(1.0, float(hd["t"]) * 1.4)) * (1.0 + sin(time * 20.0 + fxx) * 0.1)
			if randf() < 0.3:
				fx.spawn_a(fxx, fg + 4.0, fyy, 0, 26, 0, Color("#ff7a1a"), 3.0, 0.3, 0.4, 0.0, 0.0)
			continue
		var tk := "olive" if hd.get("olive", false) else String(hd.get("kind", "oil"))
		var tr: Array = TRAP.get(tk, TRAP["oil"])
		if not haz_nodes.has(id):
			var root := Node3D.new()
			var slick := item_node(String(tr[0]))
			slick.scale = Vector3.ONE * float(tr[1])
			root.add_child(slick)
			# a pulsing ring the size of the hit area, a soft glow, and a warning sign above
			var edge := MeshInstance3D.new()
			edge.mesh = _flat_ring(11.2, 16.0)
			edge.material_override = _basic(Color("#1a0d06"), 0.55)
			edge.position.y = 0.22
			edge.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			root.add_child(edge)
			var ring := MeshInstance3D.new()
			ring.mesh = _flat_ring(12.6, 14.6)
			ring.material_override = haz_ring_mat
			ring.position.y = 0.26
			ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			root.add_child(ring)
			var glow := _halo(Color(String(tr[2])), float(tr[3]))
			glow.position.y = float(tr[4])
			root.add_child(glow)
			var warn := MeshInstance3D.new()
			var q := QuadMesh.new()
			q.size = Vector2(7.5, 7.5)
			warn.mesh = q
			var wm := StandardMaterial3D.new()
			wm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			wm.albedo_texture = warn_tex
			wm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			wm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
			wm.disable_fog = true
			warn.material_override = wm
			warn.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			warn.position.y = 13.0
			root.add_child(warn)
			add_child(root)
			haz_nodes[id] = {"n": root, "warn": warn}
		var hn: Dictionary = haz_nodes[id]
		var r: Node3D = hn["n"]
		var x := float(hd["x"])
		var y := float(hd["y"])
		# on the road it was dropped on, at any height (it used to lie on the floor underneath), and along its slope
		r.position = Vector3(x, race.haz_ground(hd) + 0.12, y)
		var hs: Array = race.haz_slope(hd)
		if absf(float(hs[0])) > 0.02:
			var up := Vector3(-float(hs[1]) * float(hs[0]), 1.0, -float(hs[2]) * float(hs[0])).normalized()
			r.quaternion = Quaternion(Vector3.UP, up) * Quaternion(Vector3.UP, float(hd["born"]) * 0.05)
		else:
			r.rotation = Vector3(0.0, float(hd["born"]) * 0.05, 0.0)
		r.scale = Vector3.ONE * maxf(0.01, minf(1.0, float(hd["born"]) * 5.0))
		(hn["warn"] as Node3D).position.y = 13.0 + bob
	for id in haz_nodes.keys():
		if not seen.has(id):
			(haz_nodes[id]["n"] as Node).queue_free()
			haz_nodes.erase(id)


static func _flat_ring(r0: float, r1: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var seg := 48
	for i in seg:
		var a0 := TAU * i / seg
		var a1 := TAU * (i + 1) / seg
		var p0 := Vector3(cos(a0) * r0, 0, sin(a0) * r0)
		var p1 := Vector3(cos(a0) * r1, 0, sin(a0) * r1)
		var p2 := Vector3(cos(a1) * r1, 0, sin(a1) * r1)
		var p3 := Vector3(cos(a1) * r0, 0, sin(a1) * r0)
		for q in [p0, p1, p2, p0, p2, p3]:
			st.set_normal(Vector3.UP)
			st.add_vertex(q)
	return st.commit()


# ---------------------------------------------------------------- one frame

var own_k: Kart = null    # cross-play guest: your own kart moves between its own steps, the others between the host's pictures
var own_al := 1.0


func draw(al: float, dt: float, racing: bool, paused: bool) -> void:
	if not paused:
		time += dt
	for k in race.karts:
		draw_kart(k, own_al if k == own_k else al, dt, racing, paused)
	for k in race.karts:
		_draw_held(k)
	_draw_boxes()
	_draw_projectiles(al, 0.0 if paused else dt)
	_draw_hazards()
	_draw_world_haz(0.0 if paused else dt)
	_draw_rings()
	if not paused:
		fx.step(dt)


# ---------------------------------------------------------------- what the race just did, drawn as the web draws it

static func _cols(names: Array) -> Array:
	var out: Array = []
	for n in names:
		out.append(Color(n))
	return out


func kart_event(k: Kart, e: String) -> void:
	if e == "wall":
		var x := k.x + k.wall_n.x * 9.0
		var y := k.y + k.wall_n.y * 9.0
		var gy := k.wy + 3.0
		for i in 10:
			fx.spawn_a(x, gy, y, (randf() - 0.5) * 40.0 - k.wall_n.x * 30.0, 10.0 + randf() * 25.0, (randf() - 0.5) * 40.0 - k.wall_n.y * 30.0, Color("#ffd36b") if i % 2 == 1 else Color("#ffffff"), 1.6, 0.3, 0.3, 60.0, 1.0)
	elif e == "land":
		for i in 10:
			var a := randf() * TAU
			fx.spawn_n(k.x + cos(a) * 4.0, k.wy + 1.0, k.y + sin(a) * 4.0, cos(a) * 18.0, 4.0 + randf() * 6.0, sin(a) * 18.0, Color("#f2e3c4"), 3.0, 9.0, 0.7, -1.0, 2.0)
	elif e == "respawn":
		fx.ring(k.x, k.wy + 0.6, k.y, Color("#7fe8ff"), 40.0, 0.6)
	elif e == "bump":
		fx.burst(k.x, k.wy + 6.0, k.y, 8, _cols(["#fff4dc", "#ffe066"]), 30.0, 2.0)


# ---------------------------------------------------------------- traffic, walkers, rolling meatballs, the train (web renderHazards)

## the boost pads: holographic strips laid on the road (web strip() + holoPadMat), which the track export can't carry
func build_pads() -> void:
	for n in pad_nodes:
		(n as Node).queue_free()
	pad_nodes.clear()
	var sh: Shader = load("res://shaders/holopad.gdshader")
	var mats: Array = []
	for v in 3:
		var m := ShaderMaterial.new()
		m.shader = sh
		m.set_shader_parameter("uV", float(v))
		mats.append(m)
	var pi := 0
	for pd in T.pads:
		var p: Dictionary = pd
		var j := int(p["j"])
		var w := float(p.get("w", 16.0))
		var lat := float(p.get("lat", 0.0))
		var loop_pad := w > 30.0
		var j0 := j - 2 if not loop_pad else j - 2
		var j1 := j + 2
		var mat: ShaderMaterial = mats[0] if loop_pad else mats[pi % 3]
		if not loop_pad:
			pi += 1
		var mesh := _strip(j0, j1, lat - w, lat + w, 0.12 if not loop_pad else 0.1, 32.0)
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mi)
		pad_nodes.append(mi)


## web strip(): a ribbon along the track from point j0 to j1, o0..o1 to the side, y above the ground
func _strip(j0: int, j1: int, o0: float, o1: float, y: float, v_len: float) -> ArrayMesh:
	var cnt := j1 - j0
	var M := maxi(1, int(round(absf(o1 - o0) / 9.0)))
	var W := M + 1
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var idx := PackedInt32Array()
	for k in cnt + 1:
		var j := posmod(j0 + k, T.N)
		var v := (k * T.L / T.N) / v_len
		var pe: float = T.ey[j] if T.multi else 0.0
		for m in M + 1:
			var o := o0 + (o1 - o0) * m / M
			var x: float = T.px[j] + T.nx[j] * o
			var z: float = T.py[j] + T.ny[j] * o
			verts.append(Vector3(x, y + T.ground(x, z) + pe, z))
			uvs.append(Vector2(float(m) / M, v))
		if k < cnt:
			for m in M:
				var a := k * W + m
				idx.append_array([a, a + W, a + 1, a + 1, a + W, a + W + 1])
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_INDEX] = idx
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return am


## copies the hazard models (from <map>_haz.glb) once per race
func build_world_haz(lib: Node3D) -> void:
	for key in whaz:
		for h in whaz[key]:
			(h["n"] as Node).queue_free()
		whaz[key] = []
	if lib == null:
		return
	var hd: Dictionary = T.haz
	var tl: Array = hd.get("traffic", [])
	for i in race.traffic.size():
		var src := lib.find_child("traffic%d" % i, true, false) as Node3D
		if src == null:
			break
		var n := src.duplicate() as Node3D
		add_child(n)
		var sc := float((tl[i] as Dictionary).get("scale", 1.0)) if i < tl.size() else 1.0
		n.scale = Vector3.ONE * sc
		var wl: Array = []
		var wd: Array = (tl[i] as Dictionary).get("wheels", []) if i < tl.size() else []
		for j in wd.size():
			var wn := n.find_child("w%d" % j, false, false) as Node3D
			if wn != null:
				wl.append({"n": wn, "r": float((wd[j] as Dictionary)["r"])})
		whaz["traffic"].append({"n": n, "wheels": wl})
	var rsrc := lib.find_child("roller", true, false) as Node3D
	if rsrc != null:
		for r in race.rollers:
			var n2 := rsrc.duplicate() as Node3D
			add_child(n2)
			whaz["rollers"].append({"n": n2})
	for i in race.walkers.size():
		var src2 := lib.find_child("walk%d" % i, true, false) as Node3D
		if src2 == null:
			break
		var n3 := src2.duplicate() as Node3D
		add_child(n3)
		var legs: Array = []
		for j in 4:
			var ln := n3.find_child("leg%d" % j, false, false) as Node3D
			if ln != null:
				legs.append(ln)
		_seat_body(n3, legs)
		whaz["walk"].append({"n": n3, "legs": legs})
	if not race.train.is_empty():
		var cars: Array = (hd.get("train", {}) as Dictionary).get("cars", [])
		for i in cars.size():
			var src3 := lib.find_child("wagon%d" % i, true, false) as Node3D
			if src3 == null:
				break
			var n4 := src3.duplicate() as Node3D
			add_child(n4)
			n4.scale = Vector3.ONE * float((cars[i] as Dictionary).get("scale", 1.0))
			n4.visible = false
			whaz["wagons"].append({"n": n4})


## a critter's body sits on its legs: on some tracks the exported body (its finished, rounded version) came out
## higher than the legs' tops, leaving a gap between the legs and the head
func _seat_body(n: Node3D, legs: Array) -> void:
	var body := n.find_child("body", false, false) as Node3D
	if body == null or legs.is_empty():
		return
	var bmin := _min_y(body)
	var ltop := -1e9
	for l in legs:
		ltop = maxf(ltop, _max_y(l as Node3D))
	if bmin > -1e8 and ltop > -1e8 and bmin > ltop - 0.6:
		body.position.y -= bmin - (ltop - 0.6)


static func _min_y(n: Node3D) -> float:
	var y := 1e9
	for m in ([n] if n is MeshInstance3D else []) + n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh != null:
			var ab := (n.transform * (Transform3D.IDENTITY if mi == n else Menu._rel_xf(mi, n))) * mi.mesh.get_aabb()
			y = minf(y, ab.position.y)
	return y if y < 1e8 else -1e9


static func _max_y(n: Node3D) -> float:
	var y := -1e9
	for m in ([n] if n is MeshInstance3D else []) + n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh != null:
			var ab := (n.transform * (Transform3D.IDENTITY if mi == n else Menu._rel_xf(mi, n))) * mi.mesh.get_aabb()
			y = maxf(y, ab.end.y)
	return y


func _draw_world_haz(dt: float) -> void:
	var tl: Array = whaz["traffic"]
	for i in mini(tl.size(), race.traffic.size()):
		var c: Dictionary = race.traffic[i]
		var n: Node3D = tl[i]["n"]
		n.visible = not bool(c["hide"])
		if not n.visible:
			continue
		n.position = Vector3(float(c["x"]), T.ground(float(c["x"]), float(c["y"])), float(c["y"]))
		n.rotation = Vector3(0.0, -float(c["ang"]), 0.0)
		for w in tl[i]["wheels"]:
			var wn: Node3D = w["n"]
			wn.rotation.z -= float(c["v"]) * dt / (float(w["r"]) * KS * 1.05)
	var rl: Array = whaz["rollers"]
	for i in mini(rl.size(), race.rollers.size()):
		var r: Dictionary = race.rollers[i]
		var j: int = r["j"]
		var n2: Node3D = rl[i]["n"]
		n2.position = Vector3(float(r["x"]), T.ground(float(r["x"]), float(r["y"])) + 8.0, float(r["y"]))
		n2.quaternion = Quaternion(Vector3(T.tx[j], 0.0, T.ty[j]).normalized(), -float(r["lat"]) / 8.0)
	var wl: Array = whaz["walk"]
	for i in mini(wl.size(), race.walkers.size()):
		var w2: Dictionary = race.walkers[i]
		var n3: Node3D = wl[i]["n"]
		var paused_w := float(w2["pause"]) > 0.0
		var ph: float = w2["ph"]
		n3.position = Vector3(float(w2["x"]), T.ground(float(w2["x"]), float(w2["y"])) + absf(sin(time * 9.0 + ph)) * (0.3 if paused_w else 1.6), float(w2["y"]))
		var rz := sin(time * 40.0) * 0.3 if float(w2["hit_t"]) > 0.0 else 0.0
		n3.rotation = Vector3(0.0, -float(w2["face"]), rz)
		var li := 0
		for l in wl[i]["legs"]:
			var ln: Node3D = l
			ln.rotation.z = sin(time * 10.0 + li * PI) * (0.15 if paused_w else 0.7)
			li += 1
	var gl: Array = whaz["wagons"]
	if not race.train.is_empty():
		var tr: Dictionary = race.train
		var cars: Array = tr["cars"]
		for i in mini(gl.size(), cars.size()):
			var c2: Dictionary = cars[i]
			var n4: Node3D = gl[i]["n"]
			var t: float = c2["t"]
			n4.visible = tr["state"] == "run" and absf(t) < float(tr["span"]) - 6.0
			if not n4.visible:
				continue
			var x := float(tr["px"]) + float(tr["ux"]) * t
			var y := float(tr["py"]) + float(tr["uy"]) * t
			n4.position = Vector3(x, T.ground(x, y) + 1.6, y)
			n4.rotation = Vector3(0.0, -atan2(float(tr["uy"]), float(tr["ux"])) + (PI if float(tr["dir"]) > 0.0 else 0.0), 0.0)


## the glide rings: a bright torus 15 across, standing across the glide line, gently breathing; the height follows the
## race's floating ring heights (they meet the player's glide line)
func _draw_rings() -> void:
	var R := race.rings()
	if R.is_empty():
		return
	if ring_nodes.size() != R.size():
		for n in ring_nodes:
			(n as Node).queue_free()
		ring_nodes.clear()
		var tm := TorusMesh.new()
		tm.inner_radius = 15.0 - 1.1
		tm.outer_radius = 15.0 + 1.1
		tm.rings = 44
		tm.ring_segments = 10
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color("#7fe8ff")
		for r in R:
			var mi := MeshInstance3D.new()
			mi.mesh = tm
			mi.material_override = mat
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			# three's torus stands in its XY plane, Godot's lies in XZ: stand it up, then turn it to the glide (web rotation.y)
			mi.set_meta("basis", Basis(Vector3.UP, float(r[3]) if (r as Array).size() > 3 else 0.0) * Basis(Vector3.RIGHT, PI / 2.0))
			add_child(mi)
			ring_nodes.append(mi)
	for i in R.size():
		var mi: MeshInstance3D = ring_nodes[i]
		var r: Array = R[i]
		var yy := float(race.ring_y[i]) if i < race.ring_y.size() else float(r[1])
		var sc := 1.0 + sin(time * 4.0 + float(i)) * 0.05
		mi.transform = Transform3D((mi.get_meta("basis") as Basis).scaled(Vector3(sc, sc, sc)), Vector3(float(r[0]), yy, float(r[2])))


func race_event(ed: Dictionary) -> void:
	var t: String = ed["t"]
	if t == "ring":
		fx.ring(float(ed["x"]), float(ed["y"]), float(ed["z"]), Color("#7fe8ff"), 30.0, 0.5, false)
		return
	if t == "hzbump":
		var kb: Kart = ed["k"]
		fx.burst(kb.x, kb.wy + 6.0, kb.y, 10, _cols(["#fff4dc", "#ffe066"]), 40.0, 2.2)
	elif t == "spin":
		var k: Kart = ed["k"]
		var cols := _cols(HITC.get(String(ed["kind"]), ["#fff4dc", "#ffe066", "#ff3b1a"]))
		var y := k.wy + 6.0 * KS
		fx.burst(k.x, y, k.y, 34, cols, 70.0, 3.4)
		for i in 12:
			var a := float(i) / 12.0 * TAU
			fx.spawn_a(k.x, y, k.y, cos(a) * 90.0, 8.0, sin(a) * 90.0, Color("#ffffff"), 2.4, 0.3, 0.35, 0.0, 4.0)
		for i in 8:
			var a2 := randf() * TAU
			fx.spawn_n(k.x + cos(a2) * 3.0, k.wy + 2.0, k.y + sin(a2) * 3.0, cos(a2) * 14.0, 6.0 + randf() * 8.0, sin(a2) * 14.0, Color("#fff4dc") if String(ed["kind"]) == "dough" else Color("#d8d0c4"), 4.0, 14.0, 0.9, -2.0, 1.5)
		fx.spawn_a(k.x, y, k.y, 0, 0, 0, Color("#ffffff"), 30.0, 6.0, 0.18)
		fx.ring(k.x, k.wy + 0.6, k.y, cols[0], 34.0, 0.55)
		fx.ring(k.x, y, k.y, Color("#ffffff"), 20.0, 0.35, false)
	elif t == "box":
		var bx := float(ed["x"])
		var by := float(ed["y"])
		var h := float(ed["h"])
		fx.burst(bx, h + 6.0, by, 26, _cols(["#ffe066", "#e0452c", "#fff4dc", "#7fd0ff"]), 60.0, 2.4)
		var cols2 := _cols(["#ffe066", "#e0452c", "#fff4dc", "#7fd0ff", "#3f9a35"])
		var Y := h + 7.0
		fx.burst(bx, Y, by, 40, cols2, 85.0, 2.6)
		for i in 16:
			var a3 := randf() * TAU
			var u := 0.4 + randf() * 0.6
			fx.spawn_a(bx, Y, by, cos(a3) * 50.0 * u, 40.0 + randf() * 50.0, sin(a3) * 50.0 * u, Color("#f5ead2") if i % 2 == 1 else Color("#d6402a"), 3.0, 1.5, 0.9, 90.0, 0.6)
		fx.spawn_a(bx, Y, by, 0, 0, 0, Color("#fff6c8"), 40.0, 8.0, 0.22)
		fx.ring(bx, h + 0.5, by, Color("#ffd24a"), 26.0, 0.5)
		fx.ring(bx, Y, by, Color("#ffffff"), 14.0, 0.3, false)
	elif t == "use":
		var k2: Kart = ed["k"]
		var col: Color = ITEM_COL.get(String(ed["it"]), Color(String(Race.ITEM_COL2.get(String(ed["it"]), "#ffe066"))))
		var gy := k2.wy + 7.0
		fx.spawn_a(k2.x, gy, k2.y, 0, 0, 0, col, 30.0, 8.0, 0.18)
		fx.ring(k2.x, k2.wy + 0.6, k2.y, col, 26.0, 0.35)
		for n in 10:
			var a4 := randf() * TAU
			fx.spawn_a(k2.x, gy, k2.y, cos(a4) * 40.0, 15.0 + randf() * 25.0, sin(a4) * 40.0, col, 2.2, 0.4, 0.3, 40.0, 1.0)
	elif t == "shield":
		var k3: Kart = ed["k"]
		fx.ring(k3.x, k3.wy + 0.6, k3.y, Color("#7fe07a"), 44.0, 0.6)
		fx.burst(k3.x, k3.wy + 7.0, k3.y, 24, _cols(["#7fe07a", "#f4ecdc", "#ffffff"]), 60.0, 2.4)
	elif t == "unshield":
		var k4: Kart = ed["k"]
		fx.burst(k4.x, k4.wy + 7.0, k4.y, 40, _cols(["#7fe07a", "#f4ecdc", "#ffffff"]), 110.0, 3.2)
		fx.ring(k4.x, k4.wy + 7.0, k4.y, Color("#c8ffc0"), 60.0, 0.5)
	elif t == "absorb":
		var hx := float(ed["x"])
		var hy := float(ed["y"])
		var g2 := T.ground(hx, hy) + 3.0
		fx.burst(hx, g2 - 1.0, hy, 14, _cols(["#ffe066", "#fff4dc", "#e0452c"]), 50.0, 2.0)
		fx.burst(hx, g2, hy, 10, _cols(["#ffffff"]), 35.0, 1.5)
	elif t == "flour":
		var fx_ := float(ed["x"])
		var fy := float(ed["y"])
		var g3 := T.ground(fx_, fy)
		for n in 26:
			var a5 := randf() * TAU
			var u2 := 0.3 + randf() * 0.7
			fx.spawn_n(fx_ + cos(a5) * 6.0, g3 + 4.0, fy + sin(a5) * 6.0, cos(a5) * 60.0 * u2, 10.0 + randf() * 24.0, sin(a5) * 60.0 * u2, Color("#f6f1e6"), 8.0, 26.0, 1.4, -3.0, 1.2)
		fx.ring(fx_, g3 + 0.8, fy, Color("#ffffff"), 50.0, 0.6)
		fx.spawn_a(fx_, g3 + 6.0, fy, 0, 0, 0, Color("#ffffff"), 46.0, 10.0, 0.2)
	elif t == "clash":
		var cx := float(ed["x"])
		var cy := float(ed["y"])
		var g4 := T.ground(cx, cy) + 6.0
		fx.burst(cx, g4, cy, 26, _cols(["#ffe066", "#ff8a1f", "#ffffff"]), 90.0, 3.0)
		fx.ring(cx, g4 - 5.0, cy, Color("#ffcf6a"), 30.0, 0.4)
	elif t == "bump":
		var cl: float = ed["cl"]
		var mx := float(ed["x"])
		var my := float(ed["y"])
		var gy2 := float(ed["h"])
		var a6: Kart = ed["a"]
		var b6: Kart = ed["b"]
		var d := Vector2(b6.x - a6.x, b6.y - a6.y).normalized()
		var n0 := mini(14, 6 + int(cl / 12.0))
		for q in n0:
			var an := randf() * 6.283
			var spd := 40.0 + randf() * 70.0
			fx.spawn_a(mx, gy2, my, cos(an) * spd + d.y * 30.0 * (randf() - 0.5), 15.0 + randf() * 45.0, sin(an) * spd - d.x * 30.0 * (randf() - 0.5), Color("#ffd36b") if q % 3 != 0 else Color("#ffffff"), 1.7, 0.3, 0.22, 90.0, 1.0)
		fx.spawn_a(mx, gy2, my, 0, 0, 0, Color("#fff2c8"), 9.0, 3.0, 0.12)
	elif t == "slice":
		var k5: Kart = ed["k"]
		var gy3 := k5.wy
		fx.ring(k5.x, gy3 + 0.6, k5.y, Color("#ff3b1a"), 80.0, 0.8)
		fx.ring(k5.x, gy3 + 8.0, k5.y, Color("#ffffff"), 46.0, 0.45, false)
		fx.burst(k5.x, gy3 + 8.0, k5.y, 56, _cols(["#ff3b1a", "#ffe066", "#ffffff", "#e9ecef"]), 130.0, 4.2)
	elif t == "oily":
		var k6: Kart = ed["k"]
		fx.burst(k6.x, k6.wy + 3.0, k6.y, 30, _cols(["#c8b23a", "#8a7a1c", "#fff3b0"]), 70.0, 2.8)
		fx.ring(k6.x, k6.wy + 0.6, k6.y, Color("#c8b23a"), 38.0, 0.45)
	elif t == "ability":
		# web itemFx(k, colour, 50) plus a wide ring on the ground
		var ka: Kart = ed["k"]
		var A: Array = Race.ABIL.get(String(ed["id"]), ["", "", "#ffe066"])
		var ac := Color(String(A[2]))
		var agy := ka.wy + 7.0
		fx.ring(ka.x, ka.wy + 0.6, ka.y, ac, 40.0, 0.5)
		fx.ring(ka.x, agy, ka.y, Color.WHITE, 22.0, 0.3, false)
		fx.burst(ka.x, agy, ka.y, 50, [ac, Color.WHITE, Color("#ffe066")], 90.0, 3.0)
		fx.spawn_a(ka.x, agy, ka.y, 0, 0, 0, ac, 40.0, 8.0, 0.22, 0.0, 0.0)
		fx.ring(ka.x, ka.wy + 0.6, ka.y, ac, 70.0, 0.8)
	elif t == "melt":
		var km: Kart = ed["k"]
		var mgy := km.wy + 7.0
		fx.burst(km.x, mgy, km.y, 30, _cols(["#fbf5e6", "#fff2cf", "#ffffff"]), 90.0, 2.8)
		fx.ring(km.x, mgy, km.y, Color("#fff2cf"), 50.0, 0.45)
	elif t == "flat":
		var kf: Kart = ed["k"]
		var fgy := kf.wy + 0.6
		fx.ring(kf.x, fgy, kf.y, Color("#c8a06a"), 46.0, 0.5)
		fx.burst(kf.x, fgy + 2.0, kf.y, 26, _cols(["#efe3cb", "#c8a06a", "#ffffff"]), 70.0, 3.0)
	elif t == "blast":
		var bx2 := float(ed["x"])
		var by2 := float(ed["y"])
		var br := float(ed["r"])
		var bcol := Color(String(ed["col"]))
		var bgy := T.ground(bx2, by2)
		var sc := maxf(1.0, br / 130.0)
		fx.burst(bx2, bgy + 6.0, by2, int(round(60.0 * sc)), [bcol, Color("#ffe066"), Color.WHITE, Color("#ff5a14")], 140.0 * sc, 4.2 * sc)
		for n in int(round(24.0 * sc)):
			var ba := randf() * TAU
			var bu := 0.3 + randf() * 0.7
			fx.spawn_n(bx2 + cos(ba) * 6.0, bgy + 4.0, by2 + sin(ba) * 6.0, cos(ba) * 70.0 * bu, 14.0 + randf() * 30.0, sin(ba) * 70.0 * bu, Color("#5a4a3a"), 9.0, 28.0, 1.4, -3.0, 1.2)
		fx.ring(bx2, bgy + 0.8, by2, bcol, br * 1.3, 0.7 + 0.3 * (sc - 1.0))
		fx.ring(bx2, bgy + 8.0, by2, Color.WHITE, br, 0.4 + 0.2 * (sc - 1.0), false)
		if sc > 1.5:
			fx.ring(bx2, bgy + 16.0, by2, bcol, br * 0.8, 0.9, false)
		fx.spawn_a(bx2, bgy + 8.0, by2, 0, 0, 0, Color("#fff2c8"), 70.0 * sc, 12.0 * sc, 0.25, 0.0, 0.0)
	elif t == "frozen":
		var kz: Kart = ed["k"]
		fx.burst(kz.x, kz.wy + 6.0, kz.y, 18, _cols(["#bfe6ff", "#ffffff", "#7fd0ff"]), 50.0, 2.6)
		fx.ring(kz.x, kz.wy + 0.6, kz.y, Color("#8fd8ff"), 26.0, 0.5)
	elif t == "sauced":
		var ks: Kart = ed["k"]
		fx.burst(ks.x, ks.wy + 8.0, ks.y, 26, _cols(["#d8301c", "#a8180a", "#ff6a3a"]), 70.0, 3.2)
		fx.ring(ks.x, ks.wy + 0.6, ks.y, Color("#d8301c"), 24.0, 0.5)
	elif t == "swap":
		for q in [ed["k"], ed["by"]]:
			var kq: Kart = q
			fx.ring(kq.x, kq.wy + 0.6, kq.y, Color("#b26bff"), 40.0, 0.6)
			fx.burst(kq.x, kq.wy + 8.0, kq.y, 30, _cols(["#b26bff", "#ffe066", "#ffffff"]), 80.0, 3.0)
	elif t == "cutblock":
		fx.burst(float(ed["x"]), 8.0 + T.ground(float(ed["x"]), float(ed["y"])), float(ed["y"]), 14, _cols(["#ffffff", "#d8dde3"]), 60.0, 2.0)
	elif t == "ricochet":
		var rx2 := float(ed["x"])
		var ry2 := float(ed["y"])
		fx.burst(rx2, T.ground(rx2, ry2) + 6.0, ry2, 10, _cols(["#ff5a2a", "#ffe066", "#ffffff"]), 60.0, 2.0)
