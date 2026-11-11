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
	_merge_pc()
	return true


## web liveries the PC's garage list leaves out (still drawn when a browser player or an old save uses one)
static var hidden := {}
## PC-only livery -> the web livery a browser player sees in its place
static var web_of := {}


## assets/liveries_pc.json: the PC's own liveries (patterns 67 on in shaders/livery.gdshader) and the plain web
## ones it leaves out of the list. The web's list has one id twice; the first wins, as the web's own lookup does.
static func _merge_pc() -> void:
	var seen := {}
	var out: Array = []
	for l in info.get("liveries", []):
		var id := String((l as Dictionary).get("id", ""))
		if seen.has(id):
			continue
		seen[id] = true
		out.append(l)
	var p := "res://assets/liveries_pc.json"
	if FileAccess.file_exists(p):
		var pj = JSON.parse_string(FileAccess.get_file_as_string(p))
		if pj is Dictionary:
			for id in (pj as Dictionary).get("hide", []):
				hidden[String(id)] = true
			for l in (pj as Dictionary).get("add", []):
				var d: Dictionary = (l as Dictionary).duplicate()
				var id2 := String(d.get("id", ""))
				if id2 == "" or seen.has(id2):
					continue
				seen[id2] = true
				d["pc"] = true
				web_of[id2] = String(d.get("web", ""))
				out.append(d)
	info["liveries"] = out


## the garage's list for a body: everything it can wear except the left-out web ones (the one on the car stays)
static func list_for(body_id: String, current := "") -> Array:
	var out: Array = []
	for l in liveries_for(body_id):
		var id := String(l["id"])
		if hidden.has(id) and id != current:
			continue
		out.append(l)
	return out


## a build as a browser sees it: a PC-only livery becomes its nearest web one (online rooms with web players)
static func web_build(b) -> Dictionary:
	if not (b is Dictionary):
		return {}
	var d: Dictionary = (b as Dictionary).duplicate()
	var t := String(d.get("t", ""))
	if web_of.has(t):
		d["t"] = String(web_of[t])
	return d


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
	for l in list_for(String(info["bodies"][b]["id"])):
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
static var stats_on := true   # Settings > Kart stats: off makes every part cosmetic


static func stat_mods(spec: Dictionary) -> Dictionary:
	if not stats_on:
		return {"spd": 1.0, "acc": 1.0, "hnd": 1.0, "wgt": 1.0, "off": 0.0}
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
	# hover bikes: the cyan glow pooled under them (web cfg.glow; the exporter leaves it out of the model)
	var hglow: MeshInstance3D = null
	if float(pl.get("hover", 0.0)) > 0.0 and body != null:
		hglow = _hover_glow(String(bd["id"]), body)
		if hglow != null:
			root.add_child(hglow)
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
		"flames": pl.get("flames", []), "spec": spec, "hglow": hglow}
	var gd: Dictionary = info["gliders"][gi]
	return {"node": root, "meta": meta, "sm": stat_mods(spec), "glider": {"id": gd["id"], "sink": gd["sink"], "air": gd["air"]}, "glider_node": glider}


static var _hg_cache := {}


## the web's hoverGlowFor: the body's outline seen from above, rasterised into a 128 x 64 grid, softened, and coloured
## from a white-cyan core to a blue fringe, on a flat additive sheet a little above the ground
static func _hover_glow(id: String, body: Node3D) -> MeshInstance3D:
	if not _hg_cache.has(id):
		_hg_cache[id] = _hover_glow_tex(body)
	var hg: Dictionary = _hg_cache[id]
	if hg.is_empty():
		return null
	var pm := PlaneMesh.new()
	pm.size = Vector2(float(hg["w"]), float(hg["h"]))
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.disable_fog = true
	m.albedo_texture = hg["tex"]
	m.albedo_color = Color(0.498, 0.847, 1.0, 0.55)   # #7fd8ff
	m.render_priority = 2
	var mi := MeshInstance3D.new()
	mi.name = "hglow"
	mi.mesh = pm
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.position = Vector3(float(hg["cx"]), 0.25, float(hg["cz"]))
	return mi


