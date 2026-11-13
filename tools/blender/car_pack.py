"""Put converted cars (car_convert.py) into the game's CAR_PACKS:  py.cmd tools/blender/car_pack.py <id> [<id> ...]
Each car goes in as `<id>` (body, far model and wheels) and `<id>_hq` (the high-quality body, which the web build
loads late, like every other `_hq` pack). A car that is already there is replaced. The car's definition (BODIES,
BODY_FN, CAR_BODIES, ENG_BODY) is written by hand: see docs/HANDOVER.md, "Adding a car".
"""
import sys, json, re
sys.path.insert(0, 'D:/crust-rush/source/tools'); import tables

SRC = 'D:/crust-rush/source/crust-rush.html'; BL = 'D:/crust-rush/blender/cars'


def entry(k, p): return k + ':{h:' + json.dumps(p['h'], separators=(',', ':')) + ",d:'" + p['d'] + "'}"


def main(ids):
    D = tables.load('CAR_PACKS')                        # (the table is files under source/data/cars: tools/tables.py)
    for cid in ids:
        d = json.load(open(f'{BL}/{cid}/{cid}.json'))
        for k, p in ((cid, d['pack']), (cid + '_hq', d.get('hq'))):
            D.pop(k, None)                                  # a car that is already there is replaced, and goes to the end as before
            if p:
                D[k] = {'h': p['h'], 'd': p['d']}; print(f'{k}: {len(p["d"]) * 3 // 4 // 1024} KB,', ' '.join(f"{x['n']}:{x['i'] // 3}" for x in p['h']['meta']))
    tables.save('CAR_PACKS', D)


if __name__ == '__main__':
    main(sys.argv[1:])
