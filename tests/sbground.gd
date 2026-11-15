extends Node
## Sandbox's ground and walls on the PC against the web's own answers for the same place.
## tools/sbground.py asks the web game (in a browser) for sbG and sbBlocked at a few hundred points and writes them to a
## file; this test asks scripts/sandbox.gd the same questions and counts the differences:
##   ground    the web's sbG(x, z, wy) against ground(x, z, wy): must agree within 0.2
##   highest   sbG(x, z) with no height against ground(x, z): the same
##   blocked   sbBlocked(x, z, wy) against blocked(x, z, wy): must be identical, except on a pizza within one square of
##             a wall's edge (the PC's ground there is a sampled height map, the web's a formula: a cliff's or a shore's
##             edge can fall a little differently)
## Prints "SBGROUND PASS" or "SBGROUND FAIL" with the counts, and the first few differences.
## Run: CR_MAP=bedroom CR_MODE=sb CR_PROBE=<file from tools/sbground.py> CR_HD=0 <godot console> --headless --path . res://tests/sbground.tscn

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	main.test_hold = true
	add_child(main)
	var T: TrackData = main.T
	var sb = main.race.sb
	if sb != null:
		# the web's session has every gate; the PC leaves out those to places it does not have. For this comparison the
		# place is read again with every gate standing
		var S = load("res://scripts/sandbox.gd")
		S.places = {}
		sb = S.new()
		sb.setup(main.race, T)
	var path := OS.get_environment("CR_PROBE")
	var j = JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else null
	if sb == null or not (j is Dictionary):
		print("SBGROUND FAIL %s" % ("this is not Sandbox (run with CR_MODE=sb)" if sb == null else "no probe file at CR_PROBE='%s'" % path))
		get_tree().quit(1)
		return
	if String(j.get("id", "")) != sb.id:
		print("SBGROUND FAIL the probe file is for %s, the map is %s" % [String(j.get("id", "")), sb.id])
		get_tree().quit(1)
		return
	var pts: Array = j["pts"]
	var n := pts.size()
	var g_bad := 0
	var h_bad := 0
	var g_max := 0.0
	var b_bad := 0
	var b_edge := 0
	var shown := 0
	var by_why := [0, 0, 0, 0]
	var hm_n := 0          # points where the PC's height map itself is not the web's ground (a pizza's bare ground is a
	var hm_max := 0.0      # formula on the web and a 10-unit grid of samples on the PC): counted apart
	var hm_g := 0
	var hm_b := 0
	if not sb.free:
		# where you keep to the road the web's sbG is not what the kart stands on (the race's own ground is): nothing to compare
		print("SBGROUND PASS %s (road): the race's own ground and walls are used here; %d gates on the PC, %d in the web's session" % [sb.id, sb.gates.size(), (j.get("gates", []) as Array).size()])
		get_tree().quit(0)
		return
	for p in pts:
		var x := float(p[0])
		var z := float(p[1])
		var wy := float(p[2])
		var g: float = sb.ground(x, z, wy)
		var bl: bool = sb.blocked(x, z, wy)
		var hi: float = sb.ground(x, z)
		var dg := absf(g - float(p[3]))
		var dh := absf(hi - float(p[5]))
		var bad := ""
		var hm := false
		if not sb.toy and (p as Array).size() > 7:
			var dm := absf(T.ground(x, z) - float(p[7]))
			hm_max = maxf(hm_max, dm)
			hm = dm > 0.2
			if hm:
				hm_n += 1
		if hm and (dg > 0.2 or dh > 0.2 or bl != (int(p[4]) != 0)):
			# the height map's own difference: not the code's
			if dg > 0.2 or dh > 0.2:
				hm_g += 1
			if bl != (int(p[4]) != 0):
				hm_b += 1
			continue
		g_max = maxf(g_max, dg)
		if dg > 0.2:
			g_bad += 1
			bad += " ground %.2f web %.2f" % [g, float(p[3])]
		if dh > 0.2:
			h_bad += 1
			bad += " highest %.2f web %.2f" % [hi, float(p[5])]
		if bl != (int(p[4]) != 0):
			# is a wall's edge within one square of here? (the answer changes somewhere among the eight points round it)
			var edge := false
			var c: float = sb.cC if sb.has_col else 5.0
			for q in 8:
				if sb.blocked(x + cos(q * 0.785398) * c, z + sin(q * 0.785398) * c, wy) != bl:
					edge = true
					break
			if edge and sb.kind == "open":
				b_edge += 1
			else:
				b_bad += 1
				bad += " blocked %s web %s%s" % [str(bl), str(int(p[4]) != 0), " (at an edge)" if edge else ""]
		if bad != "":
			by_why[int(p[6])] += 1
			if shown < 12:
				shown += 1
				print("SBGROUND   at %.2f, %.2f height %.2f (kind %d):%s" % [x, z, wy, int(p[6]), bad])
	var ok := g_bad == 0 and h_bad == 0 and b_bad == 0
	print("SBGROUND %s %s (%s): %d points; ground differs at %d (largest %.3f), highest surface at %d, blocked differs at %d, and at %d more within a square of a wall's edge (allowed on a pizza); differences by kind of point [random at ground level, random height, along the lap, at the gates] %s; the web session's export %s the map's. The PC's height map is off the web's bare ground by more than 0.2 at %d points (largest %.2f): there the ground differed at %d and blocked at %d, not counted above" % [
		"PASS" if ok else "FAIL", sb.id, sb.kind, n, g_bad, g_max, h_bad, b_bad, b_edge, str(by_why), "is the same as" if bool(j.get("same_export", false)) else "DIFFERS from", hm_n, hm_max, hm_g, hm_b])
	get_tree().quit(0 if ok else 1)
