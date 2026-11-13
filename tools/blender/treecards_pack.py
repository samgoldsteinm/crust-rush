"""Lay the pictures treecards.py rendered into the two sheets the game uses, and store them (no Blender: Pillow).
usage: py.cmd tools/blender/treecards_pack.py
  tex_toy_sprays   1024 x 1024: the four leaf sprays, 2 x 2; each fades out toward its edge (the slab it was cut from
                   stops at the picture's frame: a card with leaves chopped off straight would show)
  tex_toy_treefar  1024 x 512: the whole tree from the south (left) and from the east (right)
"""
import subprocess, sys
import numpy as np
from PIL import Image
D = 'D:/crust-rush/blender/treecards'; PUT = 'D:/crust-rush/source/tools/blender/put_tex.py'
sheet = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
yy, xx = np.mgrid[0:512, 0:512]; r = np.hypot(xx - 255.5, yy - 255.5) / 256; fade = np.clip((1.0 - r) / .14, 0, 1)
for i in range(4):
    a = np.asarray(Image.open(f'{D}/spray{i}.png').convert('RGBA').resize((512, 512), Image.LANCZOS)).astype(np.float32)
    a[..., 3] *= fade; a[..., :3] = np.clip(a[..., :3] * 1.25, 0, 255)                # a little lighter: the vertices' shade and tints darken it again
    sheet.paste(Image.fromarray(a.astype(np.uint8)), ((i % 2) * 512, (i // 2) * 512))
sheet.save(f'{D}/sprays.png')
far = Image.new('RGBA', (1024, 512), (0, 0, 0, 0))
for i, n in enumerate(('far_s', 'far_e')): far.paste(Image.open(f'{D}/{n}.png').convert('RGBA').resize((512, 512), Image.LANCZOS), (i * 512, 0))
far.save(f'{D}/far.png')
subprocess.check_call([sys.executable, PUT, 'tex_toy_sprays', f'{D}/sprays.png', '1024'])
subprocess.check_call([sys.executable, PUT, 'tex_toy_treefar', f'{D}/far.png', '1024'])
