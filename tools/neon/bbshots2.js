//wait 300 //shot out
(()=>{/* the player loses the single balloon: out */player.bbL=2;player.bal=1;const by=karts.find(k=>k!==player);battleHit(player,by);return {dead:player.bbDead,place:player.bbPlace,left:BB.left,spec:SPEC.on};})()
----
//wait 2600 //shot watching
(()=>({spec:SPEC.on,watching:camT&&camT.r&&camT.r.name,btn:document.getElementById('specRes').textContent.trim(),hud:document.getElementById('bbHud').textContent}))()
----
//wait 400 //shot watching_blimp
(()=>{specCam();return {mode:SPEC.mode,label:document.getElementById('specMode').textContent};})()
----
//wait 300 //shot skipping
(()=>{const t0=BB.t;specExit(true);return {skip:BB.skip,t:Math.round(t0)};})()
----
//wait 20000 //shot results
(()=>({over:BB.over,skip:BB.skip,t:Math.round(BB.t),left:BB.left,results:!document.getElementById('results').hidden,spec:SPEC.on,title:document.getElementById('resTitle').textContent,rows:[...document.querySelectorAll('#resList li')].map(l=>l.textContent)}))()
