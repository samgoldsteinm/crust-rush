"""Patch 62 (web v217): solid paints that look like real car paint.
The owner (with photos of a Verde Mantis roadster and a Rosso Corsa coupe): "make the solid colors for the cars look better currently they
don't look that great. They are dull ... study them and fix our colors".
What the photos show and ours lacked: a deep, fully saturated colour under a glass-like clear coat; bright tops, darker flanks, dark
reflections of the ground along the sills; small sharp white highlights. Ours were:
  - pale hues: the film tone curve (ACES) washes bright saturated colours toward pastel and pushes red to orange, and the swatches were
    already mid-tones (Tomato #e0452c read orange beside the Ferrari's red; Basil #3f9a35 a dull leaf green beside the mantis green);
  - part metal (.14 karts, .32 car bodies): metalness tints the colour with the grey surroundings and flattens the light-to-dark range.
Now: the swatches are deep car colours chosen for the tone curve (Tomato a true racing red, Basil a vivid mantis green, Cheddar a giallo
yellow, Ocean a deep blue, ...: names unchanged); the solid finish is a non-metal base (roughness .36) under a sharp clear coat
(clearcoatRoughness .02) with a stronger environment, on karts and car bodies alike. A livery keeps its own finish.
The PC: kart_builder.gd the same finish; the paints come with the garage export.
Run once: py.cmd tools/mini/patch62.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 62' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const PAINTS=[null,'#e0452c','#ff8a1f','#f6c548','#3f9a35','#2f7fd8','#7b4bd8','#ff6fae','#2a2626','#f3ead8'];",
    "const PAINTS=[null,'#c40c0c','#ff5a00','#ffb400','#3fae0c','#0b49c9','#5317ad','#ff2c84','#1c1d22','#efe4cb'];/* (patch 62: deep car colours, chosen for the tone curve) */")
rep("const paint=new THREE.MeshPhysicalMaterial({color:col,roughness:.2,metalness:.14,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.45})/* (patch 49c: glossier) */;",
    "const paint=new THREE.MeshPhysicalMaterial(lv?{color:col,roughness:.2,metalness:.14,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.45}:{color:col,roughness:.36,metalness:0,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.75})/* (patch 62: a solid colour is a non-metal base under a sharp clear coat, as real paint; a livery keeps its finish) */;M.__solid=!lv;")
# (M is declared on the next line: carry the flag on the material instead)
s = s.replace(";M.__solid=!lv;", ";paint.userData.solid=!lv;", 1)
rep("M.carPaint=new THREE.MeshPhysicalMaterial({color:M.paint.color.clone(),vertexColors:true,metalness:.32,roughness:.2,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.5});",
    "M.carPaint=new THREE.MeshPhysicalMaterial(M.paint.userData.solid?{color:M.paint.color.clone(),vertexColors:true,metalness:0,roughness:.36,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.75}:{color:M.paint.color.clone(),vertexColors:true,metalness:.32,roughness:.2,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.5});/* (patch 62: the solid finish) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 62 applied')
