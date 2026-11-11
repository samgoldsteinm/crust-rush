class_name Sfx
extends Node
## Sound, made at start-up from simple waveforms (as the web game does with Web Audio): an
## engine that follows the speed, a tyre squeal while drifting, and short effects. Each kind of kart body has its own
## engine voice (a buzzy kart, a screaming race car, a burbling V8, a smooth jet or electric hum), pitched with the revs
## through the gears like the web's. It speaks up when you work it (pulling away, each gear, a boost) and settles back
## to a soft hum at a steady speed, so it is there without droning all race.

## engine voice per kart body and its tuning (web ENG_BODY / ENG_PROF): [pitch, gears, voice, unused, level]
const ENG_BODY := {"delivery": "v8", "formula": "race", "interceptor": "race", "hyper": "race", "onyx": "race", "roadster": "race", "scissor": "race",
	"gt": "race", "coupe": "race", "muscle": "v8", "monster": "v8", "suv": "v8", "rocket": "jet", "bike_rocket": "jet", "bike_moto": "bike", "bike_mx": "bike",
	"bike_neutron": "bike", "bike_june": "hum", "oven": "chug", "chariot": "chug"}
const ENG_PROF := {"std": [1.0, true, "pulse", 1.0, 1.0], "race": [1.55, true, "scream", 1.0, 0.8], "v8": [0.62, true, "v8", 1.0, 1.15],
	"jet": [2.2, false, "hum", 1.0, 0.7], "bike": [1.25, true, "pulse", 1.0, 0.95], "hum": [3.1, false, "hum", 1.0, 0.6], "chug": [0.8, true, "v8", 1.0, 1.1]}
const ENG_BASE := 46.0     # every voice's loop is built on this fundamental

const RATE := 22050
var bank := {}
var pool: Array[AudioStreamPlayer] = []
var eng: AudioStreamPlayer
var eng2: AudioStreamPlayer
var rec: AudioStreamPlayer        # the recorded engine voice
var prof: Array = ENG_PROF["std"]
var rec_name := ""
var voice := ""
var prev_sp := -1.0
var prev_gi := 0
var kick := 0.0
var act := 0.0
var skid: AudioStreamPlayer
var wind: AudioStreamPlayer
var rng := RandomNumberGenerator.new()
var volume := 0.8


func _ready() -> void:
	rng.seed = 7
	_build()
	for i in 10:
		var p := AudioStreamPlayer.new()
		add_child(p)
		pool.append(p)
	eng = _loop_player("engine")
	eng2 = _loop_player("engine2")
	rec = AudioStreamPlayer.new()
	rec.volume_db = -60.0
	add_child(rec)
	skid = _loop_player("skid")
	wind = _loop_player("wind")


func _loop_player(name_: String) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = bank[name_]
	p.volume_db = -60.0
	add_child(p)
	p.play()
	return p


func _wav(s: PackedFloat32Array, loop := false) -> AudioStreamWAV:
	var data := PackedByteArray()
	data.resize(s.size() * 2)
	for i in s.size():
		data.encode_s16(i * 2, int(clampf(s[i], -1.0, 1.0) * 32000.0))
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = RATE
	w.stereo = false
	w.data = data
	if loop:
		w.loop_mode = AudioStreamWAV.LOOP_FORWARD
		w.loop_begin = 0
		w.loop_end = s.size()
	return w


