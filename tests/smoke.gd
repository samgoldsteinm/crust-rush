extends Node
## Headless test: loads the race, lets the auto-driver run all the laps and prints what happens.
## Prints "SMOKE PASS" when the race finishes, "SMOKE FAIL" otherwise.

const MAX_T := 320.0
var main: Node
var steps := 0
var next_print := 0.0
var respawns := 0
var prev_inv := 0.0
var max_air := 0.0
var glides := 0
var was_glide := false
var jumps := 0
var was_big := false
var wall_hits := 0
var prev_wall := 0.0


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	main.auto_drive = true
	print("SMOKE start: %d track points, %d laps, %d ramps, %d pads, %d obstacles" % [main.T.N, main.T.LAPS, main.T.ramps.size(), main.T.pads.size(), main.T.obstacles.size()])


func _physics_process(dt: float) -> void:
	steps += 1
	var t := steps * dt
	var k: Kart = main.kart
	if k.inv > 2.9 and prev_inv <= 2.9:
		respawns += 1
	prev_inv = k.inv
	if k.glide and not was_glide:
		glides += 1
	was_glide = k.glide
	if k.big and not was_big:
		jumps += 1
	was_big = k.big
	if k.wall_t > 0.3 and prev_wall <= 0.3:
		wall_hits += 1
	prev_wall = k.wall_t
	max_air = maxf(max_air, k.z)
	if t >= next_print:
		next_print += 10.0
		print("SMOKE t=%5.1f %s lap %d prog %d idx %d speed %.0f pos (%.0f, %.0f) h %.1f air %s glide %s boost %.2f" % [t, main.state, k.lap(), k.prog, k.idx, k.speed, k.x, k.y, k.wy, k.air, k.glide, k.boost])
	if main.state == "finished":
		print("SMOKE PASS finished in %.2f s, respawns %d, ramp jumps %d, glides %d, highest %.1f, wall hits %d" % [k.finish_time, respawns, jumps, glides, max_air, wall_hits])
		get_tree().quit(0)
	elif t > MAX_T:
		print("SMOKE FAIL no finish after %d s: prog %d of %d, respawns %d" % [int(t), k.prog, main.T.LAPS * main.T.N, respawns])
		get_tree().quit(1)
