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
- PC toolchain is set up (2026-11-12): D:\crust-rush\tools holds a portable Node, a Python venv (playwright, pillow,
  numpy, matplotlib), the Playwright browser, and py.cmd, which runs any script with the right settings:
  `D:\crust-rush\tools\py.cmd D:\crust-rush\source\tools\neon\webtest.py` builds (stamp inside that file, now v155) and
  serves the test copy on port 8771; then boottest.py, loadtest.py, simtest.py, shots.py, chase.py as before.
  The scripts' paths were rewritten by D:\crust-rush\tools\port_paths.py; webtest.sh is replaced by webtest.py.
  The test browser uses the RTX 3060 (channel='chromium', ANGLE D3D11), so Ultra pictures take seconds.
- "Before" pictures for the realism pass: D:\crust-rush\scratch\neon_before_*.png (cameras in scratch\cams_bed.txt,
  taken with VP=1280x720 HOLD=1, quality ultra). On a real graphics card the track shows a mottled, felt-like
  surface (the fine surface detail every plain material gets): it should be smooth moulded plastic.

## Realism pass progress (from the PC session, 2026-11-12 night)
- Blender: no live connection in the Claude Code session; it is run in the background with scripts
  (`D:lenderlender.exe --background --python <script>`), which is enough to build, render and export GLB.
- Item 1 done on web (not yet published, source only): sunlight through the window only.
  - Engine patch 4 (`tools/mini/patch4.py`, applied): `TOYSUN`, `sunBox()`, `sunBeam(holes,reach)`, `sunShadeAll()`,
    `sunReset()`. On a toy map the sun's shadow camera is fixed on the window opening (it does not follow the player)
    and the shadow shader treats everything outside that beam as shade. The switch is the light's shadow radius: 51 on
    toy maps, 1 everywhere else (the shader subtracts the 50 again, so the Fast and Lite shadow filter is unchanged).
  - `toyBedroom` calls `sunBeam([[x0,x1,y0,y1,z0,z1]], reach)` with the window opening. Every new room needs the same
    call for each opening the sun shines through; an outdoor track (Backyard) simply does not call it.
  - Things outdoors that should stay in full sun (the view outside, item 4) must set `userData.sunlit=true`, because
    `sunShadeAll()` makes every other mesh receive shadows on toy maps (otherwise it would be sunlit inside the room).
  - Bedroom light now: sun from the north window, direction (-.1,.56,-.82), colour #ffdcaa, strength 2.7; sky fill
    #cfdcf0 over #b3937a at .54; exposure .98. The chair moved to (-345,372) so the beam falls on the loop and the rug.
  - Tested: boot, load, races forward 212 s / reverse 162 s (8 finish, 0 respawns, 0 stuck), margherita regression,
    Lite/Fast/Balanced/Ultra pictures, bedroom -> regular track -> bedroom switch, quality change mid-race.
  - Pictures: scratch
eon_s1b_*.png (same cameras as neon_before_*), chase_s1c_*.png.
  - PC still to do for item 1: shadow range to the room on toy tracks, walls cast, same sun direction and colours.
- Item 2 done on web (source only): room reflections.
  - Engine patch 5 (`tools/mini/patch5.py`, applied): `envProbe()` hands over to `toyRoomEnv()` (mini.js) when `TOYENV`
    is set. The room is photographed once per load from `TOYENV` ([x,height,z], an open spot over the rug) into a cube
    map (256, or 128 on Fast and Lite; two passes; karts hidden) and that becomes `scene.environment`. The view outside
    is drawn 6 times brighter in that photograph only (`userData.envGain`), so the window acts as a light in reflections.
  - Track and rails are glossy again (roughness .34, clearcoat 1, clearcoat roughness .07, full reflections) and marked
    `userData.noHQ`, so Ultra's surface speckle no longer mottles them. Rail meshes are `noMerge` (merging swapped their
    plastic for a plain batch material).
  - Gotcha: `TM.mat` caches by name. `toyorange` and `toyblue` are defined both in mini.js (TOYOR, TOYBL) and in
    models.js (the spare track piece); whichever runs first wins, so the two definitions must stay identical.

