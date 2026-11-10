import re
F=open('liv_frag.glsl').read()
B=open('liv_body.glsl').read()
def floats(code):
    # protect: lpat comparisons, for(int ...) headers
    prot={}
    ints0=set(re.findall(r'\bint\s+(\w+)',code))
    def keep(m):
        n=len(prot);k='PROT'+''.join(chr(65+int(d)) for d in str(n))+'X';prot[k]=m.group(0);return k
    code=re.sub(r'for\s*\(int[^)]*\)',keep,code)
    ints=ints0|set(re.findall(r'\bint\s+(\w+)',code))|{'lpat'}
    for nm in re.findall(r'for\s*\(int\s+(\w+)',code):ints.add(nm)
    for nm in ints:
        code=re.sub(r'\b'+nm+r'\s*(==|!=|<=|>=|<|>)\s*-?\d+(?![\w.])',keep,code)
        code=re.sub(r'\bint\s+'+nm+r'\s*=\s*-?\d+(?![\w.])',keep,code)
    # integer literals not part of identifiers or floats
    code=re.sub(r'(?<![\w.])(\d+)(?![\w.\d])',r'\1.0',code)
    # numbers like "8." -> "8.0" (glsl allows, godot too) ; ".5" fine
    for k,v in prot.items():code=code.replace(k,v)
    return code
F2=F.replace('varying vec3 vLivP;varying vec3 vLivN;','')
F2=re.sub(r'uniform [^;]*;','',F2)
F2=floats(F2)
B2=floats(B)
B2=B2.replace('texture2D(','texture(')
def m2(m):
    a=[x.strip() for x in m.group(1).split(',')]
    return 'mat2(vec2(%s,%s),vec2(%s,%s))'%tuple(a) if len(a)==4 else m.group(0)
B2=re.sub(r'mat2\(([^()]*)\)',m2,B2)
B2=B2.replace('diffuseColor.rgb*=lc;','ALBEDO=COLOR.rgb*lc;\n  ROUGHNESS=livR>=0.0?livR:rough;\n  if(uLQ>1.5)NORMAL=normalize(NORMAL+lvFN*0.32);')
head='''shader_type spatial;
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
'''
vert='''
void vertex() {
	vLivP = (liv_xf * vec4(VERTEX, 1.0)).xyz;
	vLivN = mat3(liv_xf) * NORMAL;
}

void fragment() {
	vec3 vViewPosition = -VERTEX;
	vec3 vNormal = NORMAL;
'''
tail='''
	METALLIC = metal;
	CLEARCOAT = coat;
	CLEARCOAT_ROUGHNESS = 0.05;
}
'''
out=head+F2+vert+B2+tail
open('/home/claude/crust-rush-godot/shaders/livery.gdshader','w').write(out)
print(len(out))
