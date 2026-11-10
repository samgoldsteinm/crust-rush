class_name KartBuilder
extends RefCounted
## Builds any kart the web game's garage can make, from parts exported by tools/rungarage.py:
## a body (paint, dark trim and stripe kept as their own materials), a wheel type, a glider and a
## driver, placed where the web's buildKart puts them for that body and wheel. Recolours the paint
## for the chosen paint or livery (shaders/livery.gdshader runs the web's livery patterns).
## Also works out the build's stats the way the web does (statMods) for the physics.

const DIR := "res://assets/garage/"

static var info := {}
static var _scenes := {}
static var _tex := {}


static func ready() -> bool:
	if not info.is_empty():
		return true
	var p := DIR + "garage.json"
	if not FileAccess.file_exists(p):
		return false
	var j = JSON.parse_string(FileAccess.get_file_as_string(p))
	if typeof(j) != TYPE_DICTIONARY:
		return false
	info = j
	return true


static func _scene(file: String) -> Node3D:
	if not _scenes.has(file):
		var ps: PackedScene = load(DIR + file) if ResourceLoader.exists(DIR + file) else null
		_scenes[file] = ps
	var ps2: PackedScene = _scenes[file]
	return ps2.instantiate() as Node3D if ps2 != null else null


static func _texture(name_: String) -> Texture2D:
	if not _tex.has(name_):
		_tex[name_] = load(DIR + name_) if ResourceLoader.exists(DIR + name_) else null
	return _tex[name_]


## the web's shade(hex, amt): towards black (amt < 0) or white
static func shade(c: Color, amt: float) -> Color:
	var tg := 0.0 if amt < 0.0 else 1.0
	var a := absf(amt)
	return Color(roundf((c.r + (tg - c.r) * a) * 255.0) / 255.0, roundf((c.g + (tg - c.g) * a) * 255.0) / 255.0, roundf((c.b + (tg - c.b) * a) * 255.0) / 255.0)


static func livery(id: String) -> Dictionary:
	if id == "":
		return {}
	for l in info.get("liveries", []):
		if l["id"] == id:
			return l
	return {}


## liveries this body can wear (web liveriesFor)
static func liveries_for(body_id: String) -> Array:
	var out: Array = []
	for l in info.get("liveries", []):
		var only = l.get("only")
		if only == null or String(only) == body_id:
			out.append(l)
	return out


## web randomBuild: a rival's kart for this race (or Grand Prix): any body, usually standard wheels,
## any glider, mostly their own colour, sometimes a livery that isn't a reward
static func random_build() -> Dictionary:
	if not ready():
		return {}
	var nb := (info["bodies"] as Array).size()
	var b := randi() % nb
	var lv: Array = []
	for l in liveries_for(String(info["bodies"][b]["id"])):
		if l.get("lock") == null or not l.get("lock"):
			lv.append(l)
	var np := (info.get("paints", []) as Array).size()
	return {"b": b, "w": 0 if randf() < 0.35 else randi() % (info["wheels"] as Array).size(), "g": randi() % (info["gliders"] as Array).size(),
		"p": 0 if randf() < 0.65 or np < 2 else 1 + randi() % (np - 1), "t": String(lv[randi() % lv.size()]["id"]) if randf() < 0.45 and not lv.is_empty() else ""}


static func wheel_of(spec: Dictionary) -> Dictionary:
	var bd: Dictionary = info["bodies"][int(spec["b"])]
	if bool(bd.get("bike", false)) and bd.get("bw") != null:
		for w in info["wheels"]:
			if w["id"] == bd["bw"]:
				return w
	return info["wheels"][clampi(int(spec.get("w", 0)), 0, (info["wheels"] as Array).size() - 1)]


## the web's statMods: body counts most, wheels less, the glider a little, soft-capped
static func stat_mods(spec: Dictionary) -> Dictionary:
	var W: Array = info.get("statW", [1.5, 1.0, 0.5])
	var o := [0.0, 0.0, 0.0, 0.0, 0.0]
	var parts_ := [info["bodies"][int(spec["b"])], wheel_of(spec), info["gliders"][int(spec.get("g", 0))]]
	for k in 3:
		var st: Array = parts_[k]["st"]
		for i in 5:
			o[i] += float(st[i]) * float(W[k])
	var e: Array = []
	for i in 5:
		e.append(4.0 * tanh(o[i] / 4.0))
	return {"spd": 1.0 + 0.022 * e[0], "acc": maxf(0.62, 1.0 + 0.09 * e[1]), "hnd": 1.0 + 0.05 * e[2], "wgt": 1.0 + 0.12 * e[3], "off": e[4] * 0.9}


