# Miniature Mayhem Cup (user spec: /mnt/user-data/attachments/009aa3b6-e96f-505b-b230-9e07dd3a3292/d7923e4b-attachment.txt)

User's answers (2026-11-12): half-width orange track; short laps and more of them (about 5); post Bedroom Blitz
first for a look/scale check, then Kitchen Chaos, Garage Overdrive, Backyard Mega Circuit. Cup name MINIATURE MAYHEM CUP.
Web first (source of truth), then PC export + parity, both posted together.

## Scale (measured)
- A kart is about 26 units long (bounding boxes 23-28 x 15-17 wide x 15-21 tall). 26 units = 7.5 cm
  -> 1 unit = 0.29 cm, 1 cm = 3.47 units, 1 m = 347 units. Use U=3.47 units per cm everywhere.
- Normal road RW=63 (126 wide = 36 cm). Toy road: RW=31, CURB=38, WALLD=42 (surface 84 wide = 24 cm, 4 lanes),
  raised rails outside WALLD.
- Bedroom 4.0 x 4.6 m = 1390 x 1600 units, ceiling 2.5 m = 868. Desk top 75 cm = 260, bed top 55 cm = 190,
  under-bed clearance 28 cm = 97, dresser 85 cm = 295, key 1.8 cm = 6.2, mug 9.5 cm = 33.

## Engine plan
- Flag toy:1 (plus arena:1 so the usual scenery is skipped), theme kitchen for indoor light, own builder.
- Per-track road width: RW/CURB/WALLD become lets set in loadMap0; LS = RW/63 scales lane numbers at the point of
  use (ai.lane, item box rows, start grid, glide rings). PC already reads RW/CURB/WALLD from the export; needs LS too.
- def.laps (5). Export LAPS from it.
- Glide without a drawn pit works (pit only in the physics: a kart 32 below the glide line respawns).
- Loop: LOOPS are automatic and off for multi-level tracks; needs an explicit, scaled loop (S, W x LS). Decide after
  the base track drives.
- Layout tool: reuse /home/claude/neon/gen.py (turtle) with OUT spacing 8-16 and the neon data fields.

## Bedroom Blitz layout (design coords: x east, y north, room centre at 0; game z = -y)
Room 4.0 x 4.8 m: x -695..695, y -833..833, ceiling 868. Lap about 7000 units -> laps: 4. Posted first as a
special track (single race) until the cup has four tracks.
- Desk 200 x 80 cm on the north wall: x -470..224, y 555..833, top 260. Track lane on the desk at y=605,
  eastbound: the start straight. Keyboard and monitor behind the lane; a side monitor on an arm over the track;
  PC tower with glass side on the desk's east end.
- East end of desk: ramp launch, land on a raised section (235), then a helix round a floor lamp in the NE corner
  (centre 555,695 R=90, 1.75 turns anticlockwise) down to the floor, leaving southbound at x=465.
- South along x=465 under the queen bed (x 168..695, y -833..-137, clearance 97): hairpin R=85 under the bed,
  back north at x=295.
- Left to westbound at y=80 through the middle of the room: toy ramp over a pile of sneakers.
- Left to southbound at x=-420 (rug), U-turn R=100 in the SW corner, then north along the west wall at x=-620
  climbing 0 -> 260 over 900, over a low dresser (west wall, y 60..476, top 156) on stacks of books, level,
  right-hand curve R=110 onto the desk.
- Loop: wanted in the middle of the room; needs the scaled explicit loop (see engine plan).

## Model library (mini/models.js -> TM.*), viewer and workflow
- Builders return a Group at real size (cm * U, U=3.47), origin on the floor, +z to the front. Helpers: slab (rounded
  slab), blob (cushion), uvw (real-size UVs), wood/fabric/plastic/metal/paint/glow/glass (shared, named toy_*).
- Inspect each model alone: `python3 view.py <sheet> "asset:az,el,zoom;..."` -> mini/view/<sheet>.jpg (server on 8772).
- Done and inspected so far: desk, deskmat, monitor (stand or arm), keyboard (87 instanced keycaps), mouse, pc.
- inject_mini.py puts tracks.json + models.js + mini.js into crust-rush.html (MINI markers). Build + test copy:
  /home/claude/neon/webtest.sh (port 8771, /webcopy6). Race test: neon/simtest.py bedroom medium 220.
  In-game photos: neon/shots.py bedroom <tag> fast|sharp "cams". Boot check: neon/boottest.py.

