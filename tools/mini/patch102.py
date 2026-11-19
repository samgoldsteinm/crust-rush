r"""Patch 102 (web v235): the Street Cruiser's fenders whole again.
The owner (on patch 99's picture): "the green wheel covers are still half disappeared and missing on the front and back".
Why: the Street Cruiser's fenders are split between its body and its WHEEL models (the lower halves were cut into the wheels when it
was converted); patch 85's wheelTrim deleted those halves from the wheels (they spun), so half of each fender was gone.
- BIKE_KEEP (bike_moto): no wheelTrim; patch 99's hold rule (every non-tyre piece reaching the tyre) holds the fender halves still, in
  the steering group. A held piece of paint (class 0) is drawn with the body's paint (M.carPaint), so it matches its upper half.
- WHEEL_SCALE now scales the rolling wheel only (the mesh, after holdOut), not the geometry: the fender halves stay where the model has
  them.
- PC: the held paint comes in the export's ph nodes; pc94: a held part never takes the Rims colour (hold_cols rimc null).
Run once, after patch 101: tools/py.cmd tools/mini/patch102.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 102' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep(r"if(bd&&bd.bike)for(const k in g)if(/^w\d$/.test(k))wheelTrim(g[k]);", r"if(bd&&bd.bike&&!BIKE_KEEP[bd.id])for(const k in g)if(/^w\d$/.test(k))wheelTrim(g[k]);/* (patch 102: not the Street Cruiser: its fenders' lower halves are in its wheels) */")
rep("  {const ws=WHEEL_SCALE[id.replace(/_hq$/,'')];if(ws)for(const k in ws)if(g[k])g[k].scale(ws[k],ws[k],1);}/* (patch 99) */", "")
rep("/* (patch 99) a bike wheel shrunk about its axle to clear its fender */const WHEEL_SCALE={bike_moto:{w1:.94}};",
    "/* (patch 99) a bike wheel shrunk about its axle to clear its fender (patch 102: the rolling part only) */const WHEEL_SCALE={bike_moto:{w1:.94}},BIKE_KEEP={bike_moto:1};")
# held paint apart
rep("  if(!hold.size)return null;const a=[],b=[];for(let t=0;t<I.length;t+=3)(hold.has(t)?b:a).push(I[t],I[t+1],I[t+2]);",
    "  if(!hold.size)return null;const a=[],b=[],bp=[];for(let t=0;t<I.length;t+=3)(hold.has(t)?(uv&&Math.floor(uv.getX(I[t])*32)===0?bp:b):a).push(I[t],I[t+1],I[t+2]);/* (patch 102: held paint apart) */")
rep("  return geo.userData.hold={spin:mk(a),hold:mk(b)};}", "  return geo.userData.hold={spin:mk(a),hold:mk(b),holdP:bp.length?mk(bp):null};}")
rep("m.castShadow=false;m.userData.held=1;if(noCal)m.visible=false;/* (patch 97) */yaw.add(m);\n",
    "m.castShadow=false;m.userData.held=1;if(noCal)m.visible=false;/* (patch 97) */yaw.add(m);\n"
    "  if(h.holdP){const mp=new THREE.Mesh(h.holdP,(M&&M.carPaint)||SH.carVC);mp.position.copy(wh.position);mp.rotation.copy(wh.rotation);mp.scale.copy(wh.scale);mp.castShadow=true;mp.userData.held=1;mp.userData.heldPaint=1;yaw.add(mp);}/* (patch 102) */\n")
rep("const wh=new THREE.Mesh(cg['w'+wi],rimVC(M.st,0,cfg.car,cg['w'+wi])||SH.carVC);/* (patch 73: the rims' colour) */wh.castShadow=false;spin.add(wh);holdOut(wh,yaw,M,cfg.car,0,cfg.car);/* (patch 88) */",
    "const wh=new THREE.Mesh(cg['w'+wi],rimVC(M.st,0,cfg.car,cg['w'+wi])||SH.carVC);/* (patch 73: the rims' colour) */wh.castShadow=false;spin.add(wh);holdOut(wh,yaw,M,cfg.car,0,cfg.car);/* (patch 88) */"
    "{const ws=WHEEL_SCALE[cfg.car];if(ws&&ws['w'+wi])wh.scale.set(ws['w'+wi],ws['w'+wi],1);}/* (patch 102: the rolling wheel only) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 102 applied')
