"""Patch 47c (web v209): headlights that look like beams.
The owner (a picture at night on Margherita Ring): "the headlights are also super weird looking they should make a clear shape of like the
light beam coming and then widening as it gets farther from the car. right now its super bright right in the front center of the car".
Patch 43's ground beam was brightest at the bumper (1.6 there, fading out), and its spot light sat 6.5 up aiming steeply down 80 ahead, so
both piled up in one hot patch in front of the kart (blown out further by the bloom). Now:
- the beam: a cone 12 wide at the bumper to 130 wide 240 ahead (16 x 24 cells); dim at the bumper, at its brightest 40 to 90 ahead, fading
  out to the far end; its sides are a clear edge (full light to 70% of the half-width, gone at the edge), at most about 0.6, never 1.6.
- the spot light: at headlight height on the bumper, aimed almost level 220 ahead, a narrower cone (0.42) with a soft edge, 3 not 5.5.
Run once: py.cmd tools/mini/patch47c.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 47c' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("const bg=new THREE.PlaneGeometry(1,1,6,12),bp=bg.attributes.position,base=new Float32Array(bp.count*2),col=new Float32Array(bp.count*3);for(let i=0;i<bp.count;i++){const f=bp.getY(i)+.5,ac=bp.getX(i)*2,u=4+f*170,v=ac*(9+f*36);base[i*2]=u;base[i*2+1]=v;",
    "const bg=new THREE.PlaneGeometry(1,1,16,24),bp=bg.attributes.position,base=new Float32Array(bp.count*2),col=new Float32Array(bp.count*3);for(let i=0;i<bp.count;i++){const f=bp.getY(i)+.5,ac=bp.getX(i)*2,u=6+f*240,v=ac*(6+f*59);base[i*2]=u;base[i*2+1]=v;/* (patch 47c) */")
rep("const e=1.6*Math.pow(1-f,.75)*Math.pow(Math.max(0,1-Math.abs(ac)),1.2)*(f<.04?f/.04:1);",
    "const ss=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);},e=.62*(.18+.82*ss(0,.28,f))*Math.pow(1-f,1.15)*(1-ss(.7,1,Math.abs(ac)));")
rep("const sp=new THREE.SpotLight('#fff1d8',0,420,.5,.55,1.0);", "const sp=new THREE.SpotLight('#fff1d8',0,520,.42,.6,1.0);")
rep("sp.intensity=on?5.5*L:0;", "sp.intensity=on?3*L:0;")
rep("sp.position.set(x+Math.cos(a)*7,y+6.5,z+Math.sin(a)*7);sp.target.position.set(x+Math.cos(a)*80,y-9,z+Math.sin(a)*80);",
    "sp.position.set(x+Math.cos(a)*8,y+3.5,z+Math.sin(a)*8);sp.target.position.set(x+Math.cos(a)*220,y-5,z+Math.sin(a)*220);")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 47c applied')
