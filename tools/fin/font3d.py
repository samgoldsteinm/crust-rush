"""The 3D letters' font for the cinematic finish (patch 110): Bungee (OFL, godot/assets/fonts) as outlines for THREE.ShapePath.
    py.cmd tools/fin/font3d.py      -> data/font3d.json  {r: units per em, a: ascender, g: {char: [advance, 'm x y l x y q cx cy x y z ...']}}
Printable ASCII only (Bungee draws capitals; lowercase maps to capitals in the game anyway). Integers in font units."""
import json
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

f = TTFont('D:/crust-rush/godot/assets/fonts/Bungee-Regular.ttf'); gs = f.getGlyphSet(); cmap = f.getBestCmap()
out = {'r': f['head'].unitsPerEm, 'a': f['hhea'].ascent, 'g': {}}
R = lambda p: f'{round(p[0])} {round(p[1])}'
for code in range(32, 127):
    ch = chr(code); gn = cmap.get(code)
    if not gn: continue
    pen = RecordingPen(); gs[gn].draw(pen); cmd = []; cur = None
    for op, pts in pen.value:
        if op == 'moveTo': cmd.append('m ' + R(pts[0])); cur = pts[0]
        elif op == 'lineTo': cmd.append('l ' + R(pts[0])); cur = pts[0]
        elif op == 'qCurveTo':
            pts = list(pts)
            if pts[-1] is None: pts = pts[:-1]   # (a contour of off-curve points only: not in Bungee)
            offs, end = pts[:-1], pts[-1]
            for i, c in enumerate(offs):
                e = end if i == len(offs) - 1 else ((c[0] + offs[i + 1][0]) / 2, (c[1] + offs[i + 1][1]) / 2)
                cmd.append('q ' + R(c) + ' ' + R(e)); cur = e
        elif op == 'curveTo': cmd.append('b ' + ' '.join(R(p) for p in pts)); cur = pts[-1]
        elif op in ('closePath', 'endPath'): cmd.append('z')
    out['g'][ch] = [gs[gn].width, ' '.join(cmd)]
json.dump(out, open('D:/crust-rush/source/data/font3d.json', 'w'), separators=(',', ':'))
print(len(out['g']), 'glyphs', len(json.dumps(out)) // 1024, 'KB')