## the 0..12 bars the garage shows (web STAT_MID 6, body/wheel/glider weighted)
static func stat_bars(spec: Dictionary) -> Array:
	var W: Array = info.get("statW", [1.5, 1.0, 0.5])
	var o := [0.0, 0.0, 0.0, 0.0, 0.0]
	var parts_ := [info["bodies"][int(spec["b"])], wheel_of(spec), info["gliders"][int(spec.get("g", 0))]]
	for k in 3:
		var st: Array = parts_[k]["st"]
		for i in 5:
			o[i] += float(st[i]) * float(W[k])
	var out: Array = []
	for i in 5:
		out.append(clampi(int(round(6.0 + 4.0 * tanh(o[i] / 4.0) * 1.5)), 0, 12))
	return out


## the colours a build wears: paint, dark trim, stripe (web buildKart's M.paint / M.dark / M.stripe)
static func colours(spec: Dictionary, ri: int) -> Dictionary:
	var rc: Dictionary = info["racers"][ri]
	var lv := livery(String(spec.get("t", "")))
	var paints: Array = info.get("paints", [])
	var p := int(spec.get("p", 0))
	var col := Color(String(rc["color"]))
	if not lv.is_empty():
		col = Color(String(lv["A"]))
	elif p > 0 and p < paints.size() and paints[p] != null:
		col = Color(String(paints[p]))
	var dark := Color(String(lv["C"])) if not lv.is_empty() else shade(col, -0.45)
	var stripe := Color(String(rc["stripe"]))
	if not lv.is_empty():
		stripe = Color(String(lv["B"]))
	elif Color(String(rc["stripe"])).to_html(false) == col.to_html(false):
		stripe = Color(String(rc["top"]))
	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv}


static func _mat4(a: Array) -> Transform3D:
	# three.js Matrix4.toArray(): column-major
	return Transform3D(Basis(Vector3(a[0], a[1], a[2]), Vector3(a[4], a[5], a[6]), Vector3(a[8], a[9], a[10])), Vector3(a[12], a[13], a[14]))


## what the race needs to know about a build without making its model: {meta, sm, glider}
static func describe(spec: Dictionary, ri: int) -> Dictionary:
	if not ready():
		return {}
	var b := clampi(int(spec.get("b", 0)), 0, (info["bodies"] as Array).size() - 1)
	var bd: Dictionary = info["bodies"][b]
	var wd := wheel_of(spec)
	var w := (info["wheels"] as Array).find(wd)
	var gi := clampi(int(spec.get("g", 0)), 0, (info["gliders"] as Array).size() - 1)
	var pl: Dictionary = info["placeBW"][b][w]
	var wl: Array = []
	for q in pl["wheels"]:
		var z := float(q["z"])
		wl.append({"name": "wheel_" + ("F" if bool(q["front"]) else "R") + ("L" if z < 0.0 else "R"), "front": bool(q["front"]), "x": float(q["x"]), "y": float(q["y"]), "z": z, "r": float(q["r"])})
	var sf := float(bd.get("sf", 1.0))
	var meta := {"scale": 1.76 * sf, "sf": sf, "wheels": wl, "top": float(pl["top"]), "axF": float(pl["axF"]), "axR": float(pl["axR"]), "axW": float(pl["axW"]),
		"hover": float(pl.get("hover", 0.0)), "bike": bool(pl.get("bike", false)), "fxL": pl.get("fxL", []), "fxP": pl.get("fxP", []), "smoke": pl.get("smoke"), "bub": pl.get("bub"),
		"flames": pl.get("flames", []), "glY": float(pl.get("glY", 0.0)), "spec": spec}
	var gd: Dictionary = info["gliders"][gi]
	return {"meta": meta, "sm": stat_mods(spec), "glider": {"id": gd["id"], "sink": gd["sink"], "air": gd["air"]}, "spec": spec, "body": bd["id"], "bodyName": bd["name"]}


