# eighth engine patch (v157): a trap only catches karts on its own level. On multi-level tracks a slick or a fork on
# an upper road used to spin karts driving directly underneath (the hit test compared map positions only).
# Traps now use the same level check thrown items already had (sameLvl). Race rule change: NET_PROTO 102, PC PROTO 102.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
# the road point a trap lies on is remembered with its height (ti is what sameLvl's pGround starts from)
rep("  if(j<0){let bd=1e9;for(let i=0;i<N;i++){const p=track[i],d=(p.x-h.x)**2+(p.y-h.y)**2-(p.ey||0)*.01;if(d<bd){bd=d;j=i;}}}\n",
    "  if(j<0&&h.ti!=null)j=h.ti;/* a lobbed trap brings the road point it was flying over */\n  if(j<0){let bd=1e9;for(let i=0;i<N;i++){const p=track[i],d=(p.x-h.x)**2+(p.y-h.y)**2-(p.ey||0)*.01;if(d<bd){bd=d;j=i;}}}\n  h.ti=j;\n")
# every trap gets its level on its first step, while its owner is still next to it
rep("CURP=null;for(let i=hazards.length-1;i>=0;i--){const h=hazards[i];CURP=h;if(h.born===0&&overPit(h.x,h.y))h.t=0;h.t-=dt;h.born+=dt;",
    "CURP=null;for(let i=hazards.length-1;i>=0;i--){const h=hazards[i];CURP=h;if(h.ey===undefined)h.ey=hazEy(h);if(h.born===0&&overPit(h.x,h.y))h.t=0;h.t-=dt;h.born+=dt;")
rep("/* a friend's own screen reports their trap hits */if((k.x-h.x)**2+(k.y-h.y)**2<200&&k.inv<=0){if(h.olive){",
    "/* a friend's own screen reports their trap hits */if((k.x-h.x)**2+(k.y-h.y)**2<200&&k.inv<=0&&sameLvl(k,h)){/* only karts on the trap's own level */if(h.olive){")
rep("if(p.t<=0){hazards.push({x:p.x,y:p.y,t:30,born:0,owner:p.owner,armed:false,mesh:itemMesh('oil')});", "if(p.t<=0){hazards.push({x:p.x,y:p.y,t:30,born:0,owner:p.owner,armed:false,ti:p.ti,mesh:itemMesh('oil')});")
# a guest decides its own trap hits from the host's copies: the copy is drawn at the trap's height, which gives its level
rep("let kind;if(id[0]==='h'){if(!m.hk||(m.ho===me&&!m.armed))continue;kind=m.hk;}",
    "let kind;if(id[0]==='h'){if(!m.hk||(m.ho===me&&!m.armed))continue;if(MULTI&&Math.abs((k.wy||0)-(m.mesh.position.y-.12))>=18)continue;/* a trap on another level */kind=m.hk;}")
rep("NET_PROTO=101", "NET_PROTO=102")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
