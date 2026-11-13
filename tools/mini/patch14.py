# fourteenth patch (v168): looks only.
# 1. Boost flames (the user's reference pictures: a hot blue-white jet at the pipe that turns yellow, then orange, in a ragged,
#    flickering shape with licks breaking off, and a warm glow on the road). Each pipe's two plain cones become two teardrop
#    flames drawn by a small shader: the outline wavers and breaks up towards the tip, the colour runs from the jet through the
#    inner colour to the outer one, brighter where you look through more flame. Colours still follow the drift tier (FLAMEC).
#    A soft glow lies on the road behind the kart, and embers fly off the flames.
# 2. Motion blur (Settings) is about a third stronger, and reaches a little further in from the edges.
# 3. Neon Cup tracks: the white streaks at the screen's edges while boosting become rainbow streaks, denser and brighter, with a
#    rainbow wash at the very edge. Neon tracks show them on every quality that has the post pass; elsewhere nothing changes.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)


# ---- 1. flames: geometry
rep("KG.flame=new THREE.ConeGeometry(.55,2.6,16,1,true);KG.flameIn=new THREE.ConeGeometry(.3,1.7,12,1,true);",
    "KG.flame=flameGeo(.64,2.6,18,12);KG.flameIn=flameGeo(.36,1.7,14,10);KG.fglow=new THREE.PlaneGeometry(1,1).rotateX(-Math.PI/2);")
# the shader material and the geometry builder, beside the old plain flame materials (still used by Fire Trail's flames on the road)
rep("const flameMat=new THREE.MeshBasicMaterial({color:'#ff7a1a',",
    r"""/* a flame's shape: a teardrop tube, open at the pipe (bottom) and closed to a point (top); uv.y runs along it */
function flameGeo(R,H,rs,hs){const g=new THREE.CylinderGeometry(1,1,H,rs,hs,true),p=g.attributes.position;for(let i=0;i<p.count;i++){const v=p.getY(i)/H+.5,r=R*Math.pow(Math.sin(Math.PI*(.16+.84*v)),.75)*(1-.2*v),x=p.getX(i),z=p.getZ(i),l=Math.hypot(x,z)||1;p.setXYZ(i,x/l*r,p.getY(i),z/l*r);}g.computeVertexNormals();return g;}
/* boost flames: the outline wavers and breaks into licks towards the tip; the colour runs from a blue-white jet at the pipe through cB
   (inner) to cA (outer) and is brighter where the view passes through more flame. ft is the clock, shared by every flame. */
const FLT={value:0};
function flameShMat(inner){return new THREE.ShaderMaterial({uniforms:{ft:FLT,cA:{value:new THREE.Color('#ff7a1a')},cB:{value:new THREE.Color('#fff0a0')},inn:{value:inner?1:0},seed:{value:Math.random()*20}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,toneMapped:false,
  vertexShader:`uniform float ft,seed;varying vec2 vUv;varying float vF;
    void main(){vUv=uv;float v=uv.y,an=atan(position.z,position.x);
      float n=sin(v*9.-ft*15.+seed)*.5+sin(v*17.-ft*24.+an*3.+seed*1.7)*.3+sin(an*2.+ft*9.+seed)*.2;
      vec3 p=position;p.xz*=1.+n*.34*v;p.x+=sin(ft*11.+v*5.+seed)*.16*v*v;p.z+=cos(ft*13.+v*4.+seed*2.)*.16*v*v;
      vec4 mv=modelViewMatrix*vec4(p,1.);vF=abs(dot(normalize(normalMatrix*normal),normalize(-mv.xyz)));gl_Position=projectionMatrix*mv;}`,
  fragmentShader:`uniform float ft,seed,inn;uniform vec3 cA,cB;varying vec2 vUv;varying float vF;
    float h2(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float ns(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h2(i),h2(i+vec2(1.,0.)),f.x),mix(h2(i+vec2(0.,1.)),h2(i+vec2(1.,1.)),f.x),f.y);}
    void main(){float v=vUv.y,core=pow(vF,1.4),u=sin(vUv.x*6.2832)*1.6;
      float nz=ns(vec2(u*2.2+seed,v*4.5-ft*7.))*.65+ns(vec2(u*4.6-seed,v*9.-ft*12.))*.35;
      float a=smoothstep(.05,.5,core*.9+(nz-.5)*.75-v*.62+.42)*(1.-smoothstep(.72,1.,v));
      vec3 col=mix(cA,cB,clamp(core*1.25-v*.7+.2,0.,1.));
      /* the jet at the pipe: the outer flame thins out there so the inner one's blue shows through, as on a gas burner */
      float jz=smoothstep(.36,.06,v);col=mix(col,vec3(.1,.42,1.)*1.15,jz*inn);a*=mix(1.,.04,jz*(1.-inn));
      col*=1.+.25*core;gl_FragColor=vec4(col,a*mix(.55,.9,inn));}`});}
const flameMat=new THREE.MeshBasicMaterial({color:'#ff7a1a',""")
# each kart: shader flames, plus a glow on the road behind the pipes (the last entry of `flames`, marked userData.glow)
rep("const flames=[],fmO=flameMat.clone(),fmI=flameInMat.clone();", "const flames=[],fmO=flameShMat(0),fmI=flameShMat(1);")
rep("  flames.forEach(f=>f.visible=false);",
    """  if(cfg.pipes.length){glowMat('#ffffff');const px=cfg.pipes.reduce((a,q)=>a+q[0],0)/cfg.pipes.length,gp=new THREE.Mesh(KG.fglow,new THREE.MeshBasicMaterial({map:_glowTex,color:'#ff8a2a',transparent:true,opacity:.5,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false,polygonOffset:true,polygonOffsetFactor:-3,polygonOffsetUnits:-3}));
    gp.position.set(px-1.9,-B.position.y+.14,0);gp.userData.glow=1;B.add(gp);flames.push(gp);}
  flames.forEach(f=>f.visible=false);""")
