# Room models built in Blender

The furniture and household things of the toy-track rooms are being rebuilt in Blender, one model at a time, where the
code-built ones (tools/mini/models.js) fall short: cloth that folds, soft shapes, bevelled edges.
There is no live Blender connection: Blender 5.3 (D:\blender\blender.exe) is run in the background with a script.

## One model, start to finish
1. Write `tools/blender/<name>.py` (see `bed.py`). It builds the model with the helpers in `crlib.py`, bakes soft
   shading into the vertex colours, renders check pictures and exports a GLB.
   `D:\blender\blender.exe --background --python D:\crust-rush\source\tools\blender\<name>.py`
   Output in `D:\crust-rush\blender\<name>\`: `<name>.blend`, `<name>.glb`, `<name>_check0.png` ...
2. Look at the check pictures. A model only goes into a room once it looks right on its own.
3. `D:\crust-rush\tools\py.cmd tools\blender\pack_glb.py <name>` packs the GLB into the game's prop format and puts it
   into `crust-rush.html` as `toy_<name>_hq`.
4. In `tools/mini/models.js` the builder starts with `if(pkReady('<name>'))return pk('<name>',{material:[gameMaterial,tileCm],...});`
   and keeps its code-built model after that line as the fallback. Then `inject_mini.py`, build, photograph in the room
   (`WAITPK=<name>` makes `shots.py` wait until the model has arrived).

## Rules that keep it working
- Metres, Z up, standing on the floor at the origin; Blender -Y is the front. Keep the old model's footprint and
  clearances exactly (the track runs under the bed, round the lamp, over the dresser).
- A Blender material's name is only a key: the game supplies the real material (wood, fabric...) and tiles it at real
  size, which is what keeps surfaces sharp when the camera is a toy car's height off the floor. One baked texture per
  model would be far too coarse at that distance.
- UVs in metres. Sheets and pillows keep the UVs of the flat grid they were made from, so the weave follows the folds;
  hard parts use `uv_box`.
- Bake the shading per vertex (`POINT` domain). Per-corner colours split every vertex on export and nearly double the
  download.
- The pack name ends in `_hq` on purpose: the build ships such packs as files that download after the menu is up, so
  nobody waits for room models at start-up. Until one arrives the room shows the code-built model.
- Budget: aim under 25,000 vertices and 700 KB per large model (the bed is 23,000 and 623 KB), far less for small things.
- Measure before placing: `pack_glb.gather` gives every part's extent in metres; compare with the walls and with whatever
  stands next to it (the bed went into two walls and onto the track when it was placed by eye).
- Do not run a Blender build while the race tests are running: both use the graphics card, and a 90-second build took
  over ten minutes.

## Done
- `bed`: oak frame, padded headboard, mattress; duvet and throw dropped on as cloth, quilted; pillows and cushion blown
  up from flat cases.

- `curtain`: two panels hung as cloth from a pinned, pleated top edge (materials curtainL, curtainR; the room uses one each
  side). Origin at the top middle. Lessons: start the pleats uneven or the cloth hangs like corrugated sheet; on tight folds
  the raw baked shade is nearly black and streaky, so `soften_ao` blurs and lightens it; in the game the curtains are marked
  `sunlit` (they throw shadows but are not tested against the sun's shadow map, which breaks up on backlit folds).

## To do (most visible first)
chair, desk, dresser, nightstand, rug, floor lamp, sneakers, backpack, books,
plant, monitors, keyboard and mouse, PC tower, door and window frames, shelf, posters, bin, cartons, skateboard,
balls, small toys.
