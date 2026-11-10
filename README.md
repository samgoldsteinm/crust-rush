# Crust Rush — native PC build (Godot 4.7)

The Windows version of Crust Rush, on its own branch. Nothing here affects the web game on `main`.
Every push builds `CrustRush.exe` (Actions → PC build → Artifacts → CrustRush-Windows).

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
- Cheat codes in Settings > More (UNLOCK, TESTING), as on the web.
- Online races between PCs: one hosts, the others join with the host's address.

## Graphics
The picture is matched to the web game's Ultra (lighting, tone mapping, colour grade, bloom, ambient occlusion,
shadows). **Settings > Graphics > PC extras** (on by default on Ultra) goes a step further: shadows reach more than
twice as far in four cascades and soften with distance, a little light bounces between nearby surfaces, textures
stay sharp at a glance and glossy paint reflects a finer sky. Turn it off for the web game's Ultra exactly.

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
- `scripts/music.gd`, `scripts/sfx.gd` — the soundtrack and the sound effects.
- `scripts/track.gd` — track data exported from the web game.
- `shaders/` — sky, post grade, livery, bubbles, particles and menu backgrounds.
- `tools/` — the exporters (tracks, garage, soundtrack), run in a browser against the web game.
- `tests/` — headless race (`smoke`), every track (`allmaps`), two-copy online race (`net`), screenshots matched step
  for step with the web game's (`shots`), menu screenshots (`menushots`).
- `.github/workflows/pc.yml` — checks, tests and builds on every push. `[quick]` in a commit message skips screenshots and export.
- `.github/workflows/maps.yml` — exports the tracks, garage and soundtrack from the web game (run by hand, or on changes to the tools).
- `.github/workflows/ios.yml` — iPhone build, manual only (paused).

## Not ported yet
Cross-play with the browser version, the online network log, key rebinding, and the TESTING cheat's shortcut prompt.
