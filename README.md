# Crust Rush — native PC build (Godot 4.7)

The Windows version of Crust Rush, on its own branch. Nothing here affects the web game on `main`.

**Download page:** https://samgoldsteinm.github.io/crust-rush/pc.html (trailer, pictures and the latest download).
Every push builds `CrustRush.exe` (Actions → PC build → Artifacts → CrustRush-Windows) and replaces the public
download, `CrustRush-Windows.zip` on the [`pc` release](https://github.com/samgoldsteinm/crust-rush/releases/tag/pc).

The PC build is a copy of the web game: same tracks, karts, items, menus, look and rules. The tracks, the garage
parts and the soundtrack are exported from the published web game by the **Export tracks** workflow and attached
to the `maps` release; the PC build downloads them from there.

## What it has
- All 17 tracks, single races, the four Grand Prix cups, Reverse, and Last Slice Standing.
- The garage: every body, car, bike, wheel set, glider and livery, with the reward liveries unlocked by achievements.
- Every item (the classics plus the newer ones and the four award items) and every driver's special ability.
- Shortcuts and side routes, loops, the glide canyons, ramps, tricks, drifting and boosts, ported line for line.
- The web game's menus: home, driver, garage, track, Settings (Graphics, Sound, Gameplay, Controls, Items & specials,
  More), Records, Achievements, How to play, Play with friends, pause and results.
- The soundtrack: a song for every track and four menu songs, rendered from the web game's music.
- Your best-run ghost, lap splits against your best, your best time under the clock.
- Keyboard keys you can change in Settings > Controls; cheat codes in Settings > More (UNLOCK, TESTING), as on the web.
- Online races between PCs: one hosts, the others join with the host's address. Settings > More > Network log keeps a
  second-by-second record of your last 6 online races (round trip, lost packets, snapshot flow), with Copy.
- Cross-play with the browser version: Play with friends > **Race with browser friends** joins a room made on a phone
  or browser with its 4-character code, or hosts one they can join, through the same public relay the web game uses.

## Graphics
The picture is matched to the web game's Ultra (lighting, tone mapping, colour grade, bloom, ambient occlusion,
shadows). **Settings > Graphics > PC extras** (on by default on Ultra) goes a step further: shadows reach more than
twice as far in four cascades and soften with distance, a little light bounces between nearby surfaces, textures
stay sharp at a glance and glossy paint reflects a finer sky. Turn it off for the web game's Ultra exactly.

**Settings > Graphics > Finished models** (on by default, Balanced and Ultra) swaps the web game's simple trackside
shapes for finished ones up close: spruces with whorls of drooping boughs that follow each web tree's own outline,
palms with arching fronds folded along the midrib and a ringed trunk, leafy bushes, real stone on the rocks, and
the ground's cheese with depth (the flecks stand up, the specks sink in, it's glossier where it's fresh, with a fine
grain close up). Leaves sway in the wind and let a little light through. Far away the web game's own shapes are
drawn, so nothing changes in the distance. Off draws the web game's shapes everywhere.

The background mountains are part of it too. The far mountain ranges keep the web game's skyline but are rebuilt with
nine times the points, with finer ridges and gullies cut into the high ground and crags from a CC0 cliff texture on
their faces. The ranges the web game paints blue (its stand-in for distance and ice) get real mountain colours
instead: grey-brown rock, snow lying on the flatter faces above a snow line (everywhere on the frozen tracks), a little
scrub low down, with the distance left to the fog. The sculpted mountains (your own mountain model, which the web game
uses at 3,500 points) are rebuilt from the full model's height field with about twenty times the triangles and lit from
a detailed map of its surface; on the frozen tracks they keep their own rock colour under the snow.

Water and buildings are part of it as well. The sea, the lakes, the pools under the glide gaps and the ponds become
real water: waves that calm into the distance, colour that deepens with the depth, the bottom showing through the
shallows with light playing on it, the sky and sun reflected, foam where it meets the shore. Pineapple Lagoon's beach
huts, pier and lighthouse are built again properly (stilts, lap boarding, shingled roofs, porches and railings,
shuttered windows; a braced timber pier with rope rails and lamps; a banded tower on a weathered rock with a gallery
and a glazed lantern room). The glide canyons end in clean crust cliffs. Signs, lit windows and neon glow from the web
game's own pictures.

