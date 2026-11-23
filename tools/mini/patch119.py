"""Patch 119 (web v250): split screen, part E: results and the rest (as the PC, tools/mini/pc121.py).
- Results: both players' rows lit, named (P1) and (P2); the title gives both places ("P1 2nd · P2 5th"), a finished cup both
  standings.
- No ghost in split screen (one kart's best lap; two drivers).
- The countdown's numbers keep their size on a half (only the small banners shrink).
Run once, after patch 118: py.cmd tools/mini/patch119.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert "' (P2)'" not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const row=(k,i,right,extra)=>'<li class=\"'+(k===player?'me':'')+'\"><span class=\"pl\">'+(i+1)+'</span><span class=\"sw\" style=\"background:'+k.r.color+'\"></span><span>'+k.r.name+(k===player?' (you)':'')+'</span>",
    "const two=SPLIT.on&&!!player2,me2=two?(player2.place||st.indexOf(player2)+1):0;/* (patch 119: split screen) */\n"
    "  const row=(k,i,right,extra)=>'<li class=\"'+(k===player||two&&k===player2?'me':'')+'\"><span class=\"pl\">'+(i+1)+'</span><span class=\"sw\" style=\"background:'+k.r.color+'\"></span><span>'+k.r.name+(two?(k===player?' (P1)':k===player2?' (P2)':''):k===player?' (you)':'')+'</span>")
rep("if(fin){const cp=order.indexOf(player)+1;try{achCup(cp);}catch(e){}resTitle.textContent=cp===1?'You won the '+CUPS[gp.cup].name+'!':cp+suf(cp)+' in the '+CUPS[gp.cup].name;",
    "if(fin){const cp=order.indexOf(player)+1;try{achCup(cp);}catch(e){}resTitle.textContent=cp===1?'You won the '+CUPS[gp.cup].name+'!':cp+suf(cp)+' in the '+CUPS[gp.cup].name;if(two){const c2=order.indexOf(player2)+1;resTitle.textContent='P1 '+ord(cp)+' \\u00b7 P2 '+ord(c2)+' in the '+CUPS[gp.cup].name;}")
rep("else{resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' \u00b7 '+cl+' class';$('againBtn').textContent='Next race';",
    "else{resTitle.textContent=two?'P1 '+ord(me)+' \\u00b7 P2 '+ord(me2):me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' \u00b7 '+cl+' class';$('againBtn').textContent='Next race';")
rep("else{gb.hidden=true;resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';",
    "else{gb.hidden=true;resTitle.textContent=two?'P1 '+ord(me)+' \\u00b7 P2 '+ord(me2):me===1?'1st place!':me+suf(me)+' place';")
rep("ghost=null;}ghostRun=null;", "ghost=null;}ghostRun=null;if(SPLIT.on)return;/* (patch 119: no ghost in split screen) */")
rep("body.split #banner.sm,body.split #banner.md{font-size:clamp(22px,5.5vmin,52px)}", "body.split #banner.sm{font-size:clamp(20px,5vmin,48px)}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 119 applied')
# (the results say why a split race is not a record)
s = open(p, encoding='utf-8', newline='').read()
rep("if(lastRun.cheat)return '<span class=\"pbo\">Not counted for records: auto-drive or developer options were on</span>';",
    "if(lastRun.cheat)return '<span class=\"pbo\">'+(SPLIT.on?'Split screen races are not counted for records':'Not counted for records: auto-drive or developer options were on')+'</span>';")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 119b applied')
