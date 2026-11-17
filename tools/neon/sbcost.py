"""Sandbox's driving distances for the delivery arrow's route (web patch 76, pc76):   py.cmd tools/neon/sbcost.py   (webtest.py serving)
Opens each Sandbox place in turn (sbprobe.py) and runs sbcost.js there: the distance from each gate to each other gate and to the start
line (a road place along the lap, the shorter way; elsewhere straight x1.15). Writes build/sb_cost.json {place: {"a>b": units}} where a, b
are the places the gates lead to ('@flag' the start line). Run it again when a place, its gates or its links change; the table is pasted
into the web (SB_COST, patch 76) and the PC (main.gd SB_COST)."""
import json, re, subprocess, sys
R = 'D:/crust-rush'
html = open(f'{R}/source/crust-rush.html', encoding='utf-8').read()
ids = re.findall(r"(\w+):'", re.search(r"const SB_AREA=\{(.*?)\};", html, re.S).group(1))
house = ['garage', 'kitchen', 'bedroom', 'backyard']
import os
OUT = f'{R}/source/build/sb_cost.json'
out = json.load(open(OUT)) if os.path.exists(OUT) and os.path.getsize(OUT) > 2 else {}   # (resumes: a place already measured is skipped)
for pid in house + [i for i in ids if i not in house]:
    if pid in out:
        continue
    for attempt in range(2):   # (a slow load can time out once)
        r = subprocess.run([f'{R}/tools/py.cmd', f'{R}/source/tools/neon/sbprobe.py', pid, f'{R}/source/tools/neon/sbcost.js'], capture_output=True, text=True, timeout=1200)
        line = next((l.strip() for l in r.stdout.splitlines() if l.strip().startswith(('"{', '{"id"'))), None)
        if line:
            break
    if not line:
        print(pid, 'FAILED', r.stdout[-300:], r.stderr[-300:], flush=True); continue
    d = json.loads(line)
    if isinstance(d, str):
        d = json.loads(d)
    out[d['id']] = d['c']
    print(pid, d['kind'], len(d['c']), flush=True)
    json.dump(out, open(OUT, 'w'), indent=0, sort_keys=True)   # (after each place)
print('SB COST written', len(out), 'places')
