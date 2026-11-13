"""Put converted cars (car_convert.py) into the game's CAR_PACKS:  py.cmd tools/blender/car_pack.py <id> [<id> ...]
Each car goes in as `<id>` (body, far model and wheels) and `<id>_hq` (the high-quality body, which the web build
loads late, like every other `_hq` pack). A car that is already there is replaced. The car's definition (BODIES,
BODY_FN, CAR_BODIES, ENG_BODY) is written by hand: see docs/HANDOVER.md, "Adding a car".
"""
import sys, json, re

SRC = 'D:/crust-rush/source/crust-rush.html'; BL = 'D:/crust-rush/blender/cars'


def entry(k, p): return k + ':{h:' + json.dumps(p['h'], separators=(',', ':')) + ",d:'" + p['d'] + "'}"


def main(ids):
    s = open(SRC, encoding='utf-8', newline='').read()
    a = s.index('const CAR_PACKS={'); e = s.index('\n', a); line = s[a:e].rstrip('\r')
    assert line.endswith("'}};"), 'the CAR_PACKS line does not end as expected'
    body = line[:-2]                                                  # without the closing "};"
    for cid in ids:
        d = json.load(open(f'{BL}/{cid}/{cid}.json'))
        for k, p in ((cid, d['pack']), (cid + '_hq', d.get('hq'))):
            m = re.search(r'[{,]' + re.escape(k) + r":\{h:", body)
            if m:                                                     # replace: cut the old entry out
                st = m.start() + 1; en = body.index("'}", st) + 2
                body = body[:st] + body[en:].lstrip(',') if body[en:en + 1] == ',' else body[:st].rstrip(',') + body[en:]
            if p:
                body += ',' + entry(k, p); print(f'{k}: {len(p["d"]) * 3 // 4 // 1024} KB,', ' '.join(f"{x['n']}:{x['i'] // 3}" for x in p['h']['meta']))
    s = s[:a] + body + '};' + s[a + len(line):]
    open(SRC, 'w', encoding='utf-8', newline='').write(s)


if __name__ == '__main__':
    main(sys.argv[1:])
