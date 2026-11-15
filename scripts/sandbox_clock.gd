## Sandbox's day and night (web v199 tools/mini/sandbox.js: THE CLOCK, sbClockF / sbClockArm / sbClockMats / sbClockApply / sbClockOff).
## One clock for the whole world: 0 midnight, .25 sunrise, .5 noon, .75 sunset; a day is 720 s of driving; it is kept in the
## Sandbox save as "t" (the web's crust-sb .t), so it carries through tunnels, fast travel and a restart, and PC and web share the shape.
## Nothing here is absolute: when a place is taken over, its own lights, fog, sky, exposure, bloom and materials are written down
## (arm) and every update scales and tints from that record; at noon a place is exactly as raced. off() puts every value back.
## Three kinds of place, as on the web: "out" (open air; the pizzas), "in" (a room of the house: lamps on at night, windows dark),
## "dark" (a night place: itself at night, lifted to a deep twilight by day). The stars are drawn by the sky shader (behind
## everything, as the web now draws its stars straight after its sky).
## It lives with the place's SandboxView (sandbox_view.gd makes it, ticks it ten times a second, and calls off() when the place goes),
## and waits while the kart is in a tunnel (sandbox_warp.gd has the lights then).

extends RefCounted

const DAY := 720.0
const WARM := Color("#ff9a4a")
const MOON := Color("#9db8ff")
const NIGHT_SKY := Color("#6f8fe0")
const NIGHT_GND := Color("#10182c")
const LAMP := Color("#ffd2a0")
const DUSK := Color("#ffc8a0")
const TW_TOP := Color("#1c2458")
const TW_HOR := Color("#6a4f9a")
const TW_BOT := Color("#1a1c3a")
const TW_FOG := Color("#2c2a5e")
const TW_HEMI := Color("#9a9ae0")
const FAR_RE := "outside|ycards|sky|mount|skyline|pano|riverbed|space"

var main: Node
var kind := "out"
var turn := false
var rec := {}
var mats: Array = []       # [material, k, base] (k: 1 a soft glow, 2 a lamp, 3 unlit paint, 4 a picture of the distance)
var sky_mat: ShaderMaterial = null
var armed := false


