"""Put Apartment Run into crust-rush.html WITHOUT re-injecting the other mini files.
inject_mini.py rebuilds the whole MINI block from tools/mini/*.js, but crust-rush.html has had patches applied to it directly since
(sandbox, battle: patch 40-61), so those copies are older than the page and re-injecting them would undo the patches. This adds only:
  the track's MAPS entry (from tracks.json, by t_apartment.py) at the end of the MINI-MAPS block,
  apartment.js at the end of the MINI block, between its own markers,
  the buildToy branch for look 'apartment'.
Idempotent: running it again replaces what it put in before.
    py.cmd tools/mini/apt_inject.py"""
import json, subprocess, sys
subprocess.check_call([sys.executable, 'D:/crust-rush/source/tools/mini/t_apartment.py'], stdout=subprocess.DEVNULL)
P = 'D:/crust-rush/source/crust-rush.html'
s = open(P, encoding='utf-8', newline='').read()


def js(v):
    if isinstance(v, str): return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, (int, float)): return ('%g' % v) if isinstance(v, float) else str(v)
    if isinstance(v, list): return '[' + ','.join(js(x) for x in v) + ']'
    if isinstance(v, dict): return '{' + ','.join(k + ':' + js(x) for k, x in v.items()) + '}'
    raise TypeError(v)


d = [t for t in json.load(open('D:/crust-rush/source/tools/mini/tracks.json')) if t['id'] == 'apartment'][0]
# 1. the MAPS entry: one line, marked, just before /*MINI-MAPS-END*/
A0, A1 = '/*APT-MAP*/', '/*APT-MAP-END*/'
if A0 in s:
    i = s.index(A0); e = s.index(A1) + len(A1) + 1; s = s[:i] + s[e:]
i = s.index('/*MINI-MAPS-END*/')
s = s[:i] + A0 + ',\n  ' + js(d) + A1 + '\n' + s[i:]
# 2. the code
C0, C1 = '/*APT-CODE*/', '/*APT-CODE-END*/'
code = open('D:/crust-rush/source/tools/mini/apartment.js', encoding='utf-8', newline='').read()
assert all(ord(c) < 0x10000 for c in code)
if C0 in s:
    i = s.index(C0); e = s.index(C1) + len(C1); s = s[:i] + s[e:]
i = s.index('/*MINI-END*/')
s = s[:i] + C0 + '\n' + code + '\n' + C1 + '\n' + s[i:]
# 3. buildToy
a = "else if(def.look==='battle')toyBattle(def);}"
b = "else if(def.look==='battle')toyBattle(def);else if(def.look==='apartment')toyApartment(def);}"
if b not in s:
    assert s.count(a) == 1, s.count(a)
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8', newline='').write(s)
print('apartment injected:', len(d['ctrl']), 'points,', len(code), 'chars of code')
