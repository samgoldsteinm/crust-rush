"""Turn the all-round sky render (outside.py -- sky -> blender/outside/sky_full.jpg) into the picture the Backyard track's
sky dome carries, and put it into the game's texture store as tex_toy_sky. No Blender: Python with Pillow.
usage: py.cmd tools/blender/sky_tex.py
- keeps the part from straight up down to 5.4 degrees under the horizon (the dome is that much of a sphere: toyYard)
- turns it a quarter round: the render's middle column looks north, the dome's picture starts at east and goes round by
  south, west and north
- levels: the render is exposed for a view from indoors; the dome is shown as it is, so the blue is brought to the game's
  daylight sky and the clouds kept under the bloom threshold
"""
import subprocess, sys
from PIL import Image, ImageChops, ImageEnhance
D = 'D:/crust-rush/blender/outside'
im = Image.open(f'{D}/sky_full.jpg').convert('RGB'); w, h = im.size
im = im.crop((0, 0, w, round(h * .53))); im = ImageChops.offset(im, w // 4, 0)
hz = h // 2 - 3; row = im.crop((0, hz, w, hz + 1))            # under the horizon the render shows the empty world, dark: carry the horizon's own haze on down instead
for y in range(hz + 1, im.size[1]): im.paste(row, (0, y))
gain = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
if gain != 1.0: im = ImageEnhance.Brightness(im).enhance(gain)
im = im.point(lambda v: min(v, 240))                         # nothing in the sky brighter than the bloom threshold
im.save(f'{D}/sky.jpg', quality=90)
subprocess.check_call([sys.executable, 'D:/crust-rush/source/tools/blender/put_tex.py', 'tex_toy_sky', f'{D}/sky.jpg', '4096', '80'])
