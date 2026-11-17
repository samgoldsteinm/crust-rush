"""The PC side of web patch 74 (v222): a delivery's arrow, under the delivery bar at the top.
    py.cmd tools/mini/pc74.py      (once; edits D:/crust-rush/godot/scripts)
main.gd: hud.sb_arrow = [angle (radians, 0 = straight ahead on the screen, + to the right), "To <place> · N m" / "Start line · N m"]
while a delivery runs: in its place, its start flag; elsewhere the gate to the next place on the shortest way (_sb_next_hop: a breadth-first
walk over SandboxMap.LINKS and HOUSE_GATES, both ways, installed places only). hud.gd draws the arrow and the line under the bar.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('main.gd', """	hud.sb_bar = SandboxActs.bar() if state == "race" and not sb_trav else []
""", """	hud.sb_bar = SandboxActs.bar() if state == "race" and not sb_trav else []
	hud.sb_arrow = _sb_del_arrow(sb) if not hud.sb_bar.is_empty() else []   # (pc74, web patch 74)
	if hud.sb_bar.is_empty():
		_sb_arrow3d(false)
""")
rep('main.gd', """const SandboxMap := preload("res://scripts/sandbox_map.gd")
""", """const SandboxMap := preload("res://scripts/sandbox_map.gd")
var _sb_hops := {}


## (pc74, web sbNextHop) the next place on the shortest way from one place to another, over the map's links, both ways
func _sb_next_hop(from: String, to: String) -> String:
	var key := from + ">" + to
	if _sb_hops.has(key):
		return _sb_hops[key]
	var adj := {}
	var add := func(a: String, b: String) -> void:
		if not Sandbox.has_place(a) or not Sandbox.has_place(b):
			return
		if not adj.has(a):
			adj[a] = {}
		if not adj.has(b):
			adj[b] = {}
		adj[a][b] = true
		adj[b][a] = true
	for a in SandboxMap.LINKS:
		for b in SandboxMap.LINKS[a]:
			add.call(String(a), String(b))
	for a in SandboxMap.HOUSE_GATES:
		for g in SandboxMap.HOUSE_GATES[a]:
			add.call(String(a), String(g[3]))
	var prev := {from: ""}
	var q: Array = [from]
	while not q.is_empty():
		var c: String = q.pop_front()
		if c == to:
			break
		for n in (adj.get(c, {}) as Dictionary).keys():
			if not prev.has(n):
				prev[n] = c
				q.append(n)
	var hop := ""
	if prev.has(to):
		var c2 := to
		while String(prev[c2]) != from and String(prev[c2]) != "":
			c2 = String(prev[c2])
		hop = c2
	_sb_hops[key] = hop
	return hop


## (pc74, web sbDelAim / sbDelArrow) the delivery's arrow: [angle on the screen, what it points at]
func _sb_del_arrow(sb) -> Array:
	var A: Dictionary = SandboxActs.act
	if A.is_empty() or String(A["a"]["kind"]) != "deliver" or kart == null or cam == null or sb_trav:
		_sb_arrow3d(false)
		return []
	var to := String(A["a"]["to"])
	var tx := 0.0
	var tz := 0.0
	var say := ""
	if String(sb.id) == to:
		if not sb.has_flag:
			_sb_arrow3d(false)
			return []
		tx = float(sb.flag[0])
		tz = float(sb.flag[2])
		say = "Start line"
	else:
		var hop := _sb_next_hop(String(sb.id), to)
		var gate = null
		for g in sb.gates:
			if String(g["to"]) == hop:
				gate = g
		if gate == null:
			_sb_arrow3d(false)
			return []
		tx = float(gate["x"])
		tz = float(gate["z"])
		var m := _map_info(hop)
		say = "To " + String(m.get("name", hop))
	var dx := tx - kart.x
	var dz := tz - kart.y
	_sb_arrow3d(true, atan2(-dz, dx))
	return [0.0, "%s · %d m" % [say, int(round(Vector2(dx, dz).length() * 0.25))]]


## (pc74, web sbDel3D; the owner: "make the arrow a 3d orange arrow that changes direction based on where you need to go and the
## direction the car is facing") a 3D orange arrow floating above the kart, turned in the world toward where to drive; it bobs a little
var _sb_a3: Node3D = null
func _sb_arrow3d(on: bool, yaw := 0.0) -> void:
	if not on or kart == null or cam == null:
		if _sb_a3 != null:
			_sb_a3.visible = false
		return
	if _sb_a3 == null or not is_instance_valid(_sb_a3):
		_sb_a3 = Node3D.new()
		var poly := CSGPolygon3D.new()
		poly.polygon = PackedVector2Array([Vector2(9, 0), Vector2(1.5, 5.6), Vector2(1.5, 1.7), Vector2(-5, 1.7), Vector2(-5, -1.7), Vector2(1.5, -1.7), Vector2(1.5, -5.6)])
		poly.depth = 1.0
		var m := StandardMaterial3D.new()
		m.albedo_color = Color("#ff7a12")
		m.emission_enabled = true
		m.emission = Color("#ff5a00")
		m.emission_energy_multiplier = 0.12   # (lit and shaded by the scene: the owner asked for lighting and shadows)
		m.roughness = 0.35
		poly.material = m
		poly.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		poly.rotation = Vector3(-PI / 2.0, 0, 0)   # (the outline lies flat, pointing +x)
		poly.position = Vector3(0, 0.8, 0)
		var tilt := Node3D.new()
		tilt.rotation = Vector3(0, 0, -0.75)
		tilt.add_child(poly)
		_sb_a3.add_child(tilt)
		_sb_a3.scale = Vector3.ONE * 0.8
	var host: Node = (view.views[kart]["g"] as Node3D).get_parent() if view != null and view.views.has(kart) else null   # (beside the kart's own model: the same space)
	if host == null:
		return
	if _sb_a3.get_parent() != host:
		if _sb_a3.get_parent() != null:
			_sb_a3.get_parent().remove_child(_sb_a3)
		host.add_child(_sb_a3)
	_sb_a3.visible = true
	var tt := Time.get_ticks_msec() / 1000.0
	_sb_a3.position = Vector3(kart.x, kart.wy + 19.0 + sin(tt * 2.4) * 0.5, kart.y)
	_sb_a3.rotation.y += wrapf(yaw - _sb_a3.rotation.y, -PI, PI) * 0.2
