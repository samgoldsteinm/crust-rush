# ninth engine patch (v165): background blur on toy tracks (Ultra on computers). Far parts of the room go soft, as in a
# close-up photograph of a miniature; everything within a few seconds' drive stays sharp. Uses the depth picture the
# ambient-occlusion pass already has, so it only exists where that does. Settings > Graphics: Background blur. Looks only.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("""<div class="seg seg2" data-k="mblur"><button data-v="1">On</button><button data-v="0">Off</button></div></div>""",
    """<div class="seg seg2" data-k="mblur"><button data-v="1">On</button><button data-v="0">Off</button></div></div>
      <div class="set-row"><div class="set-t"><b>Background blur</b><small>On the toy tracks the far side of the room goes soft, like a close-up photo of a model; the track ahead stays sharp. Ultra on computers.</small></div><div class="seg seg2" data-k="dof"><button data-v="1">On</button><button data-v="0">Off</button></div></div>""")
rep("shake:true,mblur:false,", "shake:true,mblur:false,dof:true,")
rep("'shake','mblur',", "'shake','mblur','dof',")
rep("uniform float exposure,bloom,sat,con,vig,aspect,edgeA,spd,tm,shp,mb;uniform vec2 px;", "uniform float exposure,bloom,sat,con,vig,aspect,edgeA,spd,tm,shp,mb,dof,foc;uniform sampler2D tD;uniform vec2 nf;uniform vec2 px;")
rep("    void main(){vec2 suv=min(vUv*us,uc);vec3 c=texture2D(tex,suv).rgb;\n",
    """    float farB(vec2 q){float z=texture2D(tD,q).r;float lz=nf.x*nf.y/(nf.y-z*(nf.y-nf.x));return clamp((lz-foc*7.)/(foc*30.),0.,1.);}
    void main(){vec2 suv=min(vUv*us,uc);vec3 c=texture2D(tex,suv).rgb;
      /* background blur (toy tracks): how soft a pixel is grows with its distance beyond seven times the distance to your kart. Twelve
         samples on a disc; each counts by how far away it is itself, so sharp things in front never smear into the blur behind them */
      if(dof>.001){float co=farB(suv)*dof;if(co>.02){vec3 acc=c*.6;float ws=.6;for(int i=0;i<12;i++){float a=float(i)*2.39996;float r=sqrt((float(i)+.5)/12.)*co*.0052;vec2 q=clamp(suv+vec2(cos(a)/aspect,sin(a))*r*us,px*.5,uc);float w=farB(q)+.04;acc+=texture2D(tex,q).rgb*w;ws+=w;}c=acc/ws;}}
""")
rep("mb:{value:0},", "mb:{value:0},dof:{value:0},foc:{value:60},tD:{value:null},nf:{value:new THREE.Vector2(1,1000)},")
rep("F.tm.value=performance.now()/1000%100;", "F.tm.value=performance.now()/1000%100;{const on=TOYT&&POST.aoW&&POST.rt.depthTexture&&CFG.dof!==false;F.dof.value=on?1:0;F.tD.value=on?POST.rt.depthTexture:null;if(on){F.nf.value.set(camera.near,camera.far);F.foc.value=clamp(k?Math.hypot(camera.position.x-k.x,camera.position.z-k.y):60,40,80);}}")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
