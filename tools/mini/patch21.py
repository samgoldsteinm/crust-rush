"""patch21 (web v187, 2026-11-13): a phone's second toy race had a BLACK track.
On touch devices freeCanvases() shrinks every scenery canvas to 1x1 once its texture is on the graphics chip (iPhone memory).
The toy code keeps its materials, textures and canvases by name between races (TM: MC, TXC, CC in tools/mini/models.js), and
disposeWorld() throws the chip's copy away when a race ends: so the next toy race uploaded the emptied canvas: black.
The fix is in models.js (TM.forget, and can()/tex() redraw an emptied canvas); this patch makes disposeWorld call TM.forget().
Found by the same test (tools/neon/phonetest.py), older: one of the three start gantries (the neon one) made its banner texture
without keepCanvas, so the banner's ONE shared canvas was emptied and every later banner in the session was blank. Fixed in
crust-rush.html by hand the same day: freeCanvases never touches bannerC, drawBanner restores its size, the gantry sets keepCanvas.
Run once: py.cmd tools/mini/patch21.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
a = "m.dispose();});});scene.remove(world);world=null;}"
assert s.count(a) == 1
s = s.replace(a, "m.dispose();});});scene.remove(world);world=null;if(typeof TM!=='undefined'&&TM.forget)TM.forget();/* the toy cache must not hand back what freeCanvases emptied */}")
open(p, 'w', encoding='utf-8', newline='').write(s)
p = 'D:/crust-rush/source/tools/mini/models.js'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep("function can(key,w,h,draw){if(!CC[key]){const c=cnv(w,h);", "/* On phones freeCanvases() (crust-rush.html) shrinks a canvas to 1x1 once its texture is on the graphics chip. Everything kept here by\n   name outlives a race, so: an emptied canvas is drawn again when next asked for, and forget() (called as a world is thrown away) drops\n   every kept material and texture whose canvas was emptied, so the next race makes them afresh. Without this a phone's second toy race\n   had a black track (web v187). */\nconst dead=c=>typeof HTMLCanvasElement!=='undefined'&&c instanceof HTMLCanvasElement&&c.width<=1;\nfunction forget(){let n=0;for(const k in MC){const m=MC[k],ts=[];for(const p in m){const v=m[p];if(v&&v.isTexture)ts.push(v);}if(m.uniforms)for(const p in m.uniforms){const v=m.uniforms[p]&&m.uniforms[p].value;if(v&&v.isTexture)ts.push(v);}\n    if(ts.some(t=>dead(t.image))){for(const t of ts)if(dead(t.image))t.dispose();m.dispose();delete MC[k];n++;}}\n  for(const k in TXC)if(dead(TXC[k].image)){TXC[k].dispose();delete TXC[k];n++;}for(const k in CC)if(dead(CC[k])){delete CC[k];n++;}return n;}\nfunction can(key,w,h,draw){if(!CC[key]||(w>1&&dead(CC[key]))){const c=cnv(w,h);")
rep("function tex(c,key,lin){const k=key+(lin?'|l':'');if(!TXC[k]){TXC[k]=T2(c,1,1,lin);}return TXC[k];}", "function tex(c,key,lin){const k=key+(lin?'|l':'');if(!TXC[k]||(TXC[k].image!==c&&dead(TXC[k].image))){TXC[k]=T2(c,1,1,lin);}return TXC[k];}")
rep("can,tex,mat,std,phy,rng});})();", "can,tex,mat,std,phy,rng,forget});})();")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
