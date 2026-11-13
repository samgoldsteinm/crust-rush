# Crust Rush handover: read this first every session

Purpose: a running record of what broke, why, and what fixed it, so a fix made several updates ago is not undone by
accident and so old fixes can be reused. Add an entry whenever a bug is fixed. Newest entries first. Keep entries short:
**what broke / why / fix / how to keep it fixed**.

## Where things are
- Web game: one source file `crust-rush.html`, built into the app repo (branch `main`). PC: Godot, branch `godot`.
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
5. PC: export from CI, `tests/tmp_neon` (AI race), `tests/tmp_cam` (pictures), then push.

### 2026-11-12 (move to the Windows PC)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Risk: a build on Windows would change every published file | Git for Windows converts line endings on checkout (`core.autocrlf=true`), and the build hashes file contents | `core.autocrlf false` in the repo, files checked out again, `.gitattributes` with `* -text` on `source`; a fresh build then differs from `main` only in the version stamp | After cloning anywhere new, set this before the first build and check `git status` in `app` after building |
| Risk: `inject_mini.py` and the patch scripts would rewrite the whole source with Windows line endings | They opened the source in text mode; on Windows Python turns every line ending into CRLF on write | `inject_mini.py` and `patch4.py` open files with `newline=''` | Any script that writes `crust-rush.html` or the files in `tools/mini` must pass `newline=''`; check `git diff --stat` shows only the lines you meant to change |
| Scripts could not run on Windows | Cloud-workspace paths, a bash build script, the software renderer flag | `tools\port_paths.py` rewrote the paths to `D:\crust-rush`, `webtest.py` replaces `webtest.sh`, `py.cmd` sets UTF-8 and the browser path | Run scripts through `py.cmd`; plain `python` reads files as cp1252 and can corrupt the source |
