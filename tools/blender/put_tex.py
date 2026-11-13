"""Put a picture into the game's texture store (PROP_TEX: source/data/tex): a JPEG, or a PNG if the picture has holes (alpha).
usage: py.cmd tools/blender/put_tex.py <name> <picture file> [max width] [quality]
The game reads it with propTex('<name>'); the build ships it as its own file."""
import base64, io, json, sys
sys.path.insert(0, 'D:/crust-rush/source/tools'); import tables
from PIL import Image
SRC = 'D:/crust-rush/source/crust-rush.html'
name, path = sys.argv[1], sys.argv[2]
maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
q = int(sys.argv[4]) if len(sys.argv) > 4 else 84
src = Image.open(path)
# a picture with holes in it (leaves, grass: anything cut out) is kept as a PNG with its holes; everything else is a JPEG
holes = src.mode in ('RGBA', 'LA') and src.getchannel('A').getextrema()[0] < 250
if holes:
    import numpy as np
    im = src.convert('RGBA')
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    A = np.asarray(im).copy(); solid = A[..., 3] > 128
    A[..., :3][~solid] = A[..., :3][solid].mean(0).astype(np.uint8)        # give the holes the picture's own average colour: left black, they show as dark edges when the picture is drawn small
    im = Image.fromarray(A).quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
else:
    im = src.convert('RGB')
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True)
D = tables.load('PROP_TEX')                             # (the table is files under source/data/tex: tools/tables.py)
D[name] = base64.b64encode(buf.getvalue()).decode()
tables.save('PROP_TEX', D)
print(name, im.size, f'{len(buf.getvalue()) / 1024:.0f} KB')
