"""Put a picture into the game's texture store (PROP_TEX in crust-rush.html) as a JPEG.
usage: py.cmd tools/blender/put_tex.py <name> <picture file> [max width] [quality]
The game reads it with propTex('<name>'); the build ships it as its own file."""
import base64, io, json, sys
from PIL import Image
SRC = 'D:/crust-rush/source/crust-rush.html'
name, path = sys.argv[1], sys.argv[2]
maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
q = int(sys.argv[4]) if len(sys.argv) > 4 else 84
im = Image.open(path).convert('RGB')
if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True)
s = open(SRC, encoding='utf-8', newline='').read()
a = s.index('const PROP_TEX=') + len('const PROP_TEX='); e = s.index('\n', a)
lit = s[a:e].rstrip(); assert lit.endswith(';'); lit = lit[:-1]
D = json.loads(lit)
assert json.dumps(D, separators=(',', ':')) == lit, 'the PROP_TEX line would not survive a rewrite unchanged'
D[name] = base64.b64encode(buf.getvalue()).decode()
s = s[:a] + json.dumps(D, separators=(',', ':')) + ';' + s[e:]
open(SRC, 'w', encoding='utf-8', newline='').write(s)
print(name, im.size, f'{len(buf.getvalue()) / 1024:.0f} KB')
