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

- `rug`: a mat that does not lie quite flat, one corner curling, a fringe at both short ends. Its `rug` material carries one
  picture over the whole mat: the builder passes a tile of `[110,150]` (across, along, in cm) to `pk`.

- `outside`: not a model but a picture: the garden seen through the bedroom window (lawn, a board fence, seven trees made of
  tens of thousands of small pointed leaves that glow where the sun is behind them, a neighbour's house), rendered with the
  sun where the game's sun is. `put_tex.py tex_toy_outside blender/outside/outside.jpg 1792 82` puts it in the texture store;
  `M.outside` hangs it behind the window, a little over full brightness. Realism-list item 4. Every other room needs its own.

- `chair`: the gaming chair. Cushions are bevelled boxes smoothed with one level of subdivision (`cushion`); parts are
  placed with matrices (`place`), the back about a reclined pivot. The game turns the whole chair by `o.turn`.
- `dresser` and `nightstand` (both built by `dresser.py`): carcasses with softened edges, drawer fronts standing proud with
  shadow gaps, bar handles on standoffs or round knobs, tapered legs. The dresser's size is fixed (the track climbs over it).
- `floorlamp` and `desk` (both built by `props1.py`): the lamp has rolled rims, a three-arm fitting and a bevelled base;
  the desk a softened top on a steel frame. Both keep the old sizes exactly (the track spirals round one and runs along the other).
- `oak_tex.py` (no Blender: numpy and Pillow): the oak floor as a tiling texture pair, `tex_toy_oak` (colour) and
  `tex_toy_oak_n` (relief), one tile 1.92 m. Every board has its own length, tone and ring figure; the relief carries the
  grain, the bevels and the gaps. Built from noise shaped in frequency space, so it repeats without a seam. First part of
  realism-list item 3. `oak_tex.py walnut` makes the desk's top the same way (`tex_toy_walnut`, `_n`: eight full-length staves
  in a 0.9 m tile, flush joints); `woodTex(key,rough,fallback)` in models.js turns such a pair into a material.

- `kitchen.py`: the kitchen's seven models in one script (`-- <name>` builds one). Uses `finish_model`, `rod` and `bar` from crlib.
- `outside.py [-- k]`: ONE garden for the whole house; the argument picks the window it is seen from.

- `garage.py`: the garage's six large models in one script (`-- <name>` builds one): gbench, gbenchn, gchest, gshelf, gtyres, gdoor.
  Also three things for its walls: gelec (the electrics), gladder (a hung ladder), grack (garden tools on a rail); the wall is the plane Y = 0.
- `ph_tex.py` (no Blender): CC0 photo-scanned surface textures from Poly Haven into the texture store (lawn, concrete, paving, planks, gbrick for the garage's walls, brick, slate, bark, soil); read in the game with `surfTex`.
- Cars (not room models; they go into CAR_PACKS, not PROP_PACKS): `car_inspect.py`, `car_rules.py`, `car_convert.py`,
  `car_all.sh`, `car_sheet.py`, `car_pack.py`. The steps are in docs/HANDOVER.md under web v173, "How a car gets in".
  Outputs are in `D:/crust-rush/blender/cars/<id>/`.

## Blender first (the user's instruction, 2026-11-13)
"From now on if you can make something better in blender than with code I want you to": a new or reworked model is built
here. Code-built geometry in models.js is the stand-in while a pack loads, and stays where code is as good (flat walls, track).
Check joints with `joined(a, b)` from crlib: parts must overlap, not merely come near.

## To do (most visible first)
desk, floor lamp, sneakers, backpack, books,
plant, monitors, keyboard and mouse, PC tower, door and window frames, shelf, posters, bin, cartons, skateboard,
balls, small toys.