static func _hover_glow_tex(body: Node3D) -> Dictionary:
	var tris: Array = []      # [ax, az, bx, bz, cx, cz] in the kart's own frame
	var x0 := 1e9
	var x1 := -1e9
	var z0 := 1e9
	var z1 := -1e9
	var ms: Array = body.find_children("*", "MeshInstance3D", true, false)
	if body is MeshInstance3D:
		ms.push_front(body)
	for n in ms:
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		var xf := body.transform * (Transform3D.IDENTITY if mi == body else Menu._rel_xf(mi, body))
		for si in mi.mesh.get_surface_count():
			var a := mi.mesh.surface_get_arrays(si)
			var vs: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
			var ix = a[Mesh.ARRAY_INDEX]
			var pts := PackedVector2Array()
			pts.resize(vs.size())
			for i in vs.size():
				var p := xf * vs[i]
				pts[i] = Vector2(p.x, p.z)
				x0 = minf(x0, p.x)
				x1 = maxf(x1, p.x)
				z0 = minf(z0, p.z)
				z1 = maxf(z1, p.z)
			var cnt: int = (ix as PackedInt32Array).size() if ix != null else vs.size()
			for t in range(0, cnt - 2, 3):
				var i0: int = (ix as PackedInt32Array)[t] if ix != null else t
				var i1: int = (ix as PackedInt32Array)[t + 1] if ix != null else t + 1
				var i2: int = (ix as PackedInt32Array)[t + 2] if ix != null else t + 2
				tris.append([pts[i0], pts[i1], pts[i2]])
	if not (x1 > x0):
		return {}
	var M := 1.7
	var W := 128
	var H := 64
	var w := x1 - x0 + M * 2.0
	var h := z1 - z0 + M * 2.0
	var ox := x0 - M
	var oz := z0 - M
	var sx := W / w
	var sz := H / h
	var O := PackedFloat32Array()
	O.resize(W * H)
	for tr in tris:
		var A: Vector2 = tr[0]
		var B: Vector2 = tr[1]
		var C: Vector2 = tr[2]
		var ax := (A.x - ox) * sx
		var az := (A.y - oz) * sz
		var bx := (B.x - ox) * sx
		var bz := (B.y - oz) * sz
		var cx := (C.x - ox) * sx
		var cz := (C.y - oz) * sz
		var d := (bx - ax) * (cz - az) - (bz - az) * (cx - ax)
		if absf(d) < 1e-6:
			continue
		var gx0 := maxi(0, floori(minf(ax, minf(bx, cx))))
		var gx1 := mini(W - 1, ceili(maxf(ax, maxf(bx, cx))))
		var gz0 := maxi(0, floori(minf(az, minf(bz, cz))))
		var gz1 := mini(H - 1, ceili(maxf(az, maxf(bz, cz))))
		for zz in range(gz0, gz1 + 1):
			for xx in range(gx0, gx1 + 1):
				var px := xx + 0.5
				var pz := zz + 0.5
				var u := ((bx - px) * (cz - pz) - (bz - pz) * (cx - px)) / d
				var v := ((cx - px) * (az - pz) - (cz - pz) * (ax - px)) / d
				if u >= -0.02 and v >= -0.02 and u + v <= 1.04:
					O[zz * W + xx] = 1.0
	var wide := _box_blur(O.duplicate(), W, H, 3, 3)
	var core := _box_blur(O.duplicate(), W, H, 1, 2)
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	for z in H:
		for x in W:
			var i := z * W + x
			var edge := minf(1.0, minf(minf(x, W - 1 - x) / 6.0, minf(z, H - 1 - z) / 6.0))
			var k := minf(1.0, wide[i] * 1.25 + core[i] * 0.35) * edge
			var hot := minf(1.0, core[i] * 0.9) * edge
			img.set_pixel(x, z, Color8(int(round(40 + 180 * hot)), int(round(150 + 100 * maxf(k, hot) * 0.8 + 20 * hot)), 255, int(round(255 * minf(1.0, k * 0.95 + hot * 0.25)))))
	img.generate_mipmaps()
	return {"tex": ImageTexture.create_from_image(img), "w": w, "h": h, "cx": ox + w / 2.0, "cz": oz + h / 2.0}


## the web's running-sum box blur: `pass` times, radius r, rows then columns
static func _box_blur(A: PackedFloat32Array, W: int, H: int, r: int, passes: int) -> PackedFloat32Array:
	var B := PackedFloat32Array()
	B.resize(A.size())
	for p in passes:
		for z in H:
			var acc := 0.0
			for x in range(-r, W + r):
				var xa := x + r
				var xb := x - r - 1
				if xa < W and xa >= 0:
					acc += A[z * W + xa]
				if xb >= 0 and xb < W:
					acc -= A[z * W + xb]
				if x >= 0 and x < W:
					B[z * W + x] = acc / (2 * r + 1)
		for x in W:
			var acc2 := 0.0
			for z in range(-r, H + r):
				var za := z + r
				var zb := z - r - 1
				if za < H and za >= 0:
					acc2 += B[za * W + x]
				if zb >= 0 and zb < H:
					acc2 -= B[zb * W + x]
				if z >= 0 and z < H:
					A[z * W + x] = acc2 / (2 * r + 1)
	return A


