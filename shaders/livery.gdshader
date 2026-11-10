shader_type spatial;
// The web game's livery paint (LIV_FRAG + LIV_BODY from the game's source, converted for Godot by
// tools/conv_liv.py): about 70 patterns computed from the paint's own position on the body, the race
// number and decals, and the finish pass (deeper sills, candy fresnel, vinyl edges, metallic flake).
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 uLA : source_color = vec3(0.8, 0.15, 0.1);
uniform vec3 uLB : source_color = vec3(1.0, 0.95, 0.86);
uniform vec3 uLC : source_color = vec3(0.16, 0.1, 0.08);
uniform float uLPat = 1.0;
uniform vec4 uLBox = vec4(-5.0, 5.0, 3.0, 4.0);
uniform float uLBelt = 1.5;
uniform float uLNum = -1.0;
uniform vec2 uLNumPos = vec2(0.0, 1.0);
uniform sampler2D uLNumTex : filter_linear, repeat_disable;
uniform sampler2D uLDec : filter_linear_mipmap, repeat_disable;
uniform vec3 uLDecI = vec3(-1.0, -1.0, 1.0);
uniform float uLQ = 2.0;
uniform float uLFl = 0.5;
uniform float metal = 0.4;
uniform float rough = 0.3;
uniform float coat = 1.0;
uniform mat4 liv_xf = mat4(1.0);
varying vec3 vLivP;
varying vec3 vLivN;

float lh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float ln2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(lh(i),lh(i+vec2(1.0,0.0)),f.x),mix(lh(i+vec2(0.0,1.0)),lh(i+vec2(1.0,1.0)),f.x),f.y);}
float lfbm(vec2 p){return .55*ln2(p)+.3*ln2(p*2.1)+.15*ln2(p*4.3);}
vec3 lvor(vec2 p){vec2 i=floor(p),f=fract(p);float d1=8.,d2=8.;vec2 id=vec2(0.);for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){vec2 g=vec2(float(x),float(y)),o=vec2(lh(i+g),lh(i+g+17.3));vec2 r=g+o-f;float d=dot(r,r);if(d<d1){d2=d1;d1=d;id=i+g;}else if(d<d2)d2=d;}return vec3(sqrt(d1),sqrt(d2),lh(id+3.1));}
vec3 lpal(float t){return .5+.5*cos(6.2832*(t+vec3(0.,.33,.67)));}

void vertex() {
	vLivP = (liv_xf * vec4(VERTEX, 1.0)).xyz;
	vLivN = mat3(liv_xf) * NORMAL;
}

