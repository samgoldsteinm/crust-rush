"""Put a converted car's check pictures on one sheet: car_sheet.py <id>  ->  D:/crust-rush/blender/cars/<id>/sheet.jpg"""
import sys, os
from PIL import Image

cid = sys.argv[1]; D = f'D:/crust-rush/blender/cars/{cid}'
names = [f'{cid}_check{i}.png' for i in range(4)] + [f'{cid}_hq0.png', f'{cid}_hq1.png', f'{cid}_far0.png']
ims = [Image.open(f'{D}/{n}').convert('RGB') for n in names if os.path.exists(f'{D}/{n}')]
w, h = ims[0].size; cols = 2; rows = (len(ims) + 1) // 2; s = Image.new('RGB', (w * cols, h * rows), (40, 40, 40))
for i, im in enumerate(ims): s.paste(im, ((i % cols) * w, (i // cols) * h))
s.resize((1900, int(1900 * h * rows / (w * cols)))).save(f'{D}/sheet.jpg', quality=88)