## Second look at the reference video (2026-11-12 night, 136 frames: every scene change plus one frame per 8 s of the daylight race)
Take the look, never the logos, banners, car names or the flame emblem. What the daylight track does:
- Track: coloured sections (orange, red, yellow, deep blue, dark grey) that change at a joint; a white dash along
  each edge about one car long with a two-car gap; glossy enough to mirror the sky and the beams overhead; glowing
  blue oval pads; chevron strips (yellow on dark, green on dark) before bends and jumps.
- Light: one hard sun. Beams and posts throw long shadows across the track, so the car drives through stripes of
  light and shade; sunlit wood is warm orange, shade is dark and slightly blue; openings to outdoors bloom.
- Wood: plywood sheets with bold grain, visible ply edges, bolts and riveted steel plates, cones standing on it.
- Outside: real trees, a chain-link fence, low buildings, blue sky with soft clouds.
- Camera: wide angle, streaks at the screen edges at speed, tyre smoke when drifting; replays use a blurred
  background and foreground.
- Cars: metallic paint with clear reflections and a dark shadow right under the body.
Applied so far: sunlight and shade (item 1), glossy mirroring track (item 2), coloured sections and edge dashes (item 6,
brought forward because it is the most recognisable part of the look). Still to do from this list: plywood and fabric
rebuilt in Blender (3), real view outside with trees and a fence (4), background blur on Ultra (5), chevron strips
before the launch and the hairpins, a stronger bloom at the window.
- Item 6 done on web (source only): coloured sections and edge dashes. `TOYSEC` (mini.js) lists a room's sections as
  [from,to,colour] in fractions of the lap: Bedroom has a red spiral (.073-.253), yellow under the bed (.347-.514) and a
  blue climb (.783-.938); the rest is orange. Road, rails and the underside take the section's colour; a white dash runs
  along each edge (in the road texture, one per 120 units). Looks only, nothing in the track data.
- Fixed on the user's report (see HANDOVER): books through the climb, side monitor in the wall, traps drawn under
  raised road. Open on the user's report: item boxes on the starting grid on some maps (being measured), and a Blender
  remodel of every object in the room ("as realistic as possible").
