"""PC: every walker's body sits on its legs, and every walker's legs step. The owner: "these guys legs are still not
connected to their body on pc". The glTF import renames repeated names (the second walker's parts are body2, leg02, leg12),
and the race view looked its parts up by the exact names, so only the first walker on a track was seated and animated; the
rest kept the export's gap between body and legs, legs standing still. Now the parts are found by their name's start.
    python tools/mini/pc110.py      (once, after pc109)"""
p = 'D:/crust-rush/godot/scripts/view.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc110' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""		var legs: Array = []
		for j in 4:
			var ln := n3.find_child("leg%d" % j, false, false) as Node3D
			if ln != null:
				legs.append(ln)
		_seat_body(n3, legs)""", """		# (pc110) the import renames repeats (body2, leg02, leg12): found by how the name starts
		var legs: Array = []
		for j in 4:
			for c in n3.get_children():
				if c is Node3D and String(c.name).begins_with("leg%d" % j):
					legs.append(c)
					break
		_seat_body(n3, legs)""")
rep("""	var body := n.find_child("body", false, false) as Node3D
	if body == null or legs.is_empty():""", """	var body: Node3D = null
	for c in n.get_children():
		if c is Node3D and String(c.name).begins_with("body"):   # (pc110) body2, body3... on the later walkers
			body = c
			break
	if body == null or legs.is_empty():""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc110 applied')
