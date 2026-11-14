import sys, os
from PIL import Image
# tile.py <out.jpg> <cols> <file> <file> ...   (files relative to D:/crust-rush/scratch unless absolute; missing ones are left black)
out, cols, fs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
rows = (len(fs) + cols - 1) // cols
s = Image.new('RGB', (640 * cols, 360 * rows))
for i, f in enumerate(fs):
    p = f if os.path.isabs(f) else 'D:/crust-rush/scratch/' + f
    if os.path.exists(p): s.paste(Image.open(p).convert('RGB').resize((640, 360)), ((i % cols) * 640, (i // cols) * 360))
s.save(out if os.path.isabs(out) else 'D:/crust-rush/scratch/' + out, quality=85)
print('tiled', len(fs))