## the kart for one build and driver. Returns {node, meta, sm, glider, glider_node}
static func build(spec: Dictionary, ri: int) -> Dictionary:
	if not ready():
		return {}
	var b := clampi(int(spec.get("b", 0)), 0, (info["bodies"] as Array).size() - 1)
	var bd: Dictionary = info["bodies"][b]
	var wd := wheel_of(spec)
	var w := (info["wheels"] as Array).find(wd)
	var gi := clampi(int(spec.get("g", 0)), 0, (info["gliders"] as Array).size() - 1)
	var pl: Dictionary = info["placeBW"][b][w]
	var pl0: Dictionary = info["placeBW"][b][0]
	var lift := float(pl["L"]) - float(pl0["L"])
	var cols := colours(spec, ri)
	var root := Node3D.new()
	root.name = "kart"
	# the body (exported on its standard wheels: lift it for bigger ones)
	var bsrc := _scene("body_%s.glb" % bd["id"])
	var body: Node3D = null
	if bsrc != null:
		body = bsrc.find_child("body", true, false) as Node3D
		if body != null:
			body = body.duplicate() as Node3D
			body.position = Vector3(0, lift, 0)
			root.add_child(body)
	var liv = (info.get("liv", []) as Array)[b] if b < (info.get("liv", []) as Array).size() else null
	if body != null:
		_paint(body, cols, liv, ri)
	# wheels: the body's own (cars on standard wheels, bikes) or the chosen wheel type
	var meta_wheels: Array = []
	var wsrc := _scene("wheel_%s.glb" % wd["id"])
	for q in pl["wheels"]:
		var wq: Dictionary = q
		var z := float(wq["z"])
		var nm := "wheel_" + ("F" if bool(wq["front"]) else "R") + ("L" if z < 0.0 else "R")
		var yaw := Node3D.new()
		yaw.name = nm
		yaw.position = Vector3(float(wq["x"]), float(wq["y"]), z)
		root.add_child(yaw)
		var own := String(wd["id"]) == "standard" and bsrc != null and bsrc.find_child("pw%d" % int(wq["i"]), true, false) != null and (bool(bd.get("car", false)) or bool(bd.get("bike", false)))
		var wm: Node3D = null
		if own:
			wm = (bsrc.find_child("pw%d" % int(wq["i"]), true, false) as Node3D).duplicate() as Node3D
			wm.transform = Transform3D.IDENTITY
		elif wsrc != null:
			var src := wsrc.find_child("wheel_" + ("L" if z < 0.0 else "R"), true, false) as Node3D
			if src == null:
				src = wsrc.find_child("wheel_R", true, false) as Node3D
			if src != null:
				wm = src.duplicate() as Node3D
				var sc: Array = wq["s"]
				wm.transform = Transform3D(Basis.from_scale(Vector3(sc[0], sc[1], sc[2])), Vector3.ZERO)
		if wm != null:
			yaw.add_child(wm)
			_paint(wm, cols, null, ri)
		meta_wheels.append({"name": nm, "front": bool(wq["front"]), "x": float(wq["x"]), "y": float(wq["y"]), "z": z, "r": float(wq["r"])})
	# the driver in their seat
	var dsrc := _scene("driver_%d.glb" % ri)
	if dsrc != null:
		var dn := dsrc.find_child("driver", true, false) as Node3D
		if dn != null:
			dn = dn.duplicate() as Node3D
			var xf := _mat4(info["placeDrv"][b][ri])
			xf.origin.y += lift
			dn.transform = xf
			root.add_child(dn)
			_paint(dn, cols, null, ri)   # vertex colours on (the importer leaves them off)
	# the glider, folded away until a glide
	var glider: Node3D = null
	var gsrc := _scene("glider_%s.glb" % info["gliders"][gi]["id"])
	if gsrc != null:
		var gn := gsrc.find_child("glider", true, false) as Node3D
		if gn != null:
			glider = gn.duplicate() as Node3D
			glider.position = Vector3(0, float(pl["glY"]), 0)
			glider.visible = false
			_paint(glider, cols, null, ri, true)
	for c in [bsrc, wsrc, dsrc, gsrc]:
		if c != null:
			(c as Node).free()
	var sf := float(bd.get("sf", 1.0))
	var meta := {"scale": 1.76 * sf, "sf": sf, "wheels": meta_wheels, "top": float(pl["top"]), "axF": float(pl["axF"]), "axR": float(pl["axR"]), "axW": float(pl["axW"]),
		"hover": float(pl.get("hover", 0.0)), "bike": bool(pl.get("bike", false)), "fxL": pl.get("fxL", []), "fxP": pl.get("fxP", []), "smoke": pl.get("smoke"), "bub": pl.get("bub"),
		"flames": pl.get("flames", []), "spec": spec}
	var gd: Dictionary = info["gliders"][gi]
	return {"node": root, "meta": meta, "sm": stat_mods(spec), "glider": {"id": gd["id"], "sink": gd["sink"], "air": gd["air"]}, "glider_node": glider}


