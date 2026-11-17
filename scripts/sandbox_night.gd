extends Node3D
## Sandbox at night on the PC (web v206 tools/mini/patch43.py; the headlights as web v210 patch49). Made and fed by sandbox_view.gd
## next to the clock (sandbox_clock.gd); L is the clock's lamp level (0 by day, 1 at night).
## - The toy tracks' wall dashes (materials "toy_toydash...") glow a cool white, like LED strips.
## - Street lamps along the road on the pizzas that have them (LAMPS, open air only): a pole, an arm, a lit head and a pool of light
##   on the ground; three real lights (two on Low) follow the lamps nearest the kart.
## - Headlights everywhere: a spot light at the bumper aimed down the road, shaped by a picture (two lobes and a low-beam cut-off,
##   as the web's cookie). Where the place has LED strips or street lamps they fade out while the kart is on the track (within the
##   road's half-width + 10 of it) and come back off it; elsewhere they are on all night.
## off() puts the dash materials back as they were (they are shared with the next visit).

const LAMPS := ["spiral", "basil", "napoli", "tour"]
const LED_COL := Color("#8fd0ff")

var main: Node
var T: TrackData
var id := ""
var kind := "out"
var lite := false
var led: Array = []          # [material, emission_enabled, emission, energy] as found
var spot: SpotLight3D = null
var hf := 1.0                # the headlights' share: 0 on a lit track, 1 off it
var lit_track := false
var lamps: Array = []        # Vector3: where each lamp's light is
var lamp_mat: StandardMaterial3D = null
var glow_mat: StandardMaterial3D = null
var pool: Array = []         # OmniLight3D
var _pick := 0.0


func arm(main_: Node, T_: TrackData, id_: String, kind_: String) -> void:
	main = main_
	T = T_
	id = id_
	kind = kind_
	lite = int(main.get("quality")) <= 0
	# the LED strips: the toy tracks' wall dashes
	var seen := {}
	var stack: Array = [main.world]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		for c in n.get_children():
			stack.append(c)
		if not (n is MeshInstance3D) or (n as MeshInstance3D).mesh == null:
			continue
		var mi: MeshInstance3D = n
		for i in mi.mesh.get_surface_count():
			var m = mi.get_active_material(i)
			if m is StandardMaterial3D and not seen.has(m) and String((m as StandardMaterial3D).resource_name).begins_with("toy_toydash"):
				seen[m] = true
				var sm: StandardMaterial3D = m
				led.append([sm, sm.emission_enabled, sm.emission, sm.emission_energy_multiplier])
				sm.emission_enabled = true
				sm.emission = LED_COL
				sm.emission_energy_multiplier = 0.0
	lit_track = LAMPS.has(id) or T.toy or not led.is_empty()
	# the headlights
	spot = SpotLight3D.new()
	spot.light_color = Color("#eef3ff")
	spot.spot_range = 420.0
	spot.spot_angle = 35.5
	spot.spot_angle_attenuation = 0.6
	spot.spot_attenuation = 1.15
	spot.light_energy = 0.0
	spot.shadow_enabled = false   # (the kart's own body would shadow its headlights: web patch 53)
	spot.light_projector = _cookie()
	add_child(spot)
	if LAMPS.has(id) and kind == "out":
		_build_lamps()


## the headlights' picture across the cone: two soft lobes side by side, a low-beam cut-off along the top (web sbHeadCookie)
static func _cookie() -> ImageTexture:
	var S := 128
	var img := Image.create(S, S, false, Image.FORMAT_RGBA8)
	for y in S:
		for x in S:
			var v := 0.0
			for cx: float in [0.39, 0.61]:
				var dx := (float(x) / S - cx) / (0.36 * 1.35)
				var dy := (float(y) / S - 0.59) / (0.36 * 0.72)
				var r := sqrt(dx * dx + dy * dy)
				v += clampf(1.0 - r, 0.0, 1.0) ** 1.4 * 0.9
			var cut := clampf((float(y) / S - 0.27) / 0.15, 0.0, 1.0)
			v = clampf(v * cut, 0.0, 1.0)
			img.set_pixel(x, y, Color(v * 0.93, v * 0.96, v, 1.0))
	return ImageTexture.create_from_image(img)


func _near_track(x: float, z: float, d: float) -> bool:
	var d2 := d * d
	for j in range(0, T.N, 2):
		if (T.px[j] - x) ** 2 + (T.py[j] - z) ** 2 < d2:
			return true
	return false


