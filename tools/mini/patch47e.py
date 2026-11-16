"""Patch 47e (web v209): the online Sandbox's list of friends no longer covers the item slots.
The owner (a phone picture: "Seared poon ba · here" over both item slots): "the player connection box is covering the items". Patch 46 put
#sbnList at a fixed right:10px, top:118px; on a phone the item slots are bigger and sit right there. Now, each time it is drawn, it is
placed to the LEFT of the item slots (#itemBtn, #itemBtn2: whichever is further left), level with their top, measured from where they
really are; with neither shown it keeps the old corner. Any new HUD box on the right must be placed by the slots the same way.
Run once: py.cmd tools/mini/patch47e.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 47e' not in s, 'already patched'
a = "e.hidden=!SBX||!list.length||state==='menu';if(!e.hidden)e.innerHTML="
assert s.count(a) == 1
s = s.replace(a, "e.hidden=!SBX||!list.length||state==='menu';if(!e.hidden){/* (patch 47e) beside the item slots, never over them */const sr=stage.getBoundingClientRect();let L=null,T=null;"
    "for(const id of ['itemBtn','itemBtn2']){const q=document.getElementById(id);if(!q||q.hidden||!q.offsetParent)continue;const r=q.getBoundingClientRect();if(r.width<4)continue;if(L==null||r.left<L)L=r.left;if(T==null||r.top<T)T=r.top;}"
    "if(L!=null){e.style.right=Math.round(sr.right-L+10)+'px';e.style.top=Math.round(T-sr.top)+'px';e.style.maxWidth=Math.max(120,Math.round((L-sr.left)*.5))+'px';}else{e.style.right='max(10px,env(safe-area-inset-right))';e.style.top='118px';}}"
    "if(!e.hidden)e.innerHTML=")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 47e applied')
