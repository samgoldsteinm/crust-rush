extends Node3D
## The warp tunnel behind every Sandbox passage, drawn (web tools/mini/sandbox.js: sbWarpMat's tube, sbRoadTex, the bright
## end). There is ONE of these, a child of main.gd, not of any place's world: it is laid behind whichever arch the
## camera is going through, and it is what the kart drives while the next place is built on another thread (the corridor
## itself is Sandbox.Tun, scripts/sandbox.gd). Because it belongs to no place it is still there, unchanged, when the place
## behind it is thrown away and the place ahead is brought in: that is how a journey shows no join.
##
## The tube has no end while the kart is travelling. Its walls' streaks and its road repeat every PERIOD units along it,
## so the piece that is drawn (long enough to reach from behind the camera to the bright end ahead) is moved along in
## whole periods as the kart goes, which cannot be seen; the bright end keeps its distance ahead of the kart until the
## place it leads to is ready, and from then on stands still where the way out is.
##
## It also owns "the tunnel's light". A place's sun, sky and colour grade would change at the moment the places are
## swapped, on the kart's paint and in the streaks' brightness. So as the camera goes in, all of that is eased to one
## fixed light (the same for every place), held while the kart is deep inside, and eased to the next place's on the way
## out: the camera gets its own Environment here (`env_o`), the suns are turned down, and the post material's grade is
## set from here.
## Loaded by its path (no class name: a fresh checkout has no class list yet).

const PERIOD := 120.0        # the walls' and the road's pattern repeats this often along the tube
const BACK := 40.0           # the drawn piece starts this far behind its anchor,
const AHEAD := 440.0         # ...and reaches this far past it
const END_GAP := 90.0        # the bright end keeps this far ahead of a kart that is still waiting for its place
const END_STILL := 210.0     # ...and stands here (the web's tunnel length) until the kart is that close to it
# the tunnel's own light (see above): what every place's look is eased to deep inside
const T_EXPOSURE := 0.85
const T_GLOW := 0.3
const T_GLOW_THR := 1.6
const T_AMB := Color(0.78, 0.74, 1.0)
const T_AMB_E := 0.85
const T_SAT := 1.07
const T_CON := 1.04
const T_VIG := 0.16

const TUBE := """
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, shadows_disabled;
// the inside of the tunnel (web sbWarpMat, tube): uv.x round it, uv.y along it (one unit to 60 of the game's);
// the three layers of streaks run at 1, 1.5 and 2 times that, so the whole picture repeats every 2 units of uv.y.
// u_clip: the part of the tube that exists, as distances along it from the piece's own start.
uniform float u_t = 0.0;
uniform vec2 u_clip = vec2(-1e9, 1e9);
varying float v_d;
float h1(float n) { return fract(sin(n * 91.345) * 47453.5453); }
vec3 lay(float a, float r, float n, float sd) {
	float b = floor(a * n);
	float f = fract(a * n);
	float id = b + sd * 1000.0;
	float on = step(0.5, h1(id));
	float sp = 0.55 + h1(id + 7.0) * 1.5;
	float ph = fract(r * (1.0 + sd * 0.5) - u_t * sp + h1(id + 3.0));
	float len = 0.22 + 0.5 * h1(id + 11.0);
	float s = smoothstep(0.0, 0.07, ph) * smoothstep(len, len * 0.25, ph);
	float w = smoothstep(0.42, 0.05, abs(f - 0.5));
	float t = h1(id + 5.0);
	vec3 col = t < 0.45 ? vec3(1.0, 0.97, 1.0) : (t < 0.72 ? vec3(0.62, 0.45, 1.0) : (t < 0.9 ? vec3(0.4, 0.6, 1.0) : vec3(0.45, 1.0, 0.7)));
	return col * on * s * w * (0.5 + 0.5 * h1(id + 13.0));
}
void vertex() { v_d = -VERTEX.z; }
void fragment() {
	if (v_d < u_clip.x || v_d > u_clip.y) { discard; }
	float a = UV.x;
	float r = UV.y;
	vec3 c = (lay(a, r, 70.0, 0.0) + lay(a, r, 120.0, 1.0) + lay(a, r, 190.0, 2.0) * 0.8) * 1.15;
	ALBEDO = c + vec3(0.012, 0.006, 0.03);
}
"""

