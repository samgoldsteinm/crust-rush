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
uniform float uLNumS = 0.0;   // PC: the number's design: 0 roundel, 1 square plate, 2 dark disc, 3 bare italic, 4 oval plate, 5 big door number
uniform float uLNumV = 0.0;   // PC: the number shown (digits 1 to 8, one or two of them); 0 = the driver's own, as on the web
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
// PC: one round glint (a star, a fleck of glitter) at a random spot in some of a grid's cells, soft-edged at any size.
// The web lit whole cells, which a 1440p screen shows close up as square pixels.
// PC helpers for the PC-only liveries (67 on): an anti-aliased band, grid lines, a five-point star, a tartan sett
float lbd(float x,float a,float b){float w=max(fwidth(x),.0005);return clamp(smoothstep(a-w,a+w,x)-smoothstep(b-w,b+w,x),0.,1.);}
float lgr(vec2 q,float t){vec2 g=abs(fract(q-.5)-.5);vec2 w=max(fwidth(q),vec2(.0005));vec2 l=1.-smoothstep(vec2(t)-w,vec2(t)+w,g);return max(l.x,l.y)*(1.-.6*clamp(max(w.x,w.y)*3.,0.,1.));}
float lstar5(vec2 p,float r,float rf){const vec2 k1=vec2(.809016994375,-.587785252292);vec2 k2=vec2(-k1.x,k1.y);p.x=abs(p.x);p-=2.*max(dot(k1,p),0.)*k1;p-=2.*max(dot(k2,p),0.)*k2;
  p.x=abs(p.x);p.y-=r;vec2 ba=rf*vec2(-k1.y,k1.x)-vec2(0.,1.);float h=clamp(dot(p,ba)/dot(ba,ba),0.,r);return length(p-ba*h)*sign(p.y*ba.x-p.x*ba.y);}
vec3 ltc(float x){float f=fract(x);vec3 c=uLA;c=mix(c,uLB,lbd(f,.12,.36));c=mix(c,uLC,lbd(f,.5,.74));c=mix(c,vec3(.9,.76,.28),lbd(f,.42,.445));
  c=mix(c,vec3(.86,.84,.8),lbd(f,.83,.845));c=mix(c,vec3(.05),lbd(f,.225,.255)+lbd(f,.605,.635));return c;}
// PC: race numbers from the digit strip (1 to 8 in eight cells). The strip is read top-down here; the web's
// pictures are read bottom-up, which is why the numbers and side logos used to come out upside down.
float lnum1(vec2 t,float dg){if(t.x<0.||t.x>1.||t.y<0.||t.y>1.)return 0.;return texture(uLNumTex,vec2((dg-1.+t.x)/8.,1.-t.y)).a;}
float lnumA(vec2 p,float n){if(n<9.5)return lnum1(p+.5,n);float d1=floor(n/10.),d2=n-d1*10.;return max(lnum1(p+vec2(.77,.5),d1),lnum1(p+vec2(.23,.5),d2));}
float lnumO(vec2 p,float n,float w){float o=lnumA(p,n);for(int i=0;i<8;i++){float an=float(i)*.7854;o=max(o,lnumA(p+vec2(cos(an),sin(an))*w,n));}return o;}
float lsp(vec2 p,float thr){vec2 i=floor(p),f=fract(p);float h=lh(i+.31);if(h<thr)return 0.;vec2 c=vec2(lh(i+5.3),lh(i+9.1))*.5+.25;
  float r=.16+.16*lh(i+2.7);float d=length(f-c);float aa=max(fwidth(d)*1.2,.01);return 1.-smoothstep(r-aa,r+aa,d);}

void vertex() {
	vLivP = (liv_xf * vec4(VERTEX, 1.0)).xyz;
	vLivN = mat3(liv_xf) * NORMAL;
}

