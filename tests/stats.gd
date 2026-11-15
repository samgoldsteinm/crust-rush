extends Node
## Headless test of the garage's stats (KartBuilder.stat_mods / stat_bars / base_bars; the web's tools/mini/patch32.py).
## (1) for every body x wheel x glider: the build's bars are the vehicle's own bars plus the wheels' and the glider's
##     points, clamped to 0..12 (a bike's wheels are built in: they are in its own bars already);
## (2) writes every combination's stat_mods to D:/crust-rush/scratch/stats/pc_stats.json (CR_STATS_OUT names another
##     file) as {"b,w,g": [spd, acc, hnd, wgt, off]} to six places, keyed by the parts' places in the garage's lists
##     (the web's BODIES / WHEELS / GLIDERS), and compares it with web_stats.json beside it when that is there.
## Prints "STATS PASS" or "STATS FAIL".
## Run: <godot console> --headless --path . res://tests/stats.tscn


func _ready() -> void:
	var why: Array = []
	if not KartBuilder.ready():
		print("STATS FAIL the garage's parts are not there")
		get_tree().quit(1)
		return
	var was := KartBuilder.stats_on
	KartBuilder.stats_on = true
	var nb := (KartBuilder.info["bodies"] as Array).size()
	var nw := (KartBuilder.info["wheels"] as Array).size()
	var ng := (KartBuilder.info["gliders"] as Array).size()
	var out := {}
	var bad := 0
	var n := 0
	for b in nb:
		var bd: Dictionary = KartBuilder.info["bodies"][b]
		var bike := bool(bd.get("bike", false)) and bd.get("bw") != null
		for w in nw:
			for g in ng:
				var spec := {"b": b, "w": w, "g": g}
				var base: Array = KartBuilder.base_bars(spec)
				var tot: Array = KartBuilder.stat_bars(spec)
				var ws: Array = KartBuilder.wheel_of(spec)["st"]
				var gs: Array = KartBuilder.info["gliders"][g]["st"]
				for i in 5:
					var want := clampi(int(base[i]) + (0 if bike else int(ws[i])) + int(gs[i]), 0, 12)
					# (the vehicle's bars are clamped too; where that clamp bit, add to the unclamped sum the way the builder does)
					if int(base[i]) == 0 or int(base[i]) == 12:
						var raw := int(floor(6.0 + 6.0 * tanh(1.5 * float(bd["st"][i]) / 4.0) + 0.5))
						want = clampi(raw + int(ws[i]) + int(gs[i]), 0, 12)
					if int(tot[i]) != want:
						bad += 1
						if bad <= 5:
							why.append("%s + %s + %s, stat %d: bars %d, vehicle %d + wheels %d + glider %d" % [bd["id"], KartBuilder.wheel_of(spec)["id"], KartBuilder.info["gliders"][g]["id"], i, tot[i], base[i], ws[i], gs[i]])
				var m: Dictionary = KartBuilder.stat_mods(spec)
				out["%d,%d,%d" % [b, w, g]] = [snappedf(m["spd"], 0.000001), snappedf(m["acc"], 0.000001), snappedf(m["hnd"], 0.000001), snappedf(m["wgt"], 0.000001), snappedf(m["off"], 0.000001)]
				n += 1
	# stats off: every part cosmetic
	KartBuilder.stats_on = false
	var off: Dictionary = KartBuilder.stat_mods({"b": nb - 1, "w": nw - 1, "g": ng - 1})
	if off != {"spd": 1.0, "acc": 1.0, "hnd": 1.0, "wgt": 1.0, "off": 0.0}:
		why.append("stats off still changes the driving: %s" % str(off))
	KartBuilder.stats_on = was
	var path := OS.get_environment("CR_STATS_OUT")
	if path == "":
		path = "D:/crust-rush/scratch/stats/pc_stats.json"
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		why.append("could not write %s" % path)
	else:
		f.store_string(JSON.stringify(out))
		f.close()
	# the web's own table, if the web side has written it
	var wp := path.get_base_dir() + "/web_stats.json"
	var cmp := "no web_stats.json beside it to compare with"
	if FileAccess.file_exists(wp):
		var web = JSON.parse_string(FileAccess.get_file_as_string(wp))
		if web is Dictionary:
			var diff := 0
			var worst := 0.0
			var first := ""
			for k in out:
				if not web.has(k):
					diff += 1
					if first == "":
						first = "%s is not in the web's table" % k
					continue
				for i in 5:
					var d := absf(float(web[k][i]) - float(out[k][i]))
					worst = maxf(worst, d)
					if d > 1.5e-6:
						diff += 1
						if first == "":
							first = "%s: web %s, PC %s" % [k, str(web[k]), str(out[k])]
						break
			for k in web:
				if not out.has(k):
					diff += 1
					if first == "":
						first = "%s is only in the web's table" % k
			cmp = "against web_stats.json (%d builds there): %d differ, largest difference %.7f%s" % [(web as Dictionary).size(), diff, worst, "" if first == "" else " | first: " + first]
			if diff > 0:
				why.append("the web's table differs")
	if bad > 0:
		why.insert(0, "%d bars are not vehicle + wheels + glider" % bad)
	print("STATS %d bodies x %d wheels x %d gliders = %d builds written to %s; %s" % [nb, nw, ng, n, path, cmp])
	print("STATS %s%s" % ["PASS" if why.is_empty() else "FAIL", "" if why.is_empty() else " | " + "; ".join(PackedStringArray(why))])
	get_tree().quit(0 if why.is_empty() else 1)
