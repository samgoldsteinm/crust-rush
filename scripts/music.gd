class_name Music
extends Node
## The soundtrack (web musTick): every track has its own song, the menus take turns through four. Songs are
## rendered from the web game's music by tools/cimusic.py (one Ogg file each, with its loop point and where its
## chorus starts). The final lap jumps straight into the chorus, a little faster.

const DIR := "res://assets/music/"

var info := {}
var on := true
var level := 0.45            # Settings > Music volume (the web's default is 45)
var players: Array[AudioStreamPlayer] = []
var cur := 0                 # which player is the live one
var key := ""                # the song playing
var menu_i := 0
var menu_t := 0.0
var mul := 0.95              # how loud for where we are (race, menu, paused, loading)
var fade := [0.0, 0.0]       # each player's fade (0..1)
var fade_to := [0.0, 0.0]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 2:
		var p := AudioStreamPlayer.new()
		p.volume_db = -80.0
		add_child(p)
		players.append(p)
	var path := DIR + "music.json"
	if FileAccess.file_exists(path):
		var j = JSON.parse_string(FileAccess.get_file_as_string(path))
		if typeof(j) == TYPE_DICTIONARY:
			info = j
	menu_i = randi() % 4


func ready() -> bool:
	return not info.is_empty()


func _stream(k: String) -> AudioStream:
	var s: Dictionary = info.get("songs", {}).get(k, {})
	if s.is_empty():
		return null
	var p := DIR + String(s["file"])
	if not ResourceLoader.exists(p):
		return null
	var st = load(p)
	if st is AudioStreamOggVorbis:
		(st as AudioStreamOggVorbis).loop = true
		(st as AudioStreamOggVorbis).loop_offset = float(s["loop"])
	return st


## what should be playing: the track's song while racing (state race, countdown, paused, loading), else a menu song
func want(map_id: String, state: String, paused: bool, dt: float) -> void:
	if not ready():
		return
	var playing := state in ["race", "countdown", "finished", "results", "loading"] or paused
	var k := ""
	if on:
		if playing:
			k = String(info.get("maps", {}).get(map_id, "margherita"))
		else:
			var ms: Array = info.get("menu", [])
			if not ms.is_empty():
				menu_t += dt
				# after about three minutes, the next menu song
				if menu_t > 180.0:
					menu_t = 0.0
					menu_i += 1
				k = String(ms[menu_i % ms.size()])
	var vol: Dictionary = info.get("vol", {})
	var m := float(vol.get("menu", 0.95))
	if paused:
		m = float(vol.get("paused", 0.3))
	elif state == "loading":
		m = float(vol.get("loading", 0.55))
	elif playing:
		m = float(vol.get("race", 0.62))
	mul += (m - mul) * minf(1.0, dt * 6.0)
	if k != key:
		_switch(k)
	for i in 2:
		fade[i] = move_toward(float(fade[i]), float(fade_to[i]), dt / (0.5 if float(fade_to[i]) > float(fade[i]) else 0.6))
		var lin := float(fade[i]) * level * mul
		players[i].volume_db = linear_to_db(maxf(0.0001, lin))
		if float(fade[i]) <= 0.0 and float(fade_to[i]) <= 0.0 and players[i].playing:
			players[i].stop()


func _switch(k: String) -> void:
	key = k
	fade_to[cur] = 0.0
	if k == "":
		return
	var st := _stream(k)
	if st == null:
		return
	cur = 1 - cur
	var p := players[cur]
	p.stream = st
	p.pitch_scale = 1.0
	p.play()
	fade[cur] = 0.0
	fade_to[cur] = 1.0


## the final lap: straight into the chorus, a little faster (web musFinalLap)
func final_lap() -> void:
	if key == "" or not ready():
		return
	var s: Dictionary = info.get("songs", {}).get(key, {})
	if s.is_empty() or bool(s.get("menu", false)):
		return
	var p := players[cur]
	if not p.playing:
		return
	p.pitch_scale = 1.06
	p.seek(float(s["chorus"]))


func stop_all() -> void:
	key = ""
	for i in 2:
		fade_to[i] = 0.0