void fragment() {
	vec3 vViewPosition = -VERTEX;
	vec3 vNormal = NORMAL;

  vec3 lp=vLivP,lnn=normalize(vLivN);float lu=(lp.x-uLBox.x)/(uLBox.y-uLBox.x),laz=abs(lp.z)/uLBox.z,lside=step(.55,abs(lnn.z));float livR=-1.;
  vec3 lc=uLA;int lpat=int(uLPat+.5);
  /* PC: three small switches rather than one long chain (the web's if/else ladder): some drivers lower a long ladder or switch
     into ever deeper nesting, and past about eighty levels the later patterns come out black */
  if(lpat<34){switch(lpat){
  case 1:{float s=step(.07,laz)*step(laz,.2);lc=mix(uLA,uLB,s);lc=mix(lc,uLC,step(lp.y,uLBelt*.42));}break;
  case 2:{float t=smoothstep(uLBelt-.03,uLBelt+.03,lp.y);lc=mix(uLB,uLA,t);lc=mix(lc,uLC,1.-smoothstep(.02,.06,abs(lp.y-uLBelt)));}break;
  case 3:{float a=smoothstep(.62,.68,lu),b=smoothstep(.3,.36,lu);lc=mix(uLC,mix(uLB,uLA,a),b);}break;
  case 4:{float n=lfbm(vec2(lp.y*1.4,lp.z*1.1+lp.x*.15));float reach=.3+.32*n+.07*sin(lp.y*6.+lp.z*4.);float f=smoothstep(1.-reach-.02,1.-reach+.02,lu);
    float core=smoothstep(1.-reach*.55-.02,1.-reach*.55+.02,lu);lc=mix(uLA,mix(uLB,uLC,core),f*step(lp.y,uLBox.w*.92));}break;
  case 5:{float band=step(uLBelt-.42,lp.y)*step(lp.y,uLBelt+.06);float ch=mod(floor(lp.x*2.3)+floor(lp.y*2.3),2.);lc=mix(uLA,mix(uLA,uLB,ch),band*lside);
    lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-(uLBelt+.1)))));}break;
  case 6:{float w=uLBelt-.2+.22*sin(lp.x*1.15+1.3);lc=lp.y<w?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.03,.07,abs(lp.y-w)));}break;
  case 7:{float n=lfbm(vec2(lp.x*.42,lp.z*.42)+lp.y*.35);lc=n<.42?uLA:(n<.6?uLB:uLC);livR=.62;}break;
  case 8:{lc=mix(uLB,uLA,smoothstep(.12,.88,lu));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}break;
  case 9:{float d=fract((lp.x+lp.y*1.15)*.16);float mid=step(.22,lu)*step(lu,.8);lc=mix(uLA,uLB,lside*mid*step(d,.11));lc=mix(lc,uLC,lside*mid*step(.14,d)*step(d,.19));}break;
  case 10:{float lo=step(lp.y,uLBelt);vec2 cq=vec2(lp.x,lp.y+lp.z)*7.;float cw=abs(step(.5,fract(cq.x))-step(.5,fract(cq.y)));float wv=cw*(.55+.45*sin(fract(cw>.5?cq.x:cq.y)*3.1416));lc=mix(uLA,mix(uLB,uLB*1.7,wv),lo);livR=lo>.5?.22:-1.;lc=mix(lc,uLC,1.-smoothstep(.015,.04,abs(lp.y-uLBelt)));}break;
  case 11:{lc=mix(uLA,uLB,step(laz,.13)*step(.28,lu));lc=mix(lc,uLC,step(.82,lu)*step(lp.y,uLBelt*.85));}break;
  case 12:{float s=step(.05,laz)*step(laz,.1)+step(.14,laz)*step(laz,.19);lc=mix(uLA,uLB,s*step(.6,lnn.y));}break;
  case 13:{livR=.72;lc=mix(uLA,uLC,step(lp.y,uLBelt*.45));lc=mix(lc,uLB,lside*(1.-smoothstep(.015,.04,abs(lp.y-uLBelt*.62))));}break;
  case 14:{float m=step(.27,lu)*step(lu,.7);lc=mix(uLA,uLB,m*step(lp.y,uLBelt+.05));lc=mix(lc,uLC,lside*(1.-smoothstep(.03,.06,abs(lp.y-uLBelt*.72))));}break;
  case 15:{float s=step(laz,.17),bd=step(.17,laz)*step(laz,.21);lc=mix(mix(uLA,uLB,s),uLC,bd);float sb=lside*step(uLBelt-.42,lp.y)*step(lp.y,uLBelt-.12);lc=mix(lc,uLB,sb);}break;
  case 16:{float d=uLBelt-.05-lp.y-.45*(1.-lu);float s1=step(0.,d)*step(d,.13),s2=step(.16,d)*step(d,.25),s3=step(.28,d)*step(d,.37);vec3 mid=mix(uLB,vec3(1.),.45);
    lc=mix(uLA,uLB,s1*lside);lc=mix(lc,mid,s2*lside);lc=mix(lc,uLC,s3*lside);}break;
  case 17:{float k=lu*1.25+lp.y/uLBox.w*.85;lc=k>1.15?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.02,.05,abs(k-1.15)));}break;
  case 18:{float zig=abs(fract(lp.y*1.2+abs(lp.z)*.9)-.5)*2.;float edge=1.-(.24+.22*zig);float f=step(edge,lu);lc=mix(uLA,uLB,f);lc=mix(lc,uLC,1.-smoothstep(.0,.025,abs(lu-edge)));}break;
  case 19:{lc=lp.y<uLBelt-.25?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.04,.07,abs(lp.y-(uLBelt-.25))));float blk=lside*step(mod(floor(lp.x*.8),3.),.5)*step(uLBelt-.62,lp.y)*step(lp.y,uLBelt-.38);lc=mix(lc,vec3(.95),blk);}break;
  case 20:{vec2 q=floor(vec2(lp.x,lp.z+lp.y*1.3)*1.6);float n=lh(q)*.6+lh(floor(q/2.)+7.)*.4;lc=n<.45?uLA:(n<.72?uLB:uLC);livR=.6;}break;
  case 21:{float y0=uLBelt-.28+.2*(abs(fract(lp.x*.42)-.5)*4.-1.);float dd=abs(lp.y-y0);lc=mix(uLA,uLB,lside*step(dd,.1));lc=mix(lc,uLC,lside*step(.1,dd)*step(dd,.14));}break;
  case 22:{float n=lfbm(vec2(lp.x*.35,lp.y*.6+lp.z*.35));float st=sin(lp.x*2.6+n*7.+abs(lp.z)*.6);lc=mix(uLA,uLB,smoothstep(.55,.62,st)*(.4+.6*smoothstep(.2,.5,n)));}break;
  case 23:{vec2 g2=vec2(lp.x,lp.y+lp.z*.6)*2.2;vec2 c2=fract(g2)-.5;float rr=length(c2),lim=.48*(1.-lu);lc=mix(uLA,uLB,step(rr,lim));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}break;
  case 24:{float a2=fract(lp.x*.32-abs(lp.y-(uLBelt-.25))*.55);float band=step(abs(lp.y-(uLBelt-.25)),.42)*lside;lc=mix(uLA,uLB,band*step(a2,.28));lc=mix(lc,uLC,band*step(.28,a2)*step(a2,.36));}break;
  case 25:{float k2=lu+lp.y/uLBox.w*.35;lc=k2>.62?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.006,.016,abs(k2-.62)));}break;
  case 26:{float t1=abs(lp.y-uLBelt),t2=abs(laz-.55);float pin=(1.-smoothstep(.015,.03,t1))*lside+(1.-smoothstep(.006,.014,t2))*step(.6,lnn.y);lc=mix(uLA,uLB,clamp(pin,0.,1.));}break;
  case 27:{float t3=clamp(lp.y/uLBox.w,0.,1.);lc=mix(uLA,uLB,smoothstep(.15,.9,t3));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt*.5))));}break;
  case 28:{vec2 h=vec2(lp.x,lp.y+lp.z)*2.4;h.y*=1.1547;h.x+=step(1.,mod(h.y,2.))*.5;vec2 f2=abs(fract(h)-.5);float e=max(f2.x*1.5+f2.y,f2.y*2.)*.9;lc=mix(uLB,uLA,smoothstep(.62,.7,e));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt))));livR=.3;}break;
  case 29:{/* molten mozzarella: cheese melting down over the sauce, with drips, bubbles and a glossy lip */
    float dx=lp.x*2.1+lp.z*1.4;float drip=pow(max(0.,sin(dx*1.3+ln2(vec2(dx*.7,2.))*4.)),6.)*.85+lfbm(vec2(dx*.6,5.))*.32;float edge=uLBelt+.18-drip;
    float ch=smoothstep(edge-.02,edge+.02,lp.y);vec2 bq=vec2(lp.x,lp.y+lp.z)*3.2;vec3 bv=lvor(bq);float bub=(1.-smoothstep(.1,.16,bv.x))*step(.55,bv.z);
    vec3 cheese=mix(uLA,uLA*1.12,lfbm(vec2(lp.x,lp.y+lp.z)*1.5))-bub*.18;vec3 sauce=mix(uLB,uLB*.7,lfbm(lp.xz*.9+lp.y));
    lc=mix(sauce,cheese,ch);lc=mix(lc,uLC,(1.-smoothstep(.0,.05,abs(lp.y-edge)))*.8);livR=ch>.5?.22:.38;}break;
  case 30:{/* ember circuit: glowing traces and solder pads on charcoal */
    vec2 g=vec2(lp.x,lp.y+lp.z*.55)*2.6;vec2 c=floor(g),f=fract(g);float r1=lh(c),r2=lh(c+9.7);
    float h=(1.-smoothstep(.04,.07,abs(f.y-.5)))*step(.45,r1),v=(1.-smoothstep(.04,.07,abs(f.x-.5)))*step(r2,.4);float pad=(1.-smoothstep(.13,.18,length(f-.5)))*step(.72,r1*r2+.3);
    float tr=clamp(h+v+pad,0.,1.);vec3 hot=mix(uLB,uLC,smoothstep(.2,.95,lu));lc=mix(uLA*(.8+.4*lfbm(lp.xz*2.)),hot,tr);lc=mix(lc,hot*.35,(1.-smoothstep(.07,.16,min(abs(f.y-.5),abs(f.x-.5))))*.4*step(.45,r1));livR=tr>.5?.3:.55;}break;
  case 31:{/* pepperoni galaxy: nebula clouds, a field of stars and little pepperoni planets */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float n=lfbm(q*.45),n2=lfbm(q*1.2+7.);lc=mix(uLA,uLB,smoothstep(.35,.75,n));lc=mix(lc,uLC,smoothstep(.55,.85,n2)*.7);
    float st=step(.986,lh(floor(q*16.)))*(1.-smoothstep(.0,.35,length(fract(q*16.)-.5)));lc+=vec3(st);
    vec3 pv=lvor(q*.9);float pl=step(.82,pv.z)*(1.-smoothstep(.2,.24,pv.x));vec3 pc=vec3(.78,.16,.1)*(1.-.35*step(.86,lh(floor(q*9.))));lc=mix(lc,pc,pl);livR=.3;}break;
  case 32:{/* basil vortex: a spiral swirl on each flank */
    vec2 c=vec2(uLBox.x+(uLBox.y-uLBox.x)*.48,uLBelt*.8);vec2 d=vec2(lp.x-c.x,(lp.y-c.y)*1.6+lp.z*.15);float r=length(d),a=atan(d.y,d.x);
    float sw=sin(a*4.+r*2.2-lfbm(d*.5)*2.);lc=mix(uLB,uLA,smoothstep(-.2,.2,sw));lc=mix(lc,uLC,(1.-smoothstep(.0,.12,abs(sw-.85)))*.9);lc=mix(lc,uLB*.6,smoothstep(3.5,6.,r)*.5);}break;
  case 33:{/* tiger crust: tapering stripes over a toasted gradient, pale belly */
    float w=lfbm(vec2(lp.x*.55,lp.y*1.3+lp.z*.9));float st=sin(lp.x*3.1+w*6.5+lp.y*.8);float th=.55+.35*smoothstep(0.,uLBox.w,lp.y);
    vec3 base=mix(uLA,uLA*.78,smoothstep(.2,.9,lu));lc=mix(base,uLB,smoothstep(th,th+.06,st));lc=mix(lc,uLC,1.-smoothstep(uLBelt*.35,uLBelt*.55,lp.y));}break;
  default:break;}}
  else if(lpat<67){switch(lpat){
  case 34:{/* shattered prism: faceted shards in a colour sweep with dark seams */
    vec3 v=lvor(vec2(lp.x,lp.y+lp.z*.7)*1.15);vec3 a=mix(uLA,uLB,v.z),b=mix(uLB,uLC,v.z);lc=mix(a,b,smoothstep(.2,.8,lu+v.z*.3-.15));
    lc*=.85+.3*v.z;lc=mix(lc,vec3(.04),1.-smoothstep(.03,.06,v.y-v.x));livR=.12+.25*v.z;}break;
  case 35:{/* topographic: contour lines over banded terrain, every fifth line bold */
    float h=lfbm(vec2(lp.x*.32,(lp.y+lp.z)*.32))*9.;float f=abs(fract(h)-.5);float bold=step(mod(floor(h+.5),5.),.5);
    lc=mix(uLA,uLB,step(.5,fract(h*.5))*.35);lc=mix(lc,uLC,1.-smoothstep(.03+bold*.04,.06+bold*.05,.5-f));livR=.4;}break;
  case 36:{/* racing heritage: rising twin stripes, nose chevrons, checkered tail band */
    float d=uLBelt+.05-lp.y-.5*(1.-lu);float s1=step(0.,d)*step(d,.16),s2=step(.21,d)*step(d,.3);lc=mix(uLA,uLB,(s1+s2)*lside);
    float chev=step(.82,lu)*step(fract(lu*14.-laz*3.),.45)*step(.6,lnn.y);lc=mix(lc,uLC,chev);
    float tail=step(lu,.1)*step(lp.y,uLBelt*.9)*lside;float ck=mod(floor(lp.x*3.)+floor(lp.y*3.),2.);lc=mix(lc,mix(vec3(.95),vec3(.05),ck),tail);
    lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt*.35))));}break;
  case 37:{/* holo foil: iridescent sheen that shifts with the body's curves, fine diagonal grain */
    float hue=fract(lp.x*.07+lnn.y*.55+lnn.x*.35+lnn.z*.2+lfbm(lp.xz*.35)*.45);vec3 rb=lpal(hue);lc=mix(uLA,rb,.62);
    lc*=.92+.08*step(.5,fract((lp.x+lp.y)*9.));lc=mix(lc,uLB,lside*(1.-smoothstep(.015,.03,abs(lp.y-uLBelt))));livR=.1;}break;
  case 38:{/* lava flow: cracked dark rock with glowing seams that run hotter toward the tail */
    vec3 v=lvor(vec2(lp.x,lp.y+lp.z*.6)*.9+lfbm(lp.xz*.6)*.6);float crack=1.-smoothstep(.0,.09+.06*(1.-lu),v.y-v.x);vec3 rock=uLA*(.7+.5*lfbm(vec2(lp.x,lp.y+lp.z)*2.3));
    vec3 hot=mix(uLB,uLC,crack*crack);lc=mix(rock,hot,crack);lc=mix(lc,uLB*.5,(1.-smoothstep(.0,.25,v.y-v.x))*.35);livR=crack>.4?.35:.75;}break;
  case 39:{/* pizza party: pepperoni, olives and basil scattered over melted cheese, crust skirt */
    vec2 q=vec2(lp.x,lp.y+lp.z*.85)*1.35;vec2 c=floor(q),f=fract(q)-.5;f-=vec2(lh(c)-.5,lh(c+4.2)-.5)*.35;float t=lh(c+11.);float r=length(f);
    lc=mix(uLA,uLA*1.08,lfbm(q*2.3));
    if(t<.42){float sp=step(.8,lh(floor(f*9.+c)));lc=mix(lc,mix(uLB,uLB*.72,sp),1.-smoothstep(.27,.29,r));}
    else if(t<.62){lc=mix(lc,vec3(.08),(1.-smoothstep(.11,.13,r))*smoothstep(.05,.07,r));}
    else if(t<.8){vec2 e=vec2(f.x*cos(t*9.)-f.y*sin(t*9.),f.x*sin(t*9.)+f.y*cos(t*9.));float lf=length(e*vec2(1.,2.4));lc=mix(lc,vec3(.16,.48,.15),1.-smoothstep(.2,.22,lf));lc=mix(lc,vec3(.1,.33,.1),(1.-smoothstep(.0,.015,abs(e.y)))*step(lf,.2));}
    lc=mix(lc,uLC*(.85+.3*lfbm(lp.xz*3.)),1.-smoothstep(uLBelt*.32,uLBelt*.42,lp.y));livR=.32;}break;
  case 40:{/* champion filigree: gold scrollwork engraved over gloss black, pinstripes and a gold dust shimmer */
    float sc=sin(lp.x*3.4+sin(lp.y*4.2+lp.z*3.)*1.6)*sin(lp.y*5.1-lp.x*.8+lp.z*2.);float fil=(1.-smoothstep(.0,.07,abs(sc)))*step(uLBelt*.45,lp.y);
    lc=mix(uLA,uLB,fil*.9);float pin=(1.-smoothstep(.012,.025,abs(lp.y-uLBelt)))*lside+(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.45)))*lside;lc=mix(lc,uLC,pin);
    lc+=uLB*lsp(vec2(lp.x,lp.y+lp.z)*38.,.97)*.75;livR=fil>.5?.18:.12;}break;
  case 41:{/* sauce rings: concentric rings spread from a target on each flank and on the nose, breaking into dashes further out */
    float L=uLBox.y-uLBox.x,zs=uLBox.z-abs(lp.z);float r1=length(vec3(lp.x-(uLBox.x+L*.4),lp.y-uLBelt*.62,zs*1.1));float r2=length(vec3(lp.x-(uLBox.x+L*.88),(uLBox.w-lp.y)*.7,lp.z))*1.15;float r=min(r1,r2);
    float w=mix(.46,.14,smoothstep(.8,2.8,r));float f=fract(r*1.3+lfbm(lp.xz*.35)*.18*smoothstep(1.2,3.,r));float a=atan(lp.y-uLBelt*.62,lp.x-(uLBox.x+L*.4));
    float dash=r>2.6?step(.28,fract(a*9.+r*.6)):1.;float ring=max((1.-smoothstep(w-.03,w+.03,f))*dash,1.-smoothstep(.26,.3,r));
    lc=mix(uLA,uLB,ring);lc=mix(lc,uLC,1.-smoothstep(uLBelt*.26,uLBelt*.34,lp.y));livR=.3;}break;
  case 42:{/* spectrum weave: diagonal wavy bands in six colours with fine dark seams */
    float u=(lp.x*.8+lp.y*.55+lp.z*.35)*3.+sin(lp.y*2.3-lp.x*.6+lp.z*1.1)*.8;float id=floor(u),f=fract(u);float h=lh(vec2(id,7.));
    vec3 c=h<.18?uLA:h<.36?uLB:h<.52?uLC:h<.68?vec3(.95,.93,.88):h<.84?vec3(.86,.2,.3):vec3(.07,.08,.12);
    lc=mix(c,vec3(.04),1.-smoothstep(.05,.09,min(f,1.-f)));lc*=.94+.06*step(.5,fract(u*6.));livR=.26;}break;
  case 43:{/* dazzle camo: angular shards in three tones with halftone dots fading off every edge */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7);vec2 r=mat2(vec2(.8,-.6),vec2(.6,.8))*q;float g1=r.x*.45+step(.5,fract(r.y*.38))*.5;float f1=fract(g1);float s1=step(.5,f1);
    float g2=(q.x*.7-q.y*1.3)*.32;float s2=step(.62,fract(g2));float e=min(abs(f1-.5),min(f1,1.-f1));
    lc=mix(uLA,uLB,s1);lc=mix(lc,uLC,s2*(1.-s1));vec2 gd=fract(q*5.5)-.5;float ht=.42*(1.-smoothstep(.0,.22,e));
    lc=mix(lc,uLB,(1.-s1)*(1.-smoothstep(ht-.03,ht,length(gd))));lc=mix(lc,uLA,s1*(1.-s2)*(1.-smoothstep(ht*.8-.03,ht*.8,length(gd))));livR=.3;}break;
  case 44:{/* rainbow sweep: six bands run low along the flank and rise over the rear quarter onto the roof */
    float b0=uLBelt*.12+smoothstep(.66,.04,lu)*uLBelt*.95;float t=(lp.y-b0)/(uLBelt*.85);float on=step(0.,t)*step(t,1.)*lside;
    vec3 rb=lpal(.02+floor(t*6.)/6.*.82)*1.05;lc=mix(uLA,rb,on);lc=mix(lc,uLB,lside*(1.-smoothstep(.02,.04,abs(t+.06)))*step(t,0.));
    lc=mix(lc,uLB,lside*(1.-smoothstep(.02,.04,abs(t-1.06)))*step(1.,t));livR=.24;}break;
  case 45:{/* prism chrome: holographic hex sequins over the top, gloss colour underneath, split by a raked line */
    vec2 h=vec2(lp.x,lp.y+lp.z)*5.;h.y*=1.1547;h.x+=step(1.,mod(floor(h.y),2.))*.5;vec2 id=floor(h);float hv=lh(id);
    vec3 holo=lpal(fract(hv*.35+lnn.y*.6+lnn.x*.4+lp.x*.05))*.72+.3;vec2 fh=abs(fract(h)-.5);holo*=.8+.2*smoothstep(.5,.38,max(fh.x,fh.y));
    float cut=uLBelt*.55+(lu-.5)*1.2;float split=smoothstep(-.03,.03,lp.y-cut);lc=mix(uLA,holo,split);lc=mix(lc,uLB,(1.-smoothstep(.02,.05,abs(lp.y-cut)))*.95);livR=split>.5?.07:.28;}break;
  case 46:{/* paint splash: warped bands of bold colour outlined in black, like a hand-painted art car */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*.55;vec2 w=vec2(lfbm(q+1.3),lfbm(q+7.1));float n=lfbm(q*1.3+w*2.2)*1.15;
    float k=floor(n*7.);vec3 c=k<2.?uLA:k<3.?uLB:k<4.?uLC:k<5.?vec3(.15,.72,.95):vec3(.52,.22,.85);
    float ed=abs(fract(n*7.)-.5);lc=mix(c,vec3(.05),(1.-smoothstep(.42,.47,ed))*.9);lc+=vec3(.08)*lsp(q*60.,.98);livR=.3;}break;
  case 47:{/* shatter drift: clean white with a spreading colour splatter cut by a black crack web */
    vec2 q=vec2(lp.x,lp.y+lp.z*.75);float n=lfbm(q*.5+3.);float sp=smoothstep(.5,.53,n+.12*sin(lp.x*.7));
    vec3 v=lvor(q*1.6);float cr=1.-smoothstep(.0,.04,v.y-v.x);vec3 v2=lvor(q*4.+9.);float cr2=1.-smoothstep(.0,.03,v2.y-v2.x);float zone=smoothstep(.38,.5,n);
    lc=mix(uLA,uLB,sp);lc=mix(lc,uLC,max(cr,cr2*.7)*zone);float drop=step(.93,lh(floor(q*7.)))*(1.-smoothstep(.15,.3,length(fract(q*7.)-.5)))*smoothstep(.3,.45,n);lc=mix(lc,uLB,drop);livR=.3;}break;
  case 48:{/* gold leaf: flaked gold with a dark scaled ribbon snaking down each side */
    float rib=lp.y-(uLBelt*.6+sin(lp.x*.9+lp.z*.3)*.42);float inR=(1.-smoothstep(.3,.33,abs(rib)))*lside;
    vec2 s=vec2(lp.x*3.,rib*6.);s.x+=step(1.,mod(floor(s.y),2.))*.5;vec2 f=fract(s)-vec2(.5,0.);float sc=1.-smoothstep(.04,.09,abs(length(f*vec2(1.,1.4))-.5));
    vec3 gv=lvor(vec2(lp.x,lp.y+lp.z)*13.+lfbm(lp.xz*2.)*.8);vec3 gold=uLA*(.8+.38*gv.z)*(1.-.22*(1.-smoothstep(.0,.06,gv.y-gv.x)));lc=mix(gold,mix(uLB,uLC*.8,sc),inR);lc=mix(lc,uLC,(1.-smoothstep(.0,.025,abs(abs(rib)-.315)))*lside);livR=inR>.5?.4:.16;}break;
  case 49:{/* liquid gold: mirror gold wrap with warped reflection streaks that slide with the body's curvature */
    float w=lfbm(vec2(lp.x*.9+lnn.y*2.,lp.y*1.4+lp.z*.6)+lnn.xz*1.5);float band=sin(w*14.+lp.x*2.2+lnn.y*5.+lnn.x*2.);
    vec3 g=uLA*(.8+.32*band)+uLB*.16*smoothstep(.55,1.,band);lc=mix(g,uLC*1.15,smoothstep(.86,1.,band)*.55);lc=mix(lc,uLA*.35,smoothstep(-.6,-1.,band)*.5);livR=.04+.06*(1.-band);}break;
  case 50:{/* turbo doodle: hand-drawn comic panels in two blues, every panel filled with its own gears, hatching or dots, all inked in black */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7)*1.25;vec3 v=lvor(q);float ed=1.-smoothstep(.0,.075,v.y-v.x);float id=v.z;
    vec3 v2=lvor(q*2.9+5.);float ed2=1.-smoothstep(.0,.07,v2.y-v2.x);vec2 cc=fract(q*2.6)-.5;float ring=1.-smoothstep(.03,.06,abs(length(cc)-.3));float gear=ring*step(.5,fract(atan(cc.y,cc.x)*2.2));
    float dots=1.-smoothstep(.1,.14,length(fract(q*3.4)-.5));float hatch=step(.62,fract((q.x+q.y)*5.));float arrow=step(.6,fract(q.x*2.))*step(abs(fract(q.y*2.)-.5)*2.,fract(q.x*2.)*1.6-.9);
    vec3 base=id<.28?uLA:id<.5?uLB:id<.68?mix(uLA,uLB,.5):id<.86?uLC:vec3(.9,.92,.95);float det=id<.28?dots:id<.5?hatch*.6:id<.68?max(ring,gear):id<.86?arrow:ed2;
    lc=mix(base,vec3(.04),max(ed,det*.95));lc=mix(lc,vec3(.04),ed2*step(.86,id)*.5);lc*=.92+.08*ln2(q*40.);livR=.32;}break;
  case 51:{/* paint riot: six colours of splatter thrown over black, drops, drips and speckle on top of each other */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);lc=uLC*.12;
    for(int i=0;i<6;i++){float fi=float(i);vec2 qq=q*(.85+fi*.16)+vec2(fi*3.1,fi*1.7);vec3 v=lvor(qq);float rad=.17+.2*lh(vec2(fi,v.z));float blob=1.-smoothstep(rad-.04,rad,v.x);
      float col=floor(qq.x*2.)+fi;float dr=step(.82,lh(vec2(col,fi)))*(1.-smoothstep(.05,.09,abs(fract(qq.x*2.)-.5)))*step(fract(qq.y*.45+lh(vec2(col,2.))),.55);
      vec3 pc=i==0?uLA:i==1?uLB:i==2?vec3(.2,.75,.95):i==3?vec3(.55,.22,.85):i==4?vec3(.98,.62,.1):vec3(.3,.8,.35);lc=mix(lc,pc,max(blob,dr*blob*2.));}
    lc+=vec3(.9)*lsp(q*55.,.98);livR=.28;}break;
  case 52:{/* chromatic tide: holographic interference waves that shift hue with the viewing angle, over a fine scan-line raster */
    float ph=lp.x*1.6+sin(lp.y*2.6+lp.z*1.4)*1.4+lfbm(vec2(lp.x,lp.y+lp.z)*.9)*4.;float wave=sin(ph*3.);
    vec3 col=lpal(fract(ph*.08+lnn.y*.25+lnn.x*.2+.6))*1.05;float ras=.78+.22*step(.5,fract((lp.y+lp.z*.3)*22.));
    lc=mix(uLA*.35,col,.55+.45*wave)*ras;lc+=vec3(.28)*smoothstep(.8,1.,wave);livR=.1;}break;
  case 53:{/* candy flake lace: deep candy orange under a repeating lace stencil, buried in rainbow metal flake */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*2.2;vec2 c=fract(q)-.5;float r=length(c);float lace=1.-smoothstep(.03,.06,abs(r-.36));lace=max(lace,(1.-smoothstep(.03,.07,abs(sin(q.x*6.28)*sin(q.y*6.28)*.5)))*.6);
    float leaf=1.-smoothstep(.0,.05,abs(abs(c.x)+abs(c.y)-.28));vec2 fp=vec2(lp.x,lp.y+lp.z)*70.;float flk=lsp(fp,.94);vec3 flc=lpal(lh(floor(fp)+1.));
    lc=mix(uLA,uLB,max(lace,leaf)*.6);lc=mix(lc,flc*1.35,flk);lc*=.85+.3*max(lnn.y,0.);livR=.12;}break;
  case 54:{/* ghost flames: candy burgundy with silver-pink pinstriped flames licking back from the nose */
    float yy=(lp.y+lp.z*.6);float edge=.3+.3*ln2(vec2(yy*2.5,3.))+.14*ln2(vec2(yy*7.,lp.x*2.))+.08*sin(yy*9.);float d=lu-edge;
    float fl=1.-smoothstep(-.01,.02,d);float inner=1.-smoothstep(-.09,-.06,d);float pin=(1.-smoothstep(.0,.015,abs(d)))+(1.-smoothstep(.0,.012,abs(d+.075)));
    float lick=step(.5,fract(yy*3.1+lp.x*.4))*smoothstep(-.25,.0,d)*step(d,0.);vec3 body=mix(uLB,uLC,ln2(vec2(lu*8.,yy*3.)));
    lc=mix(uLA,body,fl*(.55+.45*inner));lc=mix(lc,uLC*1.2,pin);lc=mix(lc,uLA,lick*.35);lc+=vec3(.2)*lsp(vec2(lp.x,lp.y+lp.z)*48.,.96);livR=.1;}break;
  case 55:{/* kandy scroll: royal blue candy with silver pinstripe scrollwork in every panel and a double line along the belt */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.1;vec2 c=fract(q)-.5;float r=length(c),a=atan(c.y,c.x);float sp=1.-smoothstep(.0,.03,abs(fract(r*4.2-a/6.283)-.5)-.0);float cell=lh(floor(q));
    float spiral=sp*(1.-smoothstep(.34,.42,r))*step(.3,cell);float frame=1.-smoothstep(.0,.025,abs(max(abs(c.x),abs(c.y))-.46));
    float belt=(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.52)))*lside+(1.-smoothstep(.012,.025,abs(lp.y-uLBelt*.58)))*lside;
    lc=mix(uLA,uLC,step(.7,cell)*.5);lc*=.85+.3*max(lnn.y,0.);lc=mix(lc,uLB,max(max(spiral,frame*.6),belt));lc+=vec3(.15)*lsp(vec2(lp.x,lp.y+lp.z)*52.,.97);livR=.08;}break;
  case 56:{/* chomp: white body covered in black marker doodles, with a toothy grin and eyes on the nose */
    vec2 q=vec2(lp.x,lp.y+lp.z*.7)*1.4;vec3 v=lvor(q);float ed=1.-smoothstep(.0,.08,v.y-v.x);float fill=step(.8,v.z);vec2 cc=fract(q*2.)-.5;float eye=1.-smoothstep(.1,.13,length(cc));
    float gum=uLBelt*.5;float t=(gum-lp.y)/.55;float teeth=step(abs(fract(lp.x*2.4)-.5)*2.,1.-t)*step(0.,t)*step(t,1.);float mouth=step(0.,t)*step(t,1.6);float nose=smoothstep(.6,.7,lu);
    lc=mix(uLA,uLC,max(ed,fill)*(1.-nose));lc=mix(lc,uLC,step(.9,v.z)*eye*(1.-nose));lc=mix(lc,uLB,mouth*nose);lc=mix(lc,uLA,teeth*nose);lc=mix(lc,uLC,(1.-smoothstep(.0,.03,abs(t)))*nose*lside);
    float ey=1.-smoothstep(.2,.24,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.8),lp.y-uLBelt*.9)));lc=mix(lc,uLC,ey*lside);lc=mix(lc,uLA,(1.-smoothstep(.07,.1,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.82),lp.y-uLBelt*.93))))*lside);livR=.34;}break;
  case 57:{/* liberty streak: gold-green pearl with magenta, violet and cyan prism streaks racing along the flank */
    float y=(lp.y+lp.z*.15)*3.+sin(lp.x*1.3)*.4+lfbm(vec2(lp.x*.6,lp.y*2.))*1.2;float id=floor(y);float f=fract(y);float h=lh(vec2(id,3.));
    vec3 sc=h<.3?uLB:h<.55?uLC:h<.75?vec3(.2,.9,.9):vec3(.95,.3,.75);float len=lh(vec2(id,9.))*.5+.3;float on=step(lu,len+.3*sin(id))*step(len-.5,lu);
    float thin=1.-smoothstep(.0,.1,abs(f-.5)-(.06+.3*lh(vec2(id,5.))));vec3 pearl=uLA*(.9+.25*lnn.y)+vec3(.1,.2,0.)*lnn.x;lc=mix(pearl,sc,thin*on);lc+=vec3(.25)*lsp(vec2(lp.x,lp.y+lp.z)*50.,.96);livR=.12;}break;
  case 58:{/* circuit board: dark green substrate with gold traces, solder pads and glowing chips */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*3.;vec2 c=fract(q);vec2 id=floor(q);float h=lh(id);float tr=h<.5?1.-smoothstep(.05,.09,abs(c.y-.5)):1.-smoothstep(.05,.09,abs(c.x-.5));
    float pad=(1.-smoothstep(.11,.15,length(c-.5)))*step(.6,lh(id+2.));float hole=(1.-smoothstep(.04,.06,length(c-.5)))*step(.6,lh(id+2.));float chip=step(.9,lh(id+5.))*step(max(abs(c.x-.5),abs(c.y-.5)),.3);
    lc=mix(uLA,uLB,max(tr,pad));lc=mix(lc,uLA*.5,hole);lc=mix(lc,vec3(.06),chip);lc=mix(lc,uLC,chip*(1.-smoothstep(.05,.08,abs(c.y-.5)))*step(.5,fract(c.x*8.)));livR=max(tr,pad)>.5?.22:.5;}break;
  case 59:{/* lava flow: cooled black crust split by glowing orange cracks that pulse brighter at the seams */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.4;vec3 v=lvor(q);float cr=1.-smoothstep(.0,.1,v.y-v.x);vec3 v2=lvor(q*2.6+3.);float cr2=1.-smoothstep(.0,.06,v2.y-v2.x);
    float heat=cr*cr+cr2*cr2*.5;lc=mix(uLA*(.7+.3*lfbm(q*3.)),uLB,heat);lc+=uLC*heat*heat*.8;lc*=.9+.1*ln2(q*30.);livR=heat>.4?.5:.28;}break;
  case 60:{/* marble and gold: white marble veined in grey with a second web of gold leaf veins */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float m=lfbm(q*1.1+lfbm(q*2.)*1.5);float vein=1.-smoothstep(.0,.16,abs(sin(m*9.+lp.x)));float vein2=1.-smoothstep(.0,.06,abs(sin(m*14.-lp.y*2.+2.)));
    lc=mix(uLA,uLB,vein*vein*.9+smoothstep(.35,.9,m)*.35);lc=mix(lc,uLC,vein2*step(.5,lfbm(q*.7+9.)));livR=vein2>.5?.12:.25;}break;
  case 61:{/* deep space: nebula clouds in two colours, dust lanes and a field of stars */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float n=lfbm(q*.6);float n2=lfbm(q*1.5+4.);float n3=lfbm(q*3.+8.);lc=mix(uLA,uLB,n)*.9;lc=mix(lc,uLC,smoothstep(.55,.8,n2)*.8);lc=mix(lc,vec3(.02),smoothstep(.6,.75,n3)*.5);
    vec2 sc=floor(q*45.);float st=lsp(q*45.,.975);lc+=vec3(1.)*st*(.55+.45*lh(sc+1.));lc+=uLC*lsp(q*45.+vec2(.5,.27),.995)*2.;livR=.22;}break;
  case 62:{/* viper scale: rows of overlapping scales that fade from belly to spine, with a dark dorsal stripe */
    vec2 h=vec2(lp.x,lp.y+lp.z*.9)*4.2;h.x+=step(1.,mod(floor(h.y),2.))*.5;vec2 f=fract(h)-vec2(.5,0.);float sc=length(f*vec2(1.,1.5));float rim=1.-smoothstep(.42,.5,sc);float hi=1.-smoothstep(.0,.3,length(f-vec2(0.,.25)));
    float t=clamp((lp.y-uLBelt*.2)/(uLBelt*.9),0.,1.);vec3 base=mix(uLA,uLB,t);lc=mix(base*.55,base*(1.+.25*hi),rim);float dorsal=1.-smoothstep(.15,.3,abs(lnn.y-1.));lc=mix(lc,uLC,dorsal*.8*step(.5,fract(lp.x*1.6)));livR=.2;}break;
  case 63:{/* comic pop: ben-day dots, a bold raked colour split and thick black panel outlines */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float cut=uLBelt*.5+(lu-.5)*1.4;float side=smoothstep(-.02,.02,lp.y-cut);float dots=1.-smoothstep(.17,.21,length(fract(q*3.6)-.5));
    vec3 top=mix(uLA,uLB,dots);vec3 bot=mix(uLB,uLC,dots);lc=mix(bot,top,side);float line=1.-smoothstep(.04,.07,abs(lp.y-cut));lc=mix(lc,vec3(.04),line);
    float burst=step(.5,fract(atan(lp.y-uLBelt*.6,lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.35))*4.))*(1.-smoothstep(.9,1.4,length(vec2(lp.x-(uLBox.x+(uLBox.y-uLBox.x)*.35),lp.y-uLBelt*.6))))*lside;lc=mix(lc,vec3(1.),burst*.9);livR=.3;}break;
  case 64:{/* soft serve swirl: three pastel ribbons twisting out of a point on each flank, edged in white */
    float L=uLBox.y-uLBox.x;vec2 c=vec2(lp.x-(uLBox.x+L*.5),lp.y-uLBelt*.5);float a=atan(c.y,c.x),r=length(c);float sw=fract(a/6.283*3.+r*.55+lfbm(c*.5)*.2);float k=floor(sw*3.);float f=fract(sw*3.);
    vec3 col=k<1.?uLA:k<2.?uLB:uLC;lc=mix(col,vec3(1.),1.-smoothstep(.03,.07,min(f,1.-f)));lc*=.9+.1*sin(r*6.);livR=.26;}break;
  case 65:{/* kevlar twill: a woven yellow and black twill with the weave catching the light */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*5.5;float wx=step(.5,fract(q.x)),wy=step(.5,fract(q.y));float weave=abs(wx-wy);float sh=.75+.25*sin(fract(weave>.5?q.x:q.y)*6.283);
    lc=mix(uLA,uLB,weave)*sh;float stripe=(1.-smoothstep(.02,.04,abs(lp.y-uLBelt*.55)))*lside;lc=mix(lc,uLC,stripe);livR=.35;}break;
  case 66:{/* stained glass: lead-lined panes in jewel tones that glow where the light hits */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*1.1;vec3 v=lvor(q);float lead=1.-smoothstep(.0,.06,v.y-v.x);float h=lh(vec2(v.z,1.));vec3 pane=h<.25?uLA:h<.5?uLB:h<.75?uLC:vec3(.95,.8,.2);
    pane*=.75+.35*lfbm(q*4.);lc=mix(pane*(.8+.5*max(lnn.y,0.)),vec3(.05),lead);livR=lead>.5?.5:.08;}
  /* ---- PC-only liveries (67 on), inspired by famous racing liveries and wrap styles; the web shows each one's nearest web livery ---- */break;
  default:break;}}
  else{switch(lpat){
  case 67:{/* powder & orange: a broad orange stripe over the middle edged with navy pinstripes, an orange flash low on the flank */
    float tp=smoothstep(.45,.7,lnn.y);lc=mix(uLA,uLB,tp*(1.-smoothstep(.17,.175+fwidth(laz),laz)));lc=mix(lc,uLC,tp*(lbd(laz,.185,.205)));
    float fy=uLBelt*.42;lc=mix(lc,uLB,lside*lbd(lp.y,fy-.09,fy+.09)*step(.12,lu)*step(lu,.9));lc=mix(lc,uLC,lside*(lbd(lp.y,fy+.11,fy+.135)+lbd(lp.y,fy-.135,fy-.11))*step(.12,lu)*step(lu,.9));livR=.26;}break;
  case 68:{/* riviera tricolore: navy, light blue and red stripes along the flank, sweeping up over the rear and across the bonnet */
    vec3 lb=vec3(.23,.6,.86);float y0=uLBelt*.5+.62*smoothstep(.55,.06,lu);float d=lp.y-y0;
    float tp=smoothstep(.5,.7,lnn.y)*smoothstep(.48,.56,lu);lc=uLA;
    lc=mix(lc,uLB,lside*lbd(d,0.,.1)+tp*lbd(laz,.05,.13));lc=mix(lc,lb,lside*lbd(d,.13,.23)+tp*lbd(laz,.16,.24));lc=mix(lc,uLC,lside*lbd(d,.26,.36)+tp*lbd(laz,.27,.35));livR=.24;}break;
  case 69:{/* royal rally: white over navy, split along a rising line with a double gold pinstripe; navy stripes on the bonnet */
    float cut=uLBelt*.42+(lu-.35)*1.05;float d=lp.y-cut;float lo=1.-smoothstep(-.012,.012,d);float tp=smoothstep(.5,.7,lnn.y)*smoothstep(.5,.58,lu);
    lc=mix(uLA,uLB,lo*lside+tp*lbd(laz,.22,.4));lc=mix(lc,uLC,lside*(lbd(d,.03,.055)+lbd(d,.08,.095)));livR=.24;}break;
  case 70:{/* argyle: orange and green diamonds crossed by thin white lines */
    vec2 q=vec2(lp.x*.85,lp.y+lp.z*.8)*1.15;vec2 r=vec2(q.x+q.y,q.x-q.y);vec2 c=floor(r);float ck=mod(c.x+c.y,2.);vec2 fr=fract(r);
    float e=min(min(fr.x,1.-fr.x),min(fr.y,1.-fr.y));float ew=fwidth(e);lc=mix(uLA,uLB,ck);lc*=.92+.08*smoothstep(.0,.3,e);
    float ln=max(lbd(fr.x,.49,.51),lbd(fr.y,.49,.51));lc=mix(lc,uLC,ln*.85);livR=.3;}break;
  case 71:{/* tricolore shards: green and red chevrons raking back from the nose over a white body */
    float k=lu*1.7+mix(laz,lp.y/uLBox.w,abs(lnn.z))*.75;lc=mix(uLA,uLB,lbd(k,1.,1.2));lc=mix(lc,uLC,lbd(k,1.26,1.46));lc=mix(lc,uLB*.85,lbd(k,1.52,1.58));livR=.26;}break;
  case 72:{/* colour block: bold raked panels in six colours with thin cream seams */
    float k=lu*4.2+lp.y/uLBox.w*1.3+laz*.5;float id=floor(k),f=fract(k);vec3 c=id<1.?uLA:id<2.?uLB:id<3.?uLC:id<4.?vec3(.84,.14,.12):id<5.?vec3(.13,.62,.9):vec3(.08,.08,.1);
    lc=mix(c,vec3(.9,.88,.82),1.-smoothstep(.0,.02+fwidth(f)*1.5,min(f,1.-f)));livR=.26;}break;
  case 73:{/* pleiades: deep blue with a cluster of six white stars on each flank and a gold pinstripe */
    float L=uLBox.y-uLBox.x,u0=L*.05;vec2 c=vec2(uLBox.x+L*.36,uLBelt*.62);vec2 q=(vec2(lp.x*(lp.z>0.?1.:-1.)-c.x*(lp.z>0.?1.:-1.),lp.y-c.y))/u0;
    float st=lstar5(q,1.,.42);st=min(st,lstar5(q-vec2(2.5,1.1),.62,.42));st=min(st,lstar5(q-vec2(4.2,-.1),.55,.42));st=min(st,lstar5(q-vec2(2.1,-1.5),.5,.42));
    st=min(st,lstar5(q-vec2(3.8,-1.8),.45,.42));st=min(st,lstar5(q-vec2(5.6,1.),.42,.42));float sw=max(fwidth(st),.01);
    lc=uLA*(.88+.22*smoothstep(0.,uLBox.w,lp.y));lc=mix(lc,vec3(.94,.94,.92),lside*(1.-smoothstep(-sw,sw,st)));lc=mix(lc,uLC,lside*lbd(lp.y,uLBelt*.27,uLBelt*.31));livR=.22;}break;
  case 74:{/* butcher chart: pink, the body divided into cuts by dashed lines */
    float L=uLBox.y-uLBox.x;float y=lp.y+lp.z*.3;float best=1e3,along=0.;
    for(int i=0;i<5;i++){float fi=float(i);float x0=uLBox.x+L*(.14+fi*.18)+sin(y*1.7+fi*2.)*.03*L;float d=abs(lp.x-x0);if(d<best){best=d;along=y;}}
    float hy=abs(lp.y-uLBelt*.62-.15*sin(lp.x*.9));if(hy<best){best=hy;along=lp.x;}
    float dash=lbd(fract(along*2.4),.0,.6);float ln=(1.-smoothstep(.02,.02+fwidth(best)*1.5,best))*dash;
    lc=mix(uLA*(.94+.08*lfbm(lp.xz*.8+lp.y)),uLB,ln);livR=.34;}break;
  case 75:{/* flower power: big swirly flowers in two colours on lilac */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*.9;vec2 id=floor(q),f=fract(q)-.5;f+=vec2(lh(id)-.5,lh(id+3.)-.5)*.3;float a=atan(f.y,f.x)+lh(id+7.)*6.;float r=length(f);
    float pet=.26+.11*cos(a*5.);float fl=1.-smoothstep(pet-.012-fwidth(r),pet+.012+fwidth(r),r);float cen=1.-smoothstep(.07,.09,r);vec3 pc=lh(id+1.)<.5?uLB:uLC;
    lc=uLA*(.92+.1*ln2(q*3.));lc=mix(lc,pc*.85,(1.-fl)*(1.-smoothstep(.0,.05,abs(sin(lfbm(q*.7)*9.+q.x*2.))))*.55);
    lc=mix(lc,mix(pc,pc*.78,smoothstep(-.2,1.,sin(a*2.+r*14.))*.5),fl);lc=mix(lc,vec3(.96,.82,.2),cen);livR=.3;}break;
  case 76:{/* graph paper: a fine grid, a bold line every fourth, and long red construction lines */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9);lc=uLA;lc=mix(lc,mix(uLA,uLB,.55),lgr(q*4.,.03));lc=mix(lc,uLB,lgr(q,.022));
    float dg=fract((q.x+q.y*1.6)*.11);lc=mix(lc,uLC,lbd(dg,.49,.51)*.9);livR=.4;}break;
  case 77:{/* synthwave: a striped sunset sun on each flank over a neon grid, the sky deepening upward */
    float L=uLBox.y-uLBox.x;vec2 sc=vec2(uLBox.x+L*.5,uLBelt*.74);float R=L*.16;vec2 d=vec2(lp.x-sc.x,lp.y-sc.y);float r=length(d);
    vec3 sky=mix(uLA,uLA*.3,smoothstep(uLBelt*.5,uLBox.w,lp.y));vec3 sun=mix(uLC,uLB,smoothstep(-R,R,d.y));
    float cut=step(d.y,0.)*lbd(fract(d.y/R*5.+(d.y/R)*(d.y/R)*1.6),.0,.38);float sn=(1.-smoothstep(R-.02-fwidth(r),R+.02+fwidth(r),r))*(1.-cut)*lside;
    lc=mix(sky,sun,sn);lc+=uLB*.22*(1.-smoothstep(R,R*1.7,r))*lside*(1.-sn);
    float gy=uLBelt*.44;float below=smoothstep(gy+.01,gy-.01,lp.y);float yy=max((gy-lp.y)/gy,0.);
    float gl=max(lbd(fract(.55/(yy+.08)),.0,.08),lbd(fract((lp.x-sc.x)/(yy+.18)*.32),.0,.08))*smoothstep(.0,.08,yy);
    lc=mix(lc,mix(uLA*.25,vec3(.25,.95,1.),gl),below);livR=.22;}break;
  case 78:{/* highland tartan: a woven sett in red, green and navy with gold and cream overchecks */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*.5;vec3 cx=ltc(q.x),cy=ltc(q.y);float tw=sin((q.x+q.y)*230.)*(1.-clamp(fwidth(q.x)*230.*.5,0.,1.));
    lc=(cx+cy)*.5*(1.+.07*tw);livR=.62;}break;
  case 79:{/* houndstooth: black and cream, with the toothed diagonal checks */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*1.9;vec2 f=fract(q);vec2 h=step(.5,f);float w=max(fwidth(q.x)*2.,.002);
    float dg=fract((f.x-f.y)*4.);float st=smoothstep(.5-w*4.,.5+w*4.,dg);float v=h.x==h.y?h.x:st;lc=mix(uLA,uLB,v);livR=.55;}break;
  case 80:{/* leopard: broken rosettes with darker centres on gold, and loose spots between */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*2.1+lfbm(lp.xz*.8)*.4;vec3 v=lvor(q);float ring=1.-smoothstep(.06,.1+fwidth(v.x),abs(v.x-.3));float brk=step(.38,ln2(q*4.5+v.z*9.));
    float inner=1.-smoothstep(.18,.28,v.x);vec2 sq=q*1.8+.3;float sp=(1.-smoothstep(.09,.12,length(fract(sq)-.5)))*step(.72,lh(floor(sq)))*step(.42,v.x);
    lc=uLA*(.9+.14*lfbm(q));lc=mix(lc,uLB,inner*.55);lc=mix(lc,uLC,max(ring*brk,sp));livR=.42;}break;
  case 81:{/* zebra: wavy black stripes that split and taper */
    float w=lfbm(vec2(lp.x*.3,lp.y*.9+lp.z*.5))*3.;float k=sin((lp.x*1.1+lp.y*.5)*3.2+w*2.5+sin(lp.y*2.+lp.z)*1.2);float th=.1*sin(lp.x*.7)+lfbm(lp.xz*1.3)*.3-.1;
    float aa=max(fwidth(k)*1.2,.001);lc=mix(uLA,uLB,smoothstep(th-aa,th+aa,k));livR=.4;}break;
  case 82:{/* tie-dye: a rainbow spiral from the middle of each flank with crinkle lines */
    float L=uLBox.y-uLBox.x;vec2 c=vec2(uLBox.x+L*.45,uLBelt*.55);vec2 d=vec2(lp.x-c.x,(lp.y-c.y)*1.3+lp.z*.3);float r=length(d),a=atan(d.y,d.x);
    float s=a/6.2832+r*.35+lfbm(d*1.5)*.25;vec3 col=mix(lpal(fract(s)),vec3(.9),.1);float cr=1.-smoothstep(.0,.12,abs(sin(a*12.+lfbm(d*3.)*6.)));
    lc=mix(col,col*1.15+.06,cr*.35)*(.92+.08*ln2(d*6.));livR=.5;}break;
  case 83:{/* woodie wagon: walnut panels framed in pale ash along the flanks, a cream body above */
    float L=uLBox.y-uLBox.x;float y0=uLBelt*.25,y1=uLBelt*.95;float zone=lside*step(y0,lp.y)*step(lp.y,y1)*step(.08,lu)*step(lu,.86);
    float gr=lfbm(vec2(lp.x*.25,lp.y*6.))*.6+ln2(vec2(lp.x*.8,lp.y*28.))*.4;vec3 wood=mix(uLB*.75,uLB*1.15,gr)*(.92+.08*sin(lp.y*90.+gr*8.));
    float px=fract((lp.x-uLBox.x)/(L*.26));float frame=zone*clamp(lbd(lp.y,y0,y0+.12)+lbd(lp.y,y1-.12,y1)+lbd(px,.0,.035)+lbd(px,.965,1.),0.,1.);
    lc=mix(uLA,wood,zone);lc=mix(lc,uLC*(.9+.2*gr),frame);livR=zone>.5?.5:-1.;}break;
  case 84:{/* pixel dissolve: a checkered nose that breaks up into scattered squares down the body */
    vec2 q=vec2(lp.x,lp.y+lp.z)*2.6;vec2 id=floor(q);float ck=mod(id.x+id.y,2.);float keep=step(lh(id+1.3),smoothstep(.2,.85,lu));vec2 f=fract(q);float w=fwidth(q.x)*1.5+.02;
    float sq=smoothstep(.0,w,f.x)*smoothstep(1.,1.-w,f.x)*smoothstep(.0,w,f.y)*smoothstep(1.,1.-w,f.y);
    lc=mix(uLA,ck>.5?uLB:uLC,keep*mix(1.,sq,1.-smoothstep(.75,.9,lu)));livR=.3;}break;
  case 85:{/* splinter camo: angular shards in four tones with rain-streak dashes */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*.5;float g1=fract(dot(q,vec2(.8,.6))*1.3+ln2(q*.5)*.2),g2=fract(dot(q,vec2(-.4,.92))*1.1+.3);
    float a1=lbd(g1,.5,1.),a2=lbd(g2,.55,1.);float k=a1+a2*2.;vec3 c=mix(mix(uLA,uLB,a1),mix(uLC,mix(uLB,uLC,.5)*.8,a1),a2);
    float rn=lbd(fract(q.x*28.),.0,.45)*lbd(fract(q.y*6.+lh(vec2(floor(q.x*28.),1.))),.0,.4);lc=mix(c,uLC*.55,rn*.45*lbd(fract(dot(q,vec2(.97,-.25))*.9+.7),.6,1.));livR=.62;}break;
  case 86:{/* great wave: curling woodblock waves along the lower body, foam claws on the crests, a pale sky */
    float x=lp.x*.9+lp.z*.3;float h=uLBelt*.55+.35*sin(x*1.3)+.18*sin(x*2.9+1.)+lfbm(vec2(x*.8,1.))*.3;float d=lp.y-h;
    float body=1.-smoothstep(-.012-fwidth(d),.012+fwidth(d),d);float bands=lbd(fract((h-lp.y)*5.+sin(x*4.)*.2),.5,1.);vec3 sea=mix(uLA,uLC,bands*.6+smoothstep(.0,-1.,d)*.3);
    float crest=lbd(d,-.08,.0);float claw=(1.-smoothstep(.06,.1,length(fract(vec2(x*3.,d*6.))-.5)))*step(-.25,d)*step(d,.05)*step(.5,fract(x*.7));
    vec3 sky=mix(vec3(.86,.8,.68),uLB,smoothstep(uLBelt,uLBox.w,lp.y)*.6);lc=mix(sky,sea,body);lc=mix(lc,vec3(.9,.88,.82),clamp(crest+claw*body,0.,1.));livR=.35;}break;
  case 87:{/* kintsugi: soft black glaze mended with veins of gold */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8)*.9+lfbm(lp.xz*.7)*.5;vec3 v=lvor(q);float e=v.y-v.x;float cr=1.-smoothstep(.018,.03+fwidth(e)*1.5,e);
    vec3 v2=lvor(q*2.3+5.);float e2=v2.y-v2.x;float cr2=(1.-smoothstep(.01,.02+fwidth(e2)*1.5,e2))*step(.6,lfbm(q*.8+3.));
    float g=max(cr,cr2*.8);lc=uLA*(.9+.15*lfbm(q*3.));lc=mix(lc,uLB*(.85+.3*ln2(q*20.)),g);livR=g>.5?.16:.7;}break;
  case 88:{/* damascus steel: folded layers of light and dark steel flowing over the body */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float w=lfbm(q*.6)*3.+lfbm(q*1.7+4.);float l=sin((q.y*3.+sin(q.x*1.3+w)*1.2+w)*6.);float aa=fwidth(l);
    lc=mix(uLA,uLB,smoothstep(-.3-aa,.3+aa,l));lc=mix(lc,uLC,smoothstep(.85,1.,l)*.6);livR=.18+.14*smoothstep(-.3,.3,l);}break;
  case 89:{/* northern lights: green and violet curtains rising from the belt into a starry night */
    vec2 q=vec2(lp.x,lp.y+lp.z*.6);float cx=q.x*.7+lfbm(vec2(q.x*.3,1.))*2.;float cur=pow(abs(sin(cx*2.+lfbm(q*.5)*3.)),3.);float hg=smoothstep(uLBelt*.3,uLBox.w*.9,lp.y);
    vec3 c=mix(uLB,uLC,hg);float rays=.6+.4*ln2(vec2(cx*9.,q.y*.5));lc=uLA*(.7+.3*(1.-hg));lc+=c*cur*rays*smoothstep(1.,.1,hg)*1.1;lc+=vec3(.9)*lsp(q*30.,.982)*hg;livR=.24;}break;
  case 90:{/* cherry blossom: dark branches heavy with pink blossom over plum, petals drifting */
    vec2 q=vec2(lp.x,lp.y+lp.z*.8);float br=abs(lp.y-(uLBelt*.7+sin(lp.x*.8)*.4+lfbm(vec2(lp.x*.6,2.))*.5));float bw=.05+.04*sin(lp.x*3.);float branch=1.-smoothstep(bw,bw+.015+fwidth(br),br);
    vec2 g=q*2.2;vec2 id=floor(g),f=fract(g)-.5;f-=vec2(lh(id)-.5,lh(id+3.)-.5)*.4;float has=step(.35,lh(id+9.))*(1.-smoothstep(.4,1.,br));float a=atan(f.y,f.x)+lh(id)*6.;float r=length(f);
    float pet=.2+.09*abs(cos(a*2.5));float bl=(1.-smoothstep(pet-.015,pet+.015,r))*has;float cen=(1.-smoothstep(.04,.06,r))*has;
    vec2 pq=q*3.7+.3;float petal=(1.-smoothstep(.05,.07,length((fract(pq)-.5)*vec2(1.,1.8))))*step(.88,lh(floor(pq)));
    lc=uLA*(.85+.2*lfbm(q*.5));lc=mix(lc,uLC,branch);lc=mix(lc,uLB*(.9+.12*cos(a*5.)),max(bl,petal));lc=mix(lc,vec3(.95,.82,.4),cen);livR=.3;}break;
  case 91:{/* halftone fade: one colour fades into the other through growing dots, with a thin stripe low on the flank */
    vec2 q=vec2(lp.x,lp.y+lp.z*.9)*3.2;vec2 r=mat2(vec2(.707,.707),vec2(-.707,.707))*q;float t=smoothstep(.15,.85,lu+(lp.y/uLBox.w-.5)*.25);float rad=t*.75;
    float d=length(fract(r)-.5);float w=max(fwidth(d),.002);lc=mix(uLB,uLA,1.-smoothstep(rad-w,rad+w,d));lc=mix(lc,uLC,lside*lbd(lp.y,uLBelt*.34,uLBelt*.4));livR=.26;}break;
  case 92:{/* pastel drift: a long two-tone swoosh sweeping up the flank, edged in a darker line */
    float x=lu;float s1=uLBelt*.3+x*x*uLBelt*.95;float s2=s1+.18+x*.28;float d1=lp.y-s1,d2=lp.y-s2;
    lc=mix(uLA,uLB,lside*smoothstep(-.012,.012,d1)*(1.-smoothstep(-.012,.012,d2)));lc=mix(lc,uLC,lside*(lbd(d1,-.035,0.)+lbd(d2,0.,.035)));
    lc=mix(lc,uLB,smoothstep(.5,.7,lnn.y)*lbd(laz,-.01,.12)*smoothstep(.3,.5,lu));livR=.3;}break;
  case 93:{/* speed lines: streaks of two colours trailing back from the nose, thicker toward the front */
    float y=lp.y+lp.z*.2;float id=floor(y*9.);float f=fract(y*9.);float len=.25+.55*lh(vec2(id,4.));float on=smoothstep(1.-len-.01,1.-len+.01,lu);
    float th=.06+.26*lh(vec2(id,7.))*smoothstep(1.-len,1.,lu);float ln=(1.-smoothstep(th,th+fwidth(f)*1.5+.01,abs(f-.5)))*on;
    lc=mix(uLA,lh(vec2(id,2.))<.5?uLB:uLC,ln);livR=.25;}break;
  default:break;}}
  if(uLNum>-.5&&abs(lnn.z)>.6){
    /* PC: the race number in one of six designs, its own number per livery (web: always the white roundel with the driver's number) */
    float sdn=lp.z>0.?1.:-1.;vec2 d=vec2((lp.x-uLNumPos.x)*sdn,lp.y-uLNumPos.y);int ns=int(uLNumS+.5);float nv=uLNumV>.5?uLNumV:uLNum+1.;float two=step(9.5,nv);
    vec3 paper=vec3(.92,.91,.88),ink=vec3(.06);
    if(ns==0||ns==2){float pd=length(d)-.6;float aa=max(fwidth(pd),.004);float pl=1.-smoothstep(-aa,aa,pd),rg=1.-smoothstep(-aa,aa,pd-.12);
      vec3 bg=ns==2?vec3(.07,.07,.08):paper;vec3 fg=ns==2?paper:ink;lc=mix(lc,ns==2?paper:uLB,rg);lc=mix(lc,bg,pl);
      float a=lnumA(d/mix(1.2,.95,two),nv)*pl;lc=mix(lc,fg,a);}
    else if(ns==1||ns==4){vec2 q=ns==4?d/vec2(.78,.55):d/vec2(.6,.6);float pd=ns==4?(length(q)-1.)*.5:(length(max(abs(q)-vec2(.8),0.))-.2)*.6;float aa=max(fwidth(pd),.004);
      float pl=1.-smoothstep(-aa,aa,pd),rg=1.-smoothstep(-aa,aa,pd-.05);lc=mix(lc,uLC*.9,rg);lc=mix(lc,paper,pl);
      float a=lnumA(d/mix(1.15,.92,two),nv)*pl;lc=mix(lc,ink,a);}
    else{float sc=ns==5?2.1:1.45;vec2 q=d/sc;q.x+=q.y*.24;float a=lnumA(q,nv),o=lnumO(q,nv,.045);
      vec3 fill=ns==5?paper:uLB;vec3 edge=ns==5?ink:(dot(uLB,vec3(.3,.59,.11))>.5?uLC*.6:paper);
      float sh=lnumA(q+vec2(-.03,.04),nv);lc=mix(lc,lc*.55,sh*(1.-o)*.8);lc=mix(lc,edge,o);lc=mix(lc,fill,a);}}
  if(abs(lnn.z)>.55){float sd=lp.z>0.?1.:-1.,L=uLBox.y-uLBox.x;
    if(uLDecI.x>-.5){vec2 c0=uLNum>-.5?vec2(uLBox.x+L*.3,uLNumPos.y):uLNumPos;float S=uLDecI.z;vec2 q=vec2((lp.x-c0.x)/S*sd+.5,(lp.y-c0.y)/S+.5);
      if(q.x>0.&&q.x<1.&&q.y>0.&&q.y<1.){vec4 t=texture(uLDec,vec2((uLDecI.x+q.x)/8.,.5-q.y*.5));lc=mix(lc,mix(uLC,uLB,t.r),t.a);}}
    if(uLDecI.y>-.5){vec2 c1=vec2(uLBox.x+L*(uLNum>-.5?.82:.26),uLBelt*.62);/* PC: .82 with a number (at the web .62 it sat on the number) */float S=L*.2;vec2 q=vec2((lp.x-c1.x)/S*sd+.5,(lp.y-c1.y)/(S*.32)+.5);
      if(q.x>0.&&q.x<1.&&q.y>.12&&q.y<.88){q.y=.5+(q.y-.5)*.3;vec4 t=texture(uLDec,vec2((uLDecI.y+q.x)/8.,1.-q.y*.5));lc=mix(lc,mix(uLC*.6,uLB,t.r),t.a*.95);}}}
  /* finish pass (Sharp and Ultra): the paint deepens toward the sills and under the curves, gets a candy-like richness at grazing
     angles, and every colour edge reads as a thin vinyl edge. Ultra adds metallic flake under the clear coat and lifts decal edges. */
  vec3 lvFN=vec3(0.);
  if(uLQ>.5){float span=max(uLBox.w-uLBelt,.4),sill=smoothstep(uLBelt-span*1.15,uLBelt+span*.2,lp.y);
    lc*=mix(.74,1.,sill)*(.84+.16*smoothstep(-.7,.35,lnn.y));
    vec3 lvV=normalize(vViewPosition);float fres=1.-clamp(abs(dot(normalize(vNormal),lvV)),0.,1.);fres*=fres;
    lc=mix(lc,lc*lc*1.55,fres*.55)*(1.-.12*fres);
    float lvE=clamp(length(fwidth(lc))*1.6,0.,1.)*(1.-smoothstep(60.,220.,length(vViewPosition)));lc*=1.-.2*lvE;
    if(uLQ>1.5){vec3 fq=lp*85.;vec3 ci=floor(fq);vec3 fr=fract(sin(vec3(dot(ci,vec3(127.1,311.7,74.7)),dot(ci,vec3(269.5,183.3,246.1)),dot(ci,vec3(113.5,271.9,124.6))))*43758.5453);
      float ffw=length(fwidth(fq)),fk=uLFl*(1.-smoothstep(.9,2.2,ffw)),on=smoothstep(.85,.9,fr.z);float fdt=1.-smoothstep(.26,.34,length(fract(fq)-(.3+.4*fr)));fk*=mix(.35,1.,fdt);on*=fdt;lvFN=(fr*2.-1.)*fk*(.22+1.45*on);lc*=1.+on*fk*.07;lc=mix(lc,lc*lc*1.5,fres*.25);
      float hh=dot(lc,vec3(.299,.587,.114));lvFN.xy+=vec2(dFdx(hh),dFdy(hh))*-1.6*(1.-smoothstep(25.,90.,length(vViewPosition)));}}
  {float wl=dot(lc,vec3(.299,.587,.114));lc*=1.-.24*smoothstep(.6,1.,wl);}
  ALBEDO=COLOR.rgb*lc;
  ROUGHNESS=livR>=0.0?livR:rough;
  // (the PC's flake is finer and gentler than the web's: at full resolution the web's read as grain)
  if(uLQ>1.5)NORMAL=normalize(NORMAL+lvFN*0.12);

	METALLIC = metal;
	CLEARCOAT = coat;
	CLEARCOAT_ROUGHNESS = 0.05;
}
