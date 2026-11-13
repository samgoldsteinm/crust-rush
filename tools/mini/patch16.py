# sixteenth patch (v170): black dots in the boost flames on phones (the user's screenshot, a Neon track on an iPhone).
# Cause: the flame's shape closes to a point at its tip, where the triangles have no area; computeVertexNormals gave those vertices
# a not-a-number direction (30 vertices of the inner flame). The shader's brightness came from that direction, so those pixels were
# not-a-number: a desktop card drops them, a phone's draws them black, and the glow pass spreads them into blobs.
# Fix: the flame's directions are set from its shape (always defined), the shader works its own out from the vertex position and
# no longer reads the stored one, and every value that could go wrong is clamped before it is drawn.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("p.setXYZ(i,x/l*r,p.getY(i),z/l*r);}g.computeVertexNormals();return g;}",
    "p.setXYZ(i,x/l*r,p.getY(i),z/l*r);g.attributes.normal.setXYZ(i,x/l,0,z/l);/* straight out from the axis: always defined, also at the tip where the shape closes to a point (computeVertexNormals gave not-a-number there, which phones drew as black dots) */}return g;}")
rep("vec4 mv=modelViewMatrix*vec4(p,1.);vF=abs(dot(normalize(normalMatrix*normal),normalize(-mv.xyz)));gl_Position=projectionMatrix*mv;}`,",
    "vec4 mv=modelViewMatrix*vec4(p,1.);vec3 nr=vec3(cos(an),0.,sin(an));/* outward, from the angle round the axis: never read from the mesh */vec3 vn=normalMatrix*nr;vF=clamp(abs(dot(vn/max(length(vn),1e-5),mv.xyz/max(length(mv.xyz),1e-5))),0.,1.);gl_Position=projectionMatrix*mv;}`,")
rep("void main(){float v=vUv.y,core=pow(vF,1.4),u=sin(vUv.x*6.2832)*1.6;", "void main(){float v=clamp(vUv.y,0.,1.),core=pow(clamp(vF,0.0001,1.),1.4),u=sin(vUv.x*6.2832)*1.6;")
rep("col*=1.+.25*core;gl_FragColor=vec4(col,a*mix(.55,.9,inn));}`});}", "col*=1.+.25*core;gl_FragColor=vec4(clamp(col,0.,4.),clamp(a,0.,1.)*mix(.55,.9,inn));}`});}")
# the embers travel with the kart (they hung in the air behind it as a trail of big dots)
rep('FXA.spawn(x-ca*d-sa*sd,z+2.2+Math.random()*2,y-sa*d+ca*sd,-ca*(14+Math.random()*22),5+Math.random()*12,-sa*(14+Math.random()*22),FLAMEC[ft][Math.random()<.5?1:0],.55,.1,.22+Math.random()*.16,-10,1.5);',
    'const ev=Math.max(0,k.speed)*.86-(14+Math.random()*22);/* embers travel with the kart and fall back from it slowly (left standing, they hung in the air as a trail of big dots) */FXA.spawn(x-ca*d-sa*sd,z+2.2+Math.random()*2,y-sa*d+ca*sd,ca*ev,5+Math.random()*12,sa*ev,FLAMEC[ft][Math.random()<.5?1:0],.5,.08,.2+Math.random()*.14,-10,.4);')
# the older boost sparks too
rep("FXA.spawn(tv.x,tv.y,tv.z,-Math.cos(k.ma)*30+(Math.random()-.5)*6,(Math.random()-.2)*6,-Math.sin(k.ma)*30+(Math.random()-.5)*6,Math.random()<.5?'#ff7a1a':'#ffd36b',2.2,.4,.25,0,2);}}",
    "const bv=Math.max(0,k.speed)*.9-30;/* the sparks leave the pipes backwards at 30 relative to the kart: thrown out at 30 over the ground they were left standing in the air, a trail of dots between you and your kart */FXA.spawn(tv.x,tv.y,tv.z,Math.cos(k.ma)*bv+(Math.random()-.5)*6,(Math.random()-.2)*6,Math.sin(k.ma)*bv+(Math.random()-.5)*6,Math.random()<.5?'#ff7a1a':'#ffd36b',1.5,.3,.22,0,.5);}}")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