## Progress log
- 2026-11-12: engine patch applied to crust-rush.html (mini/patch_engine.py; backup scratchpad/crust-rush.v151.html):
  RW/CURB/WALLD/LS per track (def.rw), def.laps, toy hooks (toyRoad, buildToy, toyDecks via neonDecks, toyScenery).
  Not yet on PC: PC needs LS for rival lanes / grid / box rows / glide rings, LAPS from export, HdKitchen skipped for toy.
- Bedroom Blitz drives (web sim: 8 karts, 4 laps in about 200 s, lap 7049 units).
- Models inspected in the viewer: desk, deskmat, monitor, keyboard, mouse, pc, bed, chair, dresser, books, floorlamp,
  rug (not yet viewed), sneaker (v3 ok), window, door, curtain, nightstand, plant, mug, sodacan (not viewed), poster
  (not viewed), shelf, bin, carton (not viewed), hoodie (v2 not viewed).
- Room assembled in mini.js toyBedroom (walls with window/door openings, skirting, ceiling light, furniture placed,
  floor shade patches). First in-game photo run pending.
- Gotchas: models must not be named like a helper exported from TM (can, tex, mat, box, cyl, add, grp, slab, blob...).
  `cm` is taken in the game (use tcm). webtest.sh now syntax-checks; boottest.py checks the menu comes up.
- To do for the bedroom: lighting/exposure tune, the loop, toy-set details (piece joints, connectors, booster look,
  start gate), fewer/neater piers, more props, thumbnails, PC port, post as special track on both.

## State on 2026-11-12 afternoon (after the user's notes: narrower track, no lengthwise lines)
- User: "track too wide from high up", "no lines along the track, the cross joints between pieces are fine".
  Done: rw=22 (CURB=RW+4, WALLD=RW+6 on toy tracks; drawn surface TOYW=WALLD+5 with rails outside), lane lines removed.
- Engine patch 2 (mini/patch2.py, applied): toy loop (def.tloops, full-loop machinery scaled by L.sc=LS; S=42),
  toyGate (toy start gate), toyPads (full-width boosters with housings), toyRamps, toyShortcut, toyRails (after
  shortcuts), start grid two wide on toy tracks, LOOP_DH reset per map, NET_PROTO=100 (PC PROTO 100, uncommitted).
- New models (batch4.js, in models.js): skateboard, ball (basket/tennis), cube, bricks, pencils, backpack,
  controller, setbox, trackpiece. Hoodie removed.
- Web sims: forward 202 s, reverse 162 s, 8 finish, 0 respawns. Draw calls 266 (oven 213, laser 154).
- Ultra menu pictures: picked and embedded for the 20 older tracks (h and m for all; a only for the neon four,
  the new aerials show black trees). Source: scratchpad/ultra/final. CI zip job: .github/workflows/shotspub.yml
  (writes run id to .github/shotspub.txt; scratch pre-release shots-tmp; write "delete" there to remove it).
- gh run download does not work here (blob storage blocked): use the shotspub route.
- PC (uncommitted in worktree): T.LS, T.toy, T.laps0, grid, lanes x LS, glbexport LAPS/LS/toy, HdKitchen skipped
  for toy, PROTO 100, new assets/shots. Still to do on PC after web v152 is live: maps.yml matrix 0-20, export,
  look at HD passes on the toy room, tests, push.
- Next: bedroom menu pictures (neon/shots.py with VP=1280x720 HOLD=1 -> scratchpad/neon_pic_*.png), info entry,
  publish web v152, then PC.

## State on 2026-11-12 evening
- Web v153 published (30d045f): fixes from the user's play-test (see the Project doc claude/crust-rush-handover.md and
  /home/claude/mini/HANDOVER.md, its source). Layout now: desk -> launch -> spiral R=150 clockwise 1.25 turns round the
  floor lamp at (460,455) -> south x=610 under the bed -> hairpin R=100 -> north x=410 -> west y=20 with the loop at
  (36,20) (sc .36) -> shortcut s8 .93 -> s10 .5 -> south x=-420 (ramp) -> hairpin -> climb x=-620 over the dresser -> desk.
  rw=31 (WALLD 42, drawn 46), TURN x1.3 on toy tracks (TOYT), 3 boosters + loop's.