func _build_lamps() -> void:
	var seg := T.L / float(maxi(1, T.N)) if T.L > 0.0 else 4.0
	var step := maxi(1, int(round(300.0 / seg)))
	var side := 1.0
	var H := 48.0
	var pole_mat := StandardMaterial3D.new()
	pole_mat.albedo_color = Color("#4a4f57")
	pole_mat.roughness = 0.55
	pole_mat.metallic = 0.4
	lamp_mat = StandardMaterial3D.new()
	lamp_mat.albedo_color = Color("#3a3d42")
	lamp_mat.roughness = 0.4
	lamp_mat.emission_enabled = true
	lamp_mat.emission = Color("#ffd7a0")
	lamp_mat.emission_energy_multiplier = 0.0
	glow_mat = StandardMaterial3D.new()
	glow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	glow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	glow_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	glow_mat.no_depth_test = false
	glow_mat.albedo_texture = _pool_tex()
	glow_mat.albedo_color = Color(1, 1, 1, 0)
	var pole := CylinderMesh.new()
	pole.top_radius = 0.55
	pole.bottom_radius = 0.85
	pole.height = H
	var arm := BoxMesh.new()
	arm.size = Vector3(11, 0.7, 0.7)
	var head := BoxMesh.new()
	head.size = Vector3(5, 1.3, 2.6)
	var quad := QuadMesh.new()
	quad.size = Vector2(80, 80)
	for j in range(0, T.N, step):
		side = -side
		var o := T.WALLD + 12.0
		var x := T.px[j] + T.nx[j] * o * side
		var z := T.py[j] + T.ny[j] * o * side
		var g := T.ground(x, z)
		var road := T.ground(T.px[j], T.py[j]) + (T.ey[j] if j < T.ey.size() else 0.0)
		if absf(g - road) > 18.0 or _near_track(x, z, T.WALLD + 4.0):
			continue
		var hx := x - T.nx[j] * side * 9.0
		var hz := z - T.ny[j] * side * 9.0
		var yaw := -atan2(hz - z, hx - x)
		_put(pole, pole_mat, Vector3(x, g + H / 2.0, z), 0.0)
		_put(arm, pole_mat, Vector3((x + hx) / 2.0, g + H - 0.5, (z + hz) / 2.0), yaw)
		_put(head, lamp_mat, Vector3(hx, g + H - 1.6, hz), yaw)
		var gq := MeshInstance3D.new()
		gq.mesh = quad
		gq.material_override = glow_mat
		gq.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		gq.position = Vector3(hx, T.ground(hx, hz) + 0.4, hz)
		gq.rotation.x = -PI / 2.0
		add_child(gq)
		lamps.append(Vector3(hx, g + H - 4.0, hz))
	for i in (2 if lite else 3):
		var l := OmniLight3D.new()
		l.light_color = Color("#ffcf95")
		l.omni_range = 170.0
		l.omni_attenuation = 1.6
		l.light_energy = 0.0
		l.shadow_enabled = false
		add_child(l)
		pool.append(l)


func _put(mesh: Mesh, mat: Material, pos: Vector3, yaw: float) -> void:
	var m := MeshInstance3D.new()
	m.mesh = mesh
	m.material_override = mat
	m.position = pos
	m.rotation.y = yaw
	add_child(m)


static func _pool_tex() -> ImageTexture:
	var S := 64
	var img := Image.create(S, S, false, Image.FORMAT_RGBA8)
	for y in S:
		for x in S:
			var r := Vector2(float(x) / (S - 1) - 0.5, float(y) / (S - 1) - 0.5).length() * 2.0
			var a := clampf(1.0 - r, 0.0, 1.0)
			a = a * a * 0.9
			img.set_pixel(x, y, Color(1.0, 0.82, 0.6, a))
	return ImageTexture.create_from_image(img)


## every frame: L the clock's lamp level; k the kart (null or in a tunnel: the lights stay where they are, the headlights off)
func frame(dt: float, L: float, k: Kart) -> void:
	for e in led:
		(e[0] as StandardMaterial3D).emission_energy_multiplier = 3.0 * L
	if lamp_mat != null:
		lamp_mat.emission_energy_multiplier = 4.0 * L
		glow_mat.albedo_color = Color(1, 1, 1, 0.85 * L)
	if spot == null:
		return
	if k == null or k.tun != null:
		spot.light_energy = 0.0
		return
	var fwd := Vector3(cos(k.a), 0.0, sin(k.a))
	var kp := Vector3(k.x, k.wy, k.y)
	var on_t := false
	if lit_track and T.N > 0:
		var j := clampi(k.idx, 0, T.N - 1)
		on_t = absf((k.x - T.px[j]) * T.nx[j] + (k.y - T.py[j]) * T.ny[j]) < T.RW + 10.0 and (k.x - T.px[j]) ** 2 + (k.y - T.py[j]) ** 2 < (T.RW + 40.0) ** 2
	hf += ((0.0 if on_t else 1.0) - hf) * minf(1.0, dt * 3.6)
	# by themselves only when it is properly dark (L .5 to .8); or on / off by hand (main.hl_mode, the L key: web patch 54)
	var hm = main.get("hl_mode")
	var hon := clampf((L - 0.5) / 0.3, 0.0, 1.0) if hm == null else (1.0 if hm else 0.0)
	spot.light_energy = 9.0 * maxf(L, 0.45) * hon * (1.0 if hm == true else hf)
	var from := kp + fwd * 7.0 + Vector3(0, 4, 0)
	var to := kp + fwd * 120.0 + Vector3(0, -10, 0)
	spot.global_position = from
	if from.distance_to(to) > 1.0:
		spot.look_at(to, Vector3.UP)
	# the lamps' real lights: on the lamps nearest the kart, a few times a second
	_pick -= dt
	if not pool.is_empty() and _pick <= 0.0:
		_pick = 0.3
		var order := lamps.duplicate()
		order.sort_custom(func(a, b): return (a as Vector3).distance_squared_to(kp) < (b as Vector3).distance_squared_to(kp))
		for i in pool.size():
			var l: OmniLight3D = pool[i]
			if i < order.size():
				l.position = order[i]
	for l in pool:
		(l as OmniLight3D).light_energy = 2.2 * L


func off() -> void:
	for e in led:
		var m: StandardMaterial3D = e[0]
		m.emission_enabled = e[1]
		m.emission = e[2]
		m.emission_energy_multiplier = e[3]
	led.clear()