void fragment() {
	vec3 vViewPosition = -VERTEX;
	vec3 vNormal = NORMAL;

  vec3 lp=vLivP,lnn=normalize(vLivN);float lu=(lp.x-uLBox.x)/(uLBox.y-uLBox.x),laz=abs(lp.z)/uLBox.z,lside=step(.55,abs(lnn.z));float livR=-1.;
  vec3 lc=uLA;int lpat=int(uLPat+.5);
  if(lpat==1){float s=step(.07,laz)*step(laz,.2);lc=mix(uLA,uLB,s);lc=mix(lc,uLC,step(lp.y,uLBelt*.42));}
  else if(lpat==2){float t=smoothstep(uLBelt-.03,uLBelt+.03,lp.y);lc=mix(uLB,uLA,t);lc=mix(lc,uLC,1.-smoothstep(.02,.06,abs(lp.y-uLBelt)));}
  else if(lpat==3){float a=smoothstep(.62,.68,lu),b=smoothstep(.3,.36,lu);lc=mix(uLC,mix(uLB,uLA,a),b);}
  else if(lpat==4){float n=lfbm(vec2(lp.y*1.4,lp.z*1.1+lp.x*.15));float reach=.3+.32*n+.07*sin(lp.y*6.+lp.z*4.);float f=smoothstep(1.-reach-.02,1.-reach+.02,lu);
    float core=smoothstep(1.-reach*.55-.02,1.-reach*.55+.02,lu);lc=mix(uLA,mix(uLB,uLC,core),f*step(lp.y,uLBox.w*.92));}
  else if(lpat==5){float band=step(uLBelt-.42,lp.y)*step(lp.y,uLBelt+.06);float ch=mod(floor(lp.x*2.3)+floor(lp.y*2.3),2.);lc=mix(uLA,mix(uLA,uLB,ch),band*lside);
    lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-(uLBelt+.1)))));}
  else if(lpat==6){float w=uLBelt-.2+.22*sin(lp.x*1.15+1.3);lc=lp.y<w?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.03,.07,abs(lp.y-w)));}
  else if(lpat==7){float n=lfbm(vec2(lp.x*.42,lp.z*.42)+lp.y*.35);lc=n<.42?uLA:(n<.6?uLB:uLC);livR=.62;}
  else if(lpat==8){lc=mix(uLB,uLA,smoothstep(.12,.88,lu));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}
  else if(lpat==9){float d=fract((lp.x+lp.y*1.15)*.16);float mid=step(.22,lu)*step(lu,.8);lc=mix(uLA,uLB,lside*mid*step(d,.11));lc=mix(lc,uLC,lside*mid*step(.14,d)*step(d,.19));}
  else if(lpat==10){float lo=step(lp.y,uLBelt);float wv=mod(floor(lp.x*7.)+floor(lp.y*7.+lp.z*7.),2.);lc=mix(uLA,mix(uLB,uLB*1.7,wv),lo);livR=lo>.5?.22:-1.;lc=mix(lc,uLC,1.-smoothstep(.015,.04,abs(lp.y-uLBelt)));}
  else if(lpat==11){lc=mix(uLA,uLB,step(laz,.13)*step(.28,lu));lc=mix(lc,uLC,step(.82,lu)*step(lp.y,uLBelt*.85));}
  else if(lpat==12){float s=step(.05,laz)*step(laz,.1)+step(.14,laz)*step(laz,.19);lc=mix(uLA,uLB,s*step(.6,lnn.y));}
  else if(lpat==13){livR=.72;lc=mix(uLA,uLC,step(lp.y,uLBelt*.45));lc=mix(lc,uLB,lside*(1.-smoothstep(.015,.04,abs(lp.y-uLBelt*.62))));}
  else if(lpat==14){float m=step(.27,lu)*step(lu,.7);lc=mix(uLA,uLB,m*step(lp.y,uLBelt+.05));lc=mix(lc,uLC,lside*(1.-smoothstep(.03,.06,abs(lp.y-uLBelt*.72))));}
  else if(lpat==15){float s=step(laz,.17),bd=step(.17,laz)*step(laz,.21);lc=mix(mix(uLA,uLB,s),uLC,bd);float sb=lside*step(uLBelt-.42,lp.y)*step(lp.y,uLBelt-.12);lc=mix(lc,uLB,sb);}
  else if(lpat==16){float d=uLBelt-.05-lp.y-.45*(1.-lu);float s1=step(0.,d)*step(d,.13),s2=step(.16,d)*step(d,.25),s3=step(.28,d)*step(d,.37);vec3 mid=mix(uLB,vec3(1.),.45);
    lc=mix(uLA,uLB,s1*lside);lc=mix(lc,mid,s2*lside);lc=mix(lc,uLC,s3*lside);}
  else if(lpat==17){float k=lu*1.25+lp.y/uLBox.w*.85;lc=k>1.15?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.02,.05,abs(k-1.15)));}
  else if(lpat==18){float zig=abs(fract(lp.y*1.2+abs(lp.z)*.9)-.5)*2.;float edge=1.-(.24+.22*zig);float f=step(edge,lu);lc=mix(uLA,uLB,f);lc=mix(lc,uLC,1.-smoothstep(.0,.025,abs(lu-edge)));}
  else if(lpat==19){lc=lp.y<uLBelt-.25?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.04,.07,abs(lp.y-(uLBelt-.25))));float blk=lside*step(mod(floor(lp.x*.8),3.),.5)*step(uLBelt-.62,lp.y)*step(lp.y,uLBelt-.38);lc=mix(lc,vec3(.95),blk);}
  else if(lpat==20){vec2 q=floor(vec2(lp.x,lp.z+lp.y*1.3)*1.6);float n=lh(q)*.6+lh(floor(q/2.)+7.)*.4;lc=n<.45?uLA:(n<.72?uLB:uLC);livR=.6;}
  else if(lpat==21){float y0=uLBelt-.28+.2*(abs(fract(lp.x*.42)-.5)*4.-1.);float dd=abs(lp.y-y0);lc=mix(uLA,uLB,lside*step(dd,.1));lc=mix(lc,uLC,lside*step(.1,dd)*step(dd,.14));}
  else if(lpat==22){float n=lfbm(vec2(lp.x*.35,lp.y*.6+lp.z*.35));float st=sin(lp.x*2.6+n*7.+abs(lp.z)*.6);lc=mix(uLA,uLB,smoothstep(.55,.62,st)*(.4+.6*smoothstep(.2,.5,n)));}
  else if(lpat==23){vec2 g2=vec2(lp.x,lp.y+lp.z*.6)*2.2;vec2 c2=fract(g2)-.5;float rr=length(c2),lim=.48*(1.-lu);lc=mix(uLA,uLB,step(rr,lim));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}
  else if(lpat==24){float a2=fract(lp.x*.32-abs(lp.y-(uLBelt-.25))*.55);float band=step(abs(lp.y-(uLBelt-.25)),.42)*lside;lc=mix(uLA,uLB,band*step(a2,.28));lc=mix(lc,uLC,band*step(.28,a2)*step(a2,.36));}
  else if(lpat==25){float k2=lu+lp.y/uLBox.w*.35;lc=k2>.62?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.006,.016,abs(k2-.62)));}
  else if(lpat==26){float t1=abs(lp.y-uLBelt),t2=abs(laz-.55);float pin=(1.-smoothstep(.015,.03,t1))*lside+(1.-smoothstep(.006,.014,t2))*step(.6,lnn.y);lc=mix(uLA,uLB,clamp(pin,0.,1.));}
  else if(lpat==27){float t3=clamp(lp.y/uLBox.w,0.,1.);lc=mix(uLA,uLB,smoothstep(.15,.9,t3));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt*.5))));}
  else if(lpat==28){vec2 h=vec2(lp.x,lp.y+lp.z)*2.4;h.y*=1.1547;h.x+=step(1.,mod(h.y,2.))*.5;vec2 f2=abs(fract(h)-.5);float e=max(f2.x*1.5+f2.y,f2.y*2.)*.9;lc=mix(uLB,uLA,smoothstep(.62,.7,e));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt))));livR=.3;}
  else if(lpat==29){/* molten mozzarella: cheese melting down over the sauce, with drips, bubbles and a glossy lip */
    float dx=lp.x*2.1+lp.z*1.4;float drip=pow(max(0.,sin(dx*1.3+ln2(vec2(dx*.7,2.))*4.)),6.)*.85+lfbm(vec2(dx*.6,5.))*.32;float edge=uLBelt+.18-drip;
    float ch=smoothstep(edge-.02,edge+.02,lp.y);vec2 bq=vec2(lp.x,lp.y+lp.z)*3.2;vec3 bv=lvor(bq);float bub=(1.-smoothstep(.1,.16,bv.x))*step(.55,bv.z);
    vec3 cheese=mix(uLA,uLA*1.12,lfbm(vec2(lp.x,lp.y+lp.z)*1.5))-bub*.18;vec3 sauce=mix(uLB,uLB*.7,lfbm(lp.xz*.9+lp.y));
    lc=mix(sauce,cheese,ch);lc=mix(lc,uLC,(1.-smoothstep(.0,.05,abs(lp.y-edge)))*.8);livR=ch>.5?.22:.38;}
  else if(lpat==30){/* ember circuit: glowing traces and solder pads on charcoal */
    vec2 g=vec2(lp.x,lp.y+lp.z*.55)*2.6;vec2 c=floor(g),f=fract(g);float r1=lh(c),r2=lh(c+9.7);
    float h=(1.-smoothstep(.04,.07,abs(f.y-.5)))*step(.45,r1),v=(1.-smoothstep(.04,.07,abs(f.x-.5)))*step(r2,.4);float pad=(1.-smoothstep(.13,.18,length(f-.5)))*step(.72,r1*r2+.3);
    float tr=clamp(h+v+pad,0.,1.);vec3 hot=mix(uLB,uLC,smoothstep(.2,.95,lu));lc=mix(uLA*(.8+.4*lfbm(lp.xz*2.)),hot,tr);lc=mix(lc,hot*.35,(1.-smoothstep(.07,.16,min(abs(f.y-.5),abs(f.x-.5))))*.4*step(.45,r1));livR=tr>.5?.3:.55;}
  else if(lpat==31){/* pepperoni galaxy: nebula clouds, a field of stars and little pepperoni planets */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float n=lfbm(q*.45),n2=lfbm(q*1.2+7.);lc=mix(uLA,uLB,smoothstep(.35,.75,n));lc=mix(lc,uLC,smoothstep(.55,.85,n2)*.7);
    float st=step(.986,lh(floor(q*16.)))*(1.-smoothstep(.0,.35,length(fract(q*16.)-.5)));lc+=vec3(st);
    vec3 pv=lvor(q*.9);float pl=step(.82,pv.z)*(1.-smoothstep(.2,.24,pv.x));vec3 pc=vec3(.78,.16,.1)*(1.-.35*step(.86,lh(floor(q*9.))));lc=mix(lc,pc,pl);livR=.3;}
  else if(lpat==32){/* basil vortex: a spiral swirl on each flank */
    vec2 c=vec2(uLBox.x+(uLBox.y-uLBox.x)*.48,uLBelt*.8);vec2 d=vec2(lp.x-c.x,(lp.y-c.y)*1.6+lp.z*.15);float r=length(d),a=atan(d.y,d.x);
    float sw=sin(a*4.+r*2.2-lfbm(d*.5)*2.);lc=mix(uLB,uLA,smoothstep(-.2,.2,sw));lc=mix(lc,uLC,(1.-smoothstep(.0,.12,abs(sw-.85)))*.9);lc=mix(lc,uLB*.6,smoothstep(3.5,6.,r)*.5);}
  else if(lpat==33){/* tiger crust: tapering stripes over a toasted gradient, pale belly */
    float w=lfbm(vec2(lp.x*.55,lp.y*1.3+lp.z*.9));float st=sin(lp.x*3.1+w*6.5+lp.y*.8);float th=.55+.35*smoothstep(0.,uLBox.w,lp.y);
    vec3 base=mix(uLA,uLA*.78,smoothstep(.2,.9,lu));lc=mix(base,uLB,smoothstep(th,th+.06,st));lc=mix(lc,uLC,1.-smoothstep(uLBelt*.35,uLBelt*.55,lp.y));}
  else if(lpat==34){/* shattered prism: faceted shards in a colour sweep with dark seams */
    vec3 v=lvor(vec2(lp.x,lp.y+lp.z*.7)*1.15);vec3 a=mix(uLA,uLB,v.z),b=mix(uLB,uLC,v.z);lc=mix(a,b,smoothstep(.2,.8,lu+v.z*.3-.15));
    lc*=.85+.3*v.z;lc=mix(lc,vec3(.04),1.-smoothstep(.03,.06,v.y-v.x));livR=.12+.25*v.z;}
  else if(lpat==35){/* topographic: contour lines over banded terrain, every fifth line bold */
    float h=lfbm(vec2(lp.x*.32,(lp.y+lp.z)*.32))*9.;float f=abs(fract(h)-.5);float bold=step(mod(floor(h+.5),5.),.5);
    lc=mix(uLA,uLB,step(.5,fract(h*.5))*.35);lc=mix(lc,uLC,1.-smoothstep(.03+bold*.04,.06+bold*.05,.5-f));livR=.4;}
  else if(lpat==36){/* racing heritage: rising twin stripes, nose chevrons, checkered tail band */
    float d=uLBelt+.05-lp.y-.5*(1.-lu);float s1=step(0.,d)*step(d,.16),s2=step(.21,d)*step(d,.3);lc=mix(uLA,uLB,(s1+s2)*lside);
    float chev=step(.82,lu)*step(fract(lu*14.-laz*3.),.45)*step(.6,lnn.y);lc=mix(lc,uLC,chev);
    float tail=step(lu,.1)*step(lp.y,uLBelt*.9)*lside;float ck=mod(floor(lp.x*3.)+floor(lp.y*3.),2.);lc=mix(lc,mix(vec3(.95),vec3(.05),ck),tail);
    lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt*.35))));}
  else if(lpat==37){/* holo foil: iridescent sheen that shifts with the body's curves, fine diagonal grain */
    float hue=fract(lp.x*.07+lnn.y*.55+lnn.x*.35+lnn.z*.2+lfbm(lp.xz*.35)*.45);vec3 rb=lpal(hue);lc=mix(uLA,rb,.62);
    lc*=.92+.08*step(.5,fract((lp.x+lp.y)*9.));lc=mix(lc,uLB,lside*(1.-smoothstep(.015,.03,abs(lp.y-uLBelt))));livR=.1;}
  else if(lpat==38){/* lava flow: cracked dark rock with glowing seams that run hotter toward the tail */
    vec3 v=lvor(vec2(lp.x,lp.y+lp.z*.6)*.9+lfbm(lp.xz*.6)*.6);float crack=1.-smoothstep(.0,.09+.06*(1.-lu),v.y-v.x);vec3 rock=uLA*(.7+.5*lfbm(vec2(lp.x,lp.y+lp.z)*2.3));
    vec3 hot=mix(uLB,uLC,crack*crack);lc=mix(rock,hot,crack);lc=mix(lc,uLB*.5,(1.-smoothstep(.0,.25,v.y-v.x))*.35);livR=crack>.4?.35:.75;}
  else if(lpat==39){/* pizza party: pepperoni, olives and basil scattered over melted cheese, crust skirt */
    vec2 q=vec2(lp.x,lp.y+lp.z*.85)*1.35;vec2 c=floor(q),f=fract(q)-.5;f-=vec2(lh(c)-.5,lh(c+4.2)-.5)*.35;float t=lh(c+11.);float r=length(f);
    lc=mix(uLA,uLA*1.08,lfbm(q*2.3));
    if(t<.42){float sp=step(.8,lh(floor(f*9.+c)));lc=mix(lc,mix(uLB,uLB*.72,sp),1.-smoothstep(.27,.29,r));}
    else if(t<.62){lc=mix(lc,vec3(.08),(1.-smoothstep(.11,.13,r))*smoothstep(.05,.07,r));}
    else if(t<.8){vec2 e=vec2(f.x*cos(t*9.)-f.y*sin(t*9.),f.x*sin(t*9.)+f.y*cos(t*9.));float lf=length(e*vec2(1.,2.4));lc=mix(lc,vec3(.16,.48,.15),1.-smoothstep(.2,.22,lf));lc=mix(lc,vec3(.1,.33,.1),(1.-smoothstep(.0,.015,abs(e.y)))*step(lf,.2));}
    lc=mix(lc,uLC*(.85+.3*lfbm(lp.xz*3.)),1.-smoothstep(uLBelt*.32,uLBelt*.42,lp.y));livR=.32;}
  else if(lpat==40){/* champion filigree: gold scrollwork engraved over gloss black, pinstripes and a gold dust shimmer */
    float sc=sin(lp.x*3.4+sin(lp.y*4.2+lp.z*3.)*1.6)*sin(lp.y*5.1-lp.x*.8+lp.z*2.);float fil=(1.-smoothstep(.0,.07,abs(sc)))*step(uLBelt*.45,lp.y);
    lc=mix(uLA,uLB,fil*.9);float pin=(1.-smoothstep(.012,.025,abs(lp.y-uLBelt)))*lside+(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.45)))*lside;lc=mix(lc,uLC,pin);
    lc+=uLB*step(.985,lh(floor(vec2(lp.x,lp.y+lp.z)*38.)))*.6;livR=fil>.5?.18:.12;}
  else if(lpat==41){/* sauce rings: concentric rings spread from a target on each flank and on the nose, breaking into dashes further out */
    float L=uLBox.y-uLBox.x,zs=uLBox.z-abs(lp.z);float r1=length(vec3(lp.x-(uLBox.x+L*.4),lp.y-uLBelt*.62,zs*1.1));float r2=length(vec3(lp.x-(uLBox.x+L*.88),(uLBox.w-lp.y)*.7,lp.z))*1.15;float r=min(r1,r2);
    float w=mix(.46,.14,smoothstep(.8,2.8,r));float f=fract(r*1.3+lfbm(lp.xz*.35)*.18*smoothstep(1.2,3.,r));float a=atan(lp.y-uLBelt*.62,lp.x-(uLBox.x+L*.4));
    float dash=r>2.6?step(.28,fract(a*9.+r*.6)):1.;float ring=max((1.-smoothstep(w-.03,w+.03,f))*dash,1.-smoothstep(.26,.3,r));
    lc=mix(uLA,uLB,ring);lc=mix(lc,uLC,1.-smoothstep(uLBelt*.26,uLBelt*.34,lp.y));livR=.3;}
  else if(lpat==42){/* spectrum weave: diagonal wavy bands in six colours with fine dark seams */
    float u=(lp.x*.8+lp.y*.55+lp.z*.35)*3.+sin(lp.y*2.3-lp.x*.6+lp.z*1.1)*.8;float id=floor(u),f=fract(u);float h=lh(vec2(id,7.));
    vec3 c=h<.18?uLA:h<.36?uLB:h<.52?uLC:h<.68?vec3(.95,.93,.88):h<.84?vec3(.86,.2,.3):vec3(.07,.08,.12);
    lc=mix(c,vec3(.04),1.-smoothstep(.05,.09,min(f,1.-f)));lc*=.94+.06*step(.5,fract(u*6.));livR=.26;}
  else if(lpat==43){/* dazzle camo: angular shards in three tones with halftone dots fading off every edge */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7);vec2 r=mat2(vec2(.8,-.6),vec2(.6,.8))*q;float g1=r.x*.45+step(.5,fract(r.y*.38))*.5;float f1=fract(g1);float s1=step(.5,f1);
    float g2=(q.x*.7-q.y*1.3)*.32;float s2=step(.62,fract(g2));float e=min(abs(f1-.5),min(f1,1.-f1));
    lc=mix(uLA,uLB,s1);lc=mix(lc,uLC,s2*(1.-s1));vec2 gd=fract(q*5.5)-.5;float ht=.42*(1.-smoothstep(.0,.22,e));
    lc=mix(lc,uLB,(1.-s1)*(1.-smoothstep(ht-.03,ht,length(gd))));lc=mix(lc,uLA,s1*(1.-s2)*(1.-smoothstep(ht*.8-.03,ht*.8,length(gd))));livR=.3;}
  else if(lpat==44){/* rainbow sweep: six bands run low along the flank and rise over the rear quarter onto the roof */
    float b0=uLBelt*.12+smoothstep(.66,.04,lu)*uLBelt*.95;float t=(lp.y-b0)/(uLBelt*.85);float on=step(0.,t)*step(t,1.)*lside;
    vec3 rb=lpal(.02+floor(t*6.)/6.*.82)*1.05;lc=mix(uLA,rb,on);lc=mix(lc,uLB,lside*(1.-smoothstep(.02,.04,abs(t+.06)))*step(t,0.));
    lc=mix(lc,uLB,lside*(1.-smoothstep(.02,.04,abs(t-1.06)))*step(1.,t));livR=.24;}
  else if(lpat==45){/* prism chrome: holographic hex sequins over the top, gloss colour underneath, split by a raked line */
    vec2 h=vec2(lp.x,lp.y+lp.z)*5.;h.y*=1.1547;h.x+=step(1.,mod(floor(h.y),2.))*.5;vec2 id=floor(h);float hv=lh(id);
    vec3 holo=lpal(fract(hv*.35+lnn.y*.6+lnn.x*.4+lp.x*.05))*.72+.3;vec2 fh=abs(fract(h)-.5);holo*=.8+.2*smoothstep(.5,.38,max(fh.x,fh.y));
    float cut=uLBelt*.55+(lu-.5)*1.2;float split=smoothstep(-.03,.03,lp.y-cut);lc=mix(uLA,holo,split);lc=mix(lc,uLB,(1.-smoothstep(.02,.05,abs(lp.y-cut)))*.95);livR=split>.5?.07:.28;}
  else if(lpat==46){/* paint splash: warped bands of bold colour outlined in black, like a hand-painted art car */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*.55;vec2 w=vec2(lfbm(q+1.3),lfbm(q+7.1));float n=lfbm(q*1.3+w*2.2)*1.15;
    float k=floor(n*7.);vec3 c=k<2.?uLA:k<3.?uLB:k<4.?uLC:k<5.?vec3(.15,.72,.95):vec3(.52,.22,.85);
    float ed=abs(fract(n*7.)-.5);lc=mix(c,vec3(.05),(1.-smoothstep(.42,.47,ed))*.9);lc+=vec3(.08)*step(.985,lh(floor(q*60.)));livR=.3;}
  else if(lpat==47){/* shatter drift: clean white with a spreading colour splatter cut by a black crack web */
    vec2 q=vec2(lp.x,lp.y+lp.z*.75);float n=lfbm(q*.5+3.);float sp=smoothstep(.5,.53,n+.12*sin(lp.x*.7));
    vec3 v=lvor(q*1.6);float cr=1.-smoothstep(.0,.04,v.y-v.x);vec3 v2=lvor(q*4.+9.);float cr2=1.-smoothstep(.0,.03,v2.y-v2.x);float zone=smoothstep(.38,.5,n);
    lc=mix(uLA,uLB,sp);lc=mix(lc,uLC,max(cr,cr2*.7)*zone);float drop=step(.93,lh(floor(q*7.)))*(1.-smoothstep(.15,.3,length(fract(q*7.)-.5)))*smoothstep(.3,.45,n);lc=mix(lc,uLB,drop);livR=.3;}
  else if(lpat==48){/* gold leaf: flaked gold with a dark scaled ribbon snaking down each side */
    float rib=lp.y-(uLBelt*.6+sin(lp.x*.9+lp.z*.3)*.42);float inR=(1.-smoothstep(.3,.33,abs(rib)))*lside;
    vec2 s=vec2(lp.x*3.,rib*6.);s.x+=step(1.,mod(floor(s.y),2.))*.5;vec2 f=fract(s)-vec2(.5,0.);float sc=1.-smoothstep(.04,.09,abs(length(f*vec2(1.,1.4))-.5));
    vec3 gold=uLA*(.82+.36*lh(floor(vec2(lp.x,lp.y+lp.z)*34.)));lc=mix(gold,mix(uLB,uLC*.8,sc),inR);lc=mix(lc,uLC,(1.-smoothstep(.0,.025,abs(abs(rib)-.315)))*lside);livR=inR>.5?.4:.16;}

  else if(lpat==49){/* liquid gold: mirror gold wrap with warped reflection streaks that slide with the body's curvature */
    float w=lfbm(vec2(lp.x*.9+lnn.y*2.,lp.y*1.4+lp.z*.6)+lnn.xz*1.5);float band=sin(w*14.+lp.x*2.2+lnn.y*5.+lnn.x*2.);
    vec3 g=uLA*(.8+.32*band)+uLB*.16*smoothstep(.55,1.,band);lc=mix(g,uLC*1.15,smoothstep(.86,1.,band)*.55);lc=mix(lc,uLA*.35,smoothstep(-.6,-1.,band)*.5);livR=.04+.06*(1.-band);}
  else if(lpat==50){/* turbo doodle: hand-drawn comic panels in two blues, every panel filled with its own gears, hatching or dots, all inked in black */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7)*1.25;vec3 v=lvor(q);float ed=1.-smoothstep(.0,.075,v.y-v.x);float id=v.z;
    vec3 v2=lvor(q*2.9+5.);float ed2=1.-smoothstep(.0,.07,v2.y-v2.x);vec2 cc=fract(q*2.6)-.5;float ring=1.-smoothstep(.03,.06,abs(length(cc)-.3));float gear=ring*step(.5,fract(atan(cc.y,cc.x)*2.2));
    float dots=1.-smoothstep(.1,.14,length(fract(q*3.4)-.5));float hatch=step(.62,fract((q.x+q.y)*5.));float arrow=step(.6,fract(q.x*2.))*step(abs(fract(q.y*2.)-.5)*2.,fract(q.x*2.)*1.6-.9);
    vec3 base=id<.28?uLA:id<.5?uLB:id<.68?mix(uLA,uLB,.5):id<.86?uLC:vec3(.9,.92,.95);float det=id<.28?dots:id<.5?hatch*.6:id<.68?max(ring,gear):id<.86?arrow:ed2;
    lc=mix(base,vec3(.04),max(ed,det*.95));lc=mix(lc,vec3(.04),ed2*step(.86,id)*.5);lc*=.92+.08*lh(floor(q*40.));livR=.32;}
  else if(lpat==51){/* paint riot: six colours of splatter thrown over black, drops, drips and speckle on top of each other */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);lc=uLC*.12;
    for(int i=0;i<6;i++){float fi=float(i);vec2 qq=q*(.85+fi*.16)+vec2(fi*3.1,fi*1.7);vec3 v=lvor(qq);float rad=.17+.2*lh(vec2(fi,v.z));float blob=1.-smoothstep(rad-.04,rad,v.x);
      float col=floor(qq.x*2.)+fi;float dr=step(.82,lh(vec2(col,fi)))*(1.-smoothstep(.05,.09,abs(fract(qq.x*2.)-.5)))*step(fract(qq.y*.45+lh(vec2(col,2.))),.55);
      vec3 pc=i==0?uLA:i==1?uLB:i==2?vec3(.2,.75,.95):i==3?vec3(.55,.22,.85):i==4?vec3(.98,.62,.1):vec3(.3,.8,.35);lc=mix(lc,pc,max(blob,dr*blob*2.));}
    lc+=vec3(.9)*step(.985,lh(floor(q*55.)));livR=.28;}
  else if(lpat==52){/* chromatic tide: holographic interference waves that shift hue with the viewing angle, over a fine scan-line raster */
    float ph=lp.x*1.6+sin(lp.y*2.6+lp.z*1.4)*1.4+lfbm(vec2(lp.x,lp.y+lp.z)*.9)*4.;float wave=sin(ph*3.);
    vec3 col=lpal(fract(ph*.08+lnn.y*.25+lnn.x*.2+.6))*1.05;float ras=.78+.22*step(.5,fract((lp.y+lp.z*.3)*22.));
    lc=mix(uLA*.35,col,.55+.45*wave)*ras;lc+=vec3(.28)*smoothstep(.8,1.,wave);livR=.1;}
  else if(lpat==53){/* candy flake lace: deep candy orange under a repeating lace stencil, buried in rainbow metal flake */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*2.2;vec2 c=fract(q)-.5;float r=length(c);float lace=1.-smoothstep(.03,.06,abs(r-.36));lace=max(lace,(1.-smoothstep(.03,.07,abs(sin(q.x*6.28)*sin(q.y*6.28)*.5)))*.6);
    float leaf=1.-smoothstep(.0,.05,abs(abs(c.x)+abs(c.y)-.28));vec2 fc=floor(vec2(lp.x,lp.y+lp.z)*70.);float flk=step(.955,lh(fc));vec3 flc=lpal(lh(fc+1.));
    lc=mix(uLA,uLB,max(lace,leaf)*.6);lc=mix(lc,flc*1.35,flk);lc*=.85+.3*max(lnn.y,0.);livR=.12;}
  else if(lpat==54){/* ghost flames: candy burgundy with silver-pink pinstriped flames licking back from the nose */
    float yy=(lp.y+lp.z*.6);float edge=.3+.3*ln2(vec2(yy*2.5,3.))+.14*ln2(vec2(yy*7.,lp.x*2.))+.08*sin(yy*9.);float d=lu-edge;
    float fl=1.-smoothstep(-.01,.02,d);float inner=1.-smoothstep(-.09,-.06,d);float pin=(1.-smoothstep(.0,.015,abs(d)))+(1.-smoothstep(.0,.012,abs(d+.075)));
    float lick=step(.5,fract(yy*3.1+lp.x*.4))*smoothstep(-.25,.0,d)*step(d,0.);vec3 body=mix(uLB,uLC,ln2(vec2(lu*8.,yy*3.)));
    lc=mix(uLA,body,fl*(.55+.45*inner));lc=mix(lc,uLC*1.2,pin);lc=mix(lc,uLA,lick*.35);lc+=vec3(.2)*step(.975,lh(floor(vec2(lp.x,lp.y+lp.z)*48.)));livR=.1;}
  else if(lpat==55){/* kandy scroll: royal blue candy with silver pinstripe scrollwork in every panel and a double line along the belt */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.1;vec2 c=fract(q)-.5;float r=length(c),a=atan(c.y,c.x);float sp=1.-smoothstep(.0,.03,abs(fract(r*4.2-a/6.283)-.5)-.0);float cell=lh(floor(q));
    float spiral=sp*(1.-smoothstep(.34,.42,r))*step(.3,cell);float frame=1.-smoothstep(.0,.025,abs(max(abs(c.x),abs(c.y))-.46));
    float belt=(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.52)))*lside+(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.58)))*lside;
    lc=mix(uLA,uLC,step(.7,cell)*.5);lc*=.85+.3*max(lnn.y,0.);lc=mix(lc,uLB,max(max(spiral,frame*.6),belt));lc+=vec3(.15)*step(.98,lh(floor(vec2(lp.x,lp.y+lp.z)*52.)));livR=.08;}
  else if(lpat==56){/* chomp: white body covered in black marker doodles, with a toothy grin and eyes on the nose */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7)*1.4;vec3 v=lvor(q);float ed=1.-smoothstep(.0,.08,v.y-v.x);float fill=step(.8,v.z);vec2 cc=fract(q*2.)-.5;float eye=1.-smoothstep(.1,.13,length(cc));
    float gum=uLBelt*.5;float t=(gum-lp.y)/.55;float teeth=step(abs(fract(lp.x*2.4)-.5)*2.,1.-t)*step(0.,t)*step(t,1.);float mouth=step(0.,t)*step(t,1.6);float nose=smoothstep(.6,.7,lu);
    lc=mix(uLA,uLC,max(ed,fill)*(1.-nose));lc=mix(lc,uLC,step(.9,v.z)*eye*(1.-nose));lc=mix(lc,uLB,mouth*nose);lc=mix(lc,uLA,teeth*nose);lc=mix(lc,uLC,(1.-smoothstep(.0,.03,abs(t)))*nose*lside);
    float ey=1.-smoothstep(.2,.24,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.8),lp.y-uLBelt*.9)));lc=mix(lc,uLC,ey*lside);lc=mix(lc,uLA,(1.-smoothstep(.07,.1,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.82),lp.y-uLBelt*.93))))*lside);livR=.34;}
  else if(lpat==57){/* liberty streak: gold-green pearl with magenta, violet and cyan prism streaks racing along the flank */
    float y=(lp.y+lp.z*.15)*3.+sin(lp.x*1.3)*.4+lfbm(vec2(lp.x*.6,lp.y*2.))*1.2;float id=floor(y);float f=fract(y);float h=lh(vec2(id,3.));
    vec3 sc=h<.3?uLB:h<.55?uLC:h<.75?vec3(.2,.9,.9):vec3(.95,.3,.75);float len=lh(vec2(id,9.))*.5+.3;float on=step(lu,len+.3*sin(id))*step(len-.5,lu);
    float thin=1.-smoothstep(.0,.1,abs(f-.5)-(.06+.3*lh(vec2(id,5.))));vec3 pearl=uLA*(.9+.25*lnn.y)+vec3(.1,.2,0.)*lnn.x;lc=mix(pearl,sc,thin*on);lc+=vec3(.25)*step(.975,lh(floor(vec2(lp.x,lp.y+lp.z)*50.)));livR=.12;}
  else if(lpat==58){/* circuit board: dark green substrate with gold traces, solder pads and glowing chips */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*3.;vec2 c=fract(q);vec2 id=floor(q);float h=lh(id);float tr=h<.5?1.-smoothstep(.05,.09,abs(c.y-.5)):1.-smoothstep(.05,.09,abs(c.x-.5));
    float pad=(1.-smoothstep(.11,.15,length(c-.5)))*step(.6,lh(id+2.));float hole=(1.-smoothstep(.04,.06,length(c-.5)))*step(.6,lh(id+2.));float chip=step(.9,lh(id+5.))*step(max(abs(c.x-.5),abs(c.y-.5)),.3);
    lc=mix(uLA,uLB,max(tr,pad));lc=mix(lc,uLA*.5,hole);lc=mix(lc,vec3(.06),chip);lc=mix(lc,uLC,chip*(1.-smoothstep(.05,.08,abs(c.y-.5)))*step(.5,fract(c.x*8.)));livR=max(tr,pad)>.5?.22:.5;}
  else if(lpat==59){/* lava flow: cooled black crust split by glowing orange cracks that pulse brighter at the seams */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.4;vec3 v=lvor(q);float cr=1.-smoothstep(.0,.1,v.y-v.x);vec3 v2=lvor(q*2.6+3.);float cr2=1.-smoothstep(.0,.06,v2.y-v2.x);
    float heat=cr*cr+cr2*cr2*.5;lc=mix(uLA*(.7+.3*lfbm(q*3.)),uLB,heat);lc+=uLC*heat*heat*.8;lc*=.9+.1*lh(floor(q*30.));livR=heat>.4?.5:.28;}
  else if(lpat==60){/* marble and gold: white marble veined in grey with a second web of gold leaf veins */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float m=lfbm(q*1.1+lfbm(q*2.)*1.5);float vein=1.-smoothstep(.0,.16,abs(sin(m*9.+lp.x)));float vein2=1.-smoothstep(.0,.06,abs(sin(m*14.-lp.y*2.+2.)));
    lc=mix(uLA,uLB,vein*vein*.9+smoothstep(.35,.9,m)*.35);lc=mix(lc,uLC,vein2*step(.5,lfbm(q*.7+9.)));livR=vein2>.5?.12:.25;}
  else if(lpat==61){/* deep space: nebula clouds in two colours, dust lanes and a field of stars */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float n=lfbm(q*.6);float n2=lfbm(q*1.5+4.);float n3=lfbm(q*3.+8.);lc=mix(uLA,uLB,n)*.9;lc=mix(lc,uLC,smoothstep(.55,.8,n2)*.8);lc=mix(lc,vec3(.02),smoothstep(.6,.75,n3)*.5);
    vec2 sc=floor(q*45.);float st=step(.985,lh(sc));lc+=vec3(1.)*st*(.5+.5*lh(sc+1.));lc+=uLC*step(.997,lh(sc+7.))*2.;livR=.22;}
  else if(lpat==62){/* viper scale: rows of overlapping scales that fade from belly to spine, with a dark dorsal stripe */
    vec2 h=vec2(lp.x,lp.y+lp.z*.9)*4.2;h.x+=step(1.,mod(floor(h.y),2.))*.5;vec2 f=fract(h)-vec2(.5,0.);float sc=length(f*vec2(1.,1.5));float rim=1.-smoothstep(.42,.5,sc);float hi=1.-smoothstep(.0,.3,length(f-vec2(0.,.25)));
    float t=clamp((lp.y-uLBelt*.2)/(uLBelt*.9),0.,1.);vec3 base=mix(uLA,uLB,t);lc=mix(base*.55,base*(1.+.25*hi),rim);float dorsal=1.-smoothstep(.15,.3,abs(lnn.y-1.));lc=mix(lc,uLC,dorsal*.8*step(.5,fract(lp.x*1.6)));livR=.2;}
  else if(lpat==63){/* comic pop: ben-day dots, a bold raked colour split and thick black panel outlines */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float cut=uLBelt*.5+(lu-.5)*1.4;float side=smoothstep(-.02,.02,lp.y-cut);float dots=1.-smoothstep(.17,.21,length(fract(q*3.6)-.5));
    vec3 top=mix(uLA,uLB,dots);vec3 bot=mix(uLB,uLC,dots);lc=mix(bot,top,side);float line=1.-smoothstep(.04,.07,abs(lp.y-cut));lc=mix(lc,vec3(.04),line);
    float burst=step(.5,fract(atan(lp.y-uLBelt*.6,lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.35))*4.))*(1.-smoothstep(.9,1.4,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.35),lp.y-uLBelt*.6))))*lside;lc=mix(lc,vec3(1.),burst*.9);livR=.3;}
  else if(lpat==64){/* soft serve swirl: three pastel ribbons twisting out of a point on each flank, edged in white */
    float L=uLBox.y-uLBox.x;vec2 c=vec2(lp.x-(uLBox.x+L*.5),lp.y-uLBelt*.5);float a=atan(c.y,c.x),r=length(c);float sw=fract(a/6.283*3.+r*.55+lfbm(c*.5)*.2);float k=floor(sw*3.);float f=fract(sw*3.);
    vec3 col=k<1.?uLA:k<2.?uLB:uLC;lc=mix(col,vec3(1.),1.-smoothstep(.03,.07,min(f,1.-f)));lc*=.9+.1*sin(r*6.);livR=.26;}
  else if(lpat==65){/* kevlar twill: a woven yellow and black twill with the weave catching the light */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*5.5;float wx=step(.5,fract(q.x)),wy=step(.5,fract(q.y));float weave=abs(wx-wy);float sh=.75+.25*sin(fract(weave>.5?q.x:q.y)*6.283);
    lc=mix(uLA,uLB,weave)*sh;float stripe=(1.-smoothstep(.02,.04,abs(lp.y-uLBelt*.55)))*lside;lc=mix(lc,uLC,stripe);livR=.35;}
  else if(lpat==66){/* stained glass: lead-lined panes in jewel tones that glow where the light hits */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.1;vec3 v=lvor(q);float lead=1.-smoothstep(.0,.06,v.y-v.x);float h=lh(vec2(v.z,1.));vec3 pane=h<.25?uLA:h<.5?uLB:h<.75?uLC:vec3(.95,.8,.2);
    pane*=.75+.35*lfbm(q*4.);lc=mix(pane*(.8+.5*max(lnn.y,0.)),vec3(.05),lead);livR=lead>.5?.5:.08;}
  if(uLNum>-.5&&abs(lnn.z)>.6){vec2 d=vec2(lp.x-uLNumPos.x,lp.y-uLNumPos.y);float r=length(d);if(r<.72){lc=r<.6?vec3(.95):uLB;
    if(r<.6){float tx=d.x/1.2*(lp.z>0.?1.:-1.)+.5,ty=d.y/1.2+.5;float a=texture(uLNumTex,vec2((uLNum+clamp(tx,0.,1.))/8.,clamp(ty,0.,1.))).a;lc=mix(lc,vec3(.06),a);}}}
  if(abs(lnn.z)>.55){float sd=lp.z>0.?1.:-1.,L=uLBox.y-uLBox.x;
    if(uLDecI.x>-.5){vec2 c0=uLNum>-.5?vec2(uLBox.x+L*.3,uLNumPos.y):uLNumPos;float S=uLDecI.z;vec2 q=vec2((lp.x-c0.x)/S*sd+.5,(lp.y-c0.y)/S+.5);
      if(q.x>0.&&q.x<1.&&q.y>0.&&q.y<1.){vec4 t=texture(uLDec,vec2((uLDecI.x+q.x)/8.,.5+q.y*.5));lc=mix(lc,mix(uLC,uLB,t.r),t.a);}}
    if(uLDecI.y>-.5){vec2 c1=vec2(uLBox.x+L*(uLNum>-.5?.62:.26),uLBelt*.62);float S=L*.2;vec2 q=vec2((lp.x-c1.x)/S*sd+.5,(lp.y-c1.y)/(S*.32)+.5);
      if(q.x>0.&&q.x<1.&&q.y>.12&&q.y<.88){q.y=.5+(q.y-.5)*.3;vec4 t=texture(uLDec,vec2((uLDecI.y+q.x)/8.,q.y*.5));lc=mix(lc,mix(uLC*.6,uLB,t.r),t.a*.95);}}}
  /* finish pass (Sharp and Ultra): the paint deepens toward the sills and under the curves, gets a candy-like richness at grazing
     angles, and every colour edge reads as a thin vinyl edge. Ultra adds metallic flake under the clear coat and lifts decal edges. */
  vec3 lvFN=vec3(0.);
  if(uLQ>.5){float span=max(uLBox.w-uLBelt,.4),sill=smoothstep(uLBelt-span*1.15,uLBelt+span*.2,lp.y);
    lc*=mix(.74,1.,sill)*(.84+.16*smoothstep(-.7,.35,lnn.y));
    vec3 lvV=normalize(vViewPosition);float fres=1.-clamp(abs(dot(normalize(vNormal),lvV)),0.,1.);fres*=fres;
    lc=mix(lc,lc*lc*1.55,fres*.55)*(1.-.12*fres);
    float lvE=clamp(length(fwidth(lc))*1.6,0.,1.)*(1.-smoothstep(60.,220.,length(vViewPosition)));lc*=1.-.2*lvE;
    if(uLQ>1.5){vec3 fq=lp*85.;vec3 ci=floor(fq);vec3 fr=fract(sin(vec3(dot(ci,vec3(127.1,311.7,74.7)),dot(ci,vec3(269.5,183.3,246.1)),dot(ci,vec3(113.5,271.9,124.6))))*43758.5453);
      float ffw=length(fwidth(fq)),fk=uLFl*(1.-smoothstep(.9,2.2,ffw)),on=smoothstep(.85,.9,fr.z);lvFN=(fr*2.-1.)*fk*(.22+1.45*on);lc*=1.+on*fk*.07;lc=mix(lc,lc*lc*1.5,fres*.25);
      float hh=dot(lc,vec3(.299,.587,.114));lvFN.xy+=vec2(dFdx(hh),dFdy(hh))*-1.6*(1.-smoothstep(25.,90.,length(vViewPosition)));}}
  ALBEDO=COLOR.rgb*lc;
  ROUGHNESS=livR>=0.0?livR:rough;
  // (the PC's flake is finer and gentler than the web's: at full resolution the web's read as grain)
  if(uLQ>1.5)NORMAL=normalize(NORMAL+lvFN*0.12);

	METALLIC = metal;
	CLEARCOAT = coat;
	CLEARCOAT_ROUGHNESS = 0.05;
}
