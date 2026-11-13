# twelfth engine patch (v167): easier computer drivers on toy tracks, from the user's play-test ("have not won a single race on
# Bedroom Blitz at 200cc": the tracks are small and fast, so items and specials come close together and a lead is hard to keep).
# On toy tracks, every class: top speed 3% lower, they ease off a little more when ahead of you and push less hard when behind,
# they slow a little more for bends, boost out of fewer bends, wait 1.5 times as long before using an item and 1.8 times as
# long before using a special. Regular and Neon tracks are unchanged.
# Computer drivers only (the host runs them): no change to kart physics or race messages, so the online version stays 104.
# The PC reads these numbers from the exported track (diffs), plus "abw" for the special's wait.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("for(const k in DIFFS0){const d=DIFFS0[k],o=DIFFS[k],h=!!def.neon&&!def.toy;o.skill=d.skill.map(v=>h?v+.025:v);o.corner=d.corner*(h?.85:1);o.boost=Math.min(1,d.boost+(h?.15:0));o.delay=d.delay.map(v=>h?v*.8:v);}",
    "for(const k in DIFFS0){const d=DIFFS0[k],o=DIFFS[k],h=!!def.neon&&!def.toy,t=!!def.toy;/* Neon tracks: sharper rivals. Toy tracks: easier ones (small, fast tracks where items and specials come close together) */o.skill=d.skill.map(v=>h?v+.025:t?v-.03:v);o.ahead=d.ahead*(t?.97:1);o.behind=t?1+(d.behind-1)*.6:d.behind;o.corner=d.corner*(h?.85:t?1.25:1);o.boost=Math.min(1,d.boost+(h?.15:0))*(t?.7:1);o.delay=d.delay.map(v=>h?v*.8:t?v*1.5:v);o.abw=t?1.8:1;}")
rep("k.abWait=(k.abWait==null?1+Math.random()*4:k.abWait)-dt;", "k.abWait=(k.abWait==null?(1+Math.random()*4)*(DIFFS[player?aiKey():'normal'].abw||1):k.abWait)-dt;")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