## notes: [[freq, start, length, volume], ...]; shape 0 sine, 1 triangle, 2 square, 3 saw
func _tones(notes: Array, shape: int, total: float) -> PackedFloat32Array:
	var n := int(total * RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	for nt in notes:
		var f: float = nt[0]
		var t0: float = nt[1]
		var ln: float = nt[2]
		var vol: float = nt[3]
		var f1: float = nt[4] if nt.size() > 4 else f
		var a := int(t0 * RATE)
		var b := mini(n, int((t0 + ln) * RATE))
		var ph := 0.0
		for i in range(a, b):
			var u := float(i - a) / float(maxi(1, b - a))
			var fr := f + (f1 - f) * u
			ph += fr / RATE
			var x := fposmod(ph, 1.0)
			var v := 0.0
			if shape == 0:
				v = sin(x * TAU)
			elif shape == 1:
				v = 4.0 * absf(x - 0.5) - 1.0
			elif shape == 2:
				v = 1.0 if x < 0.5 else -1.0
			else:
				v = 2.0 * x - 1.0
			var envl := minf(1.0, u * 30.0) * pow(1.0 - u, 1.6)
			out[i] += v * vol * envl
	return out


## filtered noise: low-pass that sweeps from c0 to c1 (0..1), fading out
func _noise(total: float, c0: float, c1: float, vol: float, hp := 0.0) -> PackedFloat32Array:
	var n := int(total * RATE)
	var out := PackedFloat32Array()
	out.resize(n)
	var lp := 0.0
	var lp2 := 0.0
	for i in n:
		var u := float(i) / float(n)
		var c := c0 + (c1 - c0) * u
		var w := rng.randf() * 2.0 - 1.0
		lp += (w - lp) * c
		lp2 += (lp - lp2) * hp
		var envl := minf(1.0, u * 40.0) * pow(1.0 - u, 1.3)
		out[i] = (lp - lp2 * (1.0 if hp > 0.0 else 0.0)) * vol * envl
	return out


func _mix(a: PackedFloat32Array, b: PackedFloat32Array) -> PackedFloat32Array:
	var out := a.duplicate()
	if b.size() > out.size():
		out.resize(b.size())
	for i in b.size():
		out[i] += b[i]
	return out


func _build() -> void:
	# engine: one second that loops cleanly (whole numbers of cycles), two voices an octave apart
	for which in 2:
		var n := RATE
		var s := PackedFloat32Array()
		s.resize(n)
		var base := 46.0 if which == 0 else 92.0
		for i in n:
			var t := float(i) / RATE
			var v := 0.0
			for h in range(1, 9):
				var amp := 1.0 / pow(h, 1.15) * (1.0 if h % 2 == 1 else 0.6)
				v += sin(TAU * base * h * t + h * 0.7) * amp
			v *= 0.75 + 0.25 * sin(TAU * base * 0.5 * t)       # a lumpy idle
			s[i] = tanh(v * 0.9) * 0.5
		bank["engine" if which == 0 else "engine2"] = _wav(s, true)
	# the voices (web engWaves): harmonic recipes on one 46 Hz fundamental, one second that loops cleanly
	var recipes := {
		"pulse": [[1, 1.0], [2, 0.55], [3, 0.6], [4, 0.28], [5, 0.33], [6, 0.12], [7, 0.16], [9, 0.07]],
		"scream": [[1, 0.8], [2, 0.7], [3, 0.55], [4, 0.5], [5, 0.38], [6, 0.32], [8, 0.2], [10, 0.12], [12, 0.07]],
		"v8": [[0.5, 0.55], [1, 1.0], [1.5, 0.35], [2, 0.5], [3, 0.3], [4, 0.14], [6, 0.06]],
		"hum": [[1, 1.0], [2, 0.18], [3, 0.08]],
	}
	for vn in recipes:
		var n2 := RATE
		var s2 := PackedFloat32Array()
		s2.resize(n2)
		var rr: Array = recipes[vn]
		var peak := 0.0
		for i in n2:
			var t := float(i) / RATE
			var v := 0.0
			for hv in rr:
				var h: float = hv[0]
				v += sin(TAU * 46.0 * h * t + h * 1.3) * float(hv[1])
			# the firing pulse: a little louder on each beat (twice as lumpy on the V8)
			var lump := 0.8 + 0.2 * sin(TAU * 46.0 * (0.25 if vn == "v8" else 0.5) * t)
			v = tanh(v * 0.7 * lump)
			s2[i] = v
			peak = maxf(peak, absf(v))
		for i in n2:
			s2[i] = s2[i] / maxf(peak, 0.01) * 0.6
		bank["eng_" + vn] = _wav(s2, true)
	# tyre squeal: narrow noise around a wavering pitch
	var sk := PackedFloat32Array()
	sk.resize(RATE)
	var lp := 0.0
	var bp := 0.0
	for i in RATE:
		var t2 := float(i) / RATE
		var w := rng.randf() * 2.0 - 1.0
		var f := 0.32 + 0.05 * sin(TAU * 3.0 * t2)
		lp += f * bp
		var hpv := w - lp - 0.12 * bp
		bp += f * hpv
		sk[i] = clampf(bp * 0.22, -1.0, 1.0) * (0.8 + 0.2 * sin(TAU * 7.0 * t2))
	bank["skid"] = _wav(sk, true)
	# wind rush at speed
	var wd := PackedFloat32Array()
	wd.resize(RATE)
	var l2 := 0.0
	for i in RATE:
		l2 += ((rng.randf() * 2.0 - 1.0) - l2) * 0.06
		wd[i] = l2 * 1.6
	for i in 2000:      # cross-fade the ends so the loop has no click
		var u := float(i) / 2000.0
		wd[i] = wd[i] * u + wd[RATE - 2000 + i] * (1.0 - u)
	wd.resize(RATE - 2000)
	bank["wind"] = _wav(wd, true)

	bank["beep"] = _wav(_tones([[440.0, 0.0, 0.22, 0.5]], 1, 0.25))
	bank["go"] = _wav(_tones([[880.0, 0.0, 0.5, 0.5], [1320.0, 0.0, 0.5, 0.25]], 1, 0.55))
	bank["pickup"] = _wav(_tones([[659.0, 0.0, 0.09, 0.4], [880.0, 0.07, 0.09, 0.4], [1319.0, 0.14, 0.16, 0.4]], 1, 0.34))
	bank["ready"] = _wav(_tones([[1047.0, 0.0, 0.12, 0.4], [1568.0, 0.09, 0.22, 0.4]], 0, 0.34))
	# a glide ring: three bells rising (web SFX.ring: 1047, 1319, 1568 Hz, .05 s apart)
	bank["ring"] = _wav(_tones([[1047.0, 0.0, 0.35, 0.3], [1319.0, 0.05, 0.35, 0.3], [1568.0, 0.1, 0.35, 0.3]], 0, 0.5))
	bank["roll"] = _wav(_tones([[1200.0, 0.0, 0.04, 0.25]], 2, 0.05))
	bank["throw"] = _wav(_mix(_noise(0.22, 0.5, 0.05, 0.6), _tones([[700.0, 0.0, 0.18, 0.25, 240.0]], 0, 0.22)))
	bank["boost"] = _wav(_mix(_noise(0.7, 0.08, 0.55, 0.7), _tones([[160.0, 0.0, 0.6, 0.35, 620.0]], 3, 0.7)))
	bank["hit"] = _wav(_mix(_noise(0.45, 0.7, 0.04, 0.9), _tones([[220.0, 0.0, 0.4, 0.6, 50.0]], 2, 0.45)))
	bank["bump"] = _wav(_mix(_noise(0.16, 0.3, 0.03, 0.8), _tones([[120.0, 0.0, 0.15, 0.7, 50.0]], 0, 0.16)))
	bank["shield"] = _wav(_tones([[784.0, 0.0, 0.3, 0.3], [988.0, 0.06, 0.3, 0.3], [1175.0, 0.12, 0.4, 0.3]], 0, 0.55))
	bank["block"] = _wav(_mix(_tones([[1175.0, 0.0, 0.2, 0.4], [784.0, 0.08, 0.3, 0.4]], 1, 0.4), _noise(0.2, 0.6, 0.1, 0.4)))
	bank["boom"] = _wav(_mix(_noise(0.8, 0.5, 0.01, 1.0), _tones([[90.0, 0.0, 0.7, 0.8, 30.0]], 0, 0.8)))
	bank["hop"] = _wav(_tones([[300.0, 0.0, 0.1, 0.3, 520.0]], 0, 0.11))
	bank["tier"] = _wav(_tones([[900.0, 0.0, 0.1, 0.3, 1400.0]], 1, 0.11))
	bank["trick"] = _wav(_tones([[523.0, 0.0, 0.08, 0.35], [784.0, 0.06, 0.08, 0.35], [1047.0, 0.12, 0.14, 0.35]], 1, 0.28))
	bank["land"] = _wav(_noise(0.14, 0.25, 0.02, 0.7))
	bank["lap"] = _wav(_tones([[784.0, 0.0, 0.14, 0.4], [1047.0, 0.12, 0.14, 0.4], [1319.0, 0.24, 0.3, 0.4]], 1, 0.56))
	bank["finish"] = _wav(_tones([[523.0, 0.0, 0.16, 0.4], [659.0, 0.14, 0.16, 0.4], [784.0, 0.28, 0.16, 0.4], [1047.0, 0.42, 0.5, 0.45], [784.0, 0.42, 0.5, 0.25]], 1, 0.95))
	bank["ability"] = _wav(_mix(_mix(_tones([[523.0, 0.0, 0.6, 0.22], [784.0, 0.06, 0.6, 0.22], [1047.0, 0.12, 0.6, 0.22], [1568.0, 0.18, 0.6, 0.2]], 0, 0.8), _noise(0.8, 0.6, 0.9, 0.18, 0.5)), _tones([[100.0, 0.0, 0.3, 0.5, 45.0]], 0, 0.3)))
	bank["warn"] = _wav(_tones([[1500.0, 0.0, 0.07, 0.3], [1500.0, 0.12, 0.07, 0.3]], 2, 0.2))


func play(name_: String, vol := 1.0, pitch := 1.0) -> void:
	if not bank.has(name_) or vol <= 0.01:
		return
	for p in pool:
		if not p.playing:
			p.stream = bank[name_]
			p.volume_db = linear_to_db(clampf(vol * volume, 0.001, 1.5))
			p.pitch_scale = pitch
			p.play()
			return


## the engine voice for a kart body (its id from the garage)
func set_body(body_id: String) -> void:
	prof = ENG_PROF.get(ENG_BODY.get(body_id, "std"), ENG_PROF["std"])
	var want := "eng_" + String(prof[2])
	prev_sp = -1.0
	act = 0.0
	if want == voice or not bank.has(want):
		return
	voice = want
	eng.stream = bank[want]
	eng.play(randf() * 0.9)


## speed 0..~1.6 of top speed; gas: whether the engine is pulling
func drive(speed: float, gas: bool, boosting: bool, drifting: bool, tier: int, on: bool) -> void:
	if not on:
		eng.volume_db = -60.0
		eng2.volume_db = -60.0
		rec.volume_db = -60.0
		skid.volume_db = -60.0
		wind.volume_db = -60.0
		return
	var s := clampf(speed, 0.0, 1.7)
	var dt := maxf(get_process_delta_time(), 1e-3)
	rec.volume_db = -60.0
	# revs climb through each gear and drop at the shift, like the web's (jets and electric motors glide)
	var GT := [0.0, 0.2, 0.42, 0.64, 0.86, 1.31]
	var r := minf(1.3, s)
	var gi := 0
	while gi < 4 and r > float(GT[gi + 1]):
		gi += 1
	var rpm: float
	if bool(prof[1]):
		rpm = minf(1.12, 0.3 + 0.7 * minf(1.0, (r - float(GT[gi])) / (float(GT[gi + 1]) - float(GT[gi]))) + (0.12 if boosting else 0.0))
	else:
		rpm = minf(1.12, 0.25 + 0.7 * minf(1.2, r) + (0.12 if boosting else 0.0))
	var ef := (24.0 + rpm * 58.0 + (gi * 4.0 if bool(prof[1]) else 0.0)) * float(prof[0])
	eng.pitch_scale = clampf(ef / ENG_BASE, 0.25, 4.0)
	eng2.pitch_scale = eng.pitch_scale
	# it speaks up when you work it (pulling away, each gear, a boost) and settles to a soft hum at a steady speed
	var a := 0.0 if prev_sp < 0.0 else (s - prev_sp) / dt
	prev_sp = s
	if gi != prev_gi:
		if a > 0.0:
			kick = 0.55
		prev_gi = gi
	kick = maxf(0.0, kick - dt * 1.4)
	var tgt := maxf(maxf(clampf(a / 0.5, 0.0, 1.0), 0.9 if boosting else 0.0), maxf(kick, 0.6 if (r < 0.12 and a > 0.01 and gas) else 0.0))
	act += (tgt - act) * (1.0 - exp(-dt / (0.1 if tgt > act else 1.2)))
	var lv := volume * float(prof[4]) * ((0.13 + 0.09 * rpm) + act * (0.13 + 0.1 * rpm)) * (1.0 if gas else 0.75)
	eng.volume_db = linear_to_db(maxf(0.0005, lv))
	eng2.volume_db = linear_to_db(maxf(0.0005, lv * 0.12 * rpm))
	skid.volume_db = linear_to_db(volume * 0.22) if drifting else -60.0
	skid.pitch_scale = 0.9 + 0.12 * tier
	wind.volume_db = linear_to_db(volume * clampf((s - 0.4) * 0.35, 0.001, 0.4))
	wind.pitch_scale = 0.8 + 0.5 * s