- Item boxes on the starting grid (user's report): measured on all 21 maps both ways round. Only holo (.9938) and synth
  (.9917) had a row inside the grid (4 units from a kart; just past the line in reverse). Engine patch 7: `boxClear`
  moves any row that lands within 56 track points before the line or 44 after it to the nearest clear spot. Closest
  box to any grid position is now 248 units. NET_PROTO is 101 on web; PC needs PROTO 101 with its next build, after
  the track export is re-run from the published v155.
- Blender remodel started (user: "remodel all the objects ... as realistic as possible"). Workflow and rules in
  `tools/blender/README.md`. The bed is the first model through it (cloth-simulated bedding). Blender models are
  geometry plus baked vertex shading; the game's tiling materials are kept, so close-ups stay sharp.
- 2026-11-12 late night: web v155 published (app f744f82, source fb9dafe): realism items 1, 2 and 6, the Blender bed, traps
  drawn on raised road, no item boxes on the grid, NET_PROTO 101. Next web stamp v156.
  User's instructions after seeing it: publish web and PC; every graphics or game change goes to both web and PC; fix traps
  hitting karts on the level underneath (both); the white dashes belong on the track's walls, not on the road; carry on with
  the Blender models and the rest of the list.
- Web v156 published (app c8132d7): bed clear of the walls, dashes on the track's walls. Web v157: traps only catch karts on
  their own level (NET_PROTO 102). PC brought level with web v157: window-only sun (walls and ceiling cast, shadows reach
  across the room), glossy track with a reflection probe of the room, warm fill light, traps at road height with the level
  rule, PROTO 102, track export re-run for v156 (it now waits for the Blender models).
- Web v158 (curtains built in Blender, hung as cloth; side monitor moved clear of them) and v159 (rug with a fringe and a
  curling corner) published. Blender models so far: bed, curtain, rug. PC: build eec44e5 (PROTO 102, room as web v156) was
  pushed; the track export has to be re-run for v159 and the PC rebuilt after it (push a change to maps.yml with [quick],
  wait for the export, then push any PC change without [quick]).
- Still to do from the agreed list: wood and fabric textures (3), real view outside with trees (4), background blur on
  Ultra (5); the remaining Blender models (tools/blender/README.md); then Kitchen Chaos, Garage Overdrive, Backyard Mega
  Circuit and the cup.
- Web v160: the view outside the bedroom window is a garden rendered in Blender (item 4 of the realism list). PC build
  eec44e5 is public (PROTO 102, room as web v156); it still needs the export for v160 and a rebuild to get the curtains,
  the rug and the garden.
- Web v161: oak floorboards from a generated texture pair (first part of item 3). Note: a push that only changes README.md
  does NOT start the PC build (pc.yml ignores it): the rebuild needs a change to a script.
- Web v162 (Blender-built gaming chair) and v163 (smooth painted walls with a fine stipple, named toy_pt_wall* as before)
  published. Blender models so far: bed, curtain, rug, chair; pictures: the garden outside, the oak floor.
  PC: build 5d0f5b6 carries the room as of web v161; a rebuild for v163 follows it (commit prepared in D:\crust-rush\godot,
  to be pushed only after build 5d0f5b6 has finished, so the two builds cannot replace the download in the wrong order).
- Next: desk, dresser, nightstand, floor lamp, sneakers, backpack and the small things in Blender; walnut and painted-board
  textures; background blur on Ultra (item 5); then the other three rooms and the cup.
- Web v164 (Blender-built dresser and nightstand) published. PC rebuild for v164 is commit 0044c08 in D:/crust-rush/godot,
  pushed automatically once build 5d0f5b6 and the v164 export (8896bb4) have both succeeded; check pc-build.json afterwards.
- Web v165: walnut desk top (generated texture), background blur on toy tracks (Ultra, item 5 of the realism list; engine
  patch 9, Settings > Background blur), and the toy-track handling change (engine patch 10: TURN 2.64, DRIN, DROUT;
  NET_PROTO 103). PC: the same blur (CameraAttributesPractical far blur, `_toy_dof`), DRIN/DROUT from the export, PROTO 103.
- 2026-11-13: PC build 98b863b5 is the public download and matches web v165 (room, handling numbers, background blur,
  PROTO 103); the cross-play test on GitHub passed for it. Web and PC are level. Next web stamp v166.
  Waiting on the user: how the new toy-track handling feels (TURN 2.64, DRIN 2.6, DROUT 0.6).
  Next work: remaining Blender models (floor lamp, sneakers, backpack, books, plant, monitors, keyboard, PC tower, door and
  window frames, shelf, small things); fabric textures; then Kitchen Chaos, Garage Overdrive, Backyard Mega Circuit and the cup.
- Web v166 (engine patch 11): item boxes spread out and back after 2 s on toy tracks, one box of a row per kart; anchovies
  are used up on a protected kart; Olive's trail is 7 slicks on toy tracks, never catches her, and shows blue to her.
  NET_PROTO 104. PC: the same rules (PROTO 104), numbers from the export.
- Web v167: easier computer drivers on toy tracks (patch 12) and the garage's stats shown as on the PC (patch 13).
  PC: item rules (PROTO 104) and `abw`; needs the export for v167 (diffs) before its build.
- Web v168: new boost flames, stronger motion blur, rainbow boost streaks on Neon tracks (patch 14). PC: the same
  (flame.gdshader, post.gdshader); needs the export (tracks for the `neon` flag, garage for `fglow`) before its build.
- 2026-11-13: web v170 and PC build 807fdc66 are level. Since v168: motion blur at its original strength with wind lines
  (patch 15), no black dots in the flames on phones and boost sparks that stay with the kart (patch 16). Next web stamp v171.
  Waiting on the user: how the toy-track handling feels, whether 200cc on Bedroom Blitz is winnable now, whether the flames are
  clean on their phone, and whether the flame glow on the road shows on PC (too faint to confirm in a local picture).
  Next work: remaining Blender models, fabric textures, then Kitchen Chaos, Garage Overdrive, Backyard Mega Circuit and the cup.

