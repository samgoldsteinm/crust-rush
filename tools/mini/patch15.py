# fifteenth patch (v169), looks only: the user's notes on v168.
# - Motion blur goes back to its original strength (.07; v168 had raised it to .095).
# - With Motion blur on, wind lines rush past instead: two layers of fine pale streaks flowing outward from the middle of the
#   picture, thin and short at cruising speed, more and longer as you go faster. They stay off the middle of the screen.
# - The Neon tracks' rainbow boost streaks are not touched; the wind lines give way to them while they show.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("vec2 st=dv*us*mb*.095*smoothstep(.01,.42,dot(da,da));", "vec2 st=dv*us*mb*.07*smoothstep(.015,.45,dot(da,da));")
rep("    vec3 hue(float h){",
    "    /* one layer of wind lines: K lines round the screen, each with its own speed, length and gaps, flowing outward */\n"
    "    float wind(vec2 q,float K,float sp,float sd){float r=length(q),a=atan(q.y,q.x)*.159155*K,n=fract(sin((floor(a)+sd)*12.9898)*43758.5453),w=1.-abs(fract(a)-.5)*2.;\n"
    "      float run=fract(r*(1.+n)-tm*sp*(.8+n*1.3)+n*7.);return step(.76,n)*smoothstep(.72,1.,w)*smoothstep(0.,.07,run)*(1.-smoothstep(.07,.24+n*.28,run))*smoothstep(.3,.74,r);}\n"
    "    vec3 hue(float h){")
rep("if(spd>.001){vec2 q=(vUv-.5)*vec2(aspect,1.);float r=length(q),an=atan(q.y,q.x),ln=floor(an*48.)",
    "/* wind (Settings > Motion blur): pale lines rushing past, more of them the faster you go; they give way to the Neon tracks' rainbow streaks */\n"
    "   if(mb>.02){vec2 q=(vUv-.5)*vec2(aspect,1.);float wv=smoothstep(.12,1.,mb)*(1.-rbw*spd);c=mix(c,vec3(.9,.95,1.),clamp((wind(q,110.,1.7,3.)*.4+wind(q,190.,2.6,11.)*.3*smoothstep(.45,1.2,mb))*wv,0.,.4));}\n"
    "   if(spd>.001){vec2 q=(vUv-.5)*vec2(aspect,1.);float r=length(q),an=atan(q.y,q.x),ln=floor(an*48.)")
rep("<b>Motion blur</b><small>The edges of the picture streak with speed; your kart and the road ahead stay sharp. Balanced and Ultra.</small>",
    "<b>Motion blur</b><small>The edges of the picture streak with speed and wind lines rush past; your kart and the road ahead stay sharp. Balanced and Ultra.</small>")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
