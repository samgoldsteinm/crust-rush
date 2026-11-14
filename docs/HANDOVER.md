# Crust Rush handover: read this first every session

Purpose: a running record of what broke, why, and what fixed it, so a fix made several updates ago is not undone by
accident and so old fixes can be reused. Add an entry whenever a bug is fixed. Newest entries first. Keep entries short:
**what broke / why / fix / how to keep it fixed**.

## Where things are
- Web game: the code is one source file, `crust-rush.html` (2 MB); every model, texture and track picture is its own file
  under `data/` (`tools/tables.py` reads and writes them; `py.cmd tools/assets.py sizes` counts them). The build
  (`build/build_gh.py`, run by `tools/neon/webtest.py`) puts the two together into the app repo (branch `main`). PC: Godot, branch `godot`.
  The PC's track files are exported by CI from the *published* web game, so web goes out first, then the export, then PC.
- Both must agree on anything that moves a kart (online play is deterministic). Bump the online version on both
  (`NET_PROTO` on web, `PROTO` in `scripts/webnet.gd`) whenever kart physics, track data or race messages change.
- Miniature Mayhem (toy tracks) working notes: `/home/claude/mini/PLAN.md`. PC notes: project docs
  `crust-rush-pc-build-notes*.md`. Rendering notes: `crust-rush-rendering-notes.md`.

## Standing rules (from the user)
- Commit and push every update. Keep the CC-BY waterfall credit (PC README and `assets/hd/waterfall/credits.txt`).
- Never change the user's uploaded kart designs. No non-BMP characters in the web source.
- Nothing that risks online play. Never ask for or use the TURN secret key.
- Assets: the user's own uploads, original designs, CC0. No copyrighted names or logos (the toy tracks are
  "inspired by" toy racing sets; never use a real brand's name, logo or box art).
- Another session also pushes to both branches: fetch and check ancestry before every push.

## Fix log

### Space (the owner, 2026-11-13: "GitHub pages has a hard 1gb limit we also have to consider")
- Measured 2026-11-13: the published site is 77 MB (models 25, textures 19, track pictures 17, code 2, three.js 5); GitHub
  reports the whole repository (all three branches and their history) at 280 MB. `release_web.py` prints both after every
  release and warns at 700 MB / 800 MB.
- What was eating the space was the source branch: 37 kept versions of a 70 MB `crust-rush.html`. Since the assets moved
  out of that file (entry below) a change stores only the files it touches.
- Rules to stay small: store a texture at the size it is seen at (1024 for most; 2048 only for a wall filling the view);
  drop a model's pack when a better one replaces it (`py.cmd tools/assets.py drop <name>`); `py.cmd tools/assets.py sizes`.
- THE SECOND SITE (set up 2026-11-13, web v189; the owner made the repository `crust-rush-assets` the same day).
  - What: a second repository with its own Pages site and its own 1 GB, for the files that load late and weigh most:
    the high-detail models (`*_hq`) and every scenery texture over 150 KB. Today that is 107 files, 32 MB of the game's 79.
  - Where: checked out at `D:/crust-rush/assets` (branch `main`). The switch is `build/asset_site.json`, `"on"`.
  - How it works: the build (`build/build_gh.py`, `far()` says which files) always writes those files there too, under the
    same hashed names. With `"on": true` it leaves them out of the game's own site and names them `far:geo/<file>`; the
    game (`farURL` in crust-rush.html) turns that into the folder beside it on the live site
    (`../crust-rush-assets/`), and into the full address anywhere else (a test copy, the PC's export run in CI, which
    serves only the game's own files). A test copy is told to use the local checkout (`window.CR_FAR`, set by `webtest.py`,
    which also links `scratch/crust-rush-assets` to the checkout). Pictures from another address are asked for with
    `crossOrigin` so they can be textures.
  - Publishing: `release_web.py` pushes the second site first; with the switch on it waits until every file of the build
    answers there before it publishes the game (15 minutes, then it stops without publishing); afterwards it removes files
    older than the previous version's. It prints both sites' sizes.
  - STATE: the files are published there; the switch is OFF (the game still carries its own copies) until Pages is
    switched on for that repository (the owner: Settings, Pages, Deploy from a branch, `main`, `/ (root)`).
    To switch over: check `https://samgoldsteinm.github.io/crust-rush-assets/current.json` answers; set `"on": true`;
    `webtest.py`; the usual tests plus one load of a toy track; `release_web.py`; then run the PC export once
    (`release_pc.py`) and check its log shows no failed downloads, because CI then fetches these files from the live site.
  - Tested with the switch on (2026-11-13): the garden loaded with 86 files from the folder beside the game, and again from
    a different address (as CI will), nothing failed, all textures drawn. The game's own site drops from 79 MB to 46.
  - Bigger worlds (Sandbox): the same mechanism takes more repositories, one per group of regions, if ever needed.

### 2026-11-13 (web v191): Sandbox in every room of the house; collision read from what is drawn; passages; races from the start line

