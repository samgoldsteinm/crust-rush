# Crust Rush — native PC build (Godot 4.7)

The Windows version of Crust Rush, on its own branch. Nothing here affects the web game on `main`.
Every push builds `CrustRush.exe` (Actions → PC build → Artifacts → CrustRush-Windows).

## What it has
- Hawaiian Bay, three laps, eight racers: you (Basil in the Hypercar) and seven computer drivers in the web game's karts.
- The web game's driving, ported line for line: drifting and mini-turbos, tricks, the glide, the loop-the-loop, boost pads.
- Nine items with the web game's rules and odds: Chili Boost, Pepperoni, Pepperoni Trio, Olive Oil, Dough Ball,
  Garlic Shield, Flour Bomb, Pizza Wheel, Delivery Rush. Two slots, keep-behind, look back to fire backwards.
- Main menu, pause menu, results, minimap, sound.
- Graphics levels (pause menu): Ultra (default), High, Low.
- Online races between PCs: one hosts, the others join with the host's address.

## Controls
- Keyboard: arrows/WASD steer · Space/Down/S drift-brake · X/E/Enter item · Z/Q/V second item · Shift/B keep item behind ·
  F look back · P/Esc pause · F11 full screen.
- Controller: left stick or d-pad · RT gas · LT drift · A/LB item · B/RB second item · X look back · Start pause.

## Files
- `scripts/kart.gd` — one kart's physics (web `stepKart`, loop-the-loop, spin-outs).
- `scripts/race.gd` — the race (web `update0`, `aiInput`, `useItem`, thrown items, item boxes, standings).
- `scripts/main.gd` — scene: drawing, camera, HUD, menus, input, online.
- `scripts/gfx.gd`, `shaders/` — lighting, shadows, screen effects, surface detail, water, sky.
- `scripts/sfx.gd` — sound, synthesised at start-up.
- `scripts/track.gd`, `assets/track/` — track data and geometry exported from the web game.
- `assets/kart/`, `assets/items/` — racers' karts, item models and icons exported from the web game.
- `tools/` — the exporter (`glbexport.js`) and its runners (run in the test browser against the web game).
- `tests/` — headless race (`smoke`), two-copy online race (`net`), screenshots (`shots`).
- `.github/workflows/pc.yml` — checks, tests and builds on every push. `[quick]` in a commit message skips screenshots and export.
- `.github/workflows/ios.yml` — iPhone build, manual only (paused).

## Not ported yet
Special abilities, the shortcut, the other tracks, the sixteen newer items, traffic and rolling meatballs on the bay,
kart and driver choice, cross-play with the browser version.