## recolour the exported marker materials: paint (or the livery), dark trim, stripe
static func _paint(n: Node, cols: Dictionary, liv, ri: int, cloth := false) -> void:
	var lv: Dictionary = cols["lv"]
	var meshes := n.find_children("*", "MeshInstance3D", true, false)
	if n is MeshInstance3D:
		meshes.push_front(n)   # the node itself (a body or wheel exported as one mesh)
	for mi in meshes:
		var m3 := mi as MeshInstance3D
		var mesh := m3.mesh
		if mesh == null:
			continue
		for si in mesh.get_surface_count():
			var sm := mesh.surface_get_material(si) as BaseMaterial3D
			if sm == null:
				continue
			var nm := _marker(sm)
			if (mesh.surface_get_format(si) & Mesh.ARRAY_FORMAT_COLOR) != 0 and not sm.vertex_color_use_as_albedo and not nm.begins_with("g_"):
				var c0 := sm.duplicate() as BaseMaterial3D
				c0.vertex_color_use_as_albedo = true
				m3.set_surface_override_material(si, c0)
			if nm.begins_with("g_paint"):
				var wrap: Texture2D = _texture("liv_%s.jpg" % String(lv["tex"])) if lv.has("tex") else null
				if wrap != null:
					# a wrap painted from a picture, on the body's own UVs (web liveryMaterial with lv.tex)
					var wm2 := StandardMaterial3D.new()
					wm2.albedo_texture = wrap
					wm2.vertex_color_use_as_albedo = true
					wm2.metallic = float(lv.get("m", 0.3))
					wm2.roughness = float(lv.get("r", 0.28))
					wm2.clearcoat_enabled = true
					wm2.clearcoat = 1.0
					wm2.clearcoat_roughness = 0.05
					wm2.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
					m3.set_surface_override_material(si, wm2)
				elif not lv.is_empty() and liv != null and not lv.has("tex"):
					m3.set_surface_override_material(si, _livery_mat(lv, liv, ri))
				else:
					var pm := StandardMaterial3D.new()
					pm.albedo_color = cols["paint"]
					pm.vertex_color_use_as_albedo = true
					pm.roughness = float(lv.get("r", 0.38)) if not lv.is_empty() else 0.38
					pm.metallic = minf(float(lv.get("m", 0.12)), 0.62) if not lv.is_empty() else 0.12
					pm.clearcoat_enabled = true
					pm.clearcoat = 1.0
					pm.clearcoat_roughness = 0.08
					m3.set_surface_override_material(si, pm)
			elif nm.begins_with("g_dark") or nm.begins_with("g_stripe"):
				var dm := StandardMaterial3D.new()
				var dark := nm.begins_with("g_dark")
				dm.albedo_color = cols["dark"] if dark else cols["stripe"]
				dm.vertex_color_use_as_albedo = true
				dm.roughness = 0.4 if dark else 0.3
				dm.metallic = 0.3 if dark else 0.1
				m3.set_surface_override_material(si, dm)
			elif cloth and sm.albedo_texture != null:
				m3.set_surface_override_material(si, _cloth(sm, cols))