const ROAD := """
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, shadows_disabled;
// web sbRoadTex: the road on the tunnel's floor: dark, a glowing line down each edge, dashes down the middle
// (uv.y: one unit to 40 of the game's, the length of one dash and its gap)
uniform vec2 u_clip = vec2(-1e9, 1e9);
varying float v_d;
float band(float x, float c, float w) { return max(0.0, 1.0 - abs(x - c) / w); }
void vertex() { v_d = -VERTEX.z; }
void fragment() {
	if (v_d < u_clip.x || v_d > u_clip.y) { discard; }
	float x = UV.x * 256.0;
	float v = fract(UV.y) * 256.0;
	vec3 c = vec3(0.027, 0.02, 0.055);
	float e = band(x, 22.0, 16.0) + band(x, 234.0, 16.0);
	c = mix(c, vec3(0.59, 0.43, 1.0), clamp(e * 0.95, 0.0, 1.0));
	float e2 = band(x, 22.0, 4.0) + band(x, 234.0, 4.0);
	c = mix(c, vec3(1.0), clamp(e2, 0.0, 1.0));
	if (x > 122.0 && x < 134.0 && v > 20.0 && v < 130.0) { c = mix(c, vec3(0.84, 0.8, 1.0), 0.9); }
	if (((x > 72.0 && x < 76.0) || (x > 184.0 && x < 188.0)) && v > 150.0 && v < 240.0) { c = mix(c, vec3(0.47, 0.63, 1.0), 0.35); }
	ALBEDO = c;
}
"""

var main: Node                 # main.gd
var tun = null                 # the journey's corridor (Sandbox.Tun) while there is one; else the tube stands behind an arch
var f := 0.0                   # how much of the tunnel's own light: 0 the place's, 1 the tunnel's
var end_s := END_STILL         # where the bright end stands, along the corridor
var on := false                # drawn (and the camera has the tunnel's Environment)
var cam_s := 0.0               # how far along the camera is
var env_o: Environment = null
var base := {}                 # the place's own look, to ease from and back to
var _tube: MeshInstance3D
var _floor: MeshInstance3D
var _end: MeshInstance3D
var _back: MeshInstance3D
var _tube_mat: ShaderMaterial
var _floor_mat: ShaderMaterial
var _end_mat: ShaderMaterial
var _wv := 0.0                 # the walls' clock (it runs backwards for a kart heading back out of an arch)
var _wu := 0.0                 # the bright end's
var _pull_mat: StandardMaterial3D
var _pulled: Array = []        # the kart's meshes that carry the "seen through the wall" overlay
var _face: Shader