The owner: "Keep working on the rest of the sandbox mode". Sandbox now starts in the bedroom, the kitchen, the garage or the
garden (the menu's track list shows the four while in Sandbox). Nothing is listed by hand any more: what stops the kart is
computed from the room's own triangles when Sandbox starts, so you drive under the bed, the desk and the kitchen table and
are stopped by their legs. How it works and what is left out: docs/SANDBOX-PLAN.md, "Collision from what is drawn".
| What broke while building it | Why | Fix | Keep it fixed |
|---|---|---|---|
| In the rooms the kart kept dropping 1.6 units and coming back | The track lookup entered each lap point only for the squares on the line across the track; where lap points are 8 apart (rooms) that left gaps | Each lap point is entered for its whole strip of track (`sbHashTrack`) | `sbtest.py <room>`: worstHeightGap |
| A wall across the bedroom's start line | A square holds a fixed number of solid stretches; the ceiling and other high things filled them and the store joined the floor plate to the banner beam | Nothing more than 70 units above the track's highest point is kept; six stretches a square | The lap test in every region |
| The kart stopped at 93% of the kitchen lap | The drawn track runs through the front edge of the worktop | "The lap is always open": on the track at its own level nothing drawn blocks (`sbBlocked`) | Same |
| Coins inside a cardboard box | A box is a hollow shell: its inside is not "blocked" | The line was moved; the test floods the floor from the track and fails on any coin it cannot reach | `sbtest.py`: "coins: every one on the floor can be driven to" |
- PASSAGES between the four places and A RACE FROM THE START LINE (the owner's request of the same day) are in this version
  too: docs/SANDBOX-PLAN.md, "Passages" and "A race from the start line". Two more faults met on the way: the engine's round
  outer limit (`RIM`) held the kart at a room's wall (off in Sandbox now), and a gate's mouth must reach 20 units into a
  room, past the skirting board.
- Tests: `sbtest.py` passes in all four places at Ultra (walls, open ground, the lap, the coins' reach, every passage both
  ways, the race offer, the race, the return); races (Bedroom, Kitchen, Backyard, Margherita), Balloon Battle and the phone
  session rerun after it.
- Not yet: the load cut into slices (so the duct is not needed to hide it), the way out to the street, the map, the clock,
  things to do, the shop, PC, friends in Sandbox and the start-line lobby.
- BALLOON BATTLE, from the owner's play-test the same day (docs/BALLOON-BATTLE-PLAN.md, last section): three balloons; only
  pepperoni, trio and chili; sixteen boxes; ramps as wide as their ledges; the fifth pan and the peel's handle gone; the
  rolling pin's handles solid. Keep the game's shapes (`bbArena`) and the Blender models (`battle.py`) the same thing: change both.

### 2026-11-13 (web v190): Balloon Battle's scoreboard is one small line
The owner: "Remove the hud that lets you see how many balloons everyone has it's way too big and In the way." The list of eight
karts is gone (`bbHud` in tools/mini/battle.js). What is left, top left: the clock, your points, your place. Everybody's balloons
are on their karts; the full table is the results screen. Do not bring a list back. (PC: Balloon Battle is not ported yet;
port it with this small line.)

### 2026-11-13 (web v188): Sandbox, the first slice: free driving in the back garden

The owner chose passage-joined regions for Sandbox (docs/SANDBOX-PLAN.md has their words and what they ask of a passage).
Built: the mode itself, on one region. How it works, file by file, is in docs/SANDBOX-PLAN.md ("How Sandbox works").
- What was tested (`py.cmd tools/neon/sbtest.py`, passes at Fast and Ultra): the kart driven straight at the house wall,
  the three fences, the shed from two sides, the tree under the spiral, a flowerpot, the pipe's side and a post under the
  high track stops at each, not before and not inside; it crosses the lawn, the patio, the goal mouth and the track where
  it lies on the grass; steered along the whole track it follows the track's own heights (260 up the tree and down), rides
  the loop and collects coins; driven off the top of the spiral it falls to the lawn. The mode starts and ends cleanly
  (one kart in, eight back in the menu). Also run in the Safari engine at phone size.
- Regressions after it: Backyard, Kitchen and Margherita races (8 finish, 0 respawns, 0 stuck), Balloon Battle, the phone session.
| What broke while building it | Why | Fix | Keep it fixed |
|---|---|---|---|
| After falling off the high track the camera hung 130 units up and the kart's body stayed tilted | The camera's rise with the track's slope, the drawn ground under the kart and the body's tilt all read the height of the kart's lap point; off the track that is only the last one it was on | In Sandbox all three read `sbG`; the camera's slope rise is skipped while `k.sbOff` | Anything new that reads `track[k.idx]` for looks needs a Sandbox case |
| Crossing the track's edge threw the kart 15 units up | The engine's crest rule launched it (`big` air, light gravity) | In Sandbox that launch is never `big` and starts at 22, not 42 | |
| Coins could not be seen | Sized and spaced in metres of garden; a kart is 12 units | A trail is a coin every 45 units; coins are 4 units across the radius | Think in kart lengths |
- Not done yet (in the plan): the other three rooms, the door passages, the map, the clock, things to do, the shop,
  the PC port, friends in Sandbox. Things in the garden do not move when hit (the football is a wall).

### 2026-11-13 (web v187): a phone's second toy race had a black track; start banners went blank on phones

The owner, with a phone screenshot of Bedroom Blitz: "The track is showing up the wrong color on the hot wheels tracks".
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| On a phone, from the second toy race of a session, the toy track (road and loop) was black with only reflections; the rails kept their colour | On touch devices `freeCanvases()` shrinks every scenery canvas to 1x1 once its texture is on the graphics chip (iPhone memory). The toy code keeps materials, textures and canvases by name between races (`TM`: `MC`, `TXC`, `CC` in `tools/mini/models.js`). `disposeWorld()` throws the chip's copy away at the end of a race, so the next toy race uploaded the emptied canvas | `TM.forget()` (called by `disposeWorld`) drops every kept material, texture and canvas whose canvas was emptied, so the next race draws them again; `TM.can()` and `TM.tex()` also redraw an emptied canvas when asked (for models that arrive late in a race). `tools/mini/patch21.py` | Anything kept between races that reads a canvas must go through `TM.can/tex/mat`, or be told to `freeCanvases` (`userData.keepCanvas` on every texture of that canvas, or `userData.shared`). Run `phonetest.py` |
| On a phone the start banner was blank from the first neon race of a session onward | All three start gantries draw on one shared canvas (`bannerC`); the neon gantry made its texture without `keepCanvas`, so the canvas was emptied and stayed 1x1 | `freeCanvases` never touches `bannerC`; `drawBanner` restores its size; the neon gantry sets `keepCanvas` | Same rule |
- Why no test caught it: every test loaded one track per page, in desktop Chromium, where nothing is ever emptied. New:
  `py.cmd tools/neon/phonetest.py <map> <map> ...` races several tracks one after another in ONE page in the Safari engine
  set up as an iPhone, watches every canvas being emptied and every upload to the graphics chip, and fails if an emptied
  canvas is ever uploaded. Pictures in `scratch/phone_<n>.png`. (WebKit for Playwright is installed in `tools/pw`.)
- One upload it reports as harmless and why: three.js r149's shadow pass has ONE shared shadow material that keeps the map
  of the last thing that cast a shadow (WebGLShadowMap sets `map` on it for every caster) and never tests it; after a world
  is thrown away it re-uploads that leftover once. No pixel changes. The test names it "shadow-pass uploads (harmless)".
- Not a PC matter: the PC build has no canvases to empty.

### 2026-11-13 (web v186, online version 109): Backyard Mega Circuit laid out again

The owner: "There's too many straights on the backyard mega circuit the track needs to be more interesting right now it's
mainly just driving straight". The first layout was one long thin lap of straights. The second (`tools/mini/t_backyard.py`,
its header says what and why) keeps the landmarks and bends everything between: a slalom along the patio, a wide S up to the
goal, two S-bends along the back fence, once round the tree, the drop swung out over the lawn, an S into the drain pipe,
back and forth under the washing line (two hairpins), behind the shed, and a weaving run home. 23 534 units a lap (was
19 996), 63 pieces (was 34); the longest straights left are the loop's run-up (3.3 m) and the one through the pipe (2.6 m).
Tests: forward, reverse and 200cc all 8 finish, 0 respawns, 0 stuck; two laps take about 5 minutes at 100cc (was 4.5).
Props that stood in the new lap were moved (`clearcheck.py backyard`: its list is in garden metres). New menu pictures.
How it was laid out without guessing: a pocket turtle in garden metres (scratch only) printed where each piece ended
against the landmarks' coordinates before the real generator closed the lap; the two straights it solves must not be parallel.

### Where web and PC stand (2026-11-13, end of the session)
- Web v191 (online 109). PC build 06c70bde = web v186 (online 109): PC and web race together. v187 (phone fix), v188
  (Sandbox, first slice) and v189 (the second site's plumbing, switched off) are web only; nothing that moves a kart in a race changed.
- Web only so far: Balloon Battle (v182 to v185). Its PC port is the next PC job, after the owner has played it on the web
  (docs/BALLOON-BATTLE-PLAN.md). Sandbox: the first slice (the back garden) is on the web (v188); docs/SANDBOX-PLAN.md.
- OWED TO THE PC (the owner, 2026-11-13: "make sure to commit these changes to the pc version as well"): Balloon Battle
  (mode, arena, rules as of web v191, the one-line scoreboard) and Sandbox (everything in docs/SANDBOX-PLAN.md that the web has).
  Neither exists in the Godot project yet. Port Balloon Battle first (its rules are settled), then Sandbox once the web's
  reaches every track, so it is ported once.
- OWED TO THE WEBSITE (the owner, same day: "once all the changes are complete lets update the website"): `pc.html` in the app
  repository says seventeen tracks and the old modes. Update it when the PC has the new modes: the count (20 tracks, 4 toy
  tracks, the battle arena), Balloon Battle, Sandbox, new stills; then a fresh trailer if the owner wants one.
- Not checked by eye on the PC: the Blender garden, the garage's open door and front yard, the leaf cards and tree pictures.
  The PC build compiled and its own checks passed; nobody has looked at those scenes in it yet (the exported tracks could
  not be fetched to this machine: there is no `gh` here).
- Still the owner's to answer: the six uploaded car models (web v173 entry); play-tests of the toy tracks' feel and of
  Balloon Battle; which way from the house to the rest of the world Sandbox should use.

### 2026-11-13 (web v182): Balloon Battle, first playable build (web, off line)

The owner's brief: docs/NEXT-MODES-BRIEF.md. The plan, what is built and what is still owed (the PC port first):
docs/BALLOON-BATTLE-PLAN.md. Code: `tools/mini/battle.js` (injected with mini.js), `patch19.py` and `patch20.py` (the engine's
hooks, all behind `BATTLE` or mode `'bb'`), `toyBattle` in mini.js, `tools/blender/battle.py`, `tools/mini/t_battle.py`.

| What broke while building it | Why | Fix | Keep it fixed |
|---|---|---|---|
| Karts left the table over its rim | A kart in the air, or on the raised route, is above a low rim | The table stands in an alcove: tall walls on three sides; over the open front edge is a fall, which costs a balloon | A wall that must hold everybody has to be taller than anything a kart can stand on or jump from |
| CPU drivers stood still for a minute | The test for "stuck" read the speedometer; a kart sliding along a wall or shunting has speed | Stuck is judged by where the kart is: under 14 units in a second, four seconds running, and it is set down on open table | Judge stuck by position |
| A "Lap 2" banner in a battle | Driving round the middle of the arena passes the ring of track points the engine still keeps | Lap banners are off in a battle | New read-outs tied to the lap: check them in a battle |
| Re-storing a model changed the built game | See the entry below (`tables._num`) | | |

Online version: unchanged by this (108). Battle is off line only; hosting or joining a friends' race leaves the mode.

### 2026-11-13 (source only, after web v181): the assets moved out of the source file

The source file had reached 73 MB (GitHub refuses a file over 100 MB) because every model, texture and picture was written
into it as text. The user: "Do what you have to do to be able to make the files fit if you need to compress them that's fine
just maintain quality". Nothing was compressed or changed: each asset is now its own file under `data/`, byte for byte.

| What changed | How | Keep it working |
|---|---|---|
| `crust-rush.html` is 2 MB of code; the four tables in it are declared empty (`const PROP_TEX={};`) | `tools/split_source.py` (the one-off that did it; do not run again). `data/cars`, `data/geo` (a `.json` header and a `.bin` each), `data/tex`, `data/shots` (the picture files), and `data/<TABLE>.order.json` (each table's order) | Never write an asset into the source file again. `from tables import load, save` |
| The build | `build_gh.py` reads the tables with `tables.load` and puts the game's small tables where the `{}` are. `build/extract.js` is no longer used | The built game was compared file by file before and after: every asset identical, the code differing only by four comments |
| The asset scripts | `pack_glb.py`, `put_tex.py`, `car_pack.py`, `embed_shots.py` use `tables`; `tools/assets.py sizes` and `drop <name>` replace the old hand-made counts and removals. PC: `tools/hd_waterfall.py` reads `data/geo/waterfall.*` | A header's numbers are written the way JavaScript writes them (`tables._num`), so re-storing an unchanged model leaves the built game byte-identical |
| The source file cannot be opened on its own any more | It has no assets in it | To run the game locally: `py.cmd tools/neon/webtest.py`, then http://localhost:8771/webcopy6/ |

### 2026-11-13 (web v181): Garage Overdrive's big door stands open

Asked for by the user: "I want the garage door open in garage overdrive with outdoor details that can be seen and the sun
coming in from outside". Looks only (online version stays 108).

| What changed | How | Keep it working |
|---|---|---|
| The door is open | `toyShell` takes the door's opening as its south-wall hole (`dr`, with `noDoor`); the model is `gdooro` (garage.py: the panels under the ceiling on curved tracks, the frame in the wall's thickness) | The strip lights moved north of the raised door (`tubes`) |
| The sun comes in through it | In this room the sun stands in the south: `toyShell({sun:[.22,.5,.84], beam:[the door's opening]})`. `sunBeam` fits the room's shadow camera to that opening | A room's `sun` and `beam` go together: the beam must be an opening the sun can shine through |
| What is outside | `toyFront` in mini.js: real things at real places (drive, lawn, a low brick wall, pavement, street, four houses, fences, ten trees, the sky dome turned so its bright side is south), all marked `sunlit` because they are outside the room's beam | Anything put outdoors of a room needs `userData.sunlit`, or it is drawn as if in the room's shade |
| The garage's window view | Rendered again with the sun in the south (`outside.py -- g` has its own sun): the garden is lit from the front there | If the garage's sun moves, change it in both places |
| PC | `cam.far` is 26 000 on every toy track (the dome is seen through the door); `PROTO := 108` | |

### 2026-11-13 (web v180, online version 108): real trees; Garage Overdrive's bench end and spiral

PC build 1f2fd8dc is level with web v179 (online 107). v180 changes the garage's track heights, so the online version is 108 on
web: the PC needs `PROTO := 108` in scripts/webnet.gd, a track export and a build before PC and web can race together again.

### (the same build, continued)

Second step toward the user's "hyper realism". The trees come from one photo-scanned tree (Poly Haven `jacaranda_tree`, CC0):
`tools/blender/treecards.py` renders it, `treecards_pack.py` lays out and stores the two sheets, `yard.py -- ytreec` builds the
garden tree that carries the leaf sprays as cut-out cards, and `outside.py` stands the real tree in the window views.

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The first leaf sprays were grey, then blue | A mesh copied out of the scan lost its texture coordinates; lit by the sky alone a picture is blue | The sprays are the whole tree seen through a thin camera slab (near and far limits), under plain white light with no tone curve | To cut a piece out of a big scan, clip with the camera; do not rebuild the mesh |
| The leaf cards were black and cream blobs | Lit by the game's sun, cards shadow one another to black and catch it flat to cream; averaged-down copies of the picture fill the holes between leaves | The cards are drawn unlit with the shade and tone baked into their vertices, and the picture has no smaller copies (`generateMipmaps=false`) | Cut-out foliage: unlit, baked shade, no mip levels |
| The crown looked like round pads | Each spray was a thick ball of the crown, solid green with a faded rim | A slab 64 cm deep at the crown's face: single fronds with sky between | A spray must have holes in it |
| GitHub warned on push: `crust-rush.html` is over 70 MB (its limit for one file is 100 MB) | Every model, texture and track picture lives in the one source file as text; this session's scans and models added about 11 MB | Four unused packs dropped (the leaf-polygon trees, the modelled gnome and ball), the brick relief map stored at 1024 | Before adding assets run a size count (CAR_PACKS 25 MB, MAP_SHOTS 22, PROP_TEX 17, PROP_PACKS 8 in Nov 2026). Drop a model's pack when a better one replaces it. If the file nears 90 MB the big tables must move out of it into `build/` files: ask the owner first, it changes how the source is edited |
| Garage Overdrive: karts sank into the workbench just before its end (reported by the user with pictures) | The drop to the spiral began 98 units before the bench ended, so the road went down through the bench top | The lap is level to 14 units past the bench's end (`s6a` in t_garage.py), then drops; the ramp stands on the bench's last stretch; the drop ends at 200, not 170, to keep the slope under .46 | A road on furniture stays level until it is past the furniture's edge. `tools/neon/probe.py` reads any kart value during a race: here the least height over the bench must be the road's own 314 |
| The tyre stack and a fuel can stood in the spiral's edges (reported by the user) | Placed by eye; the stack's 58 cm tyres left 5 units to the inner rail | Smaller tyres (the stack is scaled .78), the can and two paint tins moved, the corner cartons smaller | `py.cmd tools/mini/clearcheck.py garage` measures every loose thing against the lap: run it after moving anything or changing the layout, and add new things to its list |
| The window views would not render | A stray leading space in a script edit | Fixed; the three views were rendered again | Run a script edit's file through Blender before walking away |

Also in this build, switched off: the first hooks for Balloon Battle (`tools/mini/battle.js`, `patch19.py`; the mode's button is
hidden). Every hook is behind `BATTLE`, which only the battle arena sets. See docs/BALLOON-BATTLE-PLAN.md.

### 2026-11-13 (web v179): the whole back garden is modelled in Blender

Asked for by the user ("use blender to actually model the whole outside scene"). While it was under way the user added: "Remember these scenes are supposed to be
hyper realism": judge every scene against photographs. First steps here: three photo-scanned CC0 models (gnome, football, hose) and a rendered sky. All of it is written up in
docs/MINIATURE-MAYHEM-PLAN.md under "Web v179". One Blender source, `tools/blender/yardlib.py`, builds every model; `yard.py`
exports them for the Backyard track and `outside.py` stands the same models in one scene for the rooms' window views and the sky.

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The shed's boards poked through its roof | Square-ended boards on a gable are longer at the bottom than the roof allows at the top; the wall's top board was taller than the eaves | Gable boards are cut to the slope (`_lap_boards`), the last board is cut down to fit | A stepped or lapped part under a slope: size it from its TOP edge |
| The washing hung dead flat | A sheet pinned at its full width has no slack to fold | The cloth is 7 % bigger than the distance between its pegs (`shrink_min = -.075`) and settles in a breath of wind | Cloth needs slack before it will drape |
| The tree's pack was 926 KB and its leaves 9 corners each instead of 6 | A new UV layer gives every face its own default corners, and the exporter splits a vertex wherever any attribute differs | The leaves' UVs are all set to zero | After adding a UV layer by script, fill it; check with a GLB reader what one small part exports as |
| The leaves' shading normals came out wrong (and split again) | A custom normal cannot lean more than a quarter turn from its face: the leaves were wound facing inward | Each leaf is wound to face the way its shading normal points | Wind the face first, then set the custom normal |
| Leaves and far trees were pale, some glinting white | A light green in full sun is over the bloom threshold (as the lawn was); any gloss makes leaves seen against the sun glint | A darker leaf green, roughness 1, no Ultra surface speckle (`noHQ`) | Outdoor foliage: dark base colour, dead matt |
| The shed's window showed an orange glow | Dark glossy glass mirrors the game's stock reflection, which is a sunset | The pane hardly mirrors (`envMapIntensity` .08) | Out of doors there is no picture of the surroundings: keep mirrors dull |
| Scanned grass clumps looked like thin dark wisps on the lawn | They are scans of dry wild grass, darker and sparser than a mown lawn | Dropped; the tufts are the Blender-built green ones | A scan must match what it stands on: look at it in the garden, not only on its own |
| A scanned model faced the wrong way | `turn=180` was given to a model whose front was already -Y | scan.py is run without it; the hose, which hangs on a wall that faces north, keeps it | Look at the check picture: the camera is on the -Y side, so it should show the model's face |
| A race started straight after the menu showed the old code-built garden for the whole race | The Blender models are packs that download after the menu; the room is built once, at load | A toy track's loading screen waits for its packs, 10 s at most and never on line (patch 18, `goRace`) | New late-loading models: nothing else to do, the wait covers every `toy_*_hq` pack |
| PC: the sky dome would not have been drawn | The PC camera sees 14 000 units; the dome is 16 000 out | `cam.far` is 26 000 on an outdoor toy track (main.gd, where the sky is built) | Anything far away added on the web: check it against the PC camera's reach |

### 2026-11-13 (web v178): the garage's walls are painted brick, with fittings built in Blender

Standing instruction from the user, same day: "From now on if you can make something better in blender than with code I
want you to". New or reworked models go through tools/blender first; code-built geometry stays only as the stand-in while
a pack loads, or where code is honestly as good (flat walls, the track).

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| (asked for) the garage's walls were flat paint | One colour and a fine stipple | A scan of painted brickwork (`ph_tex.py`, key gbrick, turned from pale blue to off-white), on the walls and, tinted grey, on the band round their foot | `M.gbrick()`; the wall material must keep a name starting `toy_pt_wall` (the PC finds the room by it) |
| Brick courses would not have met round the window or at the corners | `toyWall` laid each piece's texture from that piece's own middle | With a `tile` it lays the texture by where the piece stands in the room (`wallTile` in `toyShell`) | Any patterned wall: pass `wallTile`; plain paint does not need it |
| The grey band came out charcoal | A grey tint multiplies the scan, which is already darker than white | A lighter tint (#a9afb8) | A tint over a texture wants to be lighter than the colour you are after |
| The hung ladder and the conduit were nearly black | Full metal indoors mirrors only the dim room | Their own material `galu`: mostly paint-like, a little metal | Bright bare metal indoors: low metalness |

### 2026-11-13 (web v176 and v177): Blender-built garage pieces; photo-scanned surfaces

Both are written up in docs/MINIATURE-MAYHEM-PLAN.md ("Web v176", "Web v177"). One PC release covers the two.

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The Blender tyre stack was pure black in the game, and its pack 736 KB | The shade baked into its vertices multiplies an already near-black rubber; every tread block was bevelled | A lighter rubber colour in the game; plain blocks (406 KB) | A model with baked shade wants a lighter base colour than the real thing |
| The track went pastel again with the scanned lawn | The scan, turned green, was pale; a pale lawn in full sun is over the bloom threshold and hazes everything | The lawn's colour is darkened in `ph_tex.py` | Check a bright new surface in a chase picture, not only on its own |
| (caught before any build) the lawn's material would have been made with roughness 0 | A probe call `surfTex('lawn',0,0,0,..)` came before the real one, and the first call makes the shared material | The probes read PROP_TEX directly | Never call a shared-material maker just to ask whether something exists |

### 2026-11-13 (web v175, PC with PROTO 107): Backyard Mega Circuit and the Miniature Mayhem Cup

All of it is in docs/MINIATURE-MAYHEM-PLAN.md under "Backyard Mega Circuit and the Miniature Mayhem Cup".

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The track looked pastel out of doors | The yard's reflection picture was mostly bright sky, and the track is glossy plastic | The yard names no reflection spot (TOYENV null) and uses the game's standard reflections | A reflection picture is for rooms |
| The goal's stays stuck out forwards | The model's back is -z and it was turned half round as well; the stays' lean had the wrong sign | Not turned; lean corrected | Look at each new model from two sides before racing past it |
| The PC's sky was the kitchen theme's sunset | The PC builds its sky from the theme, the web from the track's own background colour | An outdoor toy track takes the exported background colour | main.gd, where the sky is built |

### 2026-11-13 (web v174): Garage Overdrive, the third toy track

All of it is in docs/MINIATURE-MAYHEM-PLAN.md under "Garage Overdrive". PC: `maps.yml` exports tracks 0..22.

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The road on the workbench could not be seen: karts drove on bare wood between the rails | The track's height there was 312, exactly the bench top's | 314 | A track lying on furniture is 2 above the surface (the kitchen's worktop 312 / track 314, table 260 / 262) |
| The glossy track washed out to white along the plank | The strip lights' glow (1.6) goes into the room's reflection picture | .55 | Anything that glows in a toy room is also in its reflections: keep emissive strengths under 1 |
| A vice and a toolbox stood on the track | Placed by eye on the bench | Moved; the strips the track takes are written in `toyGarage` | Look at a fixed-camera picture of every surface the track crosses before publishing |

### 2026-11-13 (web v173, PC with PROTO 105): six new cars from the user's models; the flame tip had no position

**The six cars** (Cars tab of the garage; ids `skywing`, `megagt`, `megawatt`, `endur`, `slip`, `retrogt`; names Skywing,
Mega GT, Megawatt, Endurance GT, Slipstream, Retro Racer). The user uploaded six downloaded models of real cars. They are in
the game the way the earlier cars are: a made-up name, no badge, plate, sticker or texture of the original (the game paints
them itself), so the "no copyrighted names or logos" rule holds. WHAT IS NOT SETTLED: the models themselves are other
people's work (their material names show they were taken out of commercial racing games) and no licence came with the
files. That was put to the user in the session's report; if the answer is "take them out", see "Removing a car" below.

How a car gets in (all of it is scripted, nothing is done by hand in Blender):
1. Unpack the model into its own new folder under `scratch/cars_in/` (never run anything from it).
2. `tools/blender/car_inspect.py -- <model>` lists its materials with where each sits on the car.
3. Add the car to `tools/blender/car_rules.py`: which material is paint, glass, lights, which trim colour, cabin, wheel.
   Always drop badges, plates, stickers, displays. Ids must not be the id of ANYTHING else in the game (see the table).
4. `sh tools/blender/car_all.sh <id>` converts it (about a minute) and makes `blender/cars/<id>/sheet.jpg`: look at it.
   `rules.txt` beside it says what each material became and where it lies, which is how a wrong rule is found.
5. `py.cmd tools/blender/car_pack.py <id>` puts `<id>` and `<id>_hq` into CAR_PACKS.
6. Add the car to `CARS` in `tools/cars/patch_cars.py` (name, description, stats, seat, roof, pipes) and run it. It writes
   the body list, the car's definition, the Cars tab and the engine sound; running it again replaces what it wrote.
7. `tools/neon/cartest.py <tag> <id>` photographs it in the garage (env Q, ROT, ZOOM, PITCH, LIV, PAINT);
   `BODY=<id> ... simtest.py` and `chase.py` race it. Bump NET_PROTO on web and PROTO on PC (a new body changes what
   two players must agree on), publish web, then the PC release: the PC gets the bodies from the garage export by itself;
   only `ENG_BODY` in `scripts/sfx.gd` is written by hand.

Removing a car: take its line out of `CARS` and run `patch_cars.py`, delete its two entries from the CAR_PACKS line
(car_pack.py shows the format), bump NET_PROTO/PROTO. NEVER remove one from the middle and leave later ones: a saved or
networked build holds a body's INDEX, so every body after it would turn into its neighbour. The six are the last six
bodies, in the order above; removing all six, or the last ones, is safe.

| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Long stray triangles sticking out of the first converted car | A group of thousands of loose pieces (a cabin) was asked to shrink to 2%: the simplifier bridges pieces | The smallest loose pieces are removed first so no group is asked for less than a tenth, and any triangle that ends up away from the original surface is dropped | `simplified`, `keep_largest`, `Ref.near` in car_convert.py |
| Tyres came out as ten-sided polygons | A simplified tyre has too few triangles left to be round | Each tyre is only measured (centre, radius, bead radius, width) and rebuilt as a clean lathe of the same size | `lathe_tyre` |
| The first pack was three times the size of the existing cars | Normals looked up per triangle differ a hair, so no two corners shared a vertex | Corners of a vertex that agree within 24 degrees share their average | `unify` |
| The ground showed through the windscreen | A cabin cut to 900 triangles loses its floor | Every car gets a plain dark tub under the cabin, facing inward (seen only through the glass) | `tub`; `tub=False` or five numbers in the car's rules to override |
| The far model was a crumpled wreck | Snapping vertices to a grid at 880 triangles | Blender's simplifier is used first; the grid only when that stops at more than 3.5 times the budget | the "far" block of `convert` |
| Lit displays in the cabin became white head lamps | One material held lamps and displays | Per-car rule: front part light, rear part tail, the middle dropped | the `megawatt` rules |
| Running the definitions script twice moved the new bodies into the WHEELS list and deleted the livery "70s Stripes" | It cleared its earlier lines by matching `{id:'<id>'` at the start of a line: that also matched the livery with id `retro`, and removing the last line took the list's closing bracket with it | The script's lines now sit between `/*cars6...*/` and `/*:cars6*/` marks and only those are cleared; it refuses to run if an id is already used; the car was renamed `retrogt` | Read `git diff -U0 crust-rush.html` after any script edits the source: it must show only the lines meant |
| New bodies were first put at the end of the BODIES list, which is not the end of the bodies | Four karts are added later by `BODIES.push(` | The new ones are pushed after that block | A build holds the body's index: new bodies go after EVERY existing one |
| "Computed radius is NaN" in the console; boost flames missing their tip | `flameGeo`: at the tip `sin(pi*(.16+.84*v))` comes out a hair below zero and a negative number to the power .75 is not-a-number, so the tip ring of both flame meshes had no position. Patch 16 had fixed the normals there but not the positions | `Math.max(0, sin(..))` | The check in the scratch test `nan2.py` idea: traverse the scene for meshes whose bounding sphere is not finite. A NaN anywhere in a geometry is a bug even when it draws |

Tests for v173: boot clean; every car photographed in the garage on Ultra and Lite, with two liveries; races with the
player in a new car on bedroom, kitchen, margherita reverse, laser, synth 200cc (8 finish, 0 respawns, 0 stuck).

### 2026-11-13 (web v170): black dots in the boost flames on phones (patch 16)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Black dots and blobs in the boost flames on an iPhone (the user's screenshot; never seen on the PC's graphics card) | `flameGeo` closes the flame to a point at its tip, where the triangles have no area; `computeVertexNormals` gave 30 vertices of the inner flame a not-a-number direction, the shader's brightness came from it, and phones draw not-a-number as black (the glow pass spreads it into blobs). A desktop card silently drops such pixels | Directions are set from the shape (always defined); the shader works its own out from the vertex position; colour and alpha are clamped before drawing | Never call `computeVertexNormals` on a shape with a closed point. Any new shader: clamp what goes into `pow` and what comes out. Desktop pictures cannot show this fault: check the mesh for bad numbers (`scratchpad/nancheck.py` did) |
| A trail of large glowing dots hung in the air between the camera and a boosting kart | The boost sparks (an older effect) and the new embers were thrown backwards at a fixed speed over the ground, so the kart drove away from them and they sat near the camera, drawn large | Both now leave the pipes at that speed relative to the kart (web and PC) | Particles meant to stay with a kart must inherit its speed |
The PC's flame shader never had the first fault (its mesh is built with defined directions).

### 2026-11-13 (web v169): motion blur back to its original strength, wind lines instead (looks only, patch 15)
The user on v168: the rainbow effect on Neon tracks is "perfect", do not change it; the stronger blur was not wanted ("dial the
motion blur back to how it originally was... add more wind screen effects so it feels more immersive instead of increasing the blur").
- Blur strength is .07 again with its original falloff (web final pass, PC post.gdshader). Do not raise it again.
- Wind lines (`wind()` in both shaders), shown only with Settings > Motion blur on: two layers of fine pale lines flowing outward,
  driven by the same speed value as the blur (`mb`), kept off the middle of the screen, and switched off while the Neon rainbow
  streaks show (`1 - rbw*spd`), so that effect is exactly as it was.

### 2026-11-13 (web v168): boost flames, stronger motion blur, rainbow streaks on Neon tracks (looks only, patch 14)
The user gave reference pictures from another kart racer for the flames: take the idea (a blue jet at the pipe, yellow then orange,
ragged licks, a glow on the road), never its art, names or characters.
- Flames: `flameGeo` (a teardrop tube) and `flameShMat` (a small shader: wavering outline, licks, blue jet, colours from FLAMEC by
  drift tier). Two per pipe (outer, inner) as before, plus a glow on the road (the LAST entry of `m.flames`, `userData.glow`) and
  embers. PC: `shaders/flame.gdshader`, `View._flame_mesh`, the glow from the garage export's `fglow`.
  Gotchas met on PC: a `source_color` uniform must be given a Color (a Vector3 came out pale); additive colour is far brighter
  under the PC's tone mapping, so the PC shader scales it down; ember size 0.45 there (0.55 on web).
- Motion blur: strength .07 -> .095 and it starts a little nearer the middle (web final pass and PC post.gdshader).
- Neon Cup tracks: the boost streaks are rainbow (`rbw` in the final pass; PC `T.neon` from the export's `neon` flag). They show on
  every quality that has the post pass on Neon tracks; other tracks keep the white streaks on Ultra only.
- `glbexport.js` must skip the glow when it lists a kart's flames (it filters `userData.glow`): otherwise the PC would treat the glow
  as a third flame.

### 2026-11-13 (web v167): easier rivals on toy tracks; the garage shows stats the PC's way
- The user had not won a race on Bedroom Blitz at 200cc ("so many items and specials close together, hard to keep a lead").
  Engine patch 12, toy tracks only, every class: computer drivers' top speed 3% lower (skill -0.03), `ahead` x0.97, `behind` 60% of
  its push, `corner` x1.25, `boost` x0.7, item `delay` x1.5, and `abw` 1.8 (the wait before a special). Set in `loadMap0` beside
  the Neon tracks' sharper numbers. The PC gets them through the exported `diffs` (and reads `abw` in race.gd).
  Computer drivers only, so the online version did not change. Still for the user to judge: whether 200cc is now winnable.
- Garage stats (patch 13, display only): a vehicle's card shows its own stats as plain values out of 12 (`valueChips`,
  `statBarsOf(b,false)`); wheels and gliders keep plus/minus chips; the panel shows the vehicle's bars in orange, what wheels and
  glider add in green and take away in red, and that change as the number (`showStats`). Scale as on the PC: 6 + soft x 1.5, 0..12.
  `statMods` (what the race uses) is untouched.

### 2026-11-13 (web v166, PC with PROTO 104): items, from the user's play-test of Bedroom Blitz
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| One kart took a whole row of item boxes on Bedroom Blitz and nobody else got any | A row's boxes stood 12.7 units apart (the regular spacing scaled to the half-width track), inside one kart's 16-unit reach; they took 4 s to come back | Toy tracks: boxes 21 units apart across the track and stepped along it (26 between any two), a kart that takes a box cannot take another for BOXCD = 0.6 s, boxes come back after BOXR = 2 s (engine patch 11) | Any new toy track gets this from the toy flag. Box positions are track data: re-export for PC |
| A homing anchovy hit a kart twice: once, then again the moment its 3 s of protection ended | The item and Anchovy's special circled a protected target and waited | An anchovy that reaches a kart still protected after a spin is used up with no effect, like other items (special: `p.sure` branch; item: target check in the kart loop). It still waits out Pesto Rush, Fire Trail and the other untouchable abilities, as before | The user asked for the protection case only |
| Olive's own slicks caught Olive | Only the first moments after dropping were safe (`armed`) | An olive slick never catches its owner (host loop and the guest's own check); the owner sees their own slicks in blue with no warning sign (`hazDecorate(mesh,kind,mine)`) | |
| Olive's trail was too long for the small toy tracks | Ten slicks whatever the track | SLICKN: 7 on toy tracks, 10 elsewhere; she is untouchable for as long as the trail takes to lay | |
| PC only (found while porting): an item box could be taken from the road above or below it on multi-level tracks | The PC's box check had no level test (the web has one) | `race.gd`: the same 18-unit level test | |
BOXR, BOXCD and SLICKN are set in `loadMap0` beside TURN, DRIN and DROUT, and exported to the PC with them (`glbexport.js`, `track.gd`).
PC tests: `tests/items.tscn` (these rules) prints the numbers the track brought.

### 2026-11-13 (web v165, PC with PROTO 103)
Handling on toy tracks, from the user's play-test of Bedroom Blitz ("turning a little too sharp"; "drift exit a little quicker";
"enter and exit drift slightly faster than the other tracks... probably how all the toy tracks have to be"):
- TURN 2.64 on toy tracks (x1.2; it was x1.3). DRIN 2.6 (a drift builds to full in 0.38 s; 1.75 elsewhere). DROUT 0.6 (a factor on
  the times that end a drift: 0.18 s with the stick straight instead of 0.3 s, 0.3 s instead of 0.5 s with the button held, grip back
  after 0.15 s instead of 0.25 s). All three are set in `loadMap0` from the toy flag, so every toy track gets them.
- PC reads TURN, DRIN and DROUT from the exported track (`glbexport.js`, `track.gd`), so the numbers can only differ if the export is stale.
- Still to be judged by the user: how it feels. The self-driving races pass either way; they cannot judge feel.

### 2026-11-12 late night (web v157, PC build with PROTO 102)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A trap on an upper road caught karts driving directly underneath (multi-level tracks) | The trap hit test compared map positions only | Web: traps use the level check thrown items already had (`sameLvl`, engine patch 8); a trap's road point (`ti`) and height are fixed on its first step; a guest uses the height of the host's copy. PC: `haz_ti`, `haz_ground`, `same_lvl` in race.gd. NET_PROTO and PROTO 102 | Same rule and the same 18-unit threshold on both. `tests/hazlvl.tscn` (PC) checks it; the web check is the same numbers (bedroom 262, holo 178) |
| PC: dropped traps lay on the floor under raised road | Drawn at ground height (same bug as the web had) | view.gd draws them at `race.haz_ground` and along the slope; the host sends that height to guests | |
| PC: thrown items of one kind stopped every thrown item being drawn (2,000 script errors a race) | `String(pd.get("ph"))` in view.gd: "ph" is a word on some items and a number on others, and String() of a number is an error in Godot 4 | `str()` | Run the PC race test on a track where every item gets used (bedroom), not only the default track; CI fails on any SCRIPT ERROR |
| PC: the track looked dull and speckled although made glossy | `HdSurface` (Finished models) laid mottling and grain over the plain plastics and replaced the pictured road with its relief shader, losing the lacquer shine | `HdSurface._moulded`: materials named `toy_toy...` are left alone | New toy-set plastics keep the `toy_toy` name prefix |
| PC: the sun lit the whole room again after any graphics setting change | `_apply_quality` resets the sun's shadow range and can switch shadows off | `_toy_sun()` runs at the end of it: on a toy room shadows stay on and reach across the room | Anything a room needs from the sun goes in `_toy_sun()` |

Releasing to PC after a web release (learned 2026-11-12, the order matters):
1. Web is published first. Then push a change to `.github/workflows/maps.yml` with `[quick]` in the message: that starts the track export
   (about 10 minutes) and does not start a PC build.
2. Wait for the export AND for any PC build already running (two PC builds running together can replace the public download in the
   wrong order).
3. Push a PC commit that changes a script, without `[quick]`, as the newest commit. A push whose newest commit says `[quick]`, or that only
   changes README.md or the workflow files, builds nothing public.
4. Check `releases/download/pc/pc-build.json`: its "build" is the first 8 characters of the commit that was built.
Known small difference on PC: brass handles look near black (metal mirrors the dim room); the web shows them as brass.

Release scripts (2026-11-13): `tools/release_web.py "<title>"` publishes the built app and bumps the stamp;
`tools/release_pc.py "<title>"` does the PC steps above in order (export, wait, build, wait) and takes about an hour: run it in the
background, one at a time. Both refuse to push if someone else has pushed.

PC toolchain on this PC (2026-11-12): Godot 4.7.2 at `D:\crust-rush\tools\godot` (console exe for headless tests). Tracks, garage and
textures come from the public `maps` release (download with curl into `godot/maps`, `godot/assets/garage`, `godot/assets/hd/cc0`); a single
track can be exported locally with `WEB=D:/crust-rush/app OUT=D:/crust-rush/godot/maps MI=<n> py.cmd tools/ciexport.py`.
`tests/room.tscn` photographs a track from fixed cameras (same camera numbers as the web's `shots.py`), `tests/hazlvl.tscn` checks trap
levels, `tests/smoke.tscn` drives a race (its pass rule wants 3 loops, so it "fails" on tracks without loops even when the race is clean).
There is no `gh` on this PC: the track export is started by pushing a change to `.github/workflows/maps.yml` (use `[quick]` in the message
so the PC build of that push does not publish), and runs are watched through the public GitHub API.

### 2026-11-12 late night (web v156)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The bed reached into the east wall (user's report), and its headboard into the wall behind it | The frame was always 10 units into the east wall and 7 into the south wall (placed by eye); the Blender bed's duvet hung further out and made it obvious | Bed moved to (412,-460); on the wall side the duvet stops at the mattress edge; nightstand, mug, books and backpack moved with it | Measure, do not eyeball: `pack_glb.gather` gives every part's extent, compare with the walls (x 695, z 833) before a model goes in |
| Moving the bed put a leg on the edge of the track that runs underneath | Legs were set 5 cm in from the frame's corners | Legs are at the corners (Blender bed and the code-built stand-in): 8 units clear of the track's wall | The track under the bed pins the bed: its east legs must stay at x 671 or more. Check legs against the centre line after any move |
| White dashes were on the road (user: they belong on the walls) | Drawn into the road texture | Dashes are geometry on the walls' top and inner face (`toyRails`), one every 120 units | |

### 2026-11-12 night (web source for v155, from the PC session; published as v155)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Dropped traps (olive slicks, oil, forks, pizza boxes, fire) lay out of sight under raised road and still hit karts driving above them (Bedroom Blitz spiral, desk and climb; any multi-level track) | They were drawn at floor height (`groundAt`) with no allowance for the raised road; the hit test only compares positions on the map | `hazEy(h)` (engine patch 6) works out the road height once, from the level the owner was on, and tilts the trap to the slope; the draw loop adds it. Hit test unchanged, so online play is unaffected; guests get the height through the mesh record | Anything placed on the road at run time must add the road height (`kEy`) on multi-level tracks. Still open: the hit test has no height check, so a trap on an upper level can catch a kart directly beneath it. Fixing that changes race results: do it on web and PC together with a version bump |
| Racers started with an item on two Neon Cup tracks (holo, synth) | A row of item boxes was placed 14 and 17 track points before the start line, inside the grid (and just past the line in reverse) | `boxClear` (engine patch 7) moves any box row out of the start zone; NET_PROTO 101 | New tracks: no box row above about .95 of the lap or below .04. Check with the box measurement (every map, both directions) before publishing track changes |
| A stack of books stuck up through the start of the climb on Bedroom Blitz | Its position came from a straight-line guess at the climb's height; the real road eases in and is lower there | The stack is placed from the track's real height (lowest point that clears it, then 48 units further up); that pier's posts stand close in, on the books | Place anything under a raised road from `track[j].ey`, never from a formula; photograph it from the side |
| The side monitor's screen went through the curtain and into the wall | Angled screen placed too close to the wall | Moved forward to y=748 | After placing props, look along every wall for things passing through it |
| Raised track edges kept a dull, speckled finish after the track was made glossy | `TM.mat` caches materials by name and the spare track piece in models.js defined `toyorange` first with the old settings; separately, merged scenery swapped the rails' material for a plain batch material | Both definitions made identical; rail meshes marked `noMerge`; track plastics marked `noHQ` | One definition per material name; a mesh that needs its own material must be `noMerge` |

### 2026-11-12 (web v153 and v154, PC build b2abf99)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Karts sank through the road at fixed spots and respawned under it in a loop (Bedroom Blitz desk; could hit any neon or arena track) | Pool hazards (`PONDS`) were only cleared in `planPonds`, which arena/neon/toy maps never reached, so pools from the *previous* track stayed active at their old coordinates | `makeHills` now calls `planPonds(def)` on the arena branch too | Any per-track state must be reset on *every* map type. When adding a map type that returns early from a builder, check what the skipped code resets |
| Kart wobbled, bounced and sat sunk in the road on the tight spiral | `kEy` (road height under a kart) projected the kart onto straight segments between track points; on a tight bend the segments overlap on the inside and leave gaps on the outside, so the height stepped at every point | On toy tracks the height is worked out along the bend (curvature-corrected distance from the nearest point): web `kEy` (TOYT branch), PC `TrackData.k_ey` (toy branch) | Same formula on web and PC. Spirals: radius 150 or more, slope about 0.2 |
| Camera too low on descents: the road behind filled the view | The chase camera sat a fixed height above the kart's own road height; on a slope the road behind is higher | Toy tracks: camera rises by the height of the road behind and looks along the slope ahead (web `cSA`, PC `cam_sb`/`cam_sa`) | Check the chase camera with `neon/chase.py` on every new slope, not only free-camera photos |
| PC only: camera sat far below the kart on every raised road (found while porting) | PC `_camera` used the terrain height without the raised deck (`rg`), web adds `kEy` | `rg = T.ground + T.k_ey` when the track is multi-level | Port camera code line by line; test the PC chase camera on a raised road |
| Leaves poked through the track | Plants placed under or beside raised track without checking their spread | Plants and book stacks moved clear | After placing props, take a top-down photo of every stretch; nothing within the rails, nothing under a low deck |
| Shortcut had gaps in its walls; a booster housing blocked its exit | Rails were dropped within a fixed distance of the junction; housings were placed before shortcuts existed | Rails are now clipped exactly where they cross the other lane (`toyRailClip`), housings are built last and skipped within 40 units of a shortcut | Junctions: both rails must meet; build decorations that depend on shortcuts after `neonShortcuts` |
| Track on the desk was invisible (only the rails showed) | The road was drawn at exactly the desk-top height and the desk top is slightly higher | Desk sections run 2 units above the desk (h=262) | Any road on furniture: 2 units above the surface |
| Toy track too hard to drive at 19 cm wide | Narrowed on request, then found too tight with tight bends and many boosters | Back to the first width (rw=31), bends at least radius 100, spiral radius 150, fewer boosters, steering 30% quicker on toy tracks (`TURN`, exported to PC) | Road width, bend radius and booster count are tuned together; test by driving, not only AI races |
| Orange track looked washed out from above (web) and pale on PC | Sky reflections on glossy plastic indoors | Web: low `envMapIntensity` and clearcoat on the track; PC: `HdToy` turns the mirror strength down on indoor materials | Indoor materials must not mirror the outdoor sky |
| PC only: orange track turned pale yellow in direct sun | The PC's sun is about twice as strong as the web's on this bright, saturated plastic and the tone curve bleaches it | Toy tracks: sun x0.5, room fill x1.25 (`main.gd`), no vivid-look changes | Compare PC and web pictures of the same view after any lighting change |
| Rug hid the track | Rug is 4 units thick; road is drawn at floor level | Rug moved clear of the track; things standing on the rug are lifted by its thickness | No floor covering under a track unless the road is raised above it |
| `gh run download` fails here | Artifact storage host is blocked from this sandbox | CI job `shotspub.yml` zips a run's artifacts onto a scratch pre-release (`shots-tmp`), fetched with `gh api ... releases/assets/<id>` | Use that route for any CI artifact |

### Earlier (kept from previous sessions)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Photo rig never produced frames | The game does not draw in state `paused` | Hold the race with `state='countdown'; cd=1e9` | Never pause to take pictures |
| Two heavy renders at once killed the job (exit 137) | Out of memory | One swiftshader browser or one local Godot render at a time | Same rule in CI: at most 8 photo jobs so the PC build is not starved |
| Game would not boot after adding toy code | `cm` and `can` clashed with existing names | Renamed (`tcm`, `sodacan`); `webtest.sh` syntax-checks, `boottest.py` checks the menu comes up | Run both after every source edit; models must not share a name with a helper exported from `TM` |
| Neon shoulders drew orange | A non-arena `else` branch also ran for neon maps | `else if(!def.neon)` | New map types: check every `else` that assumed "normal track" |
| A release was stamped with the old version | Build script run with the previous stamp | Version lives in `neon/webtest.sh`; bump it straight after publishing | Check `sw.js` for the version before committing |
| Fire blew out to white (PC) | Additive blending | Premultiplied alpha at half strength | |

## How to test before publishing
1. `neon/webtest.sh` (syntax check + build), `neon/boottest.py`, `neon/loadtest.py <track>`.
2. `neon/simtest.py <track> medium 230` and `reverse`: all 8 finish, 0 respawns, 0 stuck.
3. `neon/chase.py` (the game's own camera round the lap) and `neon/shots.py` (free camera) for looks.
4. One regular track as a regression (`simtest.py margherita medium 200`).
4c. Sandbox: `neon/sbtest.py`, then `neon/sbtest.py bedroom`, `kitchen`, `garage` (any change to the kart's physics, the toy
    tracks or rooms, a room's furniture, or battle.js): SANDBOX TEST passed in each.
4b. A phone session: `neon/phonetest.py bedroom kitchen bedroom margherita grid bedroom` (any change to textures, materials,
    scenery caches or track loading): PHONE TEST passed, and look at `scratch/phone_*.png` for the repeat visits.
5. PC: export from CI, `tests/tmp_neon` (AI race), `tests/tmp_cam` (pictures), then push.

### 2026-11-12 (move to the Windows PC)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Risk: a build on Windows would change every published file | Git for Windows converts line endings on checkout (`core.autocrlf=true`), and the build hashes file contents | `core.autocrlf false` in the repo, files checked out again, `.gitattributes` with `* -text` on `source`; a fresh build then differs from `main` only in the version stamp | After cloning anywhere new, set this before the first build and check `git status` in `app` after building |
| Risk: `inject_mini.py` and the patch scripts would rewrite the whole source with Windows line endings | They opened the source in text mode; on Windows Python turns every line ending into CRLF on write | `inject_mini.py` and `patch4.py` open files with `newline=''` | Any script that writes `crust-rush.html` or the files in `tools/mini` must pass `newline=''`; check `git diff --stat` shows only the lines you meant to change |
| Scripts could not run on Windows | Cloud-workspace paths, a bash build script, the software renderer flag | `tools\port_paths.py` rewrote the paths to `D:\crust-rush`, `webtest.py` replaces `webtest.sh`, `py.cmd` sets UTF-8 and the browser path | Run scripts through `py.cmd`; plain `python` reads files as cp1252 and can corrupt the source |
