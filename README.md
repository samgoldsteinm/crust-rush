# Crust Rush — native build (Godot 4.7) · PAUSED

Paused on 2026-11-10 by choice (iPhone install route). Nothing here affects the web game on `main`.

## What's here
- `project.godot`, `export_presets.cfg` — Godot 4.7 project, Mobile renderer (Metal on iPhone), landscape, 120 Hz physics.
- `scripts/track.gd` — loads a track exported from the web game (centre line, walls, ramps, pads, obstacles, start grid, height maps).
- `scripts/kart.gd` — the web game's `stepKart` ported line for line: steering, drift hop and charge tiers, mini-turbos,
  off-road, slopes, walls, ramps, jumps, tricks, the glide section, obstacles, boost pads, laps. Not ported yet: items,
  abilities, the loop lane, shortcuts, AI.
- `scripts/main.gd` — race scene: sky/sun/fog from the web values, chase camera, far-clutter culling, HUD,
  touch/keyboard/controller input, fps and resolution toggles. Not yet run in Godot.
- `shaders/sky.gdshader` — the web sky gradient.
- `assets/track/bay.json`, `assets/kart/hypercar.glb|json` — exported data and kart (small, committed).
- `tools/glbexport.js`, `tools/runexport.py` — the exporter that bakes a web track into glTF (run in the test browser).
  The bay geometry (~48 MB) is not committed; rerun the exporter to regenerate it into `assets/track/`.
- `.github/workflows/ios.yml` — cloud build of an unsigned iPhone app (proven working with a test scene; Xcode 26.3).

## Resuming
1. Regenerate `assets/track/bay.gltf` (+ `.bin`, `bay_tex/`) with the exporter.
2. Open in Godot 4.7.2 on PC and press Play — this also works as a native Windows build, no iPhone needed.