func _ready() -> void:
	main = get_parent()
	visible = false
	var sh := Shader.new()
	sh.code = TUBE
	_tube_mat = ShaderMaterial.new()
	_tube_mat.shader = sh
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for s in 32:
		var a0 := float(s) / 32.0 * TAU
		var a1 := float(s + 1) / 32.0 * TAU
		var u0 := float(s) / 32.0
		var u1 := float(s + 1) / 32.0
		# (a unit tube: the node's own scale gives it its width and height)
		var p0 := Vector3(sin(a0), cos(a0), BACK)
		var p1 := Vector3(sin(a1), cos(a1), BACK)
		var q0 := Vector3(sin(a0), cos(a0), -AHEAD)
		var q1 := Vector3(sin(a1), cos(a1), -AHEAD)
		for v in [[p0, u0, BACK / 60.0], [q0, u0, -AHEAD / 60.0], [q1, u1, -AHEAD / 60.0], [p0, u0, BACK / 60.0], [q1, u1, -AHEAD / 60.0], [p1, u1, BACK / 60.0]]:
			st.set_uv(Vector2(float(v[1]), float(v[2])))
			st.add_vertex(v[0])
	_tube = _mesh(st.commit(), _tube_mat)
	var sr := Shader.new()
	sr.code = ROAD
	_floor_mat = ShaderMaterial.new()
	_floor_mat.shader = sr
	st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var c := [[Vector3(-1, 0, BACK), Vector2(0, -BACK / 40.0)], [Vector3(1, 0, BACK), Vector2(1, -BACK / 40.0)], [Vector3(1, 0, -AHEAD), Vector2(1, AHEAD / 40.0)], [Vector3(-1, 0, -AHEAD), Vector2(0, AHEAD / 40.0)]]
	for i in [0, 1, 2, 0, 2, 3]:
		st.set_uv(c[i][1])
		st.add_vertex(c[i][0])
	_floor = _mesh(st.commit(), _floor_mat)
	_floor.position.y = 0.3
	# the bright end, and the way out: the same picture (web: the end plane, sbWarpMat(0, c .5 .42, s .55, core 1.1))
	var SandboxView = load("res://scripts/sandbox_view.gd")
	_face = SandboxView.face_shader()
	_end_mat = ShaderMaterial.new()
	_end_mat.shader = _face
	_end_mat.set_shader_parameter("u_tube", 0.0)
	_end_mat.set_shader_parameter("u_c", Vector2(0.5, 0.42))
	_end_mat.set_shader_parameter("u_s", 0.55)
	_end_mat.set_shader_parameter("u_core", 1.1)
	var q := QuadMesh.new()
	q.size = Vector2(2.0, 1.0)
	_end = _mesh(q, _end_mat)
	# behind, once the mouth the kart came in by is gone: a dark stop (only a camera looking back sees it)
	var bm := StandardMaterial3D.new()
	bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.albedo_color = Color(0.012, 0.006, 0.03)
	bm.cull_mode = BaseMaterial3D.CULL_DISABLED
	bm.disable_fog = true
	_back = _mesh(q, bm)
	_back.position.z = BACK - 0.5


