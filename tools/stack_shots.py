"""Stacks screenshots for a before/after comparison: stack_shots.py out.png a.png b.png [c.png ...] (one above the other,
each scaled to the first one's width; a label in the corner from the file name)."""
import sys
from PIL import Image, ImageDraw

out, files = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).convert('RGB') for f in files]
w = ims[0].width
ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
c = Image.new('RGB', (w, sum(im.height for im in ims)))
y = 0
for f, im in zip(files, ims):
    c.paste(im, (0, y))
    d = ImageDraw.Draw(c)
    lab = f.replace('\\', '/').split('/')[-1].rsplit('.', 1)[0]
    d.rectangle([0, y, 8 + 7 * len(lab), y + 18], fill=(0, 0, 0))
    d.text((4, y + 3), lab, fill=(255, 255, 255))
    y += im.height
c.save(out)
print(out)