- Engine patch 3 (mini/patch3.py): planPonds on arena maps, kEy TOYT branch, camera cSA, TURN/TOYT lets.
- Motion blur option added on web (CFG.mblur, final pass uniform mb) and PC (mblur_on, post.gdshader mb): NOT yet
  published (web source and PC worktree, uncommitted). Next web version stamp: v154 (webtest.sh already says v154).
- PC: 230b7ee pushed [quick] (HdToy, k_ey toy branch, camera rg + slope, maps.yml 0-20). Export for v153 done
  (map-bedroom.zip asset 740925896). Still to do: local race + render check with the new export, then push a full build
  (no [quick]) together with motion blur.
- Tools: neon/chase.py <map> <tag> "idx,..." photographs the game's own chase camera with a self-driving player.

## Realism pass (user's request after seeing a reference video they could not be shown to me: send screenshots)
The user wants the toy rooms to feel like the reference game: real-feeling light, deep wood grain and shadows, realistic
trees outside, light reflecting off the track and karts. No copyrighted names or logos. Blender is not available.
Plan, highest value first (web, then the PC equivalent of each):
1. Room reflections: capture a cube map of the finished room once (CubeCamera at the room centre, about 150 up),
   PMREM it, use as scene.environment on toy maps (the track and karts then reflect the window and walls, not the
   outdoor sky). PC: a ReflectionProbe (box projection, interior, update once) in HdToy.
2. Sunlight through the window only: the sun's shadow map covers the whole room on toy maps (walls and ceiling cast),
   so there are sun patches on the desk and floor and soft shade elsewhere; raise the fill (hemisphere) light and add
   a warm ceiling-lamp point light and a bounce light over the sun patch. PC: same (shadow range to the room size on
   toy tracks, walls cast again, OmniLights without shadows).
3. Window and outdoors: a brighter window that blooms, a painted backdrop with depth (sky gradient, soft trees at
   two distances, a fence, a neighbour's roof), slight blur; real 3D tree branches just outside if cheap.
4. Wood: deeper grain normal maps, board gaps with bevels, roughness variation, so the floor shows the window's
   reflection. Fabric and wall: fine normal detail.
5. Small things: dust motes in the sun shaft, contact shadows under props (toyShade exists), SSAO stays on.
After that: Kitchen Chaos, Garage Overdrive, Backyard Mega Circuit and the cup.
Open items the user raised: booster housings near shortcut mouths (guarded in toyBooster), shortcut walls (toyRailClip).
- 2026-11-12 late: web v154 (f241156, motion blur) and PC b2abf99 (Bedroom Blitz v153 layout, motion blur, toy sun
  x0.5) are published. PC chase-camera test: tests/tmp_chase (CR_MAP, IDX, TAG). Next web stamp v155.
- The user says they connected Blender, but no Blender tool or linked computer is visible in this session.
- Not started: realism pass (plan above; touching the sun shadow map needs care: applyQuality, the frame-rate
  ladder's sm, snapSun all set its size), the other three tracks, the cup.

## Work moved to the user's PC (2026-11-12 evening)
- Everything lives in D:\crust-rush (C: is nearly full, keep work off it): app (branch main, the published web game),
  source (branch source: crust-rush.html, build, tools, docs), godot (branch godot, PC), blender (model files),
  scratch (test output), reference (contact sheets from the reference video, 9 frames each, 14 s apart).
- Installed on the PC: Python 3.12 (%LOCALAPPDATA%\Programs\Python\Python312), ffmpeg, yt-dlp, Deno, Git (D:\git),
  Blender 5.3 (D:\blender\blender.exe). Not yet set up: Node, Playwright, Godot; the build and test scripts still use
  the cloud workspace's Linux paths and need pointing at D:\crust-rush.
- Reference video (a toy-car racing game; take lighting and materials from it, never names or logos). What makes it
  look real: one strong low sun with hard-edged warm patches and darker blue shade; glossy track that mirrors the
  sky and lights at low angles (coloured streaks on the night track); plywood with grain, knots, layered edges,
  bolts and scuffs; real trees, fence and buildings outside under a blooming sky; background blur in close shots,
  streaks at speed; metallic kart paint with a dark contact shadow; white dashes along the track edges, seams,
  coloured sections.
- Agreed order for Bedroom Blitz: 1 sunlight through the window only, 2 room reflections on track and karts (undo the
  earlier turned-down reflections), 3 wood and fabric rebuilt in Blender, 4 real view outside, 5 background blur on
  Ultra, 6 edge dashes and coloured sections. Show before and after pictures after 1 and 2.
