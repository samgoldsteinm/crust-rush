# Crust Rush — native PC build (Godot 4.7)

The Windows version of Crust Rush, on its own branch. Nothing here affects the web game on `main`.
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
their faces. The sculpted mountains (your own mountain model, which the web game uses at 3,500 points) are rebuilt
from the full model's height field with about twenty times the triangles and lit from a detailed map of its surface.

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
- `scripts/music.gd`, `scripts/sfx.gd` — the soundtrack and the sound effects.
- `scripts/track.gd` — track data exported from the web game.
- `scripts/props.gd`, `scripts/hd_ground.gd`, `scripts/hd_mount.gd`, `shaders/foliage.gdshader`, `shaders/mountain*.gdshader`
  — the finished trees, bushes, rocks, ground and background mountains.
- `shaders/` — sky, post grade, livery, bubbles, particles and menu backgrounds.
- `tools/` — the exporters (tracks, garage, soundtrack), run in a browser against the web game; `hd_textures.py`
  (the leaf, frond, bough and bark pictures), `hd_ground.py` (the ground's relief and gloss maps, made in the build),
  `hd_fetch.py` (downloads the CC0 textures), `hd_mount.py` (the mountain's height field, surface and colour from the
  original mountain model).
- `tests/` — headless race (`smoke`), every track (`allmaps`), two-copy online race (`net`), screenshots matched step
  for step with the web game's (`shots`), menu screenshots (`menushots`).
- `.github/workflows/pc.yml` — checks, tests and builds on every push. `[quick]` in a commit message skips screenshots and export.
- `.github/workflows/maps.yml` — exports the tracks, garage and soundtrack from the web game (run by hand, or on changes to the tools).
- `.github/workflows/hd.yml` — downloads the CC0 textures from Poly Haven into the `maps` release (`hd.zip`).
- `.github/workflows/trailer.yml` — films a gameplay clip on three tracks with Godot's Movie Maker (`tests/trailer.gd`),
  joins it (`tools/trailer_cut.py`) and attaches `trailer.mp4`, `poster.jpg` and stills to the `pc` release.
- `.github/workflows/ios.yml` — iPhone build, manual only (paused).

## Not ported yet
Cross-play with the browser version.

## Credits
The web game's credits all carry over. The finished models' bark and stone surfaces are CC0 textures from
[Poly Haven](https://polyhaven.com) (bark_brown_02, bark_willow, rock_boulder_dry and others listed in
`assets/hd/cc0/credits.txt` in the build), used under CC0 with thanks. The leaf, frond, bough and ground maps are
made by this project's own tools.