## which marker a material is: kart bodies name theirs (g_paint, g_dark, g_stripe); the imported cars carry the marker colour
static func _marker(sm: BaseMaterial3D) -> String:
	var nm := String(sm.resource_name)
	if nm.begins_with("g_"):
		return nm
	var tags: Dictionary = info.get("mark", {}).get("tags", {})
	var c := sm.albedo_color
	for key in ["paint", "stripe", "dark"]:
		var t: PackedStringArray = String(tags.get(key, "")).split(",")
		if t.size() != 3:
			continue
		var lin := Color(float(t[0]) / 1000.0, float(t[1]) / 1000.0, float(t[2]) / 1000.0)
		var srgb := lin.linear_to_srgb()
		for want in [lin, srgb]:
			if absf(c.r - want.r) < 0.02 and absf(c.g - want.g) < 0.02 and absf(c.b - want.b) < 0.02:
				return "g_" + key
	return nm


static func _livery_mat(lv: Dictionary, liv: Dictionary, ri: int) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/livery.gdshader")
	m.set_shader_parameter("uLA", Color(String(lv["A"])))
	m.set_shader_parameter("uLB", Color(String(lv["B"])))
	m.set_shader_parameter("uLC", Color(String(lv["C"])))
	m.set_shader_parameter("uLPat", float(lv.get("pat", 1)))
	var box: Array = liv["box"]
	m.set_shader_parameter("uLBox", Vector4(box[0], box[1], box[2], box[3]))
	m.set_shader_parameter("uLBelt", float(liv["belt"]))
	m.set_shader_parameter("uLNum", float(ri) if bool(lv.get("num", false)) else -1.0)
	var np: Array = liv["numPos"]
	m.set_shader_parameter("uLNumPos", Vector2(np[0], np[1]))
	m.set_shader_parameter("uLNumTex", _texture("liv_num.png"))
	m.set_shader_parameter("uLDec", _texture("liv_dec.png"))
	var id := String(lv["id"])
	var h := _hash(id)
	var hw := _hash(id + "w")
	var dec := float(lv["dec"]) if lv.get("dec") != null else (-1.0 if h % 9 == 8 else float(h % 8))
	var word := float(lv["word"]) if lv.get("word") != null else (-1.0 if hw % 3 == 0 else float(hw % 8))
	m.set_shader_parameter("uLDecI", Vector3(dec, word, (float(box[1]) - float(box[0])) * 0.11))
	m.set_shader_parameter("uLQ", 2.0)
	var mm := float(lv.get("m", 0.3))
	var rr := float(lv.get("r", 0.3))
	var chrome := bool(lv.get("chrome", false)) or id == "chrome"
	m.set_shader_parameter("uLFl", 0.35 if chrome else minf(0.85, maxf(0.25, mm * 1.3)) * (0.55 if rr > 0.6 else 1.0))
	m.set_shader_parameter("metal", minf(mm, 0.92 if chrome else 0.62))
	m.set_shader_parameter("rough", rr)
	m.set_shader_parameter("coat", 1.0 if rr < 0.6 else 0.2)
	var xf := _mat4(liv["xf"])
	m.set_shader_parameter("liv_xf", Projection(xf))
	return m


## the web's hashS: h = h*31 + char, unsigned 32-bit, starting at 7
static func _hash(s: String) -> int:
	var h := 7
	for ch in s.to_utf8_buffer():
		h = (h * 31 + ch) & 0xffffffff
	return h


## glider cloth drawn in the marker colours: the PC recolours it with a small shader
static func _cloth(sm: BaseMaterial3D, cols: Dictionary) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/marker_tex.gdshader")
	m.set_shader_parameter("tex", sm.albedo_texture)
	m.set_shader_parameter("tint", sm.albedo_color)
	m.set_shader_parameter("mk_paint", Color(String(info["mark"]["paint"])))
	m.set_shader_parameter("mk_stripe", Color(String(info["mark"]["stripe"])))
	m.set_shader_parameter("mk_dark", Color(String(info["mark"]["dark"])))
	m.set_shader_parameter("c_paint", cols["paint"])
	m.set_shader_parameter("c_stripe", cols["stripe"])
	m.set_shader_parameter("c_dark", cols["dark"])
	m.set_shader_parameter("rough", sm.roughness)
	m.set_shader_parameter("double", sm.cull_mode == BaseMaterial3D.CULL_DISABLED)
	return m
