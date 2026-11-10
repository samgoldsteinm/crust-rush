class_name Ghost
extends Node3D
## Your best run, raced against you (web ghostStart / recTick / ghostTick / recLap): your kart is recorded ten
## times a second while you race, and when that run is a new personal best it is saved with the record. Next
## time on that track and class a see-through copy of the kart replays it, and each lap shows how far ahead
## or behind it you are. Drawing only: nothing here touches the race simulation.

const HZ := 10.0
const MAX := 6000              # samples (ten minutes)
const OPACITY := 0.36
const OPACITY_NEAR := 0.16     # fainter when it is right by the camera

var rec := PackedByteArray()   # this run: 7 int16 per sample (position x4, rotation quaternion x32767)
var rec_t := 0.0
var rec_n := 0
var rec_laps: Array = []
var recording := false
var run := PackedByteArray()   # the best run being replayed
var run_n := 0
var run_laps: Array = []
var model: Node3D = null
var meshes: Array[GeometryInstance3D] = []
var scale_k := 1.0


## a new race: start recording; load the best run for this track and class (when the setting is on)
func start(best: Dictionary, show: bool, ri: int, my_spec: Dictionary) -> void:
	rec = PackedByteArray()
	rec_t = 0.0
	rec_n = 0
	rec_laps = []
	recording = true
	run = PackedByteArray()
	run_n = 0
	run_laps = []
	if model != null:
		model.queue_free()
		model = null
	meshes.clear()
	visible = false
	if not show or best.is_empty() or String(best.get("g", "")) == "" or not KartBuilder.ready():
		return
	run = Marshalls.base64_to_raw(String(best["g"]))
	run_n = run.size() / 14
	run_laps = best.get("laps", [])
	if run_n < 2:
		run_n = 0
		return
	var spec: Dictionary = best.get("spec", {})
	if spec.is_empty():
		spec = my_spec
	var built := KartBuilder.build(spec, int(best.get("dr", ri)))
	if built.is_empty():
		run_n = 0
		return
	model = built["node"]
	scale_k = float((built["meta"] as Dictionary).get("scale", 1.76))
	add_child(model)
	var gl = built.get("glider_node")
	if gl != null:
		(gl as Node).free()
	# see-through, with the faint blue glow of the web's ghost
	for n in model.find_children("*", "GeometryInstance3D", true, false):
		var gi := n as GeometryInstance3D
		gi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		gi.transparency = 1.0 - OPACITY
		meshes.append(gi)
		var mi := gi as MeshInstance3D
		if mi != null and mi.mesh != null:
			for si in mi.mesh.get_surface_count():
				var m := mi.get_active_material(si) as StandardMaterial3D
				if m != null:
					m = m.duplicate() as StandardMaterial3D
					m.emission_enabled = true
					m.emission = Color("#3a6aff")
					m.emission_energy_multiplier = 0.35
					mi.set_surface_override_material(si, m)


## record your kart (its drawn position and turn) while racing
func record(t: float, xf: Transform3D, finished: bool) -> void:
	if not recording or finished:
		return
	while rec_t <= t and rec_n < MAX:
		var q := xf.basis.get_rotation_quaternion()
		var i := rec.size()
		rec.resize(i + 14)
		var vals := [xf.origin.x * 4.0, xf.origin.y * 4.0, xf.origin.z * 4.0, q.x * 32767.0, q.y * 32767.0, q.z * 32767.0, q.w * 32767.0]
		for j in 7:
			rec.encode_s16(i + j * 2, clampi(int(round(float(vals[j]))), -32767, 32767))
		rec_n += 1
		rec_t += 1.0 / HZ


func _sample(i: int) -> Array:
	var o := i * 14
	var p := Vector3(run.decode_s16(o), run.decode_s16(o + 2), run.decode_s16(o + 4)) / 4.0
	var q := Quaternion(run.decode_s16(o + 6) / 32767.0, run.decode_s16(o + 8) / 32767.0, run.decode_s16(o + 10) / 32767.0, run.decode_s16(o + 12) / 32767.0).normalized()
	return [p, q]


## replay the best run at this moment of the race
func tick(t: float, racing: bool, cam_pos: Vector3) -> void:
	if model == null or run_n < 2:
		visible = false
		return
	var f := t * HZ
	var i := int(floor(f))
	if not racing or i >= run_n - 1 or i < 0:
		visible = false
		return
	var u := f - i
	var a := _sample(i)
	var b := _sample(i + 1)
	var p: Vector3 = (a[0] as Vector3).lerp(b[0], u)
	var q: Quaternion = (a[1] as Quaternion).slerp(b[1], u)
	visible = true
	global_transform = Transform3D(Basis(q) * Basis.from_scale(Vector3.ONE * scale_k), p)
	var near := Vector2(p.x - cam_pos.x, p.z - cam_pos.z).length_squared() < 30.0 * 30.0
	var tr := 1.0 - (OPACITY_NEAR if near else OPACITY)
	for gi in meshes:
		if is_instance_valid(gi):
			gi.transparency = tr


## a lap done: the split against the best run (web recLap), e.g. "+1.23s vs best", or "" without one
func lap(t: float, lap_n: int) -> String:
	if not recording:
		return ""
	rec_laps.append(t)
	var j := lap_n - 2
	if j < 0 or j >= run_laps.size():
		return ""
	var d := t - float(run_laps[j])
	return ("\u2212" if d < 0.0 else "+") + "%.2fs vs best" % absf(d)


## the run is over: what to save with it, when it is a personal best
func finish() -> Dictionary:
	recording = false
	if rec_n < 2:
		return {}
	return {"g": Marshalls.raw_to_base64(rec), "laps": rec_laps.duplicate()}


func stop() -> void:
	recording = false
	visible = false