""")
rep('hud.gd', """var sb_bar: Array = []    # Sandbox: the one under way, [title, line, fraction, hurry]
""", """var sb_bar: Array = []    # Sandbox: the one under way, [title, line, fraction, hurry]
var sb_arrow: Array = []  # (pc74) a delivery's way: [angle on the screen (0 ahead, + right), "To <place> · N m"]
""")
rep('hud.gd', """		var fr := clampf(float(sb_bar[2]), 0.0, 1.0)
		if fr > 0.0:
			_rbox(x + 14.0, y + 44.0, (w - 28.0) * fr, 5.0, Color("#e8542f") if bool(sb_bar[3]) else Color("#ffd65a"), Color(0, 0, 0, 0), 0.0, 3.0)
""", """		var fr := clampf(float(sb_bar[2]), 0.0, 1.0)
		if fr > 0.0:
			_rbox(x + 14.0, y + 44.0, (w - 28.0) * fr, 5.0, Color("#e8542f") if bool(sb_bar[3]) else Color("#ffd65a"), Color(0, 0, 0, 0), 0.0, 3.0)
		if sb_arrow.size() == 2:
			# (pc74) the arrow and what it points at, under the bar (web patch 74)
			var lt := String(sb_arrow[1])
			var aw := _str_w(f_bold, lt, 13.0) + 28.0
			var ax := W / 2.0 - aw / 2.0
			var ay := y + 64.0
			_rbox(ax, ay, aw, 30.0, Color(18.0 / 255, 9.0 / 255, 6.0 / 255, 0.7), Color(1, 0.957, 0.863, 0.35), 2.0, 12.0)
			_text(f_bold, lt, ax + 14.0, ay + 7.0, 13.0, CREAM)
""")
print('pc74 applied')

# the owner: "the character special ability is covering the coin box on sandbox on pc": in Sandbox the Special and Rear buttons go below
# the place's read-out (top 64, 76 high), as the web's do
rep('hud.gd', """		_draw_special(btn, top)   # (in Sandbox too since web v200: abilities work there)""",
    """		_draw_special(btn, _special_top(top))   # (in Sandbox too since web v200: abilities work there; pc74: below its read-out)""")
rep('hud.gd', """func special_rect() -> Rect2:
	var btn := _btn()
	var size := btn * 0.95
	var x := maxf(8.0, btn * 0.12) + 16.0
	return Rect2(Vector2(x, 12.0 + _hud_top()) * s, Vector2(size, size) * s)""", """func special_rect() -> Rect2:
	var btn := _btn()
	var size := btn * 0.95
	var x := maxf(8.0, btn * 0.12) + 16.0
	return Rect2(Vector2(x, 12.0 + _special_top(_hud_top())) * s, Vector2(size, size) * s)


## (pc74) the Special button's top: in Sandbox below the place's read-out (64 + 76 + a gap), else the usual
func _special_top(top: float) -> float:
	if race != null and race.mode == "sb" and race.sb != null:
		return maxf(top, 64.0 + 76.0 + 12.0 - 12.0 + 10.0)
	return top""")
print('pc74 (Sandbox special) applied')

# the owner: "when doing a mission fast travel should not be allowed": the map's fast travel is refused while a delivery or a challenge is
# under way (a Retry still goes back by fast travel: SandboxActs.retry)
rep('main.gd', """func _sb_map_travel(id: String) -> void:
	if id == "shop":""", """func _sb_map_travel(id: String) -> void:
	if not SandboxActs.act.is_empty() and SandboxActs.retry == "":
		_toast("No fast travel during a mission: drive there")   # (pc74)
		return
	if id == "shop":""")
rep('main.gd', """	if SandboxActs.retry == "" and not SandboxActs.act.is_empty() and String(SandboxActs.act["a"]["kind"]) == "deliver":
		SandboxActs.finish("cancel")   # (fast travel cannot finish a delivery)""", """	if SandboxActs.retry == "" and not SandboxActs.act.is_empty():
		_toast("No fast travel during a mission: drive there")   # (pc74: refused, not the mission ended)
		return""")
print('pc74 (no fast travel) applied')
