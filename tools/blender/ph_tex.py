"""Photo-scanned surface textures from Poly Haven (polyhaven.com: every asset there is CC0, free for any use with no
attribution needed) for the toy tracks' large surfaces. No Blender: Python with Pillow.
usage: py.cmd tools/blender/ph_tex.py [key ...]        (no key: all of TEX)
For each key it downloads the scan's colour and normal map (2K JPEG) into D:/crust-rush/scratch/ph, adjusts the colour as
TEX says, writes D:/crust-rush/blender/tex/<key>.jpg and <key>_n.jpg and puts both into the game's texture store as
tex_toy_<key> and tex_toy_<key>_n (put_tex.py). The game reads such a pair with woodTex('<key>', ...) in models.js.
Nothing of the game or its owner is sent: these are plain downloads of public files.

Scale: the scans are of about 2 m of real surface. A toy kart is 7.5 cm long and its camera is a few centimetres up, so at
true scale a scan is a blur under it. The game therefore lays each one smaller than life (the `tile` it is used with in
models.js / mini.js): the lawn reads as a close-cut one, the concrete as finer, and both are sharp from the kart.
"""
import json, os, subprocess, sys, urllib.request
from PIL import Image, ImageEnhance

SP = 'D:/crust-rush/scratch/ph'; OUT = 'D:/crust-rush/blender/tex'; PUT = 'D:/crust-rush/source/tools/blender/put_tex.py'
# key: (Poly Haven id, colour treatment)
TEX = {
    'lawn': ('leafy_grass', 'lawn'),              # grass with fallen leaves: turned to a fresh green
    'concrete': ('brushed_concrete', 'lighter'),  # the garage floor (as scanned it is charcoal under the game's light)
    'paving': ('precast_stone_paving', 'light'),  # the patio
    'planks': ('brown_planks_09', 'none'),        # the fence and the shed
    'gbrick': ('painted_brick', 'whitewash', 2048),   # the garage's walls: painted brickwork (the scan is pale blue; the paint is turned off-white)
    'brick': ('red_brick', 'none'),               # the house's back wall, seen from the garden
    'slate': ('grey_roof_tiles_02', 'none'),      # the roofs
    'bark': ('bark_brown_02', 'none'),            # the trees' trunks and boughs
    'soil': ('brown_mud', 'dark'),                # the flower bed, the earth in the pots
    'asphalt': ('asphalt_02', 'none'),            # the street outside the garage's open door
}


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 10000: return
    req = urllib.request.Request(url, headers={'User-Agent': 'asset-fetch/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f: f.write(r.read())


def main(keys):
    os.makedirs(SP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    for key in keys:
        pid, treat = TEX[key][:2]; size = str(TEX[key][2]) if len(TEX[key]) > 2 else '1024'
        info = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/files/{pid}', headers={'User-Agent': 'asset-fetch/1.0'}), timeout=60).read())
        meta = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/info/{pid}', headers={'User-Agent': 'asset-fetch/1.0'}), timeout=60).read())
        col = info['Diffuse']['2k']['jpg']['url']; nor = info['nor_gl']['2k']['jpg']['url']
        get(col, f'{SP}/{pid}_col.jpg'); get(nor, f'{SP}/{pid}_nor.jpg')
        im = Image.open(f'{SP}/{pid}_col.jpg').convert('RGB')
        if treat == 'lawn':                       # dry leaves and earth to grass: keep the scan's light and dark, push its hue to green
            g = im.convert('L'); gr = Image.merge('RGB', (g.point(lambda v: int(v * .50)), g.point(lambda v: min(255, int(v * 1.0 + 6))), g.point(lambda v: int(v * .30))))
            im = Image.blend(im, gr, .78); im = ImageEnhance.Brightness(im).enhance(.74)   # no lighter: a pale lawn in full sun blooms and hazes the whole picture
        elif treat == 'light': im = ImageEnhance.Brightness(im).enhance(1.25)
        elif treat == 'dark': im = ImageEnhance.Brightness(im).enhance(.8)
        elif treat == 'whitewash':                # keep the scan's light and dark (the chips, the shaded joints), drop its colour, lift it to an off-white paint
            g = im.convert('L'); med = sorted(g.resize((64, 64)).getdata())[2048]
            lut = [min(255, int(232 * (v / med) ** .8)) if v < med else min(255, int(232 + (v - med) * .35)) for v in range(256)]
            g = g.point(lut); im = Image.merge('RGB', (g, g.point(lambda v: int(v * .985)), g.point(lambda v: int(v * .95))))
        elif treat == 'lighter': im = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(1.75)).enhance(.8)
        im.save(f'{OUT}/{key}.jpg', quality=92); Image.open(f'{SP}/{pid}_nor.jpg').convert('RGB').save(f'{OUT}/{key}_n.jpg', quality=92)
        print(key, pid, 'real size mm', meta.get('dimensions'), 'licence CC0')
        subprocess.check_call([sys.executable, PUT, f'tex_toy_{key}', f'{OUT}/{key}.jpg', size, '84'])
        subprocess.check_call([sys.executable, PUT, f'tex_toy_{key}_n', f'{OUT}/{key}_n.jpg', size, '86'])


if __name__ == '__main__':
    main(sys.argv[1:] or list(TEX))
