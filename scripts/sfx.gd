class_name Sfx
extends Node
## Sound, made at start-up from simple waveforms (as the web game does with Web Audio): an
## engine that follows the speed, a tyre squeal while drifting, and short effects.

const RATE := 22050
var bank := {}
var pool: Array[AudioStreamPlayer] = []
var eng: AudioStreamPlayer
var eng2: AudioStreamPlayer
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


## speed 0..~1.6 of top speed; gas: whether the engine is pulling
func drive(speed: float, gas: bool, boosting: bool, drifting: bool, tier: int, on: bool) -> void:
	if not on:
		eng.volume_db = -60.0
		eng2.volume_db = -60.0
		skid.volume_db = -60.0
		wind.volume_db = -60.0
		return
	var s := clampf(speed, 0.0, 1.7)
	eng.pitch_scale = 0.7 + s * 1.15 + (0.12 if boosting else 0.0)
	eng2.pitch_scale = eng.pitch_scale
	eng.volume_db = linear_to_db(volume * (0.2 + 0.14 * s) * (1.0 if gas else 0.6))
	eng2.volume_db = linear_to_db(volume * maxf(0.001, (s - 0.35) * 0.2) * (1.3 if boosting else 1.0))
	skid.volume_db = linear_to_db(volume * 0.22) if drifting else -60.0
	skid.pitch_scale = 0.9 + 0.12 * tier
	wind.volume_db = linear_to_db(volume * clampf((s - 0.4) * 0.35, 0.001, 0.4))
	wind.pitch_scale = 0.8 + 0.5 * s