func _mesh(mesh: Mesh, mat: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.extra_cull_margin = 1000.0
	add_child(mi)
	return mi


## the corridor's frame the tube stands in this frame: the journey's, or the arch the camera is going into
func _frame(sb, cp: Vector3) -> Dictionary:
	if tun != null:
		return {"ox": tun.ox, "oz": tun.oz, "dx": tun.dx, "dz": tun.dz, "y": tun.y, "rx": tun.rx, "ry": tun.ry, "cam_in": tun.cam_in, "hw": tun.hw, "travel": true}
	if sb == null:
		return {}
	for g in sb.gates:
		var gd: Dictionary = g
		if bool(gd["road"]) or bool(gd["plain"]):
			continue   # (an arch over a road, and the garage's door, have a tunnel only for a kart that has committed)
		var dc: float = (cp.x - float(gd["x"])) * float(gd["nx"]) + (cp.z - float(gd["z"])) * float(gd["nz"])
		var lc: float = (cp.x - float(gd["x"])) * float(gd["tx"]) + (cp.z - float(gd["z"])) * float(gd["tz"])
		var fr: Dictionary = sb.frame_in(gd, null)
		if dc > -float(fr["cam_in"]) and absf(lc) < float(gd["hw"]) + 14.0:
			fr["travel"] = false
			return fr
	return {}


func _process(dt: float) -> void:
	if main == null or main.get("race") == null or main.get("cam") == null:
		return
	var race = main.race
	var cam: Camera3D = main.cam
	var sb = race.sb if race != null else null
	var k: Kart = main.kart
	if sb == null and tun == null:
		if on:
			_show(false)
		_pull(false)
		return
	var cp := cam.global_position
	var fr := _frame(sb, cp)
	var paused := bool(main.get("paused"))
	if not paused:
		_wu = fmod(_wu + dt * 0.5, 1000.0)
	_end_mat.set_shader_parameter("u_t", _wu)
	# the kart where it is drawn this frame (between two physics steps)
	var kx := k.x
	var kz := k.y
	var view = main.get("view")
	if view != null and (view.views as Dictionary).has(k):
		kx = float(view.views[k]["rx"])
		kz = float(view.views[k]["ry"])
	var pull := _gate_pull(sb, k, kx, kz, cp)
	if fr.is_empty():
		if on:
			_show(false)
		_pull(pull)
		return
	var dx := float(fr["dx"])
	var dz := float(fr["dz"])
	var ks := (kx - float(fr["ox"])) * dx + (kz - float(fr["oz"])) * dz
	cam_s = (cp.x - float(fr["ox"])) * dx + (cp.z - float(fr["oz"])) * dz
	var cl := (cp.x - float(fr["ox"])) * -dz + (cp.z - float(fr["oz"])) * dx
	var travel: bool = fr["travel"]
	var show := true
	var clip0 := 0.3
	var clip1 := 1e9
	var heading_out := false
	if not travel:
		end_s = END_STILL
		heading_out = cos(k.ma) * dx + sin(k.ma) * dz < 0.0
	else:
		if tun.swapped:
			# laid onto the place the kart comes out in: the tube ends at that mouth, the bright picture stands a little
			# inside it, and all of it goes once the camera has followed the kart out
			end_s = tun.s_exit - tun.e_off
			clip0 = -1e9
			clip1 = tun.s_exit - 0.3
			if cam_s > end_s - 3.0:
				main.call("_sb_reveal")
			if k.tun == null and cam_s > tun.s_exit + (7.2 if tun.room_out else 0.9) + 2.0:
				show = false
				main.call("_sb_tun_over")
		else:
			end_s = maxf(END_STILL, ks + END_GAP)
			if tun.sealed:
				clip0 = -1e9
			else:
				clip0 = tun.clip0
				show = cam_s > -tun.cam_in and absf(cl) < float(fr["hw"]) + 14.0
	if not show:
		if on:
			_show(false)
		_pull(pull)
		return
	# the piece that is drawn, moved along in whole periods so it always reaches from behind the camera to the end
	var anchor := maxf(0.0, floorf((ks - 80.0) / PERIOD) * PERIOD) if not (travel and tun.swapped) else floorf((ks - 80.0) / PERIOD) * PERIOD
	global_transform = Transform3D(Basis(Vector3.UP, atan2(-dx, -dz)), Vector3(float(fr["ox"]) + dx * anchor, float(fr["y"]), float(fr["oz"]) + dz * anchor))
	var rx := float(fr["rx"])
	var ry := float(fr["ry"])
	_tube.scale = Vector3(rx, ry, 1.0)
	_floor.scale = Vector3(rx, 1.0, 1.0)
	_end.scale = Vector3(rx, ry, 1.0)
	_end.position = Vector3(0.0, ry * 0.5, -(end_s - anchor))
	_back.scale = Vector3(rx, ry * 2.0, 1.0)
	_back.visible = clip0 < -1e8
	var clip := Vector2(clip0 - anchor, clip1 - anchor)
	_tube_mat.set_shader_parameter("u_clip", clip)
	_floor_mat.set_shader_parameter("u_clip", clip)
	if not paused:
		_wv = fmod(_wv + dt * 0.9 * (-1.0 if heading_out else 1.0) + 1000.0, 1000.0)
	_tube_mat.set_shader_parameter("u_t", _wv)
	if not on:
		_show(true)
	# the tunnel's light: eased in over the first 80 units past the mouth, and out again over the last 80 before the
	# mouth the kart leaves by
	if travel and tun.swapped:
		f = smoothstep(0.0, 80.0, tun.s_exit - cam_s)
	else:
		f = smoothstep(0.0, 80.0, cam_s)
	_look()
	# the kart beyond the bright picture it is about to drive out through, the camera still before it
	if travel and tun.swapped and ks > end_s - 4.0 and cam_s < end_s + 2.0:
		pull = true
	if travel and not tun.swapped and not tun.sealed and ks > -4.0 and cam_s < 2.0:
		pull = true
	_pull(pull)


## the kart on one side of an arch's face and the camera on the other, going in or coming out: it is drawn through it
func _gate_pull(sb, k: Kart, kx: float, kz: float, cp: Vector3) -> bool:
	if sb == null:
		return false
	for g in sb.gates:
		var gd: Dictionary = g
		if bool(gd["plain"]):
			continue
		var dk: float = (kx - float(gd["x"])) * float(gd["nx"]) + (kz - float(gd["z"])) * float(gd["nz"])
		var lk: float = (kx - float(gd["x"])) * float(gd["tx"]) + (kz - float(gd["z"])) * float(gd["tz"])
		var dc: float = (cp.x - float(gd["x"])) * float(gd["nx"]) + (cp.z - float(gd["z"])) * float(gd["nz"])
		if absf(lk) < float(gd["hw"]) + 8.0 and absf(k.wy - float(gd["y"])) < 30.0 and ((dk > -4.0 and dk < 80.0 and dc < 2.0 and dc > -80.0) or (dk < 4.0 and dk > -80.0 and dc > -2.0 and dc < 80.0)):
			return true
	return false


# ---------------------------------------------------------------- the tunnel's light

func _show(v: bool) -> void:
	on = v
	visible = v
	if v:
		_engage()
	else:
		_disengage()


## the place's own look, noted, and the camera given the tunnel's Environment (a copy of the place's, without its sky
## in the kart's paint: that is the one thing that changes at once, as the camera goes through the mouth)
func _engage() -> void:
	var env: Environment = main.env
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	var pm: ShaderMaterial = main.post_mat
	if env == null or sun == null:
		return
	if not base.is_empty() and base.get("env") == env:
		# (the same place as last time: its own look is what was noted then, not what the tunnel has made of it since)
		pass
	else:
		base = {"env": env, "exp": env.tonemap_exposure, "glow": env.glow_intensity, "thr": env.glow_hdr_threshold, "amb": env.ambient_light_color, "amb_e": env.ambient_light_energy,
			"sun": sun.light_energy, "rim": rim.light_energy if rim != null else 0.0,
			"sat": float(pm.get_shader_parameter("sat")) if pm != null and pm.get_shader_parameter("sat") != null else T_SAT,
			"con": float(pm.get_shader_parameter("con")) if pm != null and pm.get_shader_parameter("con") != null else T_CON,
			"tint": pm.get_shader_parameter("tint") if pm != null and pm.get_shader_parameter("tint") != null else Vector3.ONE,
			"vig": float(pm.get_shader_parameter("vig")) if pm != null and pm.get_shader_parameter("vig") != null else T_VIG}
	_env_copy(env)


func _env_copy(env: Environment) -> void:
	env_o = env.duplicate()
	env_o.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env_o.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env_o.fog_enabled = false
	main.cam.environment = env_o


## the next place has taken the last one's place (main.gd, deep in the tunnel, f = 1): its look is what the light eases
## back to on the way out. Nothing on the screen changes here: at f = 1 every place looks the same.
func rebase(env: Environment, sun: DirectionalLight3D, rim: DirectionalLight3D, grade: Dictionary) -> void:
	base = {"env": env, "exp": env.tonemap_exposure, "glow": env.glow_intensity, "thr": env.glow_hdr_threshold, "amb": env.ambient_light_color, "amb_e": env.ambient_light_energy,
		"sun": sun.light_energy, "rim": rim.light_energy if rim != null else 0.0,
		"sat": float(grade.get("sat", T_SAT)), "con": float(grade.get("con", T_CON)), "tint": grade.get("tint", Vector3.ONE), "vig": float(grade.get("vig", T_VIG))}
	if on:
		_env_copy(env)
		_look()
	else:
		_restore()


func _look() -> void:
	if base.is_empty() or env_o == null:
		return
	env_o.tonemap_exposure = lerpf(float(base["exp"]), T_EXPOSURE, f)
	env_o.glow_intensity = lerpf(float(base["glow"]), T_GLOW, f)
	env_o.glow_hdr_threshold = lerpf(float(base["thr"]), T_GLOW_THR, f)
	env_o.ambient_light_color = (base["amb"] as Color).lerp(T_AMB, f)
	env_o.ambient_light_energy = lerpf(float(base["amb_e"]), T_AMB_E, f)
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	if sun != null and is_instance_valid(sun):
		# (never quite off: its shadows go on being drawn, so nothing has to start up when the kart comes out)
		sun.light_energy = lerpf(float(base["sun"]), 0.003, f)
	if rim != null and is_instance_valid(rim):
		rim.light_energy = lerpf(float(base["rim"]), 0.0, f)
	var pm: ShaderMaterial = main.post_mat
	if pm != null:
		pm.set_shader_parameter("sat", lerpf(float(base["sat"]), T_SAT, f))
		pm.set_shader_parameter("con", lerpf(float(base["con"]), T_CON, f))
		pm.set_shader_parameter("tint", (base["tint"] as Vector3).lerp(Vector3.ONE, f))
		pm.set_shader_parameter("vig", lerpf(float(base["vig"]), T_VIG, f))


func _restore() -> void:
	if base.is_empty():
		return
	var sun: DirectionalLight3D = main.sun
	var rim: DirectionalLight3D = main.rim
	if base.get("env") == main.env:
		if sun != null and is_instance_valid(sun):
			sun.light_energy = float(base["sun"])
		if rim != null and is_instance_valid(rim):
			rim.light_energy = float(base["rim"])
		var pm: ShaderMaterial = main.post_mat
		if pm != null:
			pm.set_shader_parameter("sat", float(base["sat"]))
			pm.set_shader_parameter("con", float(base["con"]))
			pm.set_shader_parameter("tint", base["tint"])
			pm.set_shader_parameter("vig", float(base["vig"]))


func _disengage() -> void:
	f = 0.0
	if main.cam != null:
		main.cam.environment = null
	env_o = null
	_restore()


## the game is leaving Sandbox, or loading a track the ordinary way: nothing of the tunnel is left behind
func reset() -> void:
	tun = null
	if on:
		_show(false)
	base = {}
	_pull(false)


# ---------------------------------------------------------------- the kart seen through a wall

## the player's kart seen through the arch's face (or the bright picture) it has driven through, until the camera has
## followed it: every mesh of the kart is drawn once more, in one flat colour, only where something is in front of it
## (web sbPull, which draws the kart itself in front; here its outline)
func _pull(want: bool) -> void:
	if want == (not _pulled.is_empty()):
		return
	if not want:
		for mi in _pulled:
			if is_instance_valid(mi):
				(mi as GeometryInstance3D).material_overlay = null
		_pulled.clear()
		return
	var view = main.get("view")
	var k = main.get("kart")
	if view == null or k == null or not (view.views as Dictionary).has(k):
		return
	if _pull_mat == null:
		_pull_mat = StandardMaterial3D.new()
		_pull_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_pull_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_pull_mat.albedo_color = Color(0.93, 0.88, 1.0, 0.8)
		_pull_mat.depth_test = BaseMaterial3D.DEPTH_TEST_INVERTED
	var root: Node3D = view.views[k]["g"]
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		if (mi as MeshInstance3D).material_overlay == null:
			(mi as MeshInstance3D).material_overlay = _pull_mat
			_pulled.append(mi)
