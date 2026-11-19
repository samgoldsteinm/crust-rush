"""Patch 96 (web v231): records set before the speed rules changed are marked "Old rules".
The owner (their 1:40.950 on Margherita, Large, no items, Megawatt + Redline + Parafoil, Basil, set on Nov 16; about 1:44.5 under today's
rules: scratch/speedcmp.py): "Just mark it as old rules and any records that came before that one or before the speed change mark as
old rules". The change: web v216 (patch 60, NET_PROTO 118) at 2026-11-17 00:54:34 -0500 = 05:54:34 UTC; the PC's at 06:08:16 UTC
(godot 4ddd3cd).
- RULES_T / RULES_T_PC (ms). recOld(r): a local record set before RULES_T.
- Your own records (crust-recs): an old-rules best still shows, tagged "Old rules"; a finished run under today's rules becomes your
  best even when slower (the old one is kept as .prev and shown under it). The HUD and the track card say "Old-rules best"; the
  finish screen compares only with a best under today's rules.
- The world boards: created_at is read; a run from before the change (RULES_T on web, RULES_T_PC on PC) is tagged "Old rules" and
  dimmed. The order stays by time (the database is not changed).
- PC: pc91 the same (its records' d is in seconds; its board rows).
Run once, after patch 95: tools/py.cmd tools/mini/patch96.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 96' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function loadRecs(){",
    "/* (patch 96) the speed rules changed (patch 60, web v216): records from before are marked old rules */\n"
    "const RULES_T=Date.UTC(2026,10,17,5,54,34),RULES_T_PC=Date.UTC(2026,10,17,6,8,16);const recOld=r=>!!(r&&(r.d||0)<RULES_T);\n"
    "const OLDTAG='<em class=\"oldr\" title=\"Set before the speed rules changed on 17 November\" style=\"font-style:normal;font-size:10px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#1a1210;background:#c2a58c;border-radius:5px;padding:1px 5px;margin-left:6px;white-space:nowrap\">Old rules</em>';\n"
    "function loadRecs(){")
# saving: an old-rules best is not the bar to beat; it is kept as prev
rep("const t=player.finishTime,key=recKey(),recs=loadRecs(),old=recs[key];",
    "const t=player.finishTime,key=recKey(),recs=loadRecs(),old0=recs[key],old=recOld(old0)?null:old0,prevOld=recOld(old0)?{t:old0.t,d:old0.d,dr:old0.dr}:(old0&&old0.prev)||null;/* (patch 96) */")
rep("if(pb){recs[key]={t,d:Date.now(),place:player.place,dr:selected,laps:recLaps.slice(),",
    "if(pb){recs[key]={t,d:Date.now(),prev:prevOld||undefined,place:player.place,dr:selected,laps:recLaps.slice(),")
# HUD and the track card
rep("{const r=loadRecs()[recKey()],e=$('hudPB');if(e){e.hidden=!r;if(r)e.textContent='Best '+fmt(r.t);}}",
    "{const r=loadRecs()[recKey()],e=$('hudPB');if(e){e.hidden=!r;if(r)e.textContent=(recOld(r)?'Old-rules best ':'Best ')+fmt(r.t);}}")
rep("{const r=loadRecs()[m.id+'|'+clsKey];if(r)chips='<em class=\"y\">Best '+fmt(r.t)+'</em>'+chips;}",
    "{const r=loadRecs()[m.id+'|'+clsKey];if(r)chips='<em class=\"y\">'+(recOld(r)?'Old-rules best ':'Best ')+fmt(r.t)+'</em>'+chips;}")
# the records screen
rep("(r?'<span class=\"tm\">'+fmt(r.t)+'</span><span class=\"dt\">'+RACERS[r.dr].name+' · '+fmtDate(r.d)+'</span>'",
    "(r?'<span class=\"tm\">'+fmt(r.t)+'</span><span class=\"dt\">'+RACERS[r.dr].name+' · '+fmtDate(r.d)+(recOld(r)?OLDTAG:'')+(r.prev?' · old rules '+fmt(r.prev.t):'')+'</span>'")
# the world boards
rep("const q='best_runs?select=name,driver,kart,platform,time_ms&map=eq.'", "const q='best_runs?select=name,driver,kart,platform,time_ms,created_at&map=eq.'")
rep("<small>'+lbEsc(r.driver)+' \\u00b7 '+lbEsc(r.kart)+'</small></span><span class=\"tm\">'+fmt(r.time_ms/1000)+'</span></li>'",
    "<small>'+lbEsc(r.driver)+' \\u00b7 '+lbEsc(r.kart)+(lbOld(r)?OLDTAG:'')+'</small></span><span class=\"tm\"'+(lbOld(r)?' style=\"opacity:.6\"':'')+'>'+fmt(r.time_ms/1000)+'</span></li>'")
rep("let lbSeq=0;function lbDraw(){", "/* (patch 96) a world-board run from before the speed change */const lbOld=r=>{const t=Date.parse(r&&r.created_at||'');return isFinite(t)&&t<(r.platform==='pc'?RULES_T_PC:RULES_T);};\nlet lbSeq=0;function lbDraw(){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 96 applied')
