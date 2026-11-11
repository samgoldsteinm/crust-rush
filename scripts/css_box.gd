@tool
class_name CssBox
extends StyleBox
## A CSS-like box for the menus: rounded corners, a linear gradient fill (any angle, several stops),
## a border, outer box-shadows (blurred, spread, offset), a soft top highlight and an inner bottom
## shade. Lets Godot buttons and panels look like the web game's menu CSS.

@export var colors := PackedColorArray([Color(0.1, 0.05, 0.03, 0.8)])
@export var stops := PackedFloat32Array([0.0])
@export var angle := 180.0                     # CSS degrees: 180 = top to bottom, 90 = left to right
@export var radius := Vector4(12, 12, 12, 12)  # top-left, top-right, bottom-right, bottom-left
@export var border_color := Color(0, 0, 0, 0)
@export var border_width := 0.0
@export var shadows: Array = []                 # [{off: Vector2, blur: float, spread: float, color: Color}]
@export var inset_top := Color(0, 0, 0, 0)      # inset 0 1px 0 <color>: a 1px highlight under the top edge
@export var inset_bottom := Color(0, 0, 0, 0)   # inset 0 -Npx Mpx <color>: a shade at the bottom
@export var inset_bottom_h := 10.0
@export var scale := 1.0                        # CSS px -> screen px
@export var grow := 0.0                         # drawn this much outside the control (CSS outline-offset), CSS px


static func make(cols: Array, ang := 180.0, r := 12.0, border := Color(0, 0, 0, 0), bw := 0.0, pad := Vector4(12, 8, 12, 8)) -> CssBox:
	var b := CssBox.new()
	var c := PackedColorArray()
	var o := PackedFloat32Array()
	for i in cols.size():
		var e = cols[i]
		if e is Array:
			c.append(e[1])
			o.append(float(e[0]))
		else:
			c.append(e)
			o.append(float(i) / maxf(1.0, cols.size() - 1.0))
	b.colors = c
	b.stops = o
	b.angle = ang
	b.radius = Vector4(r, r, r, r)
	b.border_color = border
	b.border_width = bw
	b.content_margin_left = pad.x
	b.content_margin_top = pad.y
	b.content_margin_right = pad.z
	b.content_margin_bottom = pad.w
	return b


func shadow(off: Vector2, blur: float, col: Color, spread := 0.0) -> CssBox:
	shadows.append({"off": off, "blur": blur, "spread": spread, "color": col})
	return self


func _col_at(f: float) -> Color:
	if colors.size() == 1:
		return colors[0]
	if f <= stops[0]:
		return colors[0]
	for i in range(1, colors.size()):
		if f <= stops[i]:
			var t := (f - stops[i - 1]) / maxf(1e-4, stops[i] - stops[i - 1])
			return colors[i - 1].lerp(colors[i], t)
	return colors[colors.size() - 1]


## the rounded rectangle's outline, clockwise from the top-left corner
static func outline(r: Rect2, rad: Vector4, seg := 6) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var rr := [rad.x, rad.y, rad.z, rad.w]
	var lim := minf(r.size.x, r.size.y) / 2.0
	for i in 4:
		rr[i] = clampf(rr[i], 0.0, lim)
	var centres := [r.position + Vector2(rr[0], rr[0]), Vector2(r.end.x - rr[1], r.position.y + rr[1]), r.end - Vector2(rr[2], rr[2]), Vector2(r.position.x + rr[3], r.end.y - rr[3])]
	var a0 := [PI, PI * 1.5, 0.0, PI * 0.5]
	for i in 4:
		var c: Vector2 = centres[i]
		var ra: float = rr[i]
		if ra <= 0.01:
			pts.append(c)
			continue
		var n := maxi(2, int(seg * clampf(ra / 8.0, 0.6, 2.0)))
		for k in n + 1:
			var a: float = a0[i] + PI * 0.5 * float(k) / n
			pts.append(c + Vector2(cos(a), sin(a)) * ra)
	return pts


## a blurred box-shadow as smooth gradient rings (full strength inside, fading to nothing over the blur), so it
## never shows the steps of stacked layers
static func _soft(ci: RID, r0: Rect2, rad: Vector4, blur: float, col: Color) -> void:
	var e0 := minf(blur * 0.5, minf(r0.size.x, r0.size.y) * 0.5 - 1.0)
	var rings := [[-e0, 1.0], [0.0, 0.5], [blur * 0.45, 0.16], [blur, 0.0]]
	var prev := outline_n(r0.grow(-e0), rad - Vector4.ONE * e0)
	var pa := col.a
	RenderingServer.canvas_item_add_polygon(ci, prev, PackedColorArray([Color(col.r, col.g, col.b, pa)]))
	for j in range(1, rings.size()):
		var g: float = rings[j][0]
		var a: float = col.a * float(rings[j][1])
		var cur := outline_n(r0.grow(g), rad + Vector4.ONE * g)
		var pts := PackedVector2Array()
		var cols := PackedColorArray()
		var idx := PackedInt32Array()
		var n := prev.size()
		var ci0 := Color(col.r, col.g, col.b, pa)
		var co0 := Color(col.r, col.g, col.b, a)
		for i in n:
			pts.append(prev[i])
			pts.append(cur[i])
			cols.append(ci0)
			cols.append(co0)
		for i in n:
			var i2 := (i + 1) % n
			idx.append_array([i * 2, i2 * 2, i * 2 + 1, i * 2 + 1, i2 * 2, i2 * 2 + 1])
		RenderingServer.canvas_item_add_triangle_array(ci, idx, pts, cols)
		prev = cur
		pa = a


