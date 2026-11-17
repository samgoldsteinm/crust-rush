"""Patch 57 (web v214): nobody is thrown out of a room's Sandbox while someone else's game is loading.
The owner (two PCs and a third device on the web app, the friend hosting): "after clicking back to sandbox i ended up getting kicked from
the game", and "i was connected on a 3rd device and i didnt join the race and when the race started this 3rd player was kicked right away".
The relay drops a link after 20 s without a word while the game is in state 'race' or 'countdown' (180 s otherwise). Driving in Sandbox
is state 'race' too, so it had the race's short limit; and a game that is loading does not run at all, so neither sends nor reads.
The host loading the race (a toy room can take a while on a slower PC) left the third player, still in Sandbox, 20 s of silence; the
friend loading Sandbox again after Back to Sandbox came out of the load with 20 s gone and dropped the host at once. (Not seen in the
tests here: loads on this PC take well under 20 s.) Now:
- the 20 s limit is for a room race only (NET.cfg); in Sandbox it is 180 s, as in the room;
- time the game itself did not run (a gap of over 3 s between two heartbeats: a load, a frozen tab) is not counted against anyone:
  every link's last-heard time moves on by that gap.
The PC's relay has the same two rules (scripts/webnet.gd).
Run once: py.cmd tools/mini/patch57.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 57' not in s, 'already patched'
a = "beat(){const now=performance.now();for(const m of this.mq)if(now-m.lastIn>10000)m.ping();\n    const lim=(state==='race'||state==='countdown')&&!NET.hostAway?20000:180000;"
assert s.count(a) == 1
s = s.replace(a, "beat(){const now=performance.now();{const gap=now-(this.lastBeat||now);this.lastBeat=now;if(gap>3000)for(const ch of this.chans.values())ch.lastIn+=gap-1000;}/* (patch 57: time this game did not run is no one's silence) */for(const m of this.mq)if(now-m.lastIn>10000)m.ping();\n"
    "    const lim=NET.cfg&&(state==='race'||state==='countdown')&&!NET.hostAway?20000:180000;/* (patch 57: the short limit in a room race only, not Sandbox) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 57 applied')
