"""PC: web patch 101 (v234): one caliper per wheel, front wheels' behind the axle, rear wheels' ahead.
    py.cmd tools/mini/pc93.py      (once, after pc92; edits tools/glbexport.js, kart_builder.gd)
- glbexport: __exportBody puts a BODY_CAL car's calipers (web userData.bodyCal) in their own node 'bcal' (not in 'body');
  __exportWheel exports the wheel type's held part per corner, hold_FL / hold_FR / hold_RL / hold_RR (turned for front or rear),
  and hold0_L / hold0_R as the model has it (the Monster wheel on the Monster Truck).
- kart_builder: 'bcal' shown with the body unless the wheel type has a pack (it brings its own caliper); a wheel type's hold taken per
  corner; pc92's skip undone (the wheel's caliper shows on every car, the body's hides instead); HOLD_K suv [7, 1].
"""
G = 'D:/crust-rush/godot/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


E = 'tools/glbexport.js'
rep(E, "const skip=o=>yaws.some(y=>under(o,y))","const skip=o=>o.userData.bodyCal||yaws.some(y=>under(o,y))")
rep(E, "  const top=[G.node('body',parts(G,g,g.matrixWorld,skip))];",
    "  const top=[G.node('body',parts(G,g,g.matrixWorld,skip))];\n"
    "  /* (pc93, web patch 101) a car's own calipers apart: the PC hides them on a wheel type that brings its own */\n"
    "  {let bc=null;g.traverse(o=>{if(o.userData.bodyCal)bc=o;});if(bc){const pr=parts(G,bc,g.matrixWorld,null);if(pr.length)top.push(G.node('bcal',pr));}}")
rep(E, "    const ph=[];for(const h of yaw.children)if(h.userData.held)ph.push(...parts(G,h,wh.matrixWorld,null));if(ph.length)top.push(G.node('hold_'+side,ph));/* (pc86) */});",
    "    /* the model's own turn (hold0_), for the car whose wheel it is */const r0=[];for(const h of yaw.children)if(h.userData.held&&h.userData.r0!=null){r0.push([h,h.rotation.z]);h.rotation.z=h.userData.r0;h.updateMatrixWorld(true);}\n"
    "    const ph=[];for(const h of yaw.children)if(h.userData.held)ph.push(...parts(G,h,wh.matrixWorld,null));if(ph.length)top.push(G.node('hold0_'+side,ph));for(const [h,z] of r0){h.rotation.z=z;h.updateMatrixWorld(true);}/* (pc86, pc93) */});\n"
    "  /* (pc93, web patch 101) each corner's caliper, turned: behind a front axle, ahead of a rear one */\n"
    "  {const fr=new Set(m.front||[]);m.wheels.forEach(q=>{const sp=q.spin,yaw=sp.parent,wh=sp.children[0];if(!wh)return;const nm='hold_'+(fr.has(yaw)?'F':'R')+(yaw.position.z<0?'L':'R');\n"
    "    const ph=[];for(const h of yaw.children)if(h.userData.held)ph.push(...parts(G,h,wh.matrixWorld,null));if(ph.length)top.push(G.node(nm,ph));});}")
K = 'scripts/kart_builder.gd'
rep(K, '''			elif wsrc != null and not ["gt", "hyper", "interceptor", "scissor", "skywing", "endur"].has(String(bd["id"])):   # (pc92, web BODY_CAL: their own calipers)
				hsrc = wsrc.find_child("hold_" + ("L" if z < 0.0 else "R"), true, false) as Node3D
				if hsrc == null:
					hsrc = wsrc.find_child("hold_R", true, false) as Node3D''',
    '''			elif wsrc != null:
				# (pc93, web patch 101) the corner's caliper, turned (front: behind the axle, rear: ahead); on its own truck, as modelled
				var sd := "L" if z < 0.0 else "R"
				if String(wd["id"]) == String(bd["id"]):
					hsrc = wsrc.find_child("hold0_" + sd, true, false) as Node3D
				if hsrc == null:
					hsrc = wsrc.find_child("hold_" + ("F" if bool(wq["front"]) else "R") + sd, true, false) as Node3D
				if hsrc == null:
					hsrc = wsrc.find_child("hold_" + sd, true, false) as Node3D''')
rep(K, '''	if body != null:
		_paint(body, cols, liv, ri)
''', '''	if body != null:
		_paint(body, cols, liv, ri)
	# (pc93, web patch 101) a car's own calipers: not on a wheel type that brings its own
	if bsrc != null and String(wd["id"]) == "standard":
		var bc := bsrc.find_child("bcal", true, false) as Node3D
		if bc != null:
			bc = bc.duplicate() as Node3D
			bc.position = Vector3(0, lift, 0)
			root.add_child(bc)
			_paint(bc, cols, liv, ri)
''')
rep(K, '''const HOLD_K := {"monster": [12, 11], "muscle": [12], "retrogt": [7], "hatch": [9],''', '''const HOLD_K := {"monster": [12, 11], "muscle": [12], "retrogt": [7], "hatch": [9], "suv": [7, 1],''')
print('pc93 applied')