## as outline(), with the same number of points whatever the size (each corner an arc of 8 steps)
static func outline_n(r: Rect2, rad: Vector4) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var rr := [rad.x, rad.y, rad.z, rad.w]
	var lim := maxf(0.3, minf(r.size.x, r.size.y) / 2.0)
	for i in 4:
		rr[i] = clampf(rr[i], 0.3, lim)
	var centres := [r.position + Vector2(rr[0], rr[0]), Vector2(r.end.x - rr[1], r.position.y + rr[1]), r.end - Vector2(rr[2], rr[2]), Vector2(r.position.x + rr[3], r.end.y - rr[3])]
	var a0 := [PI, PI * 1.5, 0.0, PI * 0.5]
	for i in 4:
		var c: Vector2 = centres[i]
		for k in 9:
			var a: float = a0[i] + PI * 0.5 * float(k) / 8.0
			pts.append(c + Vector2(cos(a), sin(a)) * float(rr[i]))
	return pts


func _fill(ci: RID, r: Rect2, rad: Vector4) -> void:
	var pts := outline(r, rad)
	if pts.size() < 3:
		return
	var ang := deg_to_rad(angle)
	var dir := Vector2(sin(ang), -cos(ang))   # CSS: 0deg points up, 90deg right, 180deg down
	var half := absf(r.size.x * dir.x) * 0.5 + absf(r.size.y * dir.y) * 0.5
	var c := r.get_center()
	var cols := PackedColorArray()
	for p in pts:
		var f := ((p - c).dot(dir) / maxf(half, 0.001)) * 0.5 + 0.5
		cols.append(_col_at(f))
	# a fan from the centre keeps a two-stop gradient exact; extra rings keep several stops close
	var rings := 1 if colors.size() <= 2 else 3
	var prev := pts
	var prev_c := cols
	for ring in range(1, rings + 1):
		var k := 1.0 - float(ring) / (rings + 1)
		var inner := PackedVector2Array()
		var inner_c := PackedColorArray()
		for p in pts:
			var q := c + (p - c) * k
			inner.append(q)
			inner_c.append(_col_at(((q - c).dot(dir) / maxf(half, 0.001)) * 0.5 + 0.5))
		for i in prev.size():
			var j := (i + 1) % prev.size()
			RenderingServer.canvas_item_add_polygon(ci, PackedVector2Array([prev[i], prev[j], inner[j], inner[i]]), PackedColorArray([prev_c[i], prev_c[j], inner_c[j], inner_c[i]]))
		prev = inner
		prev_c = inner_c
	var cc := _col_at(0.5)
	for i in prev.size():
		var j := (i + 1) % prev.size()
		RenderingServer.canvas_item_add_polygon(ci, PackedVector2Array([prev[i], prev[j], c]), PackedColorArray([prev_c[i], prev_c[j], cc]))


func _draw(ci: RID, rect: Rect2) -> void:
	var s := scale
	var rad := radius * s
	if grow != 0.0:
		rect = rect.grow(grow * s)
		rad += Vector4.ONE * grow * s
	# outer shadows, widest first
	for sh in shadows:
		var d: Dictionary = sh
		var col: Color = d["color"]
		var blur: float = float(d["blur"]) * s
		var spread: float = float(d.get("spread", 0.0)) * s
		var r0 := Rect2(rect.position + (d["off"] as Vector2) * s, rect.size).grow(spread)
		if blur <= 0.5:
			var p0 := outline(r0, rad + Vector4.ONE * spread)
			RenderingServer.canvas_item_add_polygon(ci, p0, PackedColorArray([col]))
			continue
		_soft(ci, r0, rad + Vector4.ONE * spread, blur, col)
	_fill(ci, rect, rad)
	if inset_bottom.a > 0.0:
		var h := minf(inset_bottom_h * s, rect.size.y * 0.5)
		var rb := Rect2(rect.position.x, rect.end.y - h, rect.size.x, h)
		var save := [colors, stops, angle]
		colors = PackedColorArray([Color(inset_bottom.r, inset_bottom.g, inset_bottom.b, 0.0), inset_bottom])
		stops = PackedFloat32Array([0.0, 1.0])
		angle = 180.0
		_fill(ci, rb, Vector4(0, 0, rad.z, rad.w))
		colors = save[0]
		stops = save[1]
		angle = save[2]
	if inset_top.a > 0.0:
		var x0 := rect.position.x + maxf(rad.x, 2.0) * 0.6
		var x1 := rect.end.x - maxf(rad.y, 2.0) * 0.6
		RenderingServer.canvas_item_add_line(ci, Vector2(x0, rect.position.y + s * 1.0), Vector2(x1, rect.position.y + s * 1.0), inset_top, s, true)
	if border_width > 0.0 and border_color.a > 0.0:
		var bw := border_width * s
		var pts := outline(rect.grow(-bw * 0.5), rad - Vector4.ONE * bw * 0.5)
		pts.append(pts[0])
		RenderingServer.canvas_item_add_polyline(ci, pts, PackedColorArray([border_color]), bw, true)
