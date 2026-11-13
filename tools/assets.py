"""The game's asset tables (tools/tables.py) from the command line.
  py.cmd tools/assets.py sizes                 how big each table is, and its largest entries
  py.cmd tools/assets.py drop <name> [...]     remove entries (a model pack or a picture that is no longer used), from whichever table has them
"""
import sys
sys.path.insert(0, 'D:/crust-rush/source/tools')
import tables
cmd = sys.argv[1] if len(sys.argv) > 1 else 'sizes'
if cmd == 'sizes':
    tot = 0
    for n in tables.NAMES:
        D = tables.load(n); size = lambda v: len(v) * 3 // 4 if isinstance(v, str) else sum(size(x) for x in v.values()) if isinstance(v, dict) else 0
        it = sorted(((size(v), k) for k, v in D.items()), reverse=True); t = sum(s for s, _ in it); tot += t
        print(f'{n:11s} {len(D):3d} entries {t / 1e6:6.1f} MB   largest:', ', '.join(f'{k} {s / 1e6:.2f}' for s, k in it[:6]))
    print(f'all four: {tot / 1e6:.1f} MB as files (each asset is its own file: no single file is near GitHub\'s 100 MB limit)')
elif cmd == 'drop':
    for n in tables.NAMES:
        D = tables.load(n); hit = [k for k in sys.argv[2:] if k in D]
        for k in hit: del D[k]; print('dropped', n, k)
        if hit: tables.save(n, D)
