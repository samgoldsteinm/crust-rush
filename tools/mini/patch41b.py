"""Patch 41b (web v205, with patch 41): the shop's details, and what changed after patch 41's first test drive.
Already made in crust-rush.html by hand after patch 41 (recorded here):
- the toy-room helpers live in the TM module: the shop calls TM.pk / TM.pkReady / TM.paint ..., and sbShopTex makes the texture-pair
  materials itself (woodTex is not exported);
- the cinematic uses the intro's own overlay (#cine: letterbox bars, the name card, Skip; stage.cinema hides the HUD and body.sbshop the
  Sandbox buttons outside it); a tap on it (introSkip) or Enter / Space / Escape skips;
- the kart holds on the bay 2.6 s; the steel is a dark grey paint (as metal it mirrored the dim room and came out black).
This patch: the materials for the details the owner asked for ("add more details inside the mechanic shop, stuff on the walls and stuff
sitting around the shop similar to the shop in the video"): three posters, a safety sign, a clock face, a TV, cones, a tarp. All drawn
here, our own: no real brands.
Run once: py.cmd tools/mini/patch41b.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 41b' not in s, 'already patched'
a = "    mblack:[paint('shop_black','#16171a',.55),60],"
assert s.count(a) == 1
s = s.replace(a, a + r"""/* (patch 41b) the pictures on the walls and the new things about the floor */
    mposter1:[mat('shop_p1',()=>sbShopSign(256,358,(g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#1d2b4a');gr.addColorStop(1,'#b8261d');g.fillStyle=gr;g.fillRect(0,0,w,h);
      g.strokeStyle='rgba(255,255,255,.25)';g.lineWidth=14;g.beginPath();g.moveTo(-20,h*.78);g.bezierCurveTo(w*.3,h*.55,w*.6,h*.95,w+20,h*.6);g.stroke();sbShopMark(g,w/2,h*.36,58);
      g.fillStyle='#fbf3df';g.textAlign='center';g.font='900 34px Arial Black, Arial';g.fillText('PIZZA',w/2,h*.68);g.fillText('GRAND PRIX',w/2,h*.79);g.fillStyle='#f2c21b';g.font='700 18px Arial';g.fillText('MARGHERITA RING \u00b7 SUNDAY',w/2,h*.9);})),100],
    mposter2:[mat('shop_p2',()=>sbShopSign(256,358,(g,w,h)=>{g.fillStyle='#f2c21b';g.fillRect(0,0,w,h);g.fillStyle='#16171a';g.beginPath();g.arc(w/2,h*.42,92,0,7);g.fill();g.fillStyle='#f2c21b';g.beginPath();g.arc(w/2,h*.42,48,0,7);g.fill();
      g.strokeStyle='#16171a';g.lineWidth=7;for(let i=0;i<16;i++){const a=i/16*6.283;g.beginPath();g.moveTo(w/2+Math.cos(a)*70,h*.42+Math.sin(a)*70);g.lineTo(w/2+Math.cos(a)*92,h*.42+Math.sin(a)*92);g.stroke();}
      g.fillStyle='#16171a';g.textAlign='center';g.font='900 38px Arial Black, Arial';g.fillText('GRIP',w/2,h*.82);g.font='700 19px Arial';g.fillText('TYRES THAT STICK LIKE CHEESE',w/2,h*.92);})),100],
    mposter3:[mat('shop_p3',()=>sbShopSign(320,240,(g,w,h)=>{g.fillStyle='#22508f';g.fillRect(0,0,w,h);g.strokeStyle='rgba(255,255,255,.18)';g.lineWidth=1;for(let x=0;x<w;x+=16){g.beginPath();g.moveTo(x,0);g.lineTo(x,h);g.stroke();}for(let y=0;y<h;y+=16){g.beginPath();g.moveTo(0,y);g.lineTo(w,y);g.stroke();}
      g.strokeStyle='#eef4ff';g.lineWidth=3;g.beginPath();g.moveTo(40,150);g.lineTo(90,110);g.lineTo(220,104);g.lineTo(280,140);g.lineTo(280,160);g.lineTo(40,160);g.closePath();g.stroke();for(const x of [85,235]){g.beginPath();g.arc(x,165,26,0,7);g.stroke();g.beginPath();g.arc(x,165,9,0,7);g.stroke();}
      g.fillStyle='#eef4ff';g.font='700 18px Arial';g.fillText('KART No.1 \u00b7 SIDE ELEVATION',20,32);g.font='14px Arial';g.fillText('scale 1:10',20,222);})),100],
    msafety:[mat('shop_saf',()=>sbShopSign(300,200,(g,w,h)=>{g.fillStyle='#f2c21b';g.fillRect(0,0,w,h);g.fillStyle='#16171a';g.fillRect(8,8,w-16,h-16);g.fillStyle='#f2c21b';g.fillRect(14,14,w-28,h-28);
      g.fillStyle='#16171a';g.beginPath();g.moveTo(58,40);g.lineTo(100,112);g.lineTo(16,112);g.closePath();g.fill();g.fillStyle='#f2c21b';g.font='900 56px Arial';g.textAlign='center';g.fillText('!',58,106);
      g.fillStyle='#16171a';g.textAlign='left';g.font='900 30px Arial Black, Arial';g.fillText('SAFETY',112,72);g.fillText('FIRST',112,106);g.font='700 18px Arial';g.fillText('GOGGLES ON IN THE BAY',22,160);})),100],
    mclock:[mat('shop_clock',()=>sbShopSign(256,256,(g,w,h)=>{g.fillStyle='#f4f1ea';g.fillRect(0,0,w,h);g.fillStyle='#16171a';for(let i=0;i<12;i++){const a=i/12*6.283;g.save();g.translate(w/2,h/2);g.rotate(a);g.fillRect(-3,-118,6,i%3?14:26);g.restore();}
      g.lineCap='round';g.strokeStyle='#16171a';g.lineWidth=8;g.beginPath();g.moveTo(w/2,h/2);g.lineTo(w/2+48,h/2-40);g.stroke();g.lineWidth=5;g.beginPath();g.moveTo(w/2,h/2);g.lineTo(w/2-20,h/2-94);g.stroke();g.strokeStyle='#b8261d';g.lineWidth=2;g.beginPath();g.moveTo(w/2,h/2);g.lineTo(w/2+70,h/2+60);g.stroke();})),100],
    mtv:[mat('shop_tv',()=>{const m=sbShopSign(340,196,(g,w,h)=>{g.fillStyle='#0c1a2c';g.fillRect(0,0,w,h);g.strokeStyle='#ff8a1f';g.lineWidth=10;g.beginPath();g.moveTo(30,150);g.bezierCurveTo(90,40,190,190,300,60);g.stroke();
      g.fillStyle='#e0452c';g.fillRect(14,14,58,24);g.fillStyle='#fff';g.font='900 16px Arial';g.fillText('LIVE',24,32);g.font='700 16px Arial';g.fillText('LAP 2/3  \u00b7  P1 PEP',190,182);});m.emissive=new THREE.Color('#ffffff');m.emissiveMap=m.map;m.emissiveIntensity=.55;return m;}),100],
    mcone:[paint('shop_cone','#ff6a1a',.5),60],mtarp:[paint('shop_tarp','#2f6f6a',.85),60],""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 41b applied')
