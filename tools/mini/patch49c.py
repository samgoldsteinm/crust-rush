"""Patch 49c (web v210): sharper, more reflective paint on karts and cars.
The owner: "the colors look pretty flat on the car and dull try to make them a little sharper and reflective". The paint's own reflections
were soft (kart roughness .38: a broad blur, so the colour read flat) and the car paint half metal (.5: metal tints its reflections and
darkens the colour under them). Now the base coat is glossier (kart .2, car .2), the car's metalness lower (.32) so the colour stays
rich, the clear coat harder (.03 / .02) and the environment's reflections stronger (1.45 / 1.5). Picture liveries likewise (.22, .03, 1.35).
Shapes and colours of the karts are untouched (the owner's designs); only how the paint catches the light.
Run once: py.cmd tools/mini/patch49c.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 49c' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("M.carPaint=new THREE.MeshPhysicalMaterial({color:M.paint.color.clone(),vertexColors:true,metalness:.5,roughness:.34,clearcoat:1,clearcoatRoughness:.04,envMapIntensity:1.2});",
    "M.carPaint=new THREE.MeshPhysicalMaterial({color:M.paint.color.clone(),vertexColors:true,metalness:.32,roughness:.2,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.5});/* (patch 49c: glossier) */")
rep("const paint=new THREE.MeshPhysicalMaterial({color:col,roughness:.38,metalness:.12,clearcoat:1,clearcoatRoughness:.08,envMapIntensity:1})",
    "const paint=new THREE.MeshPhysicalMaterial({color:col,roughness:.2,metalness:.14,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.45})/* (patch 49c: glossier) */")
rep("metalness:lv.m??.3,roughness:lv.r??.28,clearcoat:1,clearcoatRoughness:.05,envMapIntensity:1.1});",
    "metalness:lv.m??.3,roughness:lv.r??.22,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.35});")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 49c applied')