static func sm(a: float, b: float, x: float) -> float:
	var t := clampf((x - a) / (b - a), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


## the day's numbers (web sbClockF): e the sun's height, D daylight, W the golden hour, L the lamps, M the moon
static func f(t: float) -> Dictionary:
	var e := sin((t - 0.25) * TAU)
	return {"t": t, "e": e, "D": sm(-0.2, 0.24, e), "W": exp(-(e / 0.26) * (e / 0.26)), "L": 1.0 - sm(-0.12, 0.14, e), "M": sm(-0.2, -0.45, e)}


## "7:40 pm", to the ten minutes (web sbClockStr)
static func label(t: float) -> String:
	var m := int(round(t * 144.0)) % 144 * 10
	var h := m / 60
	var mm := m % 60
	return "%d:%02d %s" % [(h + 11) % 12 + 1, mm, "am" if h < 12 else "pm"]


func arm(main_: Node, T: TrackData, id: String) -> void:
	main = main_
	kind = "dark" if T.theme == "night" else ("in" if T.toy and id != "backyard" else "out")
	turn = not T.toy and T.theme != "night"
	var env: Environment = main.env
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	if env == null or sun == null:
		return
	rec = {"sun_c": sun.light_color, "sun_e": sun.light_energy, "rim_e": rim.light_energy if rim != null else 0.0, "sun_basis": sun.global_transform.basis,
		"amb": env.ambient_light_color, "amb_e": env.ambient_light_energy, "exp": env.tonemap_exposure, "glow": env.glow_intensity, "thr": env.glow_hdr_threshold,
		"fog": env.fog_light_color, "fog_e": env.fog_light_energy}
	sky_mat = null
	if env.sky != null and env.sky.sky_material is ShaderMaterial:
		sky_mat = env.sky.sky_material
		for p in ["top_col", "hor_col", "bot_col", "sun_col"]:
			rec[p] = sky_mat.get_shader_parameter(p)
	mats.clear()
	var seen := {}
	var re := RegEx.new()
	re.compile(FAR_RE)
	var stack: Array = [main.world]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		for c in n.get_children():
			stack.append(c)
		if not (n is MeshInstance3D):
			continue
		var mi: MeshInstance3D = n
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var m = mi.get_active_material(i)
			if not (m is BaseMaterial3D) or seen.has(m):
				continue
			seen[m] = true
			var bm: BaseMaterial3D = m
			if bm.emission_enabled and bm.emission_energy_multiplier > 0.0 and (bm.emission.r + bm.emission.g + bm.emission.b) > 0.02:
				mats.append([bm, 2 if bm.emission_energy_multiplier >= 0.3 else 1, bm.emission_energy_multiplier])
			elif bm.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED and bm.blend_mode != BaseMaterial3D.BLEND_MODE_ADD:
				var nm := String(bm.resource_name)
				if nm == "sky_window" or re.search(nm) != null:
					mats.append([bm, 4, bm.albedo_color])
				else:
					mats.append([bm, 3, bm.albedo_color])
	armed = true


func apply(t: float) -> void:
	if not armed:
		return
	var env: Environment = main.env
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	if env == null or sun == null:
		return
	var F := f(t)
	var D: float = F["D"]
	var N := 1.0 - D
	var W: float = F["W"]
	var L: float = F["L"]
	var sun_k := 1.0
	var amb_k := 1.0
	var rim_k := 1.0
	var paint_k := 1.0
	var lamp_k := 1.0
	var fill_k := 1.0
	var exp_k := 1.0
	var sk := Color(1, 1, 1)
	var stars := 0.0
	if kind == "dark":
		sun_k = 1.0 + 0.3 * D
		amb_k = 1.0 + 0.6 * D
		lamp_k = 1.0 - 0.1 * D
		sun.light_color = rec["sun_c"]
		env.ambient_light_color = (rec["amb"] as Color).lerp(TW_HEMI, 0.3 * D)
		env.fog_light_color = (rec["fog"] as Color).lerp(TW_FOG, 0.5 * D)
		if sky_mat != null:
			sky_mat.set_shader_parameter("top_col", (rec["top_col"] as Color).lerp(TW_TOP, 0.55 * D))
			sky_mat.set_shader_parameter("hor_col", (rec["hor_col"] as Color).lerp(TW_HOR, 0.55 * D))
			sky_mat.set_shader_parameter("bot_col", (rec["bot_col"] as Color).lerp(TW_BOT, 0.55 * D))
		sk = Color(1.0 + 0.5 * D, 1.0 + 0.45 * D, 1.0 + 0.6 * D)
		env.glow_intensity = float(rec["glow"]) - 0.06 * D
	else:
		var ins := kind == "in"
		sun_k = D * (1.0 - 0.3 * W) + N * float(F["M"]) * (0.05 if ins else 0.11)
		sun.light_color = (rec["sun_c"] as Color).lerp(WARM, 0.7 * W * D).lerp(MOON, N)
		if ins:
			amb_k = 0.6 + 0.4 * D
			rim_k = 0.5 + 0.5 * D
			paint_k = 0.75 + 0.25 * D
			lamp_k = 1.0 + 1.4 * L
			fill_k = 0.7 + 0.3 * D
			env.ambient_light_color = (rec["amb"] as Color).lerp(LAMP, 0.55 * N)
		else:
			# (more fill than the web's .3 at night: here a share of the fill comes from the sky, which goes dark, and the PC's
			#  night came out near black where the web's is a readable blue)
			amb_k = 0.75 + 0.25 * D
			rim_k = 0.5 + 0.5 * D
			paint_k = 0.16 + 0.84 * D
			lamp_k = 1.0 + 1.1 * L
			fill_k = 0.3 + 0.7 * D
			exp_k = 1.0 + 0.25 * N
			env.ambient_light_color = (rec["amb"] as Color).lerp(NIGHT_SKY, 0.75 * N).lerp(DUSK, 0.3 * W).lerp(NIGHT_GND, 0.25 * N)
		sk = Color(1, 1, 1).lerp(Color(1, 0.7, 0.5), 0.5 * W) * (0.05 + 0.95 * D)
		sk.r += 0.012 * N
		sk.g += 0.02 * N
		sk.b += 0.05 * N
		env.fog_light_color = (rec["fog"] as Color) * sk
		if sky_mat != null:
			sky_mat.set_shader_parameter("top_col", (rec["top_col"] as Color) * sk)
			sky_mat.set_shader_parameter("hor_col", (rec["hor_col"] as Color).lerp(WARM, 0.45 * W) * sk)
			sky_mat.set_shader_parameter("bot_col", (rec["bot_col"] as Color) * sk)
			sky_mat.set_shader_parameter("sun_col", (rec["sun_col"] as Color).lerp(WARM, 0.6 * W * D).lerp(MOON, N) * (D + N * float(F["M"]) * 0.55))
		env.glow_intensity = float(rec["glow"]) + (0.1 if ins else 0.12) * L
		env.glow_hdr_threshold = float(rec["thr"]) * (1.0 - 0.03 * L / 0.94)
		if not ins:
			stars = N * N * 0.95
	if sky_mat != null:
		sky_mat.set_shader_parameter("stars", stars)
	sun.light_energy = float(rec["sun_e"]) * sun_k
	env.ambient_light_energy = float(rec["amb_e"]) * amb_k
	if rim != null:
		rim.light_energy = float(rec["rim_e"]) * rim_k
	env.tonemap_exposure = float(rec["exp"]) * exp_k
	if turn:
		# the sun crosses the sky and sets; the moon comes up on the other side once the sun's light is gone (web sbClockApply)
		var b0: Basis = rec["sun_basis"]
		var to_sun := b0.z.normalized()
		var az0 := atan2(to_sun.z, to_sun.x)
		var el0 := asin(clampf(to_sun.y, -1.0, 1.0))
		var e: float = F["e"]
		var az: float
		var el: float
		if e > -0.2:
			el = maxf(0.3, el0 * (0.32 + 0.68 * sm(0.0, 1.0, e)))
			az = az0 + (t - 0.5) * 2.2
		else:
			el = maxf(0.55, el0 * 0.9)
			az = az0 + 2.6 + (fmod(t + 0.5, 1.0) - 0.5) * 1.2
		var d := Vector3(cos(el) * cos(az), sin(el), cos(el) * sin(az))
		var tr := sun.global_transform
		sun.global_transform = Transform3D(Basis.looking_at(-d, Vector3.UP if absf(d.y) < 0.99 else Vector3.FORWARD), tr.origin)
	for r in mats:
		var m: BaseMaterial3D = r[0]
		match int(r[1]):
			1:
				m.emission_energy_multiplier = float(r[2]) * fill_k
			2:
				var e0: float = r[2]
				m.emission_energy_multiplier = e0 * (1.0 + (lamp_k - 1.0) * 0.4 if e0 > 1.0 else lamp_k)
			3:
				var c: Color = (r[2] as Color) * paint_k
				if kind == "out":
					c.r *= 1.0 - 0.3 * N
					c.g *= 1.0 - 0.15 * N
				c.a = (r[2] as Color).a
				m.albedo_color = c
			4:
				var c4: Color = (r[2] as Color) * sk
				c4.a = (r[2] as Color).a
				m.albedo_color = c4


## everything back as the place itself has it
func off() -> void:
	if not armed:
		return
	armed = false
	var env: Environment = main.env
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	if is_instance_valid(sun):
		sun.light_color = rec["sun_c"]
		sun.light_energy = rec["sun_e"]
		var tr := sun.global_transform
		sun.global_transform = Transform3D(rec["sun_basis"], tr.origin)
	if rim != null and is_instance_valid(rim):
		rim.light_energy = rec["rim_e"]
	if env != null:
		env.ambient_light_color = rec["amb"]
		env.ambient_light_energy = rec["amb_e"]
		env.tonemap_exposure = rec["exp"]
		env.glow_intensity = rec["glow"]
		env.glow_hdr_threshold = rec["thr"]
		env.fog_light_color = rec["fog"]
	if sky_mat != null:
		for p in ["top_col", "hor_col", "bot_col", "sun_col"]:
			sky_mat.set_shader_parameter(p, rec[p])
		sky_mat.set_shader_parameter("stars", 0.0)
	for r in mats:
		var m: BaseMaterial3D = r[0]
		match int(r[1]):
			1, 2:
				m.emission_energy_multiplier = r[2]
			_:
				m.albedo_color = r[2]
	mats.clear()
