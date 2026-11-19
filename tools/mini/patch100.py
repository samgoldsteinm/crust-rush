"""Patch 100 (web v234): the Chariot's accent as before (patch 98 undone); the dark shapes on its body made symmetrical instead.
The owner: "for the chariot the issue wasnt the accent colors i liked what you had before better. the lime green looked better the
issue for me was the shapes. on one side of the front of the chariot you have a triangle but on the other side its not there ... make
sure all those shapes on the front line up symetrically".
- ACC_SYM is empty (patch 98's relabel no longer runs: all the carbon takes the accent again).
- shapeSym(g,'add') (carGeos, SHAPE_SYM chariot): a carbon triangle with no twin across the body's centre gets one: each paint
  triangle (b_paint) whose mirror point lies on such a carbon piece moves into b_vc as carbon (class 6, its shading kept). 63 triangles
  on the Chariot (scratch/paint/charsym.js compares add / remove).
- PC: from the export (the body as the web builds it).
Run once, after patch 99: tools/py.cmd tools/mini/patch100.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 100' not in s or 'const ACC_SYM={};/* (patch 100' in s
fn = open('D:/crust-rush/scratch/shapesym.txt', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


if 'const ACC_SYM={chariot:1};' in s:
    rep('const ACC_SYM={chariot:1};', "const ACC_SYM={};/* (patch 100: the owner preferred the accent on all its carbon) */")
rep("  if(ACC_SYM[id.replace(/_hq$/,'')])symAcc(g);/* (patch 98) */",
    "  if(ACC_SYM[id.replace(/_hq$/,'')])symAcc(g);/* (patch 98) */\n  if(SHAPE_SYM[id.replace(/_hq$/,'')])shapeSym(g,'add');/* (patch 100) */")
rep("function rotorMark(geo,os,sp){",
    "/* (patch 100) a body's dark shapes made symmetrical: carbon with no twin across the centre gets one from the paint opposite */\nconst SHAPE_SYM={chariot:1};\n" + fn + "\nfunction rotorMark(geo,os,sp){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 100 applied')