# the per-frame update: colours through the shader's uniforms, a steadier length (the shader flickers), the glow, embers
rep("if(m.flames.length&&m.fTi!==ft){m.fTi=ft;m.flames[0].material.color.set(FLAMEC[ft][0]);if(m.flames[1])m.flames[1].material.color.set(FLAMEC[ft][1]);}}",
    "if(m.flames.length&&m.fTi!==ft){m.fTi=ft;for(const fl of m.flames){const mt=fl.material;if(fl.userData.glow)mt.color.set(FLAMEC[ft][0]);else if(mt.uniforms){const inn=mt.uniforms.inn.value>0;mt.uniforms.cA.value.set(FLAMEC[ft][inn?1:0]);mt.uniforms.cB.value.set(inn?'#fff6e0':FLAMEC[ft][1]);}}}\n     FLT.value=time%1000;if(Math.random()<.28){/* embers fly off the flames */const d=Math.abs(m.axR||10)+4,ca=Math.cos(a),sa=Math.sin(a),sd=(Math.random()-.5)*5;FXA.spawn(x-ca*d-sa*sd,z+2.2+Math.random()*2,y-sa*d+ca*sd,-ca*(14+Math.random()*22),5+Math.random()*12,-sa*(14+Math.random()*22),FLAMEC[ft][Math.random()<.5?1:0],.55,.1,.22+Math.random()*.16,-10,1.5);}}")
rep("for(const fl of m.flames){fl.visible=on;if(on){const L=sl*(.8+Math.random()*.5),u=fl.userData.fl;fl.scale.set(sw,L,sw);if(u)fl.position.x=u[0]+u[1]*(1-L);}}}",
    "for(const fl of m.flames){fl.visible=on;if(!on)continue;if(fl.userData.glow){const f=.85+.15*Math.sin(time*37+k.ri*5)+Math.random()*.08;fl.scale.set(5*sl*f,1,3.6*sw);fl.material.opacity=.5*f;continue;}const L=sl*1.4*(1+.07*Math.sin(time*29+k.ri*3)+Math.random()*.06),u=fl.userData.fl;fl.scale.set(sw,L,sw);if(u)fl.position.x=u[0]+u[1]*(1-L);}}")
# the old materials were compared by identity when a kart's materials are disposed: per-kart shader flames are simply disposed with it

# ---- 2. motion blur
rep("vec2 st=dv*us*mb*.07*smoothstep(.015,.45,dot(da,da));", "vec2 st=dv*us*mb*.095*smoothstep(.01,.42,dot(da,da));")

# ---- 3. rainbow streaks on Neon tracks
rep("uniform float exposure,bloom,sat,con,vig,aspect,edgeA,spd,tm,shp,mb,dof,foc;", "uniform float exposure,bloom,sat,con,vig,aspect,edgeA,spd,tm,shp,mb,dof,foc,rbw;")
rep("    float farB(vec2 q){", "    vec3 hue(float h){return clamp(abs(fract(h+vec3(0.,.6667,.3333))*6.-3.)-1.,0.,1.);}\n    float farB(vec2 q){")
rep("float run=fract(r*1.3-tm*(2.6+n*1.6)+n*9.),st=step(.7,n)*smoothstep(.55,1.,w)*smoothstep(0.,.18,run)*(1.-smoothstep(.18,.5,run))*smoothstep(.3,.75,r);c=mix(c,vec3(1.),st*spd*.32);}",
    "float run=fract(r*1.3-tm*(2.6+n*1.6)+n*9.),st=step(mix(.7,.5,rbw),n)*smoothstep(mix(.55,.3,rbw),1.,w)*smoothstep(0.,.18,run)*(1.-smoothstep(.18,mix(.5,.7,rbw),run))*smoothstep(mix(.3,.46,rbw),mix(.75,.95,rbw),r);\n"
    "    /* Neon tracks (rbw): the streaks are rainbow, denser and longer, over a rainbow wash at the very edge of the picture */\n"
    "    vec3 rb=hue(an*.3183+n*.35+tm*.25);c=mix(c,mix(vec3(1.),rb*1.15+.12,rbw),st*spd*mix(.32,.55,rbw));c+=rb*rbw*spd*.16*smoothstep(.5,1.05,r)*(.55+.45*sin(an*9.+tm*5.+n*6.));}")
rep("mb:{value:0},dof:{value:0},", "mb:{value:0},rbw:{value:0},dof:{value:0},")
rep("{const k=camT,on=QUAL[qKey].streaks&&k&&state==='race'&&k.boost>0&&!k.spin,", "{const k=camT,nm=MAPS[mapIdx]&&MAPS[mapIdx].neon&&!MAPS[mapIdx].toy;F.rbw.value=nm?1:0;const on=(QUAL[qKey].streaks||nm)&&k&&state==='race'&&k.boost>0&&!k.spin,")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