## Controls
- Keyboard: arrows/A D steer · Space/Down/S drift, brake · X/Enter first item · Z/Q second item · Shift/B keep behind ·
  hold F to look back (and throw backwards) · C/R special · P/Esc pause · F11 full screen.
- Controller: left stick or d-pad · RT gas · LT drift · A/LB first item · B/RB second item · Y special · X look back ·
  Start pause.

## Files
- `scripts/kart.gd` — one kart's physics (web `stepKart`, loops, shortcuts, spin-outs).
- `scripts/race.gd` — the race (web `update0`, `aiInput`, items, abilities, hazards, boxes, standings, Last Slice).
- `scripts/main.gd` — the game scene: camera, lighting, input, Settings, results, online.
- `scripts/view.gd`, `scripts/fx.gd` — drawing karts, items and effects; the particle pools.
- `scripts/hud.gd`, `scripts/menu.gd` — the race HUD and the menus, drawn to match the web game's CSS.
- `scripts/kart_builder.gd` — builds a kart from garage parts and paints its livery.
- `scripts/ach.gd`, `scripts/ghost.gd` — achievements, records, the best-run ghost.
- `scripts/netlog.gd` — the network log of online races.
- `scripts/webnet.gd`, `scripts/mqtt.gd` — cross-play with the browser version: the web game's room codes, relay and
  race messages (version 97), as guest or host.
- `scripts/music.gd`, `scripts/sfx.gd` — the soundtrack and the sound effects (an engine voice per kind of kart body,
  pitched through the gears like the web's: louder when you work it, a soft hum at a steady speed).
- `scripts/track.gd` — track data exported from the web game.
- `scripts/props.gd`, `scripts/hd_ground.gd`, `scripts/hd_mount.gd`, `shaders/foliage.gdshader`, `shaders/mountain*.gdshader`
  — the finished trees, bushes, rocks, ground and background mountains.
- `scripts/hd_water.gd`, `shaders/water.gdshader` — the water. `scripts/hd_set.gd`, `shaders/hd_wood.gdshader` — the
  rebuilt set pieces and the glide canyons' ends. `scripts/hd_surface.gd`, `shaders/relief.gdshader` — the finish on
  plain and pictured scenery. `scripts/hd_kitchen.gd` — the kitchen tracks' room.
- `shaders/` — sky, post grade, livery, bubbles, particles and menu backgrounds.
- `tools/` — the exporters (tracks, garage, soundtrack), run in a browser against the web game; `hd_textures.py`
  (the leaf, frond, bough and bark pictures), `hd_ground.py` (the ground's relief and gloss maps, made in the build),
  `hd_fetch.py` (downloads the CC0 textures), `hd_mount.py` (the mountain's height field, surface and colour from the
  original mountain model).
- `tests/` — headless race (`smoke`), every track (`allmaps`), two-copy online race (`net`), a race against the
  published web game in a browser (`xplay`, both ways round, through `tools/mqtt_broker.py`), screenshots matched step
  for step with the web game's (`shots`), menu screenshots (`menushots`).
- `.github/workflows/pc.yml` — checks, tests and builds on every push. `[quick]` in a commit message skips screenshots and export.
- `.github/workflows/maps.yml` — exports the tracks, garage and soundtrack from the web game (run by hand, or on changes to the tools).
- `.github/workflows/xplay.yml` — the cross-play race, browser hosting and PC hosting, on changes to the cross-play code.
- `.github/workflows/hd.yml` — downloads the CC0 textures from Poly Haven into the `maps` release (`hd.zip`).
- `.github/workflows/trailer.yml` — films a gameplay clip on three tracks with Godot's Movie Maker (`tests/trailer.gd`),
  joins it (`tools/trailer_cut.py`) and attaches `trailer.mp4`, `poster.jpg` and stills to the `pc` release.
- `.github/workflows/ios.yml` — iPhone build, manual only (paused).

## Credits
The web game's credits all carry over. The finished models' bark and stone surfaces are CC0 textures from
[Poly Haven](https://polyhaven.com) (bark_brown_02, bark_willow, rock_boulder_dry and others listed in
`assets/hd/cc0/credits.txt` in the build), used under CC0 with thanks. The leaf, frond, bough and ground maps are
made by this project's own tools. The background mountain is the user's own mountain model at full detail.
