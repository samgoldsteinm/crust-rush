"""One-off (run 2026-11-13, after web v181): take the four big asset tables out of crust-rush.html and store each asset as
its own file under data/ (tools/tables.py says how and why). Kept as the record of what was done; do not run it again.
It checks itself: the tables read back from data/ must equal the ones that were in the source file, key for key."""
import json, subprocess, sys
sys.path.insert(0, 'D:/crust-rush/source/tools')
import tables
SRC = 'D:/crust-rush/source/crust-rush.html'; GH = 'D:/crust-rush/source/build'
s = open(SRC, encoding='utf-8', newline='').read()
assert 'const PROP_TEX={};' not in s, 'already split'
subprocess.run(['D:/crust-rush/tools/node/node.exe', GH + '/extract.js', SRC], check=True, cwd=GH, stdout=subprocess.DEVNULL)
spans = json.load(open(GH + '/spans.json'))
for name in tables.NAMES:
    D = json.load(open(f'{GH}/{name}.json')); n = tables.save(name, D); B = tables.load(name)
    assert list(B) == list(D), name + ': order'
    for k in D:
        assert B[k] == D[k] and (isinstance(D[k], str) or list(B[k]) == list(D[k])), (name, k)
    print(name, len(D), 'entries ->', n, 'files written; read back identical')
for name in sorted(spans, key=lambda k: -spans[k]['start']):
    a, b = spans[name]['start'], spans[name]['end']
    assert s[a - len(name) - 7:a] == f'const {name}=', name
    s = s[:a] + '{}' + s[b:]
    i = s.index(';', a) + 1; assert s[a:i] == '{};', (name, s[a:i + 20])
    s = s[:i] + f"/* kept as files under data/ ({tables.DIRS[name]}/): tools/tables.py reads and writes them, the build puts the table in here */" + s[i:]
open(SRC, 'w', encoding='utf-8', newline='').write(s)
print('source file is now', round(len(s.encode()) / 1e6, 2), 'MB')
