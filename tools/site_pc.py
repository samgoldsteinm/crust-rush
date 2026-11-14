"""Bring the PC Edition page (D:/crust-rush/app/pc.html, kept by hand in the app repository) level with the PC build:
   py.cmd tools/site_pc.py            (then look at it, commit in D:/crust-rush/app and push main)
- the track strip lists every track the PC has, in the menu's order, with a thumbnail made from the game's own menu picture
  (source/data/shots/<id>-h.jpg -> app/pc/img/t-<id>.jpg, 440 x 248);
- the counts and the modes say what the PC build has TODAY: edit HAS below when that changes (Sandbox is not on the PC yet);
- the download's size is read from the release's pc-build.json.
The page's words are replaced by exact match, so the script stops if the page has been reworded by hand."""
import json, os, re, sys, urllib.request
from PIL import Image
APP = 'D:/crust-rush/app'; SHOTS = 'D:/crust-rush/source/data/shots'
HAS = {'battle': True, 'sandbox': False}
TRACKS = [('margherita', 'Margherita Ring'), ('bay', 'Hawaiian Bay'), ('peaks', 'Pepperoni Peaks'), ('frosty', 'Frosty Freezer'), ('basil', 'Basil Boulevard'), ('lagoon', 'Pineapple Lagoon'),
          ('mozz', 'Midnight Mozzarella'), ('burn', 'Freezer Burn Pass'), ('oven', 'Oven Rush Raceway'), ('calzone', 'Calzone Coast'), ('napoli', 'Neon Napoli'), ('glacier', 'Glacier Crust'),
          ('spiral', 'Sauce Spiral'), ('tour', 'Topping Tour'), ('moon', 'Pepper Moon Circuit'), ('peak', 'Frozen Pie Peak'), ('grid', 'Neon Grid Arena'), ('laser', 'Laser Slice Skyway'),
          ('holo', 'Hologram Heights'), ('synth', 'Synthwave Supreme'), ('bedroom', 'Bedroom Blitz'), ('kitchen', 'Kitchen Chaos'), ('garage', 'Garage Overdrive'), ('backyard', 'Backyard Mega Circuit')]
for tid, _ in TRACKS:
    im = Image.open(f'{SHOTS}/{tid}-h.jpg').convert('RGB').resize((440, 248), Image.LANCZOS); im.save(f'{APP}/pc/img/t-{tid}.jpg', quality=82, optimize=True)
p = f'{APP}/pc.html'; s = open(p, encoding='utf-8', newline='').read()
try: mb = json.load(urllib.request.urlopen(urllib.request.Request('https://github.com/samgoldsteinm/crust-rush/releases/download/pc/pc-build.json', headers={'User-Agent': 'asset-fetch/1.0'}), timeout=60))['bytes'] / 1e9
except Exception as e: sys.exit('could not read the PC build\'s size: ' + str(e)[:100])
size = f'About {mb:.1f} GB'


def sub(rx, new, n=1):
    global s
    s, k = re.subn(rx, new, s)
    assert k == n, (rx, k)


sub(r"var T=\[\[.*?\]\];", 'var T=' + json.dumps([list(t) for t in TRACKS], ensure_ascii=False).replace('"', "'") + ';')
sub(r"<h3>\d+ tracks</h3><p>[^<]*</p>", f"<h3>{len(TRACKS)} tracks</h3><p>Single races, five Grand Prix cups, Reverse, Last Slice Standing, where the last kart drops out every lap" + (", and Balloon Battle on its own arena" if HAS['battle'] else "") + (", plus Sandbox: one world to drive freely" if HAS['sandbox'] else "") + ".</p>")
sub(r"<h2>[A-Za-z-]+ <em>tracks</em></h2>", "<h2>Twenty-four <em>tracks</em></h2>")
sub(r"<p>Online races between PCs:[^<]*</p>", "<p>Online races and whole Grand Prix cups with friends on PC or in the browser: one player opens a room, the others join with its four-letter code.</p>")
sub(r"<p>Xbox and other controllers work out of the box\.[^<]*</p>", "<p>Xbox and other controllers work out of the box, with an on-screen pointer in the menus. Keyboard keys can be changed in Settings.</p>")
sub(r"<small>About [0-9.]+ [MG]B · free</small>", f"<small>{size} · free</small>")
sub(r"<small>About [0-9.]+ [MG]B · Windows 10 and 11</small>", f"<small>{size} · Windows 10 and 11</small>")
sub(r"CrustRush-Windows\.zip \(about [0-9.]+ [MG]B\)", f"CrustRush-Windows.zip (about {mb:.1f} GB)")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc.html updated:', len(TRACKS), 'tracks,', size, HAS)