## a built kart repainted for another paint or livery (the garage's livery pictures): body and wheels
static func repaint(root: Node3D, spec: Dictionary, ri: int) -> void:
	var b := clampi(int(spec.get("b", 0)), 0, (info["bodies"] as Array).size() - 1)
	var cols := colours(spec, ri)
	var liv = (info.get("liv", []) as Array)[b] if b < (info.get("liv", []) as Array).size() else null
	for c in root.get_children():
		var nm := String(c.name)
		if nm == "body":
			_paint(c, cols, liv, ri)
		elif nm.begins_with("wheel_"):
			_paint(c, cols, null, ri)


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
			var fmt: int = mesh.surface_get_format(si)
			if not nm.begins_with("g_") and _is_car_vc(sm, fmt):
				m3.set_surface_override_material(si, car_vc_mat())
				continue
			if (fmt & Mesh.ARRAY_FORMAT_COLOR) != 0 and not sm.vertex_color_use_as_albedo and not nm.begins_with("g_"):
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
					var pcol: Color = cols["paint"]
					# bright white paint keeps a little room so the clear coat's reflections show on it (as the liveries)
					pcol = pcol * (1.0 - 0.24 * smoothstep(0.6, 1.0, pcol.get_luminance()))
					pcol.a = 1.0
					pm.albedo_color = pcol
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


## The imported cars, bikes and wheels draw every part but the paint with one material (the web's SH.carVC): the part's
## colour is in the vertex colours, and its finish (clear coat, roughness, metalness) comes from a 32 x 1 lookup picture,
## one pixel per kind of part, picked by the vertex's u coordinate. That picture isn't in the exported models, which then
## read as fully metal and fully rough everywhere: dark, flat metal all over. The table is the web's CAR_PBR.
const CAR_CLS := ["paint", "dark", "stripe", "tail", "light", "glass", "carbon", "metal", "rubber", "seat", "chrome", "rim",
	"disc", "caliper", "blue", "gunmetal", "green", "red", "bluem", "bronze", "white"]
const CAR_PBR := {"paint": [0.36, 0.5, 1.0], "dark": [0.36, 0.25, 1.0], "stripe": [0.36, 0.5, 1.0], "tail": [0.4, 0.0, 0.0],
	"light": [0.2, 0.0, 0.0], "glass": [0.05, 0.0, 1.0], "carbon": [0.36, 0.25, 1.0], "metal": [0.32, 0.9, 0.0],
	"rubber": [0.9, 0.0, 0.0], "seat": [0.8, 0.0, 0.0], "chrome": [0.1, 1.0, 0.0], "rim": [0.24, 0.95, 0.0],
	"disc": [0.45, 0.85, 0.0], "caliper": [0.35, 0.2, 0.8], "blue": [0.3, 0.0, 0.0], "gunmetal": [0.26, 0.9, 0.4],
	"green": [0.34, 0.6, 0.8], "red": [0.3, 0.5, 0.9], "bluem": [0.22, 0.85, 0.6], "bronze": [0.3, 0.95, 0.3], "white": [0.3, 0.0, 0.9]}
static var _car_vc: StandardMaterial3D = null


static func _is_car_vc(sm: BaseMaterial3D, fmt: int) -> bool:
	return sm.metallic > 0.99 and sm.roughness > 0.99 and sm.albedo_texture == null \
		and (fmt & Mesh.ARRAY_FORMAT_TEX_UV) != 0 and (fmt & Mesh.ARRAY_FORMAT_COLOR) != 0


## the parts' material: vertex colour, with roughness and metalness read from the lookup (green and blue, as the web's
## roughnessMap and metalnessMap) and the clear coat from a second one (its red)
static func car_vc_mat() -> StandardMaterial3D:
	if _car_vc != null:
		return _car_vc
	var rm := Image.create(32, 1, false, Image.FORMAT_RGBA8)
	var cc := Image.create(32, 1, false, Image.FORMAT_RGBA8)
	rm.fill(Color(1, 1, 0, 1))
	cc.fill(Color(0, 1, 0, 1))
	for i in CAR_CLS.size():
		var p: Array = CAR_PBR[CAR_CLS[i]]
		rm.set_pixel(i, 0, Color(1, float(p[0]), float(p[1]), 1))
		cc.set_pixel(i, 0, Color(float(p[2]), 1, 0, 1))
	var m := StandardMaterial3D.new()
	m.resource_name = "car_vc"
	m.vertex_color_use_as_albedo = true
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	var rt := ImageTexture.create_from_image(rm)
	m.roughness = 1.0
	m.roughness_texture = rt
	m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
	m.metallic = 1.0
	m.metallic_texture = rt
	m.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
	m.metallic_specular = 0.5
	m.clearcoat_enabled = true
	m.clearcoat = 1.0
	m.clearcoat_roughness = 0.08
	m.clearcoat_texture = ImageTexture.create_from_image(cc)
	_car_vc = m
	return m


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
	if bool(lv.get("num", false)):
		# PC: each livery its own number (digits 1 to 8, one or two) and number design, unless the list sets them
		var hn := _hash(String(lv["id"]) + "#n")
		var nv := 1 + hn % 8
		if (hn >> 4) % 3 != 0:
			nv = nv * 10 + 1 + (hn >> 8) % 8
		m.set_shader_parameter("uLNumV", float(lv.get("nv", nv)))
		m.set_shader_parameter("uLNumS", float(lv.get("ns", (hn >> 12) % 6)))
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
