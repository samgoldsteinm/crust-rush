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

### 2026-11-18 (web v224 / PC, not released yet)
- GARAGE IS A REAL WORKSHOP (81, web). The owner: the paint's sides were still flat ("lacking stuff to reflect"); "make high quality 3d
  models and make the garage look very realisitic". gStudioSet: the Garage track's scanned Blender models at real size (1 m = 2.7
  units; TM.U is units per CENTIMETRE: scale K/(TM.U*100)) round the turntable, concrete and brick on new materials over the track's
  scanned pictures, LED panels and an LED strip (HDR); the car's reflections are made from that room (PMREMGenerator(gR).fromScene),
  rebuilt on opening until every scanned model has downloaded. Zoom out limited to 1.1 so the camera stays inside.
- RIMS = THE SPOKES, CALIPERS THEIR OWN COLOUR (82 / pc85; the first takes pc82 / pc84 painted too much: pc82 went out in the v223 PC
  build). The owner, in turn: the rim colour "only changes the brake drum"; "the entire wheel shouldnt change colors only the brake
  caliper and the wheel spokes"; "still have colored brake rotors/drums"; "make it so you can pick a different color for the spokes and
  calipers ... figure out exactly what the spokes and calipers are on a wheel". Measured every wheel (scratch/paint/wheelan.js: each
  colour class's spread from the axle and depth along it; wheelqa3.py pictures the wheels alone): the spokes are ONE class per wheel
  (WHEEL_SPOKES, web and PC kart_builder.gd: 'rim' 11 by default; chrome 10 suv, retrogt, the bikes; dark 1 concept, chariot; carbon
  6 skywing; steel 21 the toy karts; wheel sets red 17 / green 16 / bluem 18 / bronze 19); the rotor is disc 12 or metal 7 / gunmetal
  15 (never painted now); the 'rim' class also holds the lip and barrel (and the Monster's tread), so only its part inside the tyre is
  painted (cut: the tyre's inner radius less 5% of the wheel, at least 45%: rimVC uCut per wheel geometry, PC _style_vc on the
  vertices). Calipers: a car body's class 13 and forged's red 17 (WHEEL_CAL), painted by the new Calipers row (slot 'cl', trim list)
  instead of the accent. Code-built kart wheels: spokes only (M.rimS / PC g_paint). Keep: a new wheel's spoke class goes in
  WHEEL_SPOKES on BOTH; check it with wheelqa3.py. tests/ugshots.gd takes UG_ST (a style as JSON).
- FLYING CAMERA (83 / pc83 + pc84). The owner: flying, the camera "only moves up and down and it struggles to follow"; then "sit lower
  behind the user". The chase camera aims between the kart and the ground under it: far below a flying kart. Flying: cy = rz - 8 (the
  race camera low behind the kart, looking ahead).
- INTERIOR COLOUR = SEATS (web v225 data, PC via the export). The owner: the interior colour changed "the literal inside of the cars
  but not the interior assets"; "as long as it won't slow down the game do that for the car models". Why: car_convert squeezed the whole
  cabin into 900 triangles and cleared small pieces first, so seats vanished (Megawatt and Slip kept 20 seat points), and the rules filed
  roof-lining, pillar, steering and belt fabric as 'seat'. Now car_convert gives the seats their own group ('seat', budget 700 / HQ 1800,
  small-part limit .04, packed into b_vc with the cabin: the game reads it as before) and car_rules.py (first match wins) files only
  seats (and Retro GT's centre console) as int:seat for the six cars with sources here (endur, skywing, megagt, megawatt, slip, retrogt;
  re-imported with car_all.sh + car_pack.py; +about 700 triangles a car; wheels identical, checked, so nothing that moves a kart changed).
  Left as they are: a stray flat panel or two that the sources tag as seat fabric (Megawatt, Skywing, Retro GT's door cards). The older
  cars (Scissor, Muscle, Hatch...) have no sources here and may be the owner's own uploads (never re-import those): their 'seat' class is
  the whole cabin shell on some (Scissor, Muscle). Pictures: scratch/paint/cabinqa.py (body and glass hidden, red interior).
- SEATS ON THE OLDER CARS (web v226 data, PC via the export). The owner then uploaded the original models of ten older cars (Bentley =
  coupe, Escalade = suv, Aventador = scissor, Camaro = muscle, Pontiac monster = monster, AMG One = onyx, Sprite = roadster, Veyron police
  = interceptor, chariot, Neutron = bike_neutron; the Jesko upload is the Skywing's own source, already done). NOT re-imported: those
  packs came from an older pipeline and are the owner's look. tools/blender/seats/ uses each source only as a map (fitted to the pack),
  and changes only the CLASS of the pack's cabin triangles: seat 9 where the source has seats, dark 1 for the rest of the old class-9
  shell (both near-black by default, so nothing looks different until an Interior colour is picked). chk.py: every triangle and the
  wheels identical, so no NET_PROTO change. The Escalade's pack had no seats at all (hollow cabin): its own seats were added (decimated,
  1326 triangles, HQ 1799, class 9). Left: the Neutron (its saddle is body paint in the pack), the Bentley's rear (none in the source).
  How and which parts: tools/blender/seats/README.md. Keep it fixed: a new car goes through car_convert (its seat group); an old pack is
  re-labelled with transfer.py, never rebuilt. Test pictures of the Chariot need the garage's default camera (gZoom .55 shows nothing).
- CLASSIC KART'S SPARE SLICE + GARAGE CEILING (87, web v227; PC kart body via the export). The owner: "The pizza slice is messed up on
  the side of this kart also if you move the camera too high in the garage you run into the ceiling". (1) The slice strapped to the
  Classic's right pod points forward with its crust end at x -.3, but two pepperoni (x -.8, -.4) and the rear strap (x -1.1) were placed
  behind that end, floating on the pod. Now the pepperoni sit on the cheese, both straps cross it and a crust (KG.crust) runs along the
  wide end. Keep it fixed: KG.slice rotated -PI/2 about z runs from its base at the given x forward by 6.45 x its scale; decorations go
  inside that triangle. (2) frameGarageCam had no height limit: pitch up to .22+1.1 rad at 1.1x zoom put the camera ~20 units up, above
  the studio's LED panels (bottom 14) and ceiling (15). Now the camera stays at y <= 12.6: it comes closer first (not nearer than 1.7 x
  the car's radius), then the tilt stops. Keep it fixed: if the studio's H changes in gStudioSet, move yM with it. The PC garage has no
  room, so its camera needed nothing. Test: scratch/paint/sliceqa.py (camera y printed at full tilt).
- CALIPERS SPUN WITH THE WHEELS (88, web v227; PC pc86 + export). The owner: "the brake calipers are spinning with some of the wheels
  ... test this for all cars and wheel types". Why: the downloaded wheel models hold what sits inside the wheel (the caliper on every
  kart wheel set and the Monster wheel; on Muscle, Monster, Retro GT, Onyx, SUV, Hatch, Tourer; the GT's, Roadster's and Onyx's hub
  carrier or strut; brake parts and a fender arc on the bikes) in the same mesh, under the spinning group. Fix: wheelHold(geo, pack)
  splits each wheel model into what rolls and what is held (connected pieces not repeated round the axle and under 200 degrees, per
  WHEEL_HOLD's rule for that pack; the MX bike's hubless ring: everything inside it); holdOut puts the held part in the steering group
  (yaw). The held part's material makes its caliper classes take the Calipers colour (a wheel set's caliper shared its class with the
  spokes and took the Rims colour). The cars whose calipers are in the BODY (Hyper, GT, Interceptor, Scissor, Endurance, Skywing,
  Mega GT) already stood still. PC: glbexport.js exports the held part as ph<i> / hold_L / hold_R; kart_builder puts it in
  'wheel_XX_hold' beside the wheel; view.gd steers it. Keep it fixed: a new wheel model with a caliper needs a WHEEL_HOLD entry (find
  the pieces with scratch/paint/calan.js and calsheet.js, check with holdtest.js: every body on every wheel type, two spin angles).
  The PC needs the same caliper classes in kart_builder HOLD_K as the web's WHEEL_HOLD k.
- ACCENT CHANGED NOTHING ON MOST VEHICLES (89, web v227; PC pc86). Measured (scratch/paint/acctest.js: every body from 4 sides, accent
  off vs neon green): accent painted classes 2, 13, 17 only; 30 of 38 bodies showed under 1% change (only their calipers). The
  Gouda's stripe is buried in its cheese (the .3 bevel). Fix: accent also paints the body's chrome trim (10) and carbon (6, ahead of the
  trim colour; not the Slip, whose carbon is its body: ACC_NO6), plus ACC_X's class where those are hidden (metal 7: Neutron, MX,
  Rocket bike, Retro GT; dark 1: Grand Coupe, Concept, Muscle, Slip). Code-built karts: accM parts (Gouda's splitter and grille,
  Tomatino's portholes and lamp brows) keep their own material until an accent is picked, named g_acc for the PC (glbexport's
  __garageBake keeps g_acc out of the vertex-colour bake). Now 2% to 36% of every vehicle changes. Keep it fixed: run acctest.js after
  adding a vehicle; a body with none of 2, 6, 10, 13, 17 on show needs an ACC_X class (web) and the same in kart_builder ACC_X (PC).
- MORE COMBOS, MY COMBOS (90, web v227; PC pc86). COMBOS 10..29 appended (KEEP THE ORDER: owned ones are 'cb'+index; style.gd the
  same): ten for everyone, ten with only:[body ids] that show first, starred, for those vehicles. My combos: 'crust-mycombos' (web) /
  user://mycombos.json (PC), up to 12 {n, p, t, st}; wearing one on another vehicle leaves off a livery made for a different vehicle and
  any colour not owned. Test: scratch/paint/comboqa.py (save on the Interceptor, wear on the Street Cruiser, delete).
- RIMS MISSED THE SPOKES; WHEEL SETS INSIDE OUT; METAL PAINTS (91, web v228; PC pc87 + export). The owner: Gold rims and Gold calipers
  on the Sport Sedan's Redline wheels: "the spokes/rim is not gold at all and the caliper is gold"; the Chariot's hub "is a part of
  the rim"; "Gold silver and bronze should also be car color options". (1) Why: patch 82's WHEEL_SPOKES gave the wheel sets their
  CALIPER's class (redline 17...); once 88 held the caliper apart, Rims painted almost nothing. Measured again on the rolling part
  (scratch/paint/clssheet.js: each wheel coloured by class; spokecls.js): see patch91.py for each wheel's classes. (2) Found on the
  way: the wheel sets' pack has no wheel positions, so on the right (+z) side Redline, Stealth, Forged, Turbo, Emerald and the Monster
  wheel showed their caliper side out. Fix: holdOut mirrors a wheel set whose spokes are not outboard of its caliper; packWheelGeo
  uses a car pack's own wheel for each side (the Monster wheel). (3) The Scissor's and Mega GT's brake discs are in the spoke class:
  rotorMark labels pieces of the spoke classes lying over 15% of the radius inboard as disc 12 (uv only). (4) PAINTS 24..26 Gold,
  Silver, Bronze with PAINT_MET (metal under the clear coat), swatches with a sheen. Keep it fixed: scratch/paint/rimtest.js (every
  car's wheel, stock vs gold rims and blue calipers) and rimtest4.js (the Sport Sedan on every wheel set, all four corners); a new
  wheel's spokes go in WHEEL_SPOKES (web) and kart_builder WHEEL_SPOKES (PC).
- RIMS ON THE WHOLE METAL WHEEL (93, web v228; PC pc88). The owner: the gold "ends before it covers the spokes completely ... the
  part that the tire wraps around should be the same as the rim color"; "for the chariot wheel rim should just change the entire
  color of the wheel". Why: patch 82's uCut stopped the spoke classes at the tyre's inner radius. Fix: the limit stays only on the
  Monster wheel (WHEEL_CUT: its tread blocks are its rim class); the lip and barrel take the Rims colour; WHEEL_ALL paints the
  Chariot's whole wheel; the Emerald set adds its rim 11, the toy cars their dish (their class 12). Keep it fixed: rimtest.js.
- CONCEPT: SPOKES ONLY (94, web v229; PC pc89). The owner: "For the concept vehicle make the rim cover only cover the spokes not the
  barrel". Its spokes and barrel are one piece of one class at the same depth (scratch/paint/concz.js). barrelMark labels the barrel
  14 (uv only): the white ribs (2) and the dark surface in the outer half facing away from the axle; WHEEL_CUT keeps its lip. Test:
  scratch/paint/rimc.js. Keep it fixed: another wheel whose barrel and spokes share a class needs the same (WHEEL_CUT + a mark).
- RECORDS FROM BEFORE THE SPEED CHANGE: "OLD RULES" (96, web v231; PC pc91). Patch 60 (web v216, 05:54:34 UTC 17 Nov; PC
  06:08:16 UTC, godot 4ddd3cd) cut a speed bar from 1.4% to .35% of top speed. The owner could not beat a 16 Nov Megawatt time:
  "mark it as old rules and any records that came before". Not a database change (no service key): the boards read created_at and
  tag older runs (web lbOld, PC lb.gd _old; web cutoff for web rows, PC cutoff for PC rows); your own records (web crust-recs d in
  ms, PC ach.gd d in seconds) older than the cutoff show "Old rules", and a run under today's rules becomes the best even if slower
  (the old one kept as prev and shown beside it). Test: scratch/oldrules.js (local and live board). NOTE for estimates: the computer
  driver (scratch/speedcmp.py) put the cost at 2-4%; a real run under today's rules (1:40.950, 18 Nov) was only ~1.5 s off the old
  1:39.417: skilled driving loses less than the top-speed ratio suggests.
- OWNER'S NOTES ON v229 (95, web v230; PC pc90 + export). (1) The Slipstream's red crescent in its wheel model spun: held
  (WHEEL_HOLD slip, class 17). (2) Accent "random spots ... that don't actually cover a part": the Slipstream's and the Concept's black
  decal patches (class 1, from ACC_X): removed; the Onyx's carbon engine cover turned the accent colour ("spoiler is messed up"):
  ACC_NO6 onyx. The Onyx, Concept and Slipstream now have little or no accent (their chrome only). Every vehicle checked:
  scratch/paint/accall.py (accent neon green from the rear-top and front-top). (3) The Interceptor's roof slots were tail-lamp
  material: TAIL_ROOF splits b_tail above y 2.2 into a Trim-coloured part; its lamps a deeper red (TAIL_DEEP). (4) GT driver fit.s
  .4 -> .22. Not changed: the GT Racer is roofless by design; the "wheels backwards" on the Megawatt was the v227 bug fixed in v228
  (scratch/paint/facing2.js: every body on every wheel set, spokes outboard of the caliper: 675 of 675).
- ADDED CALIPERS (92, web v228; PC via the export's ph<i>). Wheels with none on show: the owner saw a prototype (scratch/paint/
  addcal3.js) and kept the cars, not the bikes ("dont worry about the calipers for bikes the rest look good"). WHEEL_ADDCAL: Grand
  Coupe, Megawatt, Luxury SUV. addCal builds a rounded block over the brake disc's rear top edge, kept behind the spokes, class 13, as
  a held part (steers, does not roll, Calipers colour). Not added: the bikes; the Concept and Go-Kart (no brake disc to sit on); the
  Onyx (it has a dark one); hubcap wheels (Roadster, Tourer, Formula, the toy cars).
- BIKE WHEELS (85, web; PC via the export): the conversion cut fenders, a tail-light piece and seat trim into the bikes' wheel meshes,
  which spun round as a second set ("remove the ones that are spinning since the bike already has them"). wheelTrim in carGeos (bikes):
  the tyre whole, anything else only well inside it (within 90% of its radius) and never body paint, stripe, tail, glass or seat.
- SANDBOX READ-OUT UP IN THE CORNER (86, web): "move the hud on the left side higher up to the corner so there is more room for the user to
  drive with touch controls": #sbHud at top max(10px, safe area) (was 64px), Special and Rear 108px (was 172px). PC unchanged.

- CHEATS DON'T COUNT TOWARDS RECORDS (79 / pc79). The owner: "make any race using cheat codes not count towards records unless its the
  unlock cheat code. using different colored cars shouldnt not make the race count but dev options alter the core function of the
  game". Before, auto-drive (TESTING) and every developer option still wrote personal bests and world leaderboard runs (only the PC's
  leaderboard skipped auto-drive). Now RTAINT (web) / race_taint (PC) is set for good when, during the countdown or race, auto-drive is
  on or a developer setting in force differs from its default (devAlt / _dev_alt: race settings in force, yours or the room host's,
  plus this device's; 'on', 'fov', 'hud' are looks and left out). A tainted race: no best, no recent-races line, no leaderboard run;
  the results say "Not counted for records". A Sandbox mission with one on sets no best time. UNLOCK, colours, coins, achievements:
  unchanged. Keep: a new developer setting changes the game unless it is added to the looks list in BOTH devAlt and _dev_alt.
  Tests: web tools/neon/cheattest.py, PC tests/cheat.tscn.
- GARAGE PAINT HAD NO REFLECTIONS (80 / pc80). The owner: the paint looks "flat or a little dull", "a very flat orange", the gold a dull
  brown; wants clearer shine at least in the garage. Why: the web garage has its own renderer (gR, its own WebGL context) but its
  environment map came from the GAME renderer's PMREM (envFrom -> pmrem). A render-target texture from one context is empty in another,
  so every garage car reflected nothing (a mirror ball in the garage was black). Races were fine (their env is made by their renderer).
  Fix: gStudioEnv(), an HDR studio (half-float equirect: full float is not filterable on every GPU and came out black too) turned into a
  PMREM by a PMREMGenerator on gR: dark walls, a long narrow overhead soft-box, a tall strip each side, front and back panels. The garage
  lights drop (hemisphere .75 -> .35, sun 2.4 -> 2.2; floor reflections .6 -> .25) as the soft-boxes now light the car too. The car models'
  body paint (carBody M.carPaint, tagged userData.cp) gets garage-only values on the garage's model: reflection 1.75 -> .8 (a livery's
  1.5 -> .75), solid base roughness .45, clear coat .04, so the colour stays rich under crisp highlights; races keep theirs. Gold
  #e3b448 r .18, silver #c9ccd2 r .16, bronze #b5763f r .26 (web TRIMS and PC style.gd). 14 more solid paints after the first 9 (a saved
  number keeps its colour; an older game falls back to the driver colour; the PC gets them from the export: glbexport.js copies PAINTS).
  Keep: anything for the garage scene (env maps, PMREM, render targets) is made with gR, never the game renderer. Pictures:
  scratch/paint/paintqa.py (web garage), raceqa.py (in a race); garage frame time unchanged (6.9 ms).

### 2026-11-17 (web v222, PC: released 2026-11-18)
Web patches 71-78 (applied in order), PC pc71-pc78. Each patch file's docstring has the detail.
- UNDERGLOW REMADE AS LED STRIPS (77 / pc77; replaces 71's picture). The owner's brief: realistic LED strips under the car, the same on PC
  and web; the PC's was a big blurry pool, the web's an over-bright cyan with spots and streaks. Why they differed: the web had two
  point lights reaching 120 units (two bright pools and, on the glossy floor, two long streaks) plus additive sheets; the PC a 40-range
  light and a different sheet; the floors' own colours differ about 40x (the PC floor is texture x 0.17), so any light added over the
  floor could never match. Now one sum on both (web ugLs, PC shaders/underglow.gdshaderinc, line for line): four strips (sills between
  the wheels, both bumpers) each summed as a continuous line source (closed form, no spots), facing down and out, blocked by the tyres
  (soft ray-through-footprint test), plus a little light bounced out from under the body; smooth-limited (1 - e^-t, never clips to
  white) and ended with a margin (no edges). The strips sit at the car's sill height (ugParams: low 5% of the body between the wheels),
  so a low supercar's glow is tight and a monster truck's wide. The numbers per body come from the web (tools/neon/ugtable.py ->
  tools/neon/ug_params.json -> pc77 pastes view.gd UG_P): rerun both when a body changes. Garage: the floor itself is lit (floor colour x
  light / the floor's colour at the middle, web ugFloorMat via onBeforeCompile, PC garage_floor.gdshader EMISSION), so the floor keeps
  its look and both versions show the same glow whatever their floor's colour. The lights under the car are short (2.4 x half-width,
  decay 2) and only tint the low panels. Colour: ugSat in sRGB HSL on both, ugComp evens brightness (blue lifted, pale cyan down).
  Keep: no long-reach lights under the car; any change to the sum goes in BOTH ugLs and underglow.gdshaderinc. Pictures:
  scratch/ug/ugqa.py (web) and scratch/ug/pcqa.sh (PC): six bodies, six colours, three angles.
- KARTS AND BIKES' UNDERGLOW (78 / pc78). The owner: on karts and bikes "it doesn't look good. Remove the under glow feature for bikes
  and fix the size ... for the karts it's too big ... it doesn't look like LEDS coming from under the car". Why: 77 pushed the strips
  out to the wheel track plus a tyre (right for a car's sills, wrong for an open-wheel kart, whose frame is far inside its wheels), and
  a code-built kart's b was wheel track + 1.1. Now a kart (the garage's Kart tab: not a bike, not in CAR_BODIES) has b = the median
  low half-width of its frame between the axles, h <= .45 x wheel radius; code-built karts b = .85 x wheel track, h = .4 x radius.
  Bikes: no strips, no lights, no Underglow row (web styleUI, PC menu _style_shop); a saved colour is kept, unused. The web garage
  camera no longer frames additive meshes (the glow made it zoom out with a bigger glow; the PC measures before adding the glow).
  The per-body table is now committed: tools/neon/ug_params.json (ugtable.py writes it, pc77/pc78 read it). Keep: a new body goes in
  CAR_BODIES if it is a car with sills, else it gets the kart glow. Local PC Grater / Oil Can show only wheels: stale local assets
  (the same in the pictures from before 78), not this change.
- Underglow (71 / pc71, superseded by 77): ugTex / View.ug_tex from the body's footprint and its wheels: a bright fall past the sill plus a soft ambient one,
  cut beside each tyre into sections (the owner's photos: "the light will shine behind the wheels but not on the ground"), colour a
  little more saturated (ugSat), light colours (white) dimmed by luminance. Races: shows only in the dark (web lights 6 x L, haze .06 +
  .4 L; PC lights 4.5 x dark, range 40, haze .1 + .6 dark): the released PC lit a big bright disc by day. The owner: the earlier pools were
  "a massive glowing block", "a circle drawn around the car", "airy, floating up the sides"; then "a little blown out. the lights are too
  powerful" (web garage lights now .6, additive .46). Keep the garage lights LOW: on a glossy floor they show as two long beams.
- Garage (72 / pc71 / pc73): dark showroom floor (gFloorTex; no ring brushing: it made moire stripes). Web: lights lit and rainbow cycles
  in the garage (only the race loop did it). PC garage: the underglow (it had none) and studio_neutral.gdshader (a dark neutral room with
  strip lights) in place of the warm studio: chrome was bronze, black brown, colours pale. ACES white 8 (AgX washed colours out). The PC
  floor must stay dull (roughness .62, specular .25): the strips make a shinier one pale grey.
- Colours (72 / 73 / pc72): Rims row (rm, trim list; rimVC / car_vc_mat_pbr), trim no longer touches wheels (PC repainted every car_vc
  mesh), PC metal trim gets metal PBR (silver was grey plastic), interior metal .45 (was a black mirror), trim includes class 7 (interior
  metal). COMBOS (10, same order web / PC; 'cb<i>' in owned): a bought combo's pieces only in their own slots (comboAllows).
  Test: tools/neon/combotest.py.
- Delivery arrow (74 / pc74): a 3D orange arrow above the kart turned toward the next gate on the shortest way (sbNextHop over SB_LINKS +
  house gates; PC SandboxMap.LINKS + HOUSE_GATES) or the destination's start line; the line under the bar says where and how far.
  PC test tests/delarrow.tscn. On the PC the arrow lives beside the kart's model (view.views[kart].g's parent): the camera's parent is
  another space. A flat arrow is edge-on to the chase camera: it is tilted nose down (-.75).
- Delivery arrow, quickest drivable way (76 / pc76). The owner: "make it point to the quickest route that is driveable ... if you have to
  go through a tunnel first it will point to the tunnel". The fewest-places hop ignored distance. Now SB_COST (web) / main.gd SB_COST
  (PC), from tools/neon/sbcost.py -> tools/neon/sb_cost.json (committed; both patches read it): each place's gate-to-gate and
  gate-to-start-line distance (road places along the lap the shorter way, open places straight x1.15). sbRouteNext / _sb_route_next
  search (place, gate came in by) from the kart's position, twice a second; the old hop is only the fallback. Measured: from Margherita's
  start line Spiral is quicker by Basil (8220 vs 8812 by the Oven: the Oven's gate is far from the start, Spiral's Oven entrance is
  closer to its line); from Margherita's Oven, Bay or Garage gates it points to the Oven. sbcost.py saves after each place and resumes
  (it took 2 runs: one place loads slowly); delete build/sb_cost.json to measure afresh, then copy it to tools/neon/. Keep: rerun
  sbcost.py and both patches' tables whenever a place, its gates or SB_LINKS change. Tests: PC delarrow (route basil), web sbprobe.
- PC Sandbox: the Special / Rear buttons sit below the place's read-out (hud._special_top); they covered the coin box.
- Road places' tunnel arches (75): no other part of the track within RW x 1.4 + 40 across, 20 below to 110 above (Sauce Spiral's arch to
  Oven Rush stood in the spiral's next level). The PC follows from the export.
- Local note: godot/assets/garage was stale (Nov 15, old paints); the CI's garage.zip has the current paints. Pictures for before/after
  must use current assets (scratch/ug/pcshots.sh).
- Still open: hard-edged car models on the PC (re-export with split normals) if the owner wants more than the lighting change.

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

### OPEN WORK, in the order to do it (rewritten 2026-11-14 after web v193; the owner's words for each are in docs/NEXT-MODES-BRIEF.md)
1. (done: a Grand Prix on line on the PC, the controller's cursor on the PC, the trees and previews: see the v195 entry.)
4. (done: Balloon Battle and Sandbox on the PC: see their entries. The PC now has every mode the web has.)
5. THE WEBSITE: `py.cmd tools/site_pc.py` brings `app/pc.html` level with the PC build (done for build 68030144 and checked again for 521732c1, 3b1ecefb, 91f7f6ea, 92bf344b, 3297721a, 8789578d and 031c895: 24 tracks,
   Balloon Battle, Sandbox, online cups, the pointer, the size). Edit `HAS` in it when the PC's modes change, run it, commit and push `app`.
6. SANDBOX, what the brief still asks for and is not built (docs/SANDBOX-PLAN.md has the plan for each): the coin shop (kart and car
   unlocks), online free roam and the start-line lobby with ready-up. The clock, things to do, Easter eggs, Back to the track, the mechanic's
   shop, abilities and hills are on both (web v201, PC build 521732c1). On the pizza tracks only what is drawn is there to explore: no new side roads or buildings have been modelled.
7. Last Slice Standing still counts laps by the count of lap points (`lssTick`, `_lss_tick`): the count is set right at every
   line crossing now, so it is at most a few points early within a lap. Give it the line test of `finAt` if anyone notices.

### 2026-11-17 (web v221): UNLOCK opens the style shop too (patch 70)
styleOwned() is true for everything while CHEAT is on (styleCheat(): CHEAT is declared further down the file, so read it in a try).
styleBuy() then sees it owned and charges nothing and records nothing: crust-own and the coins stay real. CHEAT lasts one session, so at
start-up (just after STYLE) any style in the saved build that is paid and not in crust-own goes back to 0 and the build is saved.
Never filter OTHER players' st (online builds are theirs). Karts and cars are not sold for coins (Awards, which CHEAT already opened).
Test: tools/neon/unlocktest.py (UNLOCK TEST passed). PC: tools/mini/pc70.py (style.gd owned(): main.cheat; start-up reset).

### 2026-11-17 (web v220): the restart key (patch 69)
KB action 'restart' (default Backspace): in a race off line (not a room, Sandbox or battle) the first press pauses and shows #rstOv
(the pause menu hidden under it); the same key again restarts (the pause menu's Restart, startRace); Esc / Keep racing goes on. The key
works while the box holds the focus (checked before keydown's overlay early return). tools/neon/rsttest.py.
PC: tools/mini/pc69.py: keys.gd "restart" [KEY_BACKSPACE]; main.gd rst_ui / _rst_ok / _rst_key / _rst_go / _rst_no (the confirm sheet
replaces the pause menu's contents in panel_pause; _toggle_pause answers Keep racing first, so Esc / P / Start resume). Not a kart
change: online stays 120. Test: CR_MODE=single CR_MAP=margherita tests/rstkey.tscn (RSTKEY PASS; real key events). Note: in Settings >
Controls Backspace CLEARS a box (Keys.capture), so it can't be typed in as a binding; Reset gives it back.

### 2026-11-17: the PC build for web v219 IS OUT: 785b5167 (online 120: web and PC play together again).
The PC build for web v220 (the restart key) IS OUT: 45bc0216.
The PC build for web v221 (UNLOCK opens the style shop) IS OUT: e6b26bcb.

### 2026-11-17 (PC build for web v219, online 120): the PC level with web v218-v219
tools/mini/pc68.py (patch 64's no-items rule, patch 65's coins, patch 68's developer options, PROTO 120, scripts/style.gd) and
tools/mini/pc65.py (the style shop: garage rows, trim/accent repaint, underglow lights, coloured smoke, headlight colour). Notes:
- New scripts are loaded by path (preload("res://scripts/style.gd")): a new class_name is unknown until the editor rebuilds its cache.
- Car bodies' trim on the PC: _style_vc repaints a COPY of the mesh's vertex colours by class (uv.x * 32), cached per mesh + colours.
- The underglow on the PC: two OmniLight3D under every glowing kart (Godot's lights light the toy tracks, unlike the web's
  ShaderMaterial track), the haze kept very faint (alpha .05-.12): with it stronger it read as a flat patch again.
- Tests: tests/dev.tscn (DEVTEST), tests/style.tscn (STYLE; with a window build/menu/style_night.png; CR_MODE=sb CR_MAP=backyard).
  tests/cpus.gd now sets the mode (a Sandbox test saves "sb" as the last mode). tests/lbtest.tscn: run WITHOUT --fixed-fps (its waits
  count frames; at fixed 120 the board's answer comes after them).
- Only the moving hazards are switchable (traffic, train, walk): race.gd _setup_haz; the local PC copy has no track with traffic.

### 2026-11-17 (web v219, ONLINE 120: the PC must follow before it can race the web): developer options (patch 68)
Unlocked by the cheat code DEVELOPER (again hides it); Settings > More, under the cheat box (devUI from the table DEVS). Store 'crust-dev'.
- RACE settings (devR: off line yours, for YOUR kart only; in a room the HOST's, sent as cfg.dev = devPack() in netBuildCfg and applied
  to EVERY kart on every screen): vehicle spd/acc/hnd/wgt (multipliers on k.sm) and off (added), drift boost (the tier boost x), gravity
  (the 260 fall x), ability charge (dt/ABIL_TIME x; always ready), rival skill (k.ai.skill x), the world's MOVING hazards (HZSET kinds
  traffic, train, walk only: ponds and city blocks are ground and buildings, and a hidden pond still swallowed karts; filtered in buildHazards; a track built with other switches is built again: HZBUILT vs hzSig() in goRace).
  devKart(k, isPlayer) at kart creation (`player` is not yet that kart there) keeps k.sm0.
- THIS DEVICE (devLocal: off line, never in a room): game speed (acc in frame), field of view, HUD (body.devnohud), invincible (spinOut),
  always this item (rollItem), unlimited pepperoni (devFrame refills), flying: devFly replaces the player's stepKart; G / the left stick
  press toggles (KB 'fly'), I / Page Up and K / Page Down (KB 'flyup' 'flydown', held) or the stick climb and descend. Cheats: +1000
  coins, the whole style shop, reset.
- tools/neon/devtest.py checks it all (DEV TEST passed). THE PC must apply cfg.dev the same (race settings) for online: NET_PROTO 120.

### 2026-11-17 (web v218, online still 119; PC NOT YET level): clean races count as No items, the style shop, coins for races
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A race with items on but none used was filed with items (the owner, Basil Boulevard) | lbRun filed NOITM only (every item switched off) | patch 64: ITMUSED, set when the PLAYER uses an item (useItem without fireItem's third argument: a special ability does not count); lbRun files ni = NOITM or not ITMUSED | noitemtest.py (its online-version check now >= 116) |
| The underglow looked like a flat coloured patch, "not light" | An additive picture adds the same colour whatever it lies on; and the toy tracks' surface is a ShaderMaterial that ignores scene lights (a ray down in Sandbox: lights false) | patch 66: two real point lights under the kart you drive (the player model and the garage preview always have them, dark when no glow: the light count never changes); patch 67: a second layer with blending ground x colour + ground (DstColor, One), premultiplied picture: the ground keeps its texture and is lit in the colour | sbprobe.py with INIT (localStorage build) and SB.clock=.95 then a wait, then freeze: scratch/coin/glow.js |
- patch 65, the style shop (garage > Colour, under the paints): TRIMS (one list for trim, accent and interior; Stock/Black/White/Silver free,
  colours 60-120, neon 150, gunmetal 150, bronze 250, gold 400, chrome 600), GLOWS (Off and Ice blue free; 200-250; Rainbow 800), LIGHTS
  (Halogen, Xenon free; 150-300), SMOKES (White free; 300-400; Rainbow 900). Owned: store 'crust-own'; wallet = Sandbox coins (sbSave().c).
  playerBuild.st = {tr, ac, in, gl, hl, sm}; travels with the build online; in the model cache key. Car bodies: styleVC (SH.carVC
  cloned, shader recolours classes dark/carbon/gunmetal, stripe/caliper/red, seat by the uv's class, keeping the baked shading; SHSET so
  never disposed); code karts: M.dark / M.stripe / SH.seat swapped. Tyre smoke: smokeC(k), thicker, plus launch smoke; FXN 420.
  Sandbox's headlight beam takes the headlight colour (sbNightFrame). CPU karts sometimes wear a glow/smoke.
- Coins for a finished race (racePay in onPlayerFinish; not the menu's demo race: RDEMO): 8 + 3 a kart beaten + 10/5/2 podium, x 1 / 1.2 /
  1.5 by class; 6 alone. "+N coins" under the results. (A bench that steps karts itself never calls onPlayerFinish: call racePay.)
- The PC build of web v217 IS OUT: 116c2fe6. release_pc.py now carries on when its export was already pushed (a run stopped part way).
- STILL TO DO on the PC: patches 64-67 (no-items rule, style shop, coins, glow, smoke). Then the developer options (asked for: below).

### 2026-11-17 (web v217): real car paint, pepperoni coin and mission medallion, PC night lights
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Solid paints looked dull next to the owner's photos (a Verde Mantis roadster, a Rosso Corsa coupe) | Mid-tone swatches washed toward pastel by the ACES tone curve (red read orange), and a part-metal finish (.14 karts, .32 car bodies) greyed the colour and flattened its light-to-dark range | patch 62: deep car swatches (PAINTS), solid finish = non-metal base, roughness .36, clear coat .02, envMapIntensity 1.75 (a livery keeps its own); PC kart_builder.gd the same (paints come with the garage export) | cartest.py PAINT=1 / PAINT=4 against the photos |
| PC: no headlights, street lights "super dim" at night | Godot dims lights as distance^-attenuation in world units; a kart is 12 units long, so attenuation 1.15 left 8% of the headlights 60 ahead and 1.6 left 1% of a lamp 30 away | sandbox_night.gd: spot attenuation .3 (energy 3.2), lamps .4 (energy 4.5) | tests/sbnight.tscn with a window takes build/menu/night_on.png / night_off.png (its LED check needs CR_MAP=backyard) |
- patch 63: sbCoinGeo(kind) also makes the hidden pepperoni coin (gold rim, red face, raised pepperoni and cheese flecks; drawn after its glow
  sprite, which otherwise covered the far half of its face) and the mission medallion (gold, the icon on both faces, turning, bobbing, a
  shadow). coinexport.py writes coin_pep.json, coin_act.json and act_<kind>.png for the PC (sandbox_view.gd uses them when present).
- The start-line duplicate the owner asked about again: fixed since web v214 (above); sbrace.py rerun on v217: no ghost during the race.
- tests/sbcoin.gd needs main.auto_drive = true, or it waits at the menu (the owner saw the window "stuck on the menu").

### 2026-11-17 (source for web v217, NOT YET PUBLISHED): Sandbox coins with detail and shadows (patch 61)
The owner: "make the coins look better in sandbox right now they look basic with very little detail maybe add a shadow for them too".
- Web: sbCoinGeo builds the coin (sunken field, raised rim, bevelled reeded edge, a raised pizza slice with crust and pepperoni on both
  faces; vertex coloured; 1336 triangles, still ONE instanced draw); glow down from .9 to .45 so the relief shows. sbCoinShadows: a soft
  ellipse on the ground under each coin, turning with it (one more instanced draw). A coin's ground is c.gy (plain 5.4 below it, hidden 8;
  none for the one hanging off a bend), also exported to the PC as the coin's 6th field.
- PC: sandbox_view.gd _coin_mesh reads assets/sandbox/coin.json, the web's own triangles (tools/neon/coinexport.py; Godot winds the other
  way, so each triangle's corners are swapped on load; a plain disc if the file is missing); _build_coin_shadows the same shadows;
  sandbox.gd coin_gy (an older export without the field: y - 5.4 / 8). Test tests/sbcoin.tscn (NOT headless: it opens a window, takes
  build/menu/sbcoin.png and closes itself; CR_MODE=sb CR_MAP=margherita) -> SBCOIN PASS.
- If sbCoinGeo changes: run coinexport.py again, or the PC's coin goes out of step.

### 2026-11-17 (source for web v217, NOT YET PUBLISHED; ONLINE 119 ON BOTH): four new karts built in Blender
The owner: "Let's work on new kart designs and really make them unique and try using blender for some of them". Each has a
silhouette no other kart has from the chase camera: Rolling Pin (retro open-wheeler, a pizza-peel wing), Grater (chunky utility kart,
a giant box grater), Calzone Comet (crimped-dough streamliner, bubble canopy), Oil Can (dragster: spout nose, huge slicks, wheelie bar).
- Made from scratch, no downloaded model: tools/blender/karts_new.py writes scratch/cars_in/karts/<id>.glb with materials named K_*;
  car_rules.py's K_RULES map them; then the car pipeline as usual (car_all.sh, car_pack.py). tools/cars/patch_karts.py adds them to
  BODIES (after every other body: builds hold the index) and BODY_FN, between /*karts4*/ marks (rerun it after any change). Seat, flames,
  number and top are given in the model's metres there and turned into game units from each pack's measured wheels.
- They are karts because they are left out of CAR_BODIES (the garage's Karts tab), with the driver in full view (drvS, noCockpit).
- Their ids: the Calzone Comet is `comet`, NOT `calzone` (that is a track's id: patch_karts.py asserts against any clash).
- Two new trims, steel and wood, appended to the class list on all three (car_convert.py CLS/PBR, the web's CAR_CLS/CAR_PBR,
  kart_builder.gd CAR_CLS/CAR_PBR): chrome and metal mirror the dim garage and read nearly black over large surfaces. Keep the
  three lists in the same order; append new classes only at the end (packs store the index).
- Engine voices: oilcan v8, grater chug, comet race (web ENG_BODY and sfx.gd). Checked: tools/neon/cartest.py (now dismisses the
  username prompt; ZOOM=1 PITCH=.3 frames a kart), scratch/statlap_k4.py: all four finish Margherita within the Classic's band (165-170 s).
- The PC build of web v216 IS OUT: build 4ddd3cdf (online 118); pc.html updated.

### 2026-11-17 (web v216 and the PC build after it; ONLINE 118 ON BOTH): what a stat point counts for
The owner: "it's hard for the karts to compete with the cars"; then, keeping Classic all zeros: "re assign the quantity that a point in a
category counts for". tools/mini/patch60.py; PC kart_builder.gd stat_mods, kart.gd (the kerb), webnet.gd PROTO 118, main.gd's texts.
- Measured, not guessed: scratch/statlap3.py races every vehicle alone (the computer driving, standard wheels and glider) three times on
  Margherita and Basil with FIXED SEEDS (Math.random replaced per run: one race alone varies by up to 12 s); scratch/fitstats.py fits
  race time to the five effective stats (r2 .91): a point of speed was worth 2.45 s a race, acceleration .76, handling .60, weight .34,
  off-road .23. Cars spent their minus points on the cheap stats, karts on the dear ones: karts 3.3 s a race behind cars.
- scratch/reweight.py chose speed x.25, weight x1.95, off-road x3.2 (acceleration, handling as they were): statMods spd 1+.0035e,
  wgt 1+.234e held to .4..1.6, off 2.88e; the kerb's share held to .70..1. No vehicle's numbers changed (Classic stays all zeros).
- Checked by racing again (statlap4.json): against Classic, karts went from +1.8 s to -0.4 s a race, cars from -1.6 to -1.2, bikes
  -0.8 to -1.1; the gap karts-cars 3.4 s -> 0.8 s (inside the noise); best to worst 13.5 s -> 8.3 s.
- statstest.py and the PC's tests/stats.tscn agree (every body x wheel x glider). If the stat values change again: both, and the
  texts in the web's Settings and main.gd's.
- The owner's brief still has one item not built: 6, coin-based kart and car unlocks (new kart models, two of the newer cars at a coin
  price, preview / buy / equip in the garage).

### 2026-11-17 (web v215; online 117): the shop in a room's Sandbox; no scenery in shortcut lanes
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A guest in a room's Sandbox who changed something in the mechanic's shop landed on the room screen with no way back into the game (owner's picture) | The garage's last button asked "a room's guest?" (ready up, the room screen) before "came from the shop?"; and toMenu put the room screen up for leaving a room's Sandbox, over the garage, also for the shop | gDone asks sbShopDone first; toMenu leaves the room screen down for the shop (SB.shopBack); the room screen in a room's Sandbox has "Back to Sandbox" (sbRoomBack: a guest to the host's last place) | tools/neon/sbshopnet.py (guest: shop, garage, change, back out; then the room screen's button) |
| A street lamp on Midnight Mozzarella's paved fast lane (shortcut audit) | The scenery's own check measured from the plain shortcut width, not the wide paved route's | scClear() as a race or place is set up: any instanced scenery detail (cullOK) standing in a shortcut's lane is shrunk away | scratch/scvert.js per place (sbprobe.py <map>); done for 13 of 23 places, all clean but Margherita (patch 55) and Mozzarella (this) |
Patches tools/mini/patch58.py, patch59.py.
- PC: THE MECHANIC'S SHOP of web v205 is on the PC now (PUBLISHED as PC build afdc79c8). godot/tools/shopexport.py starts the local test copy in Sandbox in the
  garage, runs glbexport.js's __exportShop and writes godot/assets/shop/mshop.glb (nodes "shop" and "door", textures inside, ~16 MB;
  Godot's import pulls the textures out next to it) and mshop.json (K, the floor, the bay, the door's place, its height). Run it again
  only when the web shop changes. sandbox_view.gd _build_shop loads it (the old code-built shop stays as _build_shop_old if the file
  is missing); the door rolls up as the kart comes at it (_shop_frame) with a light inside; main.gd _sb_cine_start/_sb_cine_tick: through
  the door the kart rolls onto the bay, the camera cuts inside, the kart's name comes up, 2.6 s (any key skips), then the driver screen.
  tests/sbshop.tscn (CR_MODE=sb CR_MAP=garage; CR_SHOT=1 windowed for pictures build/sbshop_*.png).
  Two faults on the way: the exporter dropped the building because it is node 0 and the list was .filter(Boolean); and the shop is
  hidden while the kart is far from it, so the export shows the whole group while it collects.
- PC: a host who opened the shop in a room's Sandbox sent every guest back to the room screen (_to_menu called web.host_menu, a
  "menu" to all). Now only after a room race (web.cfg set), as the web's toMenu.
- PC: relay heartbeats count no time the game did not run (webnet.gd poll, _last_poll), as web patch 57.
- Shortcut audit finished (scratch/scvert_all*.log): all 23 places clean after patches 55 and 58 (a few vertices of big merged road
  meshes show at some junctions: markings, not objects).

### 2026-11-16 (web v214; online 117): headlights, the second host, shortcuts; PC catch-up (night, D-pad, frame counter, tunnels)
Web: tools/mini/patch53.py, 54, 55.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A dark V in front of the kart, light only at its edges (owner's picture) | The headlight spot sits at the bumper, inside the kart's own shape, and cast shadows | Headlights cast no shadows (web and PC sandbox_night.gd) | A light that sits on or in the kart must not cast shadows |
| In a room's Sandbox race the guest saw the host twice: one frozen at the start line | Sandbox's friend cars (SBN.peers) were left in the scene when the race loaded | netBeginLoad drops every friend car and tag; Sandbox draws them again from the next list | sbrace.py checks no friend car is drawn during the race ("ghosts") |
| Posts and lamps standing in Margherita's shortcut where it rejoins the raised road | The causeway's posts, poles and lamps (CAUSE) had no shortcut check | nearSC(x,z,SCW+4) skips them | A row of things along the road edge checks nearSC; scratch/scvert.js lists anything standing in a shortcut's lane (per Sandbox place) |
- BALLOON BATTLE, a controller's item button (patch 56; owner: "throwing items is slow and also a copy of the item gets dropped behind
  you on the ground"): a holdable item (pepperoni, dough, flour) was held trailing behind on the press and thrown on letting go; in a
  battle the press throws it now (web: mode==='bb', NOT the BATTLE flag, which is the free-driving physics and is off in a real
  battle; PC: race.mode != "bb"). Races keep holding behind. scratch/bbpress.py (pretend pad): fired on the press, nothing held.
- THROWN OUT OF A ROOM'S SANDBOX (patch 57; owner, three players on the web app, the friend hosting: the guest who went Back to
  Sandbox, and a third player who had not joined the race the moment it started). The relay drops a link after 20 s of silence in
  state race/countdown, and Sandbox driving is state 'race'; a load (the host loading the race, the guest loading Sandbox again)
  stops the game entirely. Now the 20 s is for a room race only (NET.cfg), and a gap of over 3 s between two of this game's own
  heartbeats is not counted as anyone's silence. sbrace.py waits 30 s in both situations (passes, but loads here are short: the
  fault itself was not reproduced). PC: the same two rules due in webnet.gd.
- Headlights come on by themselves only when it is properly dark (L .5 to .8), still off on a lit track; keyboard 'lights'
  "Headlights (Sandbox)", L by default, switches them on or off by hand (web SB.hl, PC main.hl_mode).
- PC: PUBLISHED as build b18a9192 (export c4a76f8, cross-play check passed) with everything below except the mechanic's shop:
  - SANDBOX AT NIGHT: scripts/sandbox_night.gd (made by sandbox_view.gd beside the clock): the toy dashes ("toy_toydash..."
    materials) glow, street lamps on spiral/basil/napoli/tour with three moving real lights, the headlight (SpotLight3D with a
    projector picture, the on-track rule, the darkness threshold, the L key). tests/sbnight.tscn (CR_MODE=sb CR_MAP=backyard) checks
    the numbers; tests/sbclock.tscn takes pictures (CR_OFF=<units> puts the kart off the track; it unpauses a window that lost focus).
  - D-PAD UP did not start races in Sandbox (owner, on the PC exe). Not reproduced (tests/sbpad.tscn passes with the press event),
    but the press only worked as an event, which the menus' controller cursor can take first. Now also read every frame
    (_read_input: sb_pdu / sb_pdd, _sb_dpad), as the web's sbTick does; the two never both act on one press.
  - FRAME COUNTER on every screen (own CanvasLayer 120, main.fps_lbl), not only in a race (owner: "should work for all modes").
  - TUNNELS: the kart points down the tube and is eased to its middle, steering does nothing there (sandbox.gd Tun.step; main.gd
    _read_input), as web v210 patch 48.
  - STILL NOT ON THE PC: the mechanic's shop of web v205 (Blender models, door, pull-in). Plan: a __exportShop in
    godot/tools/glbexport.js (building and door as two nodes, from a running Sandbox), loaded by sandbox_view.gd's _build_shop.

### 2026-11-16 (web v213 and the PC build after it; ONLINE 117 ON BOTH): a room's Sandbox race from a start line, with invites
The owner: anyone (guest or host) at a start line can start a race and "send out like an invite to the other person and they can just be
teleported to the race and when the race is over they just stay at the track when they go back into sandbox"; agreed rule: "the host would
always have to be in an online race in sandbox" (the host's game runs every room race: one world is loaded at a time, so a host cannot
run a race on a track it is not on). Web: tools/mini/patch52.py. PC: scripts/webnet.gd (PROTO 117, RACE_T and sb_race in _send_to,
sb_race_start / sb_race_end, the messages), main.gd (the _sbi_* block after _sb_race_here; _sb_race_solo; _sb_return; results).
- At a start line in a room's Sandbox: Race with friends / Race alone / Cancel (1 / 2 / Esc; controller up / down; driving away cancels).
- With friends: the host sends {t:'sbinv', id, mi, by, name, me}; everyone else (driving in Sandbox) sees "<name> wants to race on
  <track>!" Join / No thanks (J / N; up / down), 10 s. Anyone not driving in Sandbox answers no by itself. If the host says no (or
  is not in Sandbox) it is off: {t:'sbinvx', why:'host'}, and whoever asked is offered a race alone.
- The race: an ordinary room race (cfg.sbr = 1, mode single) for the host and those who joined. The host keeps their ids
  (web NET.sbRace, PC sb_race) and every race message (netAll / _send_to: s, hit, tst, go, load, menu, elim, sbend), the load
  resend, "everyone loaded" and the grid leave the others out; they keep driving, their places still relayed by the host.
- After it: results show only "Back to Sandbox" (sbBack / _sb_return): each racer goes back into Sandbox at that track. The host going
  back ends it for anyone still racing ({t:'sbend'}); a guest going back first sends {t:'quit'}.
- Race alone in a room: the start line's own race off line; NET.soloSb lets goRace past the room's ready-up (the PC never had that stop).
- Tests: tools/neon/sbrace.py (two browsers: the friend asks from the garage while the host is on Margherita, both race on the garage,
  both back in the garage; the host says no; the friend says no while the host races) PASS; cross-play CR_XMODE=sbr / MODE=sbr (the PC
  asks, the web host joins, both race, both back) PASS both sides; gpnet2, bbnet, xplay, PC smoke and sandbox still pass.
  A test that asks before the host is driving in Sandbox gets "the host can't race": wait for the host's car (sbr in xmodes.gd).

### 2026-11-16 (web v212 and the PC build after it; ONLINE 116 ON BOTH): the PC catches up, a key for Back to the track
- Web v212, tools/mini/patch51.py: keyboard action 'sbback' "Back to the track (Sandbox)", T by default, in Settings > Controls like every
  key (owner: "make it bindable like the other keys"). Driving in Sandbox it pauses and asks the pause menu's question (sbBackAsk).
  Checked: scratch/tkey.js with sbprobe.py (paused, asked). PC: scripts/keys.gd "sbback" [KEY_T], main.gd's Sandbox keys; tests/sbkey.tscn.
- PC port of web v209-v211 (D:/crust-rush/godot):
  - ONLINE 116: webnet.gd PROTO 116, "ni" in the host's settings (_build_cfg: main.all_items_off()); a guest reads web.cfg["ni"].
  - NO ITEMS: main.all_items_off() (every unlocked item off in Settings > Items); race.noitm set in _start_race (never the background
    race, Last Slice, Battle or Sandbox); a no-items race EMPTIES race.boxes, so nothing draws, takes or guesses a box. The menu's
    Items On / Off (menu.gd, under Computer racers; setting_changed "items"). PC-to-PC rooms carry cfg["ni"] too. tests/noitems.tscn.
  - WORLD LEADERBOARD: scripts/lb.gd (child "Lb" of main): the same Supabase functions and view as the web, publishable key only;
    token and name in user://leaderboard.cfg, a queue of runs sent when there is a name (platform 'pc', ver 'pc'); run() from
    _progress_finish (not the test drive, not lss/bb/sb). Menu sheets "lb" (class, With rivals / Alone / No items, top 20) and
    "lbname" (username, the account code). Records cards are clickable (menu.lb_open; the card's children ignore the mouse so the click
    reaches it; the controller's cursor clicks with a real mouse event). Settings > More > Username: Change, Copy account code. The
    username is the room name too (_web_name). First menu: the username sheet once a run. tests/lbtest.tscn reads only.
  - GARAGE: the Colour tab is back (taken out 2026-11-11 in a93e6d8; the owner asked for it back). PAINT glossier as web v210
    (kart roughness .2, clear coat .03; CAR_PBR paint/stripe [0.2, 0.32, 1.0]; car clear coat .03).
  - Controller cursor speed (Settings > Controls: "curs", 70 % by default; pad_cursor.gd); the Sandbox friends list beside the
    item slots (hud.gd: left of item_rect(2)).
  - Tests passed: smoke, battle (CR_MAP=preptable CR_MODE=bb), sandbox (CR_MAP=margherita CR_MODE=sb), gpnet, cpus, noitems, lbtest,
    sbkey; cross-play with web v211: xplay (race) PASS both sides, xmodes sb PASS both sides.
  - NOT on the PC yet: Sandbox at night (LED strips, street lamps, headlights: web v206/v210), the mechanic's shop and its pull-in
    (web v205), the tunnel camera lock (web v210 patch 48; the PC's tunnel is its own).

### 2026-11-16 (web v211; online still 116): THE TUNNEL FREEZE FIXED
The owner: "the whole game froze for like 5 seconds, it should be smooth". Patches tools/mini/patch50.py, 50b, 50c, 50d and build/build_gh.py.
Measured with sbprobe.py and scratch/lights.js, glprof.js, glstack.js, fsplit.js, ftrip.js (margherita -> garage, the worst trip):
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| One warm-up step of 7.3 s on a trip | A shader is built for a COUNT of each kind of light. The garage has a room lamp (PointLight) Margherita has not, the SB_LAMPS places three; a trip that changed the count rebuilt every material's shader, the karts' livery shader too | sbLightPad: every Sandbox place has the same number of point lights (lite 3, else 4), dark placeholders making up the rest; called from sbNightArm and sbWarmG | Anything that adds or removes a light in Sandbox keeps each kind's count the same in every place; a light is dimmed to 0, never hidden or removed (patch 49 headlights) |
| ~20 steps of 170-420 ms after it | renderer.compile ran with no render target (shaders for the screen, sRGB); the game draws into the post pass's target (linear), a different shader: the warm-up was wasted and the real ones were built in the draw step | Compile into the same target (wtg) | Any warm-up compiles into the target the game really draws to |
| A last step of 2.4-2.9 s | warmScene() at the end drew the whole place three times, nothing culled: post target, screen, a 64 px target; the last two need shaders Sandbox never uses | In the tunnel: one draw into wtg (builds the shadows' shaders too); with no post pass the one-object draws are skipped | Do not call warmScene() from the tunnel |
| Steps of up to 330 ms inside renderer.compile | build_gh.py's three.js change skipped the blocking getUniforms only for the material that CREATED a program; a second material sharing a program still being built asked for it and waited (2.2 s in all) | Every material compiled with __crDefer skips it (set up at its first draw) | build_gh.py's three.js replacement is the place; glprof.js shows getProgramParameter's worst call |
| Frames of 100-375 ms in warm3/warm4 | The tunnel's loop ran 16 steps before reading the clock; warm3 asked all ~300 programs each step (24 ms) | Clock after every step; warm3 asks only unfinished programs (marked __crOk), once a frame; new programs at most 3 a frame (yield 'warmF') | Keep the budget check inside the inner loop |
Result (first trip to the garage, this PC): worst frame in the tunnel 7-8 s -> 152 ms, the game's own work at most 28 ms a frame; the
first frame after arriving ~110 ms; later trips worst ~100 ms. What is left is the graphics driver finishing in the background. sbtest.py
garage passes; sbtest.py (back garden) fails only its two known wall checks (see 2026-11-15).

### 2026-11-16 (web v210; online still 116): tunnels, headlights, garage tabs, glossier paint
Patches tools/mini/patch48.py (tunnel), 49 (headlights), 49b (garage tabs on a phone), 49c (paint).
- TUNNEL CAMERA: the tunnel copied the game camera as it was at the gate, so coming in on a turn it looked off to the side all the way
  (the owner's picture: half the screen the black outside of the tube), and steering slid the kart and the camera. Now the camera sits
  square behind the kart looking down the tube, and steering does nothing in the tunnel (owner: "lock the player into driving straight").
- TUNNEL LAG, found but NOT fixed yet: SB.lastWarp.log / the probe scratch/tunnel48c.js. Every long stall is sbWarmG's "warm2" step
  (renderer.compile of 8 objects at a time): 150-330 ms a step, and one step of 7.1 s (8.5 s in another run) on margherita -> garage, a
  step whose materials carry the 1604-character onBeforeCompile (MeshStandard/Physical). 384 programs after one trip. Next: find which
  onBeforeCompile that is and whether its programs could be shared or compiled before the trip.
- HEADLIGHTS (owner: "just looks like a white triangle beam, try to make it look more realistic", with reference pictures; and "only make
  the headlights turn on when the player is not on the track" where there are track lights or street lights). The additive cone laid on
  the ground is gone; the spot light makes the beam: cool white, bumper height, 120 ahead, cone .62 with a cookie (SpotLight.map: two soft
  lobes, a low-beam cut-off), 24 x the night's L (legacy lights: at 7 it barely showed on dark grass). Every Sandbox place has it; where
  the place has LED strips (toy tracks) or SB_LAMPS it fades out on the track (nearTrack RW+10) and in off it. The light is never hidden
  (only its strength changes): a light switched in or out recompiles every shader. Pictures: scratch/head49_*.js with sbprobe.py.
- GARAGE TABS on a phone held sideways: seven tabs needed 492 px of 427, so Theme sat off the right edge; narrower tabs up to 960 px wide.
  The PC's garage lost its Colour tab on 2026-11-11 (commit a93e6d8): to be put back in the PC port.
- PAINT (owner: "the colors look pretty flat on the car and dull try to make them a little sharper and reflective"): kart paint roughness
  .38 -> .2, clear coat .08 -> .03, reflections 1 -> 1.45; car paint metalness .5 -> .32 (metal darkened the colour), roughness .34 -> .2,
  reflections 1.2 -> 1.5; picture liveries .28 -> .22. Subtle in the dark garage, clearer outdoors. Same change due on the PC.
- Checked, no change needed: Pepperoni Storm and thrown items go behind with the left stick pulled back or while looking back (web:
  scratch/pepback.py, stickback.py; the PC reads the stick the same way). A held item let go with the stick back is fired behind (the
  'hold' release is releaseHeld(k,true), a throw, not a drop). A test that waits 0.5 s can miss it: a slice thrown back at a rival
  right behind is gone by then; test with no rivals.

### 2026-11-16 (web v209, ONLINE VERSION 116 on the web; the PC is 115 until it is ported): no items, Sandbox fixes, headlights, cursor
Patches tools/mini/patch47.py (no items, NET_PROTO 116), 47b (Sandbox guest's place), 47c (headlights), 47d (cursor), 47e (friends list).
Database: tools/mini/lb_schema_noitems.sql, run by the owner in the SQL editor on 2026-11-16 (adds runs.noitems; keeps every time).
- NO ITEMS (owner: "a without items section", "when you turn items off the item boxes should just disappear ... the game will pull from
  the hosts selected options"). The item guide may switch every item off (it used to keep one); every item off = no items, and the
  menu's new Items On/Off is the same setting (Off: all off; On: the guide's defaults). NOITM (resetRace): off line from the guide, on
  line from the host's cfg.ni; never in Last Slice, Balloon Battle, Sandbox or the demo. The boxes are not drawn and give nothing (host
  loop and guest prediction skipped). Specials still work. World boards: With rivals | Alone | No items; the view (best_runs) gives a
  no-items run solo = null so the older boards never show it; such a run is sent with p_noitems (others exactly as before).
  Locked items (itemUnlocked false) count as neither on nor off for "all on" (the menu's note once said "some switched off" for them).
  Test: tools/neon/noitemtest.py. NOTE for tests: wait_for_function on an expression that ends in a function (`&&window.__ev`) never
  passes (a function is not a value Playwright reads): end it with `!!window.__ev`.
- SANDBOX GUEST STARTED IN THE BACKYARD (owner: "the host spawned in garage like selected but the guest started in backyard"). The guest's
  sbgo set mapIdx, then goRace(mapIdx); goRace loads a map only when mi !== mapIdx, so the menu's map stayed. Now goRace(d.mi). Never set
  mapIdx before goRace. sbnet.py now starts the friend on the backyard (passes).
- HEADLIGHTS were one bright patch at the bumper (the ground beam was brightest there, the spot light aimed steeply down close in). Now
  the beam is dim at the bumper, brightest 40 to 90 ahead, widening to 130 across 240 ahead with a clear edge; the spot sits at headlight
  height aiming nearly level, 3 not 5.5. Pictures: sbprobe.py with scratch/night6.js (probe_beam47c_*.png).
- CONTROLLER CURSOR could not click the Records rows (li.lb-open had only an onclick; A clicks what matches PAD_CLICK): added to PAD_CLICK.
  New Settings > Controller cursor speed (CFG.curs, 25-200 %, 70 by default: the owner found it too fast). A pretend-controller check
  (scratch/startpad.py): Start pauses and resumes in a race and in Sandbox; A on a Records row opens its board.
- FRIENDS LIST covered the item slots on a phone (fixed top:118px): now placed left of #itemBtn/#itemBtn2, measured each time.
- Not done yet: the PC port of all this (PROTO 116, cfg.ni, no items, the leaderboard), the lag in Sandbox's tunnels, the Sandbox
  start-line race lobby on line.

### 2026-11-16 (PC build for web v208, ONLINE VERSION 115 on the PC too): Balloon Battle and Sandbox on line on the PC, the rivals count
PUBLISHED as PC build 031c895 (export 1a3bf97; its cross-play check passed). Web v209 moved to online 116 the same day, so this
build cannot join web rooms again until the PC has v209's changes (cfg.ni, PROTO 116).
The PC port of web v208 (patches 45, 46). All in D:/crust-rush/godot:
- webnet.gd: PROTO 115; the six battle fields at the end of REM, bbDead in ZB, bb [clock, over] in the host's snapshots; `_build_cfg`
  sets mode "bb" on the arena; `_battle(d, mine)` turns a guest's changes into the same race.fx events the host makes (bb_pop, +1, out,
  the winner). Sandbox: `sbx`, `sb_peers`, `sb_in`; every 80 ms a place is sent (`_sb_send`); the host relays all places with its clock
  (`sps`); a guest takes `sbgo` from any screen except a room race or while loading (it first took it only on the menu: the PC sat on a
  results screen and never came). leave() clears all of it.
- main.gd: `_web_sb_start`, `_sb_mine`, `sb_peer_nodes` (friends' cars, name tags, 100 ms behind), `_sb_peers_frame`; Sandbox's
  "Race here" off and leaving goes back to the room as on the web; a guest's battle ends with the host's (race.bb.over). hud.gd: the
  friends list. menu.gd: Balloon Battle and Sandbox are offered in rooms.
- THE RIVALS COUNT DID NOTHING (owner: "setting the cpu number has no effect on the game, i just set it to 0 and still had a full cpu
  lobby"). `_start_race` gave a full grid whenever `state == "menu"`, meant for the menu's background race; but a race started from
  the menu also starts while the state is still "menu", so every race had seven rivals. Now `_start_race(cfg, bg)`: only the three
  background-race callers pass bg=true. Test: tests/cpus.tscn (0, 1, 3 rivals from the menu, a full background grid).
- Tests: tests/xmodes.tscn + tools/xmodes_web.py (browser hosts, PC joins; CR_XMODE=bb | sb): both pass both sides; xplay (race
  cross-play), gpnet, smoke, battle, sandbox, cpus pass. Not tested: the PC hosting a web friend in battle or Sandbox.
- Memory: the cross-play tests need about 5 GB free (a browser plus Godot); twice Claude Code stopped them when the machine ran low.
  Close other apps first, and stop leftovers by their script names (xmodes_web.py, mqtt_broker.py, xmodes.tscn) afterwards.

### 2026-11-16 (web v208, ONLINE VERSION 115 on the web; the PC is still 114 and cannot join web rooms until it is ported): Balloon Battle and Sandbox on line
The owner: "lets add sandbox and balloon battle online to the web version before porting to pc". Web: tools/mini/patch45.py (battle),
patch46.py (Sandbox), patch46b.py (the username sheet closes when a race or a place starts). Tests: tools/neon/bbnet.py, sbnet.py (two
browser windows through the real matchmaking; both pass), and gpnet2.py still passes.
- BALLOON BATTLE ON LINE uses the race's model: the host runs it (rules, clock, CPU drivers, boxes, hits), friends predict their own kart.
  NET_REM gained bal, bbL, bbS, bbOut, bbDead, bbPlace (bbDead in NET_ZB); a battle's snapshot carries bb:[BB.t, over]. A friend's screen
  (netBattle) turns the changes into what the host shows its own player: pops, +1, "Back with N", "Last balloon!", "X is out", the
  winner banner, the read-out; out of the round it watches (bbWatch) and the results wait for BB.over (netOnSnap and onPlayerFinish: a
  battle logs no race time). While a friend waits for a new set the guest step slows its kart as battleTick does. Results on line:
  bbRank order with bbResRow points (renderResultsNet, bat).
- SANDBOX ON LINE is NOT the race's model: each player's Sandbox runs on their own screen as off line (NET.cfg stays null); the room only
  carries where everyone is. NET.sbx is set by the host's netHostStart in mode 'sb' ({t:'sbgo', mi} to everyone; a late friend is sent in
  every 2 s until its first place arrives: NET.sbIn). 12 times a second: guest {t:'sp', p:{reg, x, y, z, a, sp, nm, ri, tr, b every 2 s}}
  -> host (NET.sbP) -> everyone {t:'sps', ck: the host's clock, l: [places]}. sbnRender draws a friend in the same place (buildKart of
  their build, a name sprite, 100 ms behind between their places, at most 0.2 s run on); #sbnList lists everyone and where they are
  (sbRegOf name). Friends never collide (nothing on line moves a kart). The clock follows the host's (sbnGot). In a room Sandbox's
  "Race here" is off; leaving Sandbox goes back to the room screen; goRace inside a room's Sandbox (the shop, Back to the track) skips the
  race's ready-up (NET.sbx && mode 'sb').
- PC: none of this yet. The PC must speak PROTO 115 (the six battle fields at the end of NET_REM, bb in snapshots) and the Sandbox
  messages (sbgo, sp, sps) before it can join a web room again; until then a PC and a browser cannot play together.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A friend's battle results said "First time logged 0:03.52" | onPlayerFinish logged the round as a timed race | onPlayerFinish in a battle only shows the results | A new mode on line: check what onPlayerFinish does for it |
| The username sheet stayed over Sandbox when a friend's room started it | It opens 2.5 s after the menu, and the room can start the game meanwhile | goRace closes it (patch46b) | Overlays that can open by themselves must close when a race starts |

### 2026-11-16 (web v207; the PC does not have it yet): usernames and the world leaderboard
The owner: "add an online leaderboard for each map where you can see the top 20 fastest runs from any player"; "each player should have to pick
a username and they can change it in settings"; off-line races count too; split "with rivals" and "alone". Web: tools/mini/patch44.py.
- THE STORE is the owner's Supabase project (free): https://ymlfwrwrewxxsazylprf.supabase.co, the publishable key sb_publishable_K_widd5...
  (in the game: LB in patch44; it is public by design). The owner made the project and ran the SQL below; the dashboard is theirs. NEVER ask
  for or use the service_role / secret key or the database password. Tables players and runs are not readable or writable from outside
  (row level security on, no grants); everything goes through four functions (security definer) and one view:
  name_free(p_name) -> bool; claim_name(p_token, p_name) -> name (claims, or renames the player holding that token; 'name taken');
  whoami(p_token) -> name; submit_run(p_token, p_map, p_cls, p_time_ms, p_driver, p_kart, p_platform, p_ver, p_solo) ('no player');
  view best_runs (map, cls, solo, name, driver, kart, platform, time_ms, created_at): each player's best per map, class and solo.
  Checks in the table: name ^[A-Za-z0-9_ .-]{3,16}$ (unique ignoring case), cls easy|medium|hard|mirror, time 20 s to 30 min,
  platform web|pc. The full SQL is in the conversation of 2026-11-16 and in tools/mini/lb_schema.sql.
- THE TOKEN (crust-lb-token, 40 hex) owns the name; Settings > More > Username > Account code shows it, and the username sheet's "Already
  have a username on another device?" takes it (whoami) to bring the name to another device or the PC.
- RUNS: saveRun -> lbRun: a finished race (not est, not the TESTING autopilot, not Last Slice / Balloon Battle / Sandbox) goes on a queue on
  the device (crust-lb-q, at most 40) and lbFlush sends it when there is a name and a connection ('online' event, menu boot, every run).
  Map key: id (+ '@'+recv), class small/medium/large/reverse -> easy/medium/hard/mirror, solo = one kart on the grid. A run the board
  refuses is dropped; "no player" or no connection waits.
- SCREENS: the username sheet (first menu of a session while there is no name; Not now allowed; name_free as you type); Settings > More >
  Username (Change, Account code); Records: tap a track for its board (lbOpen): speed class, With rivals / Alone, top 20 (your row lit).
  Online rooms use the username (netName).
- TEST: tools/neon/lbtest.py (reads the real board; claim_name and submit_run are caught in the page, nothing is written).
- OPEN: the PC (same functions over HTTPS from Godot: HTTPRequest; platform 'pc'); a "your world rank" line on the results screen.

### 2026-11-16 (web v206 and PC build 8789578d; Sandbox only; that PC build has the PC fixes below but NOT the night lights): Sandbox at night
The owner: "When it's nighttime on the tracks make those little white lines we added to the walls on the hot wheels maps light up like leds
and make the shadows and lighting looks good. Do this for every map in sandbox but maybe for some add street lights or for more off road type
of maps give the cars headlights instead". Web: tools/mini/patch43.py (sbNightArm, built when a place is armed, into SB.grp; sbNightFrame each
frame, after everything else in sbRender; both follow the clock's L, 0 by day and 1 at night).
- LED: toyRails' dash mesh is tagged userData.led; its material glows #8fd0ff at night (emissive 2.4*L) and a copy of the dashes drawn adding
  light (#6fc2ff, opacity .85*L) is the halo. Rooms keep their own lamps, so the effect is gentler indoors.
- HEADLIGHTS under every open sky (kind 'out'): a SpotLight just ahead of the kart (shadows except Lite/Fast) and, because most pizza ground is
  unlit paint that no light reaches, a beam on the ground: a 7 x 13 vertex strip set down on the ground (sbG) each frame from 4 to 174 ahead,
  18 to 90 wide, its light in vertex colours (additive).
- STREET LAMPS on SB_LAMPS (spiral, basil, napoli, tour): posts every ~300 units beside the road (skipping water, shortcuts, other road, drawn
  things, banks), glowing heads, an additive pool of light on the ground under each, and a pool of 3 point lights (2 on Lite/Fast) moved to
  the nearest lamps four times a second. Posts are solid (SB.shapes cyl, night:1).
- Neon places are night already: unchanged.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The headlight did nothing on the pizzas | Their ground is unlit painted scenery (k 3 in sbClockMats): lights do not reach it | The ground beam | A light added for a pizza needs a drawn stand-in on the ground |
| The beam was invisible | Its texture's bright part was where flipY put the transparent end; then it faced down (culled) | Vertex-coloured strip, DoubleSide | Test a new mesh in a flat colour first (scratch/night4.js) |

PC fixes in the same PC build (2026-11-16), none of them online-visible:
- Specials backwards: race.gd use_ability read player_inp["look"], which main.gd never set, so off line and when hosting every special went
  forward (the owner: "the pepperoni special ability needs to be able to go backwards as well"). main.gd's control dict now carries
  "look": aim_back (looking back, or the left stick pulled back), the same as items. A guest of a browser room was already right.
- Frozen tracks burned out to white (the owner, a picture of Frosty Freezer): Vivid's x1.25 sun is not applied on the freezer theme, and its
  exposure is x0.84 and fill x0.85. tests/snap.tscn (CR_MAP, CR_SNAP_T, CR_SNAP_OUT; not headless) takes one picture of a race to judge it.
- A friend's PC on Ultra broke into spreading black squares (fine on Fast): SSIL is off for good (main.gd _apply_quality), the mountain
  shader's normal can no longer be the normalised zero vector, and post.gdshader turns any NaN/Inf pixel black and clamps the rest.
  Not reproduced here (it is the friend's graphics card); if it comes back, ask for the card and a screenshot.

### 2026-11-16 (web v205; Sandbox only, online stays 114; the PC still has the old playset shop): the mechanic's shop, and pulling in
The owner sent a video of a car pulling into a mechanic's garage in another game: "that is what i want for the garage in sandbox. it should
be cool like in the video when you pull in", then "add some texture to the garage building" and "add more details inside the mechanic shop,
stuff on the walls and stuff sitting around the shop similar to the shop in the video". Copied: the feel and the camera (the door rolling
up, a low shot from behind a lift post, the name card); nothing of the other game's names, signs or look. Web: tools/mini/patch41.py and
patch41b.py; the model tools/blender/mechshop.py (toy_mshop_hq 725 KB, toy_mshopdoor_hq 75 KB).
- THE MODEL is a real-size workshop, 14.6 x 13.1 m, 6.7 m to the parapet; the game shrinks it by SHOP_K = 100/14.6 units a metre onto
  SB_SHOP's old footprint (100 x 90 units, a kart about 1.9 m). Front (the door) is +z. Outside: brick plinth, painted block, a blue
  band, our sign (drawn: "CRUST RUSH GARAGE · TUNING & REPAIRS" with a spanner-and-slice mark), roller door box, wall lamps, bollards,
  a hazard-striped apron. Inside: a two-post lift with swing arms, bench with vice and pegboard, tool chests and carts, compressor,
  tyre stacks and a rail of hung tyres, drums, shelving, engine hoist, tyre changer, axle stands, drain pan, cans, cones, a pallet of
  crates, a bin and broom, posters (PIZZA GRAND PRIX, GRIP tyres, a kart blueprint), safety signs, a clock, a TV, an electrics panel,
  an extinguisher, a wall fan, strip lights, steel beams, pennant strings. The texture pairs: concrete, painted brick (gbrick), brick,
  asphalt, ash (sbShopTex: the toy module does not export woodTex).
- THE TOY MODULE: the toy-room helpers (pk, pkReady, paint, metal, mat, std ...) live in `TM` (const TM=(function(){...})()), not in the
  game's own scope: call them as TM.pk etc. from anywhere outside tools/mini/models.js.
- PULLING IN (sbShopTick / sbShopInp / sbShopFrame): the door rolls up over 1.1 s while the kart is in front of it (and down over 1.4 s
  once it is away); its curtain is solid until 80% open (SB.shopDr). Past the threshold the shop drives (the update loop takes
  sbShopInp for the player: straight for the bay, slower and slower), the camera sits low inside behind the right lift post and drifts
  (fov 48), #cine's letterbox bars and card show the kart's name ("Pep's ride · Mechanic's shop"), the HUD and Sandbox's buttons hide
  (stage.cinema, body.sbshop). The kart stops on the bay, holds 2.6 s, the screen fades to black and the driver screen opens as before.
  A tap (#cine's own handler, introSkip) or Enter / Space / Escape skips. Back out: sbShopPut leaves the door open behind you.
  Until the two packs arrive (they load after the menu) the old code-built playset stands there and works as before; sbShopTick swaps
  the new one in once they have.
- Tested: scratch/shop_drive2.js (sbprobe garage): door 0 at rest, opening as the kart comes, the kart stops on the bay (y -448, the bay
  is -447), the card, the fade, the driver screen; scratch/shop_walls.js photographs each inside wall (fixed two mirrored posters and
  axle stands that stood in the cinematic's view).
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The first build of the shop code stopped Sandbox's step: "pkReady is not defined" | The toy helpers are inside the TM module | TM.pkReady / TM.pk / TM.paint ... | Search for a helper's scope before calling it from outside its file |
| The cinematic camera was overridden | sbCam (the chase camera's walls check) ran after it | sbShopFrame runs last in sbRender | Anything that owns the camera goes at the end of sbRender |
| Pictures on side walls came out mirrored | uv01 maps the face's across axis one way; a picture seen from inside a left wall reads the other way | uv01(o, ax, flip) per wall: front flip, left not, right flip | Photograph each wall from inside after changing a picture |
| A kart in a hollow on Oven Rush could not drive out: "an invisible border was blocking me" | sbBlocked counted a drawn thing in the way when its top stood a step above the KART; cheese and pepperoni discs lying on a slope ahead do, only because the hill rises | patch42 (and PC sandbox.gd blocked): on a pizza a drawn thing counts from the higher of the kart and the ground under it | scratch/dip_find.js: 200 random spots off the road, can a kart drive out in six directions (1 trapped before, 0 after) |
| The owner could not take item boxes on the kitchen track in Sandbox on the PC | NOT reproduced: godot tests/sbbox.tscn (CR_MAP=kitchen CR_MODE=sb) takes all 9, set down on them and driven through at speed; the web takes them too | (open: asked the owner what happened) | Run sbbox.tscn after any change to the box test or Sandbox's ground |

The PC: (1) after leaving an online room the menu still thought it was in one and kept hiding Balloon Battle and Sandbox (off line only)
until a restart: webnet.leave() now clears menu.net (the owner: "both balloon battle and sandbox disappeared"). (2) The PC's shop is still the
old playset: porting the model and the pulling in is open work.

### 2026-11-16 (the PC build after 92bf344; no online change): three things a PC guest saw wrong in a browser host's race
The owner, on the PC exe as a guest: "when throwing a projectile for some you dont see them come from the car for example the anchovie",
"the sound effect for hitting an item wasnt working on pc", "i can drive right inside the other online players car, on their end it shows
us hitting each other but on the pc end it was showing me inside their car". All three are the picture or the sound on the guest only;
the host still decides everything, so nothing here changes what the race does (no online version change). webnet.gd, view.gd, kart.gd.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| No box break or pickup sound when a PC guest drove through an item box | A PC guest's boxes changed only by snapshot, and nothing made a "box" event; the web guest breaks the box at once (netGuestStep) | webnet `_box_guess` after each step (the race's own box test, `pr` marks it), and `_snap` breaks a box someone else took (nearest kart), as the web's boxFx(b, nk, true) | A guest shows what it can predict at once; the host's snapshot only confirms |
| A guest's own anchovy (any fast throw) first appeared far up the road | It exists only in the host's snapshots, which reach the guest a trip late, while the guest's own kart is drawn where it is now | `_snap` gives a guest's own new projectile `lox/loy/lt` (the gap to the kart); view._draw_projectiles closes it over 0.3 s | Picture only; never move the projectile itself on a guest |
| A PC guest seemed to drive inside a friend the host showed it bumping | The guest's kart is drawn where it is now, the others where the last snapshot put them: half a round trip plus a snapshot behind, about a kart length at speed | Kart.lead (webnet `_snap`: half the ping plus one snapshot, at most 0.15 s); view.draw_kart draws the others that much further along their heading | Picture only; the bump itself is the host's |
The web guest has the same two picture gaps (projectiles, other karts drawn late); not changed there yet.

### 2026-11-16 (web v204 and PC build 92bf344b; Sandbox only, online stays 114): drive up the hills on every pizza
The owner, with a picture of the dunes beside Oven Rush Raceway: "You should be able to drive up them unless of course they are straight up
and down. The car should struggle a little like a real car would ... better off-roading will help as well". Web: tools/mini/patch40.py;
PC: kart.gd (the pull) and sandbox.gd `blocked` (the cliff), the same numbers.
- Measured first (scratch/oven_probe.js, sbprobe.py): the land beside the pizza tracks rises 50-75 degrees for its first 40-60 units, then
  rolls gently. v200's limit (about 40 degrees for a middle kart) stopped every kart at the foot of every dune. The red and white kerb
  beside the road is 4.6 high: already a step. What else stands there (68 of 286 sides on Oven Rush) is drawn things: the start arch's
  legs, trees, rocks.
- sbClimb (the cliff): a rise over SB_R of tan 1.88 + 0.24*off, clamped 1.19..2.75: about 62 degrees for a middle kart, 70 the best
  off-road, 50 the worst. sbGrav: the pull uphill in Sandbox is 165*sin(slope)*(.69-.04*off, clamped .4..95) (it was tan(slope) times
  .45-.085*off, which grows without end on steep ground). The engine's own push (ACCEL 110 x acceleration, less as the speed rises) is what
  climbs, so a kart's acceleration matters as a real car's power does.
- scratch/climb7.js (the climb test with bands 20-72 degrees, 8 s): Oven Rush and Margherita: the middle kart climbs all to 50, most at
  50-57, about half at 57-64, none steeper; the best off-road everything to 64; the worst stalls past 50. A middle kart takes about 1.2-1.5 s
  for the last 36 units from a standstill (about a sixth of its top speed): the struggle.
- TESTS: web sbtest bedroom and margherita passed; PC tests/sandbox.tscn (CR_MAP=margherita CR_MODE=sb) PASS.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| PC tests/sandbox.tscn failed "it comes out of the matching gate garage>margherita", also with PC build 91f7f6ea's own maps and without this change | The kart comes out of the tunnel still moving and had driven 60.8 when measured; the limit was 60 | The limit is 80 (other gates are hundreds away, so it still tells the right gate) | Read fromGate in its report before calling a failure a wrong gate |

The owner said (2026-11-16) Balloon Battle and Sandbox were not on the PC. The copy in their Downloads (build 91f7f6ea) has the arena and
every place's Sandbox block, and tests/menushots.tscn with CR_MAPS set to that copy's maps folder shows both in the home screen's Mode row.
They are hidden only inside Play with friends (both are off line). If it comes up again, ask for a screenshot of the home screen and the
build number printed small in its bottom right corner.

### 2026-11-15 (web v203 and PC build 91f7f6ea; ONLINE VERSION 114 on both): the vehicles evened out; Shockwave through garlic; two unblockable anchovies
The owner, after the trial below: "Yes go ahead with the vehicle changes", then: "make the pineapple go through the garlic shield but not
the mozz shield let's also make anchovy not blockable instead let's go with the 2 anchovies instead of 3". Web: tools/mini/patch38.py
(vehicles) and patch39.py (specials); PC: scratch/pc_patch38.py and pc_patch39.py made the edits in kart_builder.gd, kart.gd, race.gd,
webnet.gd, tests/abil.gd, assets/kart/roster.json (and the git-ignored assets/garage/garage.json, which the release exports again from the
live web anyway).
- SPEED per point 2.2% -> 1.4% (statMods `.spd`, KartBuilder.stat_mods). HANDLING is grip too: outside a drift the path follows the
  facing `(gripT?7:9) * (1 + 1.2*(hnd-1))` as fast. WEIGHT in a wall hit: every `k.speed*=1-X*dot` (7 on the web, `_slide` and the
  shortcut wall on the PC) is times `wallK(k)` / `wall_k()` = 1 - 0.4*(wgt-1). OFF-ROAD: kerb .86+.03*off (was .02), grass
  clamp(.58+.08*off, .36, .86) (was .06, .4, .82).
- STAT SUMS (numbers only, models untouched): Slicer [2,-2,1,-1,-2] -> [2,-1,1,-1,-1]; Pronto [0,-1,0,2,1] -> [0,-2,0,2,1];
  Tomatino [-1,1,0,0,2] -> [-1,0,0,0,2]. Interceptor stays +1.
- TRIAL after the change (abiltest.py trial, 3 maps): worst body +10% behind the best (was +12%); Monster Truck and Vintage Tourer last.
  0.8% per point was tried too: no better (worst +9.5%) and speed would mean almost nothing, so 1.4% stayed. The solo trial is noisy
  (the same body differs 10% between tracks) and cannot show weight's worth (bumps, spins), so do not tune it below about 5%.
  What still holds the heavy, slow-turning bodies back alone is turning (the auto driver's steering scales with hnd).
- PINEAPPLE: only a Mozz Melt Shield (shield with mzH) is popped without a spin; garlic (shL) no longer stops it: spun, cloves kept.
- ANCHOVY: two fish (`j<=2`, spread (j-1.5)*.25), nothing blocks one: the held-item stop of patch 37 is gone, and a Mozz shield is
  cleared before the forced spin. A hop still dodges; blinking after a hit, Pesto Rush, Fire Trail etc. still make it wait as before.
- TESTS: abiltest / tests/abil.gd updated (garlic spun with 2 cloves left; a fish through a held item and a Mozz shield); web boottest,
  simtest margherita (8 finished, 0 respawns) and bedroom (8, 0), sbtest bedroom passed; PC abil, items and smoke on margherita and
  bedroom, battle (preptable) and stats PASS.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| PC tests/stats.tscn failed after the speed change (2924 builds differ) | It compares with scratch/stats/web_stats.json, written by the web's statstest.py, and that file was from before; statstest.py also had .022 written in | statstest.py now checks .014; run it first, then the PC test | Whenever statMods changes: change statstest.py, run it, then run tests/stats.tscn |

PC build 91f7f6ea (godot 91f7f6e, tracks exported from web v203, online 114) is OUT: PC and web race each other again.
(Before it, PC build 3b1ecefb went out with web v202's tracks, online 113.)

### 2026-11-15 (web v202 and PC build 3b1ecefb; ONLINE VERSION 113 on both): the drivers' specials evened out
The owner asked which specials were too strong or too weak, then: "Let's commit those changes". Web: tools/mini/patch37.py; PC: race.gd,
view.gd, webnet.gd (scratch/pc_patch37.py made the PC edits). The descriptions in ABIL say the same on both.
- PINEAPPLE (Spiky Shockwave) was the one hit nothing stopped, 260 across, karts in the air too. Now 150; still through ability boosts
  and Delivery Rush, but `spinOut(force)` returns false for a kart in the air or gliding or still blinking (inv), and a shield (Mozz's
  cheese, garlic: shield / mzH / shL) is popped with no spin.
- ANCHOVY (School of Fish): three sure hits; now a held item stops one (`absorbHeld` in the sure branch of itemsProj; PC _absorb_held).
- SHROOM: MEGA_T 5.5 -> 4.5, FLAT_T (squashed) 3 -> 2.   MOZZ: the boost .7 -> 2 s (and the Shockwave only pops the shield).
- OLIVE: slicks catch within r 17.9 (320 squared, was 200) on the host and in a friend's claim (netGuestClaims), drawn 1.5x with the
  ring 1.27x; a 1.2 s boost as the trail starts. Computer racers on a race track never steered round slicks (aiInput has no hazard
  dodge), so nothing was needed there.
- PEP (Pepperoni Storm): slices 15% faster; the first wall bounce turns a slice up to .5 rad toward the nearest racer ahead within 420
  (pepAim / _pep_aim; it reads kart positions, so it runs where the projectiles run: the host).
- BASIL, CHILI: unchanged.
- TESTS: web tools/neon/abiltest.py (ABILITY TEST passed), PC tests/abil.tscn (ABIL PASS, the same numbers: the slice turns 18.4 degrees).
  abiltest.py `trial <map>` also times every vehicle alone on a track (no items, fixed random numbers, standard wheels and parachute;
  run ONE map at a time: three in one browser ran the machine out of memory). Found (margherita, peaks, kitchen; scratch/trial_sum.py):
  the vehicle's own top-speed point decides nearly everything: speed +2 bodies 1-4% behind the best, +1 3-7%, 0 7-9%, -1 9-12% (about
  20 s over a race between Formula and Monster Truck); acceleration, handling, weight and off-road barely move it. Vehicle points sum
  to 0 except Interceptor +1, Pronto +2, Tomatino +2, Slicer -2. (Acted on in web v203, above.)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A test kart placed 700 units off the track was never reached by a sure anchovy | Off the track a projectile is folded back inside RIM (1662 on Margherita) | Test karts stay on the grid or on track points | Place test karts with `track[j]` (web) or on their grid spots (PC) |
| A time trial never finished | The countdown is ended by a timer, not by update(); a script that only calls update() stays in 'countdown' and finAt is never asked | The trial sets state='race' and raceTime=0 after resetRace | Any script that drives races by calling update() must do the same |

### 2026-11-15 (web v201 and PC build 521732c1, online 112 on both): in Sandbox Y is the special ability, the map is Select
The owner: "if y is to use an item on controller in sandbox then the map should be the select button". Select (View / Back / Minus)
already opened the map in Sandbox and nothing else uses it there (in a race it looks behind; Sandbox gave that up in v193). Y now fires
the ability as in a race, Select alone opens and closes the map; v200's R3 for the ability is gone. Web: tools/mini/patch36.py and the
texts in sandbox.js; PC: main.gd (Select only; Y is the ability, not while paused), hud.gd's badge, sandbox_map.gd and menu.gd texts.

### 2026-11-15 (web v200 and the next PC build; ONLINE VERSION 112 on both: a grid may now have fewer than eight)
The owner, after v199: the controller pointer and scrolling slower on a phone; the speed slider over the item slots; abilities in
Sandbox; a mechanic's shop in the garage to change driver and kart without leaving; choose how many computer racers (none to practise,
one for a one-on-one); hills in Sandbox you can drive up, harder the steeper, off-road helping. Engine patch: tools/mini/patch35.py.
- COMPUTER RACERS: a stepper on the home panel ("Computer racers", 0 to 7, kept as crust-cpus; the PC: menu.gd `cpus`, sel "cpus").
  `cpuCount()` (PC `_cpu_count`): the menu's background race always seven; Last Slice and Balloon Battle at least one. Offline the rivals
  take the slots nearest the player's (3,5,2,6,1,7,0); online the host's count fills the seats the friends leave (web netBuildCfg, PC
  webnet.gd and race.gd `trim_cpus`) and the guests race the list they are sent. NET_PROTO / PROTO 112 so an older build is not put in a
  room with a short grid. Checked: a race alone finishes 1st with a one-row table; a one-on-one finishes; Last Slice with 0 gets 1; an
  online cup with the host's 1 rival has three karts on both screens and the cup goes on (scratch/gpnet_cpu.py).
- ABILITIES IN SANDBOX: `useAbility` returned in every battle-rules mode; now not in Sandbox (`BATTLE&&!SBX`), the button shows there
  (battle.js `body.battle:not(.sbx)`), and on a pad it is R3 (Y is Sandbox's map: the owner's earlier choice); its badge says R3 there.
  PC the same (race.gd, hud.gd, main.gd JOY_BUTTON_RIGHT_STICK).
- HILLS IN SANDBOX: two things stopped a kart on the pizzas' slopes. (1) The engine pulls every kart back by the slope under it
  (`k.speed-=sl*165*dt`): enough to stop one on anything over about 18 degrees. In Sandbox, uphill, it is now `sbGrav(k)` of that:
  .45 for a middle kart, down to .12 for the best off-road and up to .9 for the worst (statMods .off). (2) The cliff test for a pizza's own
  ground was a fixed step (5.5 over SB_R 6.5, about 40 degrees): now `sbClimb(k)`, about 40 degrees for a middle kart, 50 the best, 26 the
  worst. Races are untouched (behind SBX). Measured (scratch/climb6.js: six hills per band, from 36 below, 4 s): middle every hill to 32
  degrees, about half at 32-38; the best off-road every hill to 46; the worst fine to 20, struggling at 20-26, none steeper. Note: in
  Sandbox the off-road share of top speed does not apply at all (the engine sets tp=1 under BATTLE), so this is where off-road counts.
  PC: kart.gd (the pull) and sandbox.gd `blocked` (the cliff), the same numbers.
  A NAME CLASH CAUGHT HERE: the first version named its helper `sbOff`, the name of the function that switches Sandbox off; the later
  declaration won and the helper returned undefined. It is `sbOffRd`. Search for a name before adding a function to sandbox.js.
- THE MECHANIC'S SHOP (sandbox.js SB_SHOP, sbShopBuild / sbShopTick / sbShopOpen / sbShopDone / sbShopPut; PC sandbox.gd SHOP, shop_put,
  sandbox_view.gd _build_shop, main.gd _sb_shop_open / _sb_shop_done, menu.gd `shop` and `shop_done`): a toy garage playset on the
  garage floor at (205, -443), door to the north, chosen by searching the floor for room and headroom away from the track (the first
  choice, by the west wall, was under a shelf's beam). Its walls are SB.shapes; drive in and the driver screen opens with "‹ Sandbox";
  the garage's last button says "Back to Sandbox"; either brings you out of the door with what you chose (no fly-over). A pin of its own
  on the map ("Mechanic", blue with a spanner); travelling there sets you down at the door.
- PHONES: patch 35's PAD_MOB / PAD_MOBS: on a touch screen the controller's pointer moves at 55% and every scroll it drives at 50%.
  The speed slider (sbSpdUi) places itself below whichever item or ability buttons stand above it, twice a second, and shortens its track.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A kart could not drive up the hills beside the pizza tracks in Sandbox | The engine's pull back down a slope stops a kart past 18 degrees, and off-road did not matter in Sandbox | sbGrav / sbClimb (above) | scratch/climb6.js after any change to the kart's acceleration or the slope pull |
| The speed slider overlapped the item slots on a phone | Its place was a fixed height from the top | It measures the buttons above it | |

### 2026-11-15 (PC build, with web v199's tracks): Sandbox's clock, things to do, Easter eggs and Back to the track on the PC
- THE CLOCK: `scripts/sandbox_clock.gd` (a port of the web's sbClock*): made by the place's SandboxView when the place is the one being
  driven and the kart is out of any tunnel (the tunnel, sandbox_warp.gd, has the lights then); ten updates a second; `off()` when the view
  leaves the tree puts every light, sky colour, fog, exposure, bloom and material back. The hour is the save's "t" (the web's crust-sb
  shape), moved on in sandbox.gd tick. Stars are a term in `shaders/sky.gdshader` (`stars`), so they are behind everything. The PC's night
  fill for open-air places is stronger than the web's (amb .75+.25D, exposure +25% at night): a share of the PC's fill comes from the sky,
  which goes dark, and the first try was near black. Pictures: `tests/sbclock.tscn` (windowed) writes build/sbclock/<map>_<hour>.png.
- THINGS TO DO AND EGGS: `scripts/sandbox_acts.gd` keeps the same table as web activities.js; the markers' and the egg's spots come from
  the export (T.sb "acts", "egg", web sbExport v199): a place exported before v199 simply has none. The activity under way is static (it
  goes through tunnels with a delivery). The offer and the objective bar are drawn by hud.gd (`sb_act`, `sb_bar`); the end panel is a sheet
  in main.gd (`_sb_act_end`, Retry / Close); `_sb_travel` ends a delivery (fast travel), `_sb_race_here` ends one, `_to_menu` drops it
  quietly. Markers: a ring and a word on a board (PIZZA DELIVERY, DRIFT, JUMP); eggs built of spheres, cones and boxes as on the web.
- BACK TO THE TRACK: main.gd `_sb_back_ask` (a sheet over the pause menu: Move me / Cancel; Esc or Start closes it) and sandbox.gd
  `back_to_track` (the nearest track point, a difference in level counting three times over, never by a loop).
- TESTS: tests/sandbox.tscn now also checks Back to the track (`_to_track`) and, on a place exported with them, every activity marker
  (offered, started, done or cancelled) and the egg (`_acts`).
  RELEASED in PC build 521732c1 (2026-11-15, godot 521732c, tracks exported from web v201, online 112): PC and web race each other again.

### 2026-11-15 (web v199, the same release): the day and night clock switched on, things to do, Easter eggs, Back to the track
- THE CLOCK (sandbox.js, `SB_CLOCK` now true; built in v197 and left off until its pictures had been looked at). Looked at, noon / sunset
  / dusk / night / the start flag at night, in margherita (out), bay, the back garden (out), bedroom and kitchen (in: lamps on, windows
  dark), laser (dark: its own look). Two faults fixed: the stars drew in front of the far tree cards (they were see-through things, sorted
  among the see-through cards, on a ball nearer than those cards): now drawn among the solid things straight after the sky, adding light,
  writing no depth, so everything drawn later covers them, and faded by colour; and the start flag blazed at night (unlit and bright, and
  the night's bloom is stronger): the clock now keeps it at half brightness and its glow at a third (`SB.flag.mats`, `.glow`, its own copy
  of the glow material). The kitchen's window panes (plain unlit blue, no picture) now darken with the sky: patch 34 names them
  `sky_window`. THE PC HAS NO CLOCK YET.
- THINGS TO DO (tools/mini/activities.js, new, carried in by inject_mini.py after sandbox.js; the brief's section 5): markers on the road
  (a coloured ring and a turning sign); stop in one and a button offers it with the coins (tap, Enter, D-pad up). Two deliveries
  (Margherita's pizzeria to Sauce Spiral's start line, the safe way through Basil Boulevard or the quick way through the Oven; Kitchen to
  Bedroom), two drift challenges (Margherita, Bay: seconds drifting in all) and two jump challenges (Back Garden, Sauce Spiral: seconds in the
  air). An objective bar at the top; at the end the coins and Retry (Enter, A) / Close (Esc, B). A delivery carries through tunnels (the
  clock stops in a tunnel, as the game does) and ends on fast travel or a race from a start line; Retry takes you back to its marker. Full
  coins the first time, half after; a quick delivery adds a third. Saved in crust-sb: `.a[id]` {n, best}.
- EASTER EGGS (activities.js, `SB_EGGS`): one in each of eight places (a cat, a seashell, a snowman, a robot, the rubber duck, a runaway
  meatball, a wrench, a garden gnome), models built in code; off the racing line (on a pizza where a kart can reach it from the road and far
  from the pepperoni coins; in a room beside a hidden coin's spot and at least the track's width plus 30 from it; on a neon road at the far
  edge). 25 coins once; saved `.e[id]`; not on the map. The web exports each place's activity markers and egg (`sbExport` .acts, .egg) so
  the PC can take the same spots. THE PC HAS NEITHER YET.
- BACK TO THE TRACK (sandbox.js `sbBackBtn`, `sbBackAsk`, `sbBackGo`). The owner, 2026-11-15: "add a button in the pause menu that can just
  take you right to the nearest spot on the track ... a confirmation pop up should pop up so the player doesn't accidentally hit the button".
  Under Map in Sandbox's pause menu; "Back to the track? / Move me / Cancel" first; then the kart stands still in the middle of the nearest
  stretch of road at the same level (a difference in height counts three times; never on a loop), facing the way the track runs, and the
  game resumes. THE PC HAS IT NOT YET.
- TESTS: the activities by a probe (scratch/acttest.js: offer, start, the bar, done and paid, retry at half, fast travel ends a delivery,
  Retry travels back, the delivery through the Oven to Sauce Spiral with its drop-off ring); every egg placed and found (8 of 8); Back to the
  track in Margherita and the bedroom (dialog, Cancel, Move me, on the road at speed 0, resumed).
- KNOWN, NOT NEW: `sbtest.py` with no place (the back garden) fails two wall checks, "shed, from the south" and "the tree, under the
  spiral" (the kart is not stopped there). The same two fail on v198 (checked on a copy of it): older than this release, not looked into.

### 2026-11-15 (web v199, online 111 unchanged: nothing here moves a kart): THE NO-STOP TUNNEL ON THE WEB
The owner: "i dont want the streaks to freeze for a second it should be the player continusously driving and eventually the new map will
load and the driver will drive out but the game will never freeze or stop to load it will be one fluid drive through the tunnel right out to
the other side". The PC has done this since build 68030144 (a thread). Until v198 the web held a still picture of the last frame, the kart
cut out on top and streaks animated by the browser, for the 1 to 5 s the load took (measured at Ultra: building the place 0.2 to 2 s,
its first draw and shaders 0.3 to 3.5 s). A browser has no second thread for this, so the load is cut into slices instead:
- THE SLICER (build time, so the source stays plain): `build/build_gh.py` runs `tools/jsparse/slice.js` (acorn, installed in
  tools/jsparse) on the game script with the names in `build/slices.txt`. Each named function becomes a generator NAMEG that yields between
  its statements (once a pass in a loop, every 64 passes in a loop inside a loop: a yield costs about as much as a small statement, and 8
  million of them made a whole load twice as slow), and NAME stays a plain function that runs it to the end at once, so every other caller
  is unchanged. In a sliced function a call to another becomes `(yield* OTHERG(...))`; `const name=function(){}` or an arrow with a block
  body, written inside a sliced function and named in the list, is sliced too (`buildBarrier`, `place`, `spots`). A callback (`forEach`,
  `traverse`) cannot pause: the two that took long were turned into loops in the source (sbColumns, toyScenery's boosters).
  `SLICE_MAP=<file>` in the environment writes each yield's id with the code after it, to find a slow slice.
  Measured, Ultra on the RTX 3060: the longest slice of a load 50 ms (was one 430 ms call), a whole load as fast as before (bay 2.2 s).
- THREE.JS: build_gh.py writes three r149 with one change, as `vendor/three-0.149.0.<hash>.js`: with `renderer.__crDefer` set,
  `renderer.compile` creates a new program and goes on (r149 asks for its uniforms at once, which waits for the driver: about 0.1 s a
  program, 1.4 s for a new place). Such a material is set up again at its next draw (its `__version` cleared). The source page still loads
  plain r149 from the CDN: there the flag does nothing and the tunnel only waits a little longer.
- THE TUNNEL (tools/mini/sandbox.js: sbTravel, sbTripG, sbWarmG, sbWarpFrame, sbWarpOut, sbWarpPrime; engine side tools/mini/patch34.py):
  the kart drives on in a scene of its own (SB.ws: the warp tube, its road, the light at the end, two lamps, a copy of the kart), drawn
  through the game's own post pass (`drawNow` with `postRender.s/.c`), steering left and right, the streaks and road running at its speed
  and the engine sound on. Each frame then spends 9 ms (6 on a phone) on `sbTripG`: the old sbTravel's steps in the same order (loadMap.G,
  the pictures decoded, sbArm.G, the kart set down inside the far gate's own tunnel), then `sbWarmG`: shaders eight things at a time
  without waiting, a frame at a time until the driver is done (KHR_parallel_shader_compile), pictures to the card one a step, each thing
  drawn once on its own into the post target (render layer 30, no shadows), then warmScene. At least 0.75 s in the tunnel (1.1 s for fast
  travel). While it runs the frame loop calls only sbWarpFrame (state 'loading') and the HUD waits.
  In Sandbox every compiled program is kept (use count raised once, `__crKeep`): a place you come back to compiles nothing.
- MEASURED (tools: scratch probes trip.js / trip2.js, the frame gaps the browser saw): coming back to a place, no slice over 0.08 s; a
  first visit to a big place (margherita, bay) has about ten frames of 0.1 to 0.16 s, each the driver finishing one shader at its first
  draw (ANGLE/D3D11 does that on the draw itself: it cannot be moved off the main thread); the frame after the tunnel about 0.1 s (the
  first full-size draw of the place). Before: one frozen picture for 1.2 to 4.3 s on the same trips. `SB.lastWarp` keeps the last trip's
  time, its slowest frame of work and any slice over 30 ms (`log`, ids from SLICE_MAP; 'draw' is the tunnel's own draw).
- THE TRACK DATA IS UNCHANGED: the PC export run locally on the new build (`godot/tools/ciexport.py` with WEB=scratch/webcopy6) gives the
  same json as the CI export of v197 for bay, kitchen and laser; on margherita only the walkers' pauses (the export's clock), the sun's last
  digit and two of the Sandbox wall grid's 50,000 cells differ, and two runs of the same build differ there just as much.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| The web's tunnel showed a still picture for 1 to 5 s | The next place was built, compiled and drawn in one go on the only thread | The load is sliced (above) and the kart keeps driving a tunnel of its own | A new step in loading a place: put the function in build/slices.txt if it takes over 30 ms; look at `SB.lastWarp.log` after a trip |
| three.js r149 waited for every new shader inside `compile` | Its getProgram reads the program's uniforms at once | The build's three.js skips that with `renderer.__crDefer` | If three.js is ever updated, the two replacements in build_gh.py must still match (it stops with an error if not); r158+ has `compileAsync` |
| The first trip of a session paused 0.3 s as it began | The kart's copy met the tunnel's lights for the first time | sbWarpPrime draws it once at the start of Sandbox | |

### 2026-11-14 (web v197, ONLINE VERSION 111 because of the part stats below; Balloon Battle itself is off line): lives and elimination; the table twice the size, an island and a top
The owner: "you start with 5 then after those are popped you have 3 then after the 3 are popped you get 1 after that is popped you are
eliminated. also lets add more item blocks and make the map bigger" and "add another higher up section or make the higher up section
bigger". The rules, the table's plan with every coordinate, the drivers and the tests are in docs/BALLOON-BATTLE-PLAN.md (last section).
- RULES (tools/mini/battle.js): `BB_SETS=[5,3,1]`; `bbSetLost`, `bbElim`, `bbFinish`, `bbRank`; no halving of points; the round ends with
  one driver left or at the clock (`BB.T` 300 s, a backstop: eight rounds of computer drivers all ended with one driver left, 44 to 141 s on the clock). An eliminated player watches
  with the engine's spectating; its button is "Skip to results" (`bbSkip`, `bbFast`: the rest of the round is played out at once).
- THE ENGINE (tools/mini/patch31.py, all behind `BATTLE&&!SBX`): `standings()` is `bbRank` in a battle; a driver still in can be watched;
  no track cameras; the spectate bar shows balloons and points; the results row says "out"; the menu's note.
- THE TABLE: 1100 x 760, five pans, the long raised route (lid, box stacks, baking sheet, the dough trays at 84, cheese wedge, block,
  bread board), the island (crates of tomatoes, two ramps), 31 item boxes, 8 spawns with headings. Models: tools/blender/battle.py
  (six packs, bbisle is new; about 1.2 MB, it was 0.55).
- THE DRIVERS find their way on a grid made from the shapes (`bbGrid`, `bbPath`, `bbClear`, `bbSee`): no list of ramps.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Computer drivers wedged in the table's north-west corner and in the inner corners between two ramps, and were set down again 3 to 5 times a round | A row of pans up to the corner made the lane behind them a dead end; and the drivers steered by three feelers only, which cannot get out of a corner they face | No pan in that corner; the grid path-finder; backing out swings the tail toward the way on | A new arena layout: run `bbtest.py` with WHERE=1 and look at where karts stood still; "set down again" should be 0 |
| The drivers hardly popped anybody after the path-finder went in | With a rival in sight they still steered at the next square of the path, so were never lined up | With a clear shot (`bbSee`) and something to throw they steer straight at the rival | |
| The eliminated kart was still drawn | The engine's own kart drawing shows it again every frame (Last Slice Standing never noticed: its kart is parked far off at once) | `battleRender` hides a `bbDead` kart every frame; the player's kart stays in place 1.6 s so the camera does not jump | |
| Under a leaning ramp a kart was stopped by nothing visible | The game's ramp is solid down to the table; the model was a thin sheet | Every leaning ramp has a board down each side (`skirts` in battle.py) | `bbprobe.py bbcheck.js` drives at every wall and measures to what is drawn: nothing over 1.5 |
| The Blender bake ran out of GPU memory | The game's tests were using the graphics card at the same time | `CR_CPU=1` builds on the processor | |
- CHECKED (the final build, 2026-11-15): `bbtest.py` six rounds, then two more: all ended with one driver left (44 to 141 s left, 68 to
  71 pops, longest still 2 to 4 s, nobody below the table, set down again 0). `bbprobe.py bbcheck.js ultra`: 31 boxes and 8 spawns ok,
  all 31 boxes taken (slowest 9.5 s), 135 places driven at: drawn against solid least -2.05, most 1.35 (the -2.05 is the baking sheet's
  low rolled rim two units before the south wall: the one place over 1.5). boottest, simtest margherita and garage (all 8 finish),
  sbtest bedroom, sbworld all 24 places, phonetest, sbphone, padtest, finishtest, gpnet2 (a whole cup through the real matchmaking): pass.
- THE STANDINGS PATCH OUTSIDE A BATTLE: patch31 changed `standings()` and spectating behind `BATTLE&&!SBX`. Checked by a run: a Last Slice
  Standing race on the bay played to the end (`MODE=lss py.cmd tools/neon/simtest.py bay medium 600`): one driver out on each of laps 1 to
  7 in last-place order, places 8 down to 2, the survivor first; and the online cup test passes. The phone test prints no memory figure,
  so there is no before/after number for the bigger arena on a phone: ASK THE OWNER whether the arena loads on the iPhone.
- FOR THE PC (not done): battle.gd needs the same rules and drivers; the export's `d['battle']` needs `sets` (BB_SETS), spawns with a
  third number (heading), 31 boxes; `BB_START`/`BB_BACK` still exist (5 and 3) but mean nothing now.
- ONLY A PERSON CAN JUDGE: whether five minutes and this pace feel right, the table's size by hand, the camera on the top and beside
  the trays, how watching and "Skip to results" feel, the look of the cheese wedge and the trays.

### 2026-11-14/15 (web v197, same release): part stats add up (ONLINE 111); Sandbox's speed slider and wider tunnel mouths; the body on a jump ramp
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| A wheel's +1 and a glider's +1 showed (and drove) as +1, not +2 (the owner: "currently the game overlaps them") | The cards show a part's own `st`, but the sum weighted wheels 1 and gliders .5 (bodies 1.5), squeezed it through tanh and rounded to bars | tools/mini/patch32.py: `statE` = clamp(4*tanh(1.5*body.st/4) + (wheel.st + glider.st)/1.5, -4, 4); `statMods` from it as before; bars = the vehicle's own round(6+1.5*eBody) + wheel st + glider st, held to 0..12. A vehicle alone is unchanged. NET_PROTO 111, PC PROTO 111 with the same sums in KartBuilder | `py.cmd tools/neon/statstest.py`: all 3060 builds, and it writes scratch/stats/web_stats.json; the PC's table must equal it to six places. A new part needs no code: its card numbers are bars |
| Tunnels were missed at full speed in Sandbox | A mouth was 34 wide: the kart's middle had 21 units (three karts) to hit at 150 a second | `SB_GW` 17 -> 26 (52 wide, 39 for the kart's middle; arch, tunnel and trigger all follow `g.hw`); `sbGuide` eases a kart that is heading in and a little off sideways into the mouth over the last 110 units; and the speed slider (`sbSpd`, save field `v`, .25 to 1; the engine multiplies the throttle by it in playerInput; `[` `]`, D-pad left and right, which no longer steer in Sandbox) | Measured (tools: scratch/spd/p3.js with sbprobe): a room's mouth is entered from 22 off centre unaided and 36 guided; a pizza's from 14 to 22 unaided, 18 to 28 guided, uneven from side to side because the crust beside a mouth is a cliff to the kart before it reaches the mouth. The PC takes `hw` from the export; it needs `sbGuide` and the slider ported |
| The body stayed level on a jump ramp | syncKart's pitch comes from `surfH`, which knows the ground and the raised road but not a ramp | `k.rampS` (looks only), set with onRamp, added to the pitch | Nothing but syncKart may read rampS; a friend's kart on line has none (not sent) and stays level |
- The PC had two more faults of its own, fixed in godot (see the PC entry): the body's pitch ignored the raised road altogether (`k_ey`),
  and boxes over a glide did not follow the player's line as the rings do (`_air_box_y`, the web's `airBoxY`).
- ONLY A PERSON CAN JUDGE: whether builds feel right now that gliders count for more and wheels a little less per point; the slider's place
  under a thumb on a real phone (it sits on the right edge between the item buttons and the drift button); whether the guide into a mouth is
  felt as help or as being pushed.

### 2026-11-15 (web v198 and PC build 68030144, online 111 on both): the rest of the PC catching up, and what the owner reported
- PC build 68030144 = web v197's tracks: Sandbox (entry below), the no-stop tunnel, Balloon Battle 5-3-1 on the bigger table, part
  stats that stack (pc_stats.json = web_stats.json for all 3060 builds), the Sandbox speed slider and mouth guide, and the fixes below.
  Web v198 adds only Settings > Kart stats (tools/mini/patch33.py; the PC has the same page in main.gd's "stats" tab: keep the two the
  same, and change both if a stat's numbers change) and the speed slider hiding under the pause sheet and Settings.
- THE NO-STOP TUNNEL (the owner: "the game will never freeze or stop to load it will be one fluid drive through the tunnel right out to
  the other side"). The PC built the next place in `load_map`, which blocked for 1.3 to 3.6 s. Now `scripts/world_build.gd` builds it on a
  thread (track json, glTF, sky, lights, every Hd* helper, props, the Race and the Sandbox object), off the tree, while the kart drives an
  endless tunnel (`scripts/sandbox_warp.gd`); the main thread then takes the new place in a stage a frame (old world out and freed a slice
  at a time, pieces in one a frame, a few frames drawn by a small camera at the exit on render layer 2, then the swap onto the exit gate).
  `scripts/xf.gd` gives a node's world transform and a mesh's points or a picture without the tree or the graphics card, so the Hd*
  helpers run off the tree. Measured, windowed, HD on: longest frame 22 to 38 ms on five trips, one of 52 ms (margherita -> basil); the
  very first trip to a new kind of place may stutter once while a shader compiles (seen twice, about 1 s). KEEP IT: world_build.gd
  repeats _build_world's steps: a change to one belongs in both. Nothing built on the thread may touch what the running game reads.
  THE WEB: done in v199 by slicing the load (see "THE NO-STOP TUNNEL ON THE WEB").
- THE KART LAY FLAT ON CLIMBS (owner's picture, Garage Overdrive by the PIT LANE sign; PC only). view.gd tilted the body by the ground's
  height around the kart, but on a raised road (toy tracks, Sauce Spiral) the climb is the road's own height (`T.k_ey`), which it left
  out; and neither platform knew a jump ramp's slope for the body. Fix: the body's four sample points add `T.k_ey`; `k.ramp_s` (looks
  only, set where the ramp physics sets on_ramp) is added on a jump ramp; the web got the ramp part (`k.rampS`) in v197. Measured: road
  slope 24.3 deg -> body 24.3 deg (was 0) on the garage, the same on kitchen, bedroom, backyard, spiral; a 10.6 deg jump ramp -> 10.5.
- ITEM BOXES UNDER THE GLIDE RINGS (PC only). The web moves a box over a glide to the height the player will pass it (`airBoxY`), as the
  rings do; the PC drew them at their exported height, up to 30 under the rings on Hologram Heights. Fix: `_air_box_y` in view.gd, a port
  of airBoxY (only where the glide has a line, `T.glide.has("p")`: a short glide has none, and reading it there was 8000 script errors).
- "MINIATURE MAYHEM CUP" RAN OVER THE NEXT PANEL (PC). The cup card's title had one size and no clip. Fix: menu.gd `_cup_card` shrinks
  the name until it fits the card, and clips.
- PART STATS (the owner: a wheel's +1 and a glider's +1 "would be a total of 2 speed increase instead of overlapping them"). The cards
  showed raw numbers; the driving weighted body 1.5, wheel 1, glider .5 and squeezed the sum with tanh, so cards and bars disagreed.
  Now: eBody = 4 tanh(1.5 body/4); e = clamp(eBody + (wheel + glider)/1.5, -4, 4); bars = round(6+1.5 eBody) + wheel + glider. NET_PROTO /
  PROTO 111. Tests: tools/neon/statstest.py (web), tests/stats.tscn (PC; it writes pc_stats.json to diff with the web's).
- THE WEBSITE: tools/site_pc.py now says Sandbox and six cups (it said five), and reruns safely.
- STILL TO CHECK BY A PERSON: Sandbox driven by hand on the PC (walls, the tunnel, the swap, music across it), the slider under a thumb,
  the guide into a mouth, the new stats' feel, a round of the new Balloon Battle, the Kart stats page on a phone.

### 2026-11-15 (PC build 68030144, with web v197; written for the first try at this build, 2026-11-14): Sandbox on the PC
- What: the web's Sandbox as it stands in v196 (the whole game as one world, free driving in the house and on the pizzas, keep-to-the-road
  on Sauce Spiral and the Neon tracks, warp tunnels with signs, coins and hidden coins, the race from the start line and the way back,
  Park, the map with zoom and fast travel). Off line only. The plan it followed is the last section of docs/SANDBOX-PLAN.md.
- HOW IT IS FED. The PC cannot read walls from what is drawn, so the web works everything out and the export carries it:
  `godot/tools/ciexport.py`, as its LAST step (after the json and the glTF are written), puts the page into Sandbox with an empty save and
  stores `sbExport()` as `d['sandbox']` (kind, the columns grid, rim, loops, gates, coins, flag, plus `water`, `N`, `multi`), and writes an
  `sb` card into `<id>.info.json` (kind, name, a short lap line for the map). A map is a Sandbox place on the PC only if its card has `sb`;
  a gate to a place that is not installed is left out. On an `open` place (a pizza) the page is built once more WITH its rocks and bushes
  for this step (`window.__hdPropsOff` in glbexport.js): the baked track leaves them out, but on the web they are in the way.
  If the Sandbox step fails for a place the exporter now EXITS 3: the run fails, the old zip stays on the "maps" release and
  `release_pc.py` builds nothing. (Before, it only printed "sandbox: NOT exported" and the place would have gone missing unseen.)
- THE CODE (every hook behind `sb != null` or `sbf`; a race reads none of it): `scripts/sandbox.gd` is tools/mini/sandbox.js in GDScript
  (surf, ground, blocked, touch, walls, idx_of, lvl, cliffs, water, solid, start, arrive, tick, save); `scripts/sandbox_view.gd` (coins, flag,
  arches, signs as Label3D on boards, the warp shader, the tunnel, the load's cover); `scripts/sandbox_map.gd` (the map and fast travel).
  Hooks: kart.gd (`sb`, `sbf`, `sb_off`, `r_bk`: walls, ground, the lap point, pads and loops only for a kart that is at them, a loop the
  other way round, a ramp from behind, the canyon crossed backwards), race.gd (`sb_want`, one kart, `sb.tick`, chili only, no special, no
  finish), main.gd (the mode, `_sb_travel`, the cover, `_sb_race_here` / `_sb_return`, Park, the keys and the pad, the camera kept out of
  walls, Map in the pause menu), hud.gd (read-out, Park button, race offer), view.gd, menu.gd (the fifth mode, "World. Start in").
  Keys: M / Y / Select the map, K / D-pad down Park, Enter / D-pad up the race at the start line. Coins are saved in `user://sandbox.json`
  (the web's `crust-sb` shape); tests and `skip_menu` runs neither read nor write it (`Sandbox.no_save`).
- THE COVER over a load: through a gate the last picture of the game is held (the kart in the tunnel, so it never leaves the screen: the
  owner's words, "i dont want the car to dissappear") with the streaks over it; by the map it is dark with streaks. The streaks stand still
  while `load_map` blocks (the web's keep moving). The cover is up two frames before the old place is freed.
- CHECKED on this PC, on the eight places exported here (bedroom, kitchen, garage, backyard, margherita, basil, spiral, grid):
  `CR_MAP=<id> CR_MODE=sb CR_HD=0 <godot> --headless --path . --fixed-fps 120 res://tests/sandbox.tscn` -> SANDBOX PASS on all eight (a lap
  forwards, a lap backwards, arches and hidden coins reachable, Park, travel through a gate and back, fast travel, Race here and back, the
  map). `smoke`, `battle`, `gpnet`, `padcur`, `allmaps` pass. Ten seeded ordinary races give the same kart positions and times before and
  after the port. Web against PC ground at about 750 points a place (`godot/tools/sbground.py`, then `tests/sbground.tscn` with
  `CR_PROBE=<file>`): no difference in ground or in blocked on bedroom, kitchen, backyard, margherita, basil, apart from 6 points on
  margherita and 2 on basil where the PC's 10-unit race height map itself is off the web's ground formula (that is the race's map, not
  Sandbox: a cliff or canyon edge can sit slightly differently there).
- KEEP IT RIGHT:
  - A change to tools/mini/sandbox.js that moves the kart or changes what stands where needs the same change in scripts/sandbox.gd AND a
    track re-export (the walls come from the export). Web first, then `release_pc.py`.
  - Two web sessions of the same pizza do not give exactly the same grid (moving scenery lands in different squares: about 300 of 50,000
    on margherita). The export is one snapshot; do not chase a few squares of difference.
  - The sixteen places not exported on this PC were first seen by the CI export of this build. If one misbehaves, export it here
    (`WEB=D:/crust-rush/app OUT=maps MI=<index> py.cmd tools/ciexport.py` in godot) and run `tests/sandbox.tscn` on it.
- DIFFERENT FROM THE WEB, on purpose or for now: no special ability in any kind of place; both-brakes full stop only for the two touch
  pedals (keyboard and pad have Park); road places use the PC race's own airborne rule; a way-out face inside each tunnel (the PC draws
  walls from both sides); "Back to the start line" in the pause menu; the flag and ring have no glow. Gliding in Sandbox counts toward the
  gliding achievement (not checked what the web does).
- NOT SEEN BY ANYONE IN MOTION (stills only, all with `CR_HD=0`): driving it by hand, a real controller (Y / Select, D-pad, the pointer on
  the map's pins), a loop ridden backwards and a ramp from behind, the kart's outline through the wall at a tunnel's mouth, the coin
  sounds (existing sounds reused), HD models on, the neon arch, a long place name in the banner. ASK THE OWNER TO DRIVE IT.

### 2026-11-14 (PC build after 254f835, with web v196): Balloon Battle on the PC
- What: the mode as the web has it, off line only. The arena (map 24, `preptable`) is exported with its shapes: `d['battle']` in
  godot/tools/ciexport.py (shapes, spawns, ramps, the clock, step, radius, the item table, the balloon colours), so nothing of the arena
  is written twice. `scripts/battle.gd` (loaded by path, no class name) is tools/mini/battle.js in GDScript: arena ground and touch tests,
  walls, thrown-item walls and level test, spawn, start, hit, rank, the tick, the read-out, the item roll, the computer drivers.
  Hooks, every one behind `T.battle` (kart, view, camera) or `race.bb != null` (race): kart.gd (`tp`, walls, ground, no kerb, no lap-line
  fix), race.gd (`setup_cfg` makes the battle on an arena map and sets `mode = "bb"`, as the web's BATTLE comes from the map), main.gd
  (boot guard, the mode loads or leaves the arena, results, camera, no ghost / best time / lap toasts / achievements), menu.gd (the mode,
  START BATTLE, no track list; the arena kept out of every track list and Records), hud.gd, view.gd (balloons, pop). `webnet.gd` is not
  touched: hosting or joining a room leaves the mode (`_bb_no_net`).
- Checked: `tests/battle.tscn` with `CR_MAP=preptable CR_MODE=bb`: BATTLE PASS, about 106 pops a round and 30 points left at the end;
  the web measured the same way gives 108 to 116 pops and 29 to 34 points (the "15 to 38" in tools/neon/bbtest.py is points left, not
  pops: a score is halved at every all-popped). `smoke`, `gpnet`, `padcur`, `allmaps` (it skips arenas) pass. The same seeded normal
  races give byte-identical kart positions before and after the port (seven races compared).
- Differences from the web, on purpose: the meatball ignores the arena's walls on both (the web's does; a comment in race.gd says so);
  `bbHome`, `bbTarget`, `bbLeader` and the freezer-by-distance are not ported (those items cannot be rolled in a battle).
- NOT SEEN BY ANYONE YET (every run was headless): the balloons, the pop, the read-out's place, the banners, the results sheet, the
  four-button mode row, the arena in the PC's renderer with HD on, the camera at walls and over the west edge, a person driving it
  (aiming, look-back fire, holding an item), and the arena has no menu picture and no song of its own. ASK THE OWNER TO PLAY A ROUND.

### 2026-11-14 (web v195, looks only; PC build 254f835 for online Grand Prix and the controller's cursor): real trees on every track; new previews
- TREES (the owner: "update all the maps with the new trees we made a while ago ... some of the older maps still have the old blocky trees
  and shrubs. take new photos for their preview when you finish"). Every tree outside the house went through `forest()` as one of five
  low-polygon models. Now `forest()` stands each up as crossed cards with a picture of a photo-scanned tree (tools/mini/patch30.py:
  `treeCards`, `TREE_PIC`, `TREE_AS`): three cards near the track, two further out; a bush is the crown of a tree set on the ground; the
  freezer tracks' 1800 green cones are small firs. Twelve tracks change (the bay, freezer and night themes) and every backdrop forest.
  The pictures: `tools/blender/treepics.py -- <poly haven id> <name>` (two side views on a clear ground, plainly lit: the game lights
  them), stored with `put_tex.py tex_tree_<name> ... 1024`. In the game: jac (jacaranda, brightened 1.4x), small (tree_small_02), isl1,
  isl2 (island_tree_01/02), fir (fir_tree_01). All Poly Haven, CC0.
  NOT DONE: the pine (pine_tree_01 needs over 5 GB to render; both pine models use the fir); the bay's palms (no scanned palm is free to
  use: they are still the code-built ones); snow on the firs (a card cannot be tinted white on top).
  Trees were never solid in a race and are not in Sandbox either (a cut-out material is left out of the columns).
- PREVIEWS: `py.cmd tools/neon/mapshots.py` with `MI=<map index>` retakes a track's menu pictures on this PC from the same camera places
  as godot/tools/cishots.py and keeps, for h, m and a, the candidate nearest the picture the track has now; then
  `py.cmd tools/neon/embed_shots.py D:/crust-rush/scratch/mapshots` (it also copies them into the PC project's assets/shots).
- THE PC, build 254f835 (= web v194's tracks, online 110):
  - A Grand Prix on line: a PC host picks a cup for the room (SET CUP; `menu.net_cup`), the cup goes out with every race (`gp_wire`,
    webnet `_build_cfg`), a PC friend reads it (`_gp_from_wire`), the results show the cup table from the standings (`_gp_net_now`), the
    host's button is Next race, a player's points are under the player (`np`). Test: `tests/gpnet.tscn` (GPNET PASS). Not yet played
    between a real PC and a real browser: the CI cross-play test (xplay) only runs a single race.
  - The controller's cursor: `scripts/pad_cursor.gd` (the last child of main, so it hears input before the menus): in the menus, the
    pause sheet and the results the left stick and D-pad move the real pointer, A is the mouse's left button at it (held, it drags),
    the pointer held at the top or bottom of something that scrolls scrolls it; the focus a screen gives its main button only says
    where the pointer starts and is then let go (no yellow ring). An event handed to `Input.parse_input_event` is in the WINDOW's
    pixels: multiply by `get_final_transform()` (the first version clicked 20 times too far out). Test: `tests/padcur.tscn`.
    The stick itself cannot be tested without a controller: ASK THE OWNER TO TRY IT.

### 2026-11-14 (web v194; Sandbox and menus only, no online change): the portal crash on phones; the tunnel seen from outside; the controller's cursor
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| On the owner's phone: "when going through the portals it send me back to the menu screen and never loads" | The cover over the load (`#sbDuct`) had five streak layers, each a box 1.8 screens across with `will-change`. The browser keeps every such layer as a picture of its own: on a phone about 100 MB each. The page ran out of memory, was thrown out and loaded again from the start (the menu). A PC never noticed | A layer is 256 px across and its transform alone makes it big (`sbDuctKf` writes the scale for the screen); the cover is `display:none` whenever it is not showing | NEVER size an animated layer by the screen: size it small and scale it. The desktop WebKit test (`sbphone.py`) does not have a phone's memory limit and passed with the fault in |
| "some of the space effect is not just in the tunnels but also behind them" | The tunnel's walls are drawn from their inner side; from outside that means the far wall shows through the near one, above a pizza's low crust | The tunnel's inside (`g.inside`) is shown only to a camera that has reached the mouth (`sbWarpTick`) | Look at an arch from the side: `sbprobe.py basil` with the kart 230 from a gate at an angle |
- THE CONTROLLER'S CURSOR (tools/mini/patch29.py; the owner: "instead of the yellow boxes on controller it should just be an on screen cursor ...
  controlled with the left stick ... scrolling a right stick function as well"): in every menu the left stick (and D-pad) moves an arrow,
  A presses what is under it, B is Back; the right stick scrolls what is under the arrow, and so does holding the arrow against the top or
  bottom (or side) of anything that scrolls. What is under the arrow lights up; nothing is ringed in yellow (`padNav` does nothing now). A new
  screen puts the arrow on its main button. Test: `py.cmd tools/neon/padtest.py` (a pretend controller): CONTROLLER CURSOR TEST passed.
  NOT ON THE PC YET (OPEN WORK).

### 2026-11-14 (web v193; Sandbox only, nothing a race reads; no online change): the whole game is one Sandbox world; warp tunnels; map; Park
What the owner asked (word for word in NEXT-MODES-BRIEF.md): Sandbox "between the rest of the maps in the game"; "i dont want the car to dissappear
i want to drive on a track where it looks like im going through a tunnel with this sort of design" (a warp star field); "a map with fast travel
in the pause menu and on controller make the y button open the map"; "signs above the tunnels"; "some maps you cant go backwards on the tracks";
"hold down both brake buttons ... completely stop the car and ... a park button on screen"; "going around the loops is a little glitchy".
- EVERY TRACK IS A PLACE (`sbRegOf`, `SB_AREA`, `SB_LINKS` in tools/mini/sandbox.js; engine hooks tools/mini/patch27.py). Three kinds:
  `toy` the house's four (as before); `open` the fifteen pizza tracks: drive anywhere on the pizza, ground = `groundAt` plus the track's own
  height, walls read from what is drawn (anything lying within 2.4 of the ground is ground), the crust is the edge, arches in the crust are the
  passages; `road` Sauce Spiral and the four Neon tracks: the road hangs in the air, so you keep to it (the race's own walls, either way round)
  and the passages are arches over the left-hand lane. `SBX` is on in all three; `SBF` ("free") only in the first two, and BATTLE is on exactly
  when SBF is. The garage's open door leads to Margherita Ring.
- WARP TUNNELS (`sbWarpMat`, `sbCover`, `sbPull`): a passage's mouth and its inside are drawn by one small shader (no picture files). The kart
  drives the tunnel for real. While the next place is built (the game stops for a second or more) the picture is held by `#sbDuct`: the last
  frame, CSS-animated streaks (the browser moves them while the game cannot) and the kart cut out of its own picture (drawn alone on black and
  on white). A kart beyond the wall it has driven through is still drawn: its depth is pulled toward the camera (`polygonOffsetUnits`).
- SIGNS: a board above every mouth with the name of where it leads; a gantry across the garage door.
- THE MAP (`sbMap`, `SB_WORLD`, `SB_SPOT`, `SB_LAND`): Y or Select on a controller, M on a keyboard, Map under Resume in the pause menu.
  A chequered pin at every start line is a fast-travel point (pick, confirm, warp). `togglePause` closes the map first if it is open.
- BACKWARDS: in Sandbox a jump ramp can be climbed from behind (a short slope up its back; no launch off its low end) and a full loop entered
  from its far end is ridden the other way round (`k.loop.rev`). Neither exists in a race (all behind `SBX`).
- STOP AND PARK (`sbStop`, `sbPark`): both on-screen brake buttons held, or the Park button (K on a keyboard, D-pad down on a controller):
  no throttle, no brake, speed taken to nothing. The throttle on a controller lets Park off.
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| "going around the loops is a little glitchy in sandbox mode" | `sbCam` (the camera's pull-in when something solid stands between it and the kart) ran inside a loop: the hoop itself was in the way, so it moved and levelled the camera every frame against the loop's own camera | `sbCam` does nothing while `camT.loop` or `camT.rth>0` | Per-frame log in the v193 commit message: camF stays 1 through a loop |
| On a pizza the kart never came down after the glide ramp (first test of Margherita Ring) | Two things. A drawn lip at the ramp's end counted as ground 1.4 above the kart as it took off, so it "landed" at once; and in the air the lap point stood still, so the glide never knew where it was | On a pizza the road is the ground at any height (`sbLvl`); a kart in the air on a pizza goes by the race's nearest lap point (`sbIdx(k,was,near)`) | `py.cmd tools/neon/sbworld.py`: lap `reached` > .98 on every place |
| Backwards on a toy track: stopped at every jump ramp and at every loop | The ramp is a solid wedge with a 6-high back; a loop could only be entered from its near end | See BACKWARDS above | `sbworld.py`: `back` is an empty list for every place |
| A pizza track's full loop could not be entered in free driving (Basil Boulevard, Pineapple Lagoon, Burn stopped the lap test) | The low rails and lips of the loop's two lanes were read as walls from what is drawn | Round a full loop anything lower than 7.5 above its foot is left out (`SB.loops` in `sbSurf`); the toy loop's hoop carries `colMin` for the same reason | `sbworld.py`: lap `reached` > .98 |
| Backwards over a glide canyon: the kart fell in and was set back on the near side facing forwards, for ever | `respawn` always faces the lap's way | In Sandbox a kart that was heading back along the track is set down facing back (it has then crossed) | `sbworld.py`: `back` empty |
- Pizza places, the edges of what can be driven (`sbBlocked`): a face of the pizza's own ground that rises more than a step from where the kart
  stands is a cliff (some tracks' land climbs 180 beside the road), and ground more than 3 under the water is a shore. An arch in the crust is
  only put where a kart can drive in a straight line from the road to it (`ray` in `sbGates`); a hidden coin likewise. `console.warn('sandbox:
  no clear way to an arch', ...)` means a place has an arch nobody can reach: look at it.
- Cost: reading a pizza's walls takes 0.5 to 0.8 s at Fast and about 2.2 s at Ultra on this PC (1.2 million triangles); it happens under the
  warp cover. A place's grid is about 12 MB while you are in it.
- ON LINE GRAND PRIX. What broke (the owner): "grand prix wasnt working online after one race it was saying race again or change driver but no to
  the next race option". Why: the online results screen never looked at the cup (it hid the cup table and always wrote "Race again" /
  "Change track or driver"; the host's button did go on, unsaid); and the cup's points were added once, when the HOST finished, so a friend
  who finished later scored nothing, and two friends driving the same racer shared one line of the cup. Fix (tools/mini/patch28.py): the cup is
  scored from the results table itself (`netGpNow`) and shown on every screen; the points are added when the host goes on; the host's button
  says "Next race"; a player's points are kept under the player (`gp.np`). Keep it fixed: `py.cmd tools/neon/gpnet2.py` (new: host and friend
  in two windows through the real matchmaking) must end ONLINE GRAND PRIX TEST passed. The PC still lacks all of this (OPEN WORK 1).
- STAND-IN FURNITURE. What broke: a toy room raced with plain blocks for furniture (the kitchen's table and chairs solid; a coin under the table
  could not be reached). Why: the room was already on screen as the menu's picture, built before its Blender models had downloaded; the loading
  screen only waited for them, and only rebuilt, when the track had to change. Fix: `LATE_BUILD` (patch28): a room built early is built again
  by goRace once the models are in. Keep it fixed: `sbtest.py kitchen`: every coin on the floor can be driven to.
- Signs (the owner: "some of the signs for the locations are covered make sure they are more visible"): the board stands on two posts 17 above
  the arch and 5 in front of it, a quarter wider, its face unshaded. The map zooms (`SBM.zoom`, `sbMapView`): picking a pin looks closely at
  that place: its lap, the blue arrow where you are, a purple ring and a label ("TUNNEL TO KITCHEN") at each tunnel. A track's tunnels are
  remembered once you have been there (`crust-sb`.g); the house's are always known. "Where am I?" zooms to your own place.
- LOOPS AND PADS ONLY ON THE TRACK. What broke: far out on Basil Boulevard's pizza the kart was suddenly inside the loop, 1600 away. Why: a kart off
  the track keeps the last lap point it was on (`sbIdx`), and a loop took any kart whose lap point was a few before the loop's (in a race that means
  "about to reach it"). Fix: in free driving a loop (either way round) and a boost pad act only on a kart that is at them (place, lane and height;
  patch27); in the air the race's nearest lap point is only taken when it is within 170. Keep it fixed: `sbtest.py basil` (the passage to Midnight
  Mozzarella after a round trip to Margherita Ring).
- An arch keeps its place between visits: `sbGates` first tries where it stood last time (`crust-sb`.g) and only searches again if that way is blocked.
- Tests: `py.cmd tools/neon/sbworld.py [quality] [maps]` (new: fast-travels to every place and checks lap, backwards lap, arches and hidden
  coins reachable); `sbtest.py <map>` now knows the three kinds; `sbprobe.py <map> <file.js>` runs any JavaScript in a Sandbox session and
  takes pictures (the way every picture for this version was made).
- NOT DONE HERE, and why: nothing new was modelled round the pizza tracks; the map shows the wider world as a diagram, not to scale (the
  house is to scale). The passage graph (`SB_LINKS`) was changed so it lies flat on the map.

### 2026-11-14 (web v192, PC to match, online version 110): racing fixes from the owner's play-test of the toy cup
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| "every race is ending slightly before the actual finish line" | A kart was finished when its count of lap points reached laps x N. Loops, shortcuts and glides each leave that count a few points ahead of the kart (measured 35 units early on the toy tracks, up to 180 on Laser Slice Skyway), and with no drift it tripped half a point before the line | `finAt(k)` (web), `_fin_at(k)` (PC race.gd): on the last lap, past lap point 0 and at or beyond the line itself. The count is also set right at every line crossing (stepKart; kart.gd) | `py.cmd tools/neon/finishtest.py <maps>`: every kart 0 to 3 units past the line |
| Kitchen Chaos: "something invisible on the track ... stopping me" on the blue climb | The jump ramp on the bridge overhead: the ramp rule went by place, never by level | A ramp more than its rise + 26 from the kart's height is skipped (stepKart; kart.gd) | `py.cmd tools/neon/kblock.py kitchen .70 .985`: stops [] |
| Kitchen Chaos: the track ran through the worktop's front edge | The last U-turn climbed all the way round and crossed the edge 33 below the worktop's top | `tools/mini/t_kitchen.py`: the climb ends at 262, the first 95 degrees of the turn reach 314, the rest is level | Look at it: `shots.py kitchen ...` (the view is in this entry's commit message) |
| Kitchen Chaos: "the books also slightly run into the track" | 17 cm between the track and the wall, a stack 24 cm wide | Moved east of the bend (toyKitchen) | |
| Toy shortcut lanes curved back into the track at their far end and steered the player into the wall | makePath drew every lane as an S-curve | On toy tracks a lane is one straight line (`str8` in makePath); it may run a little closer to the track (WALLD+W-2); the bedroom's lane was moved so it leaves and rejoins at about 45 degrees | `neon shortcut does not fit` in the console means a lane was rejected: the track then has NO shortcut |
- Sandbox, same version (looks only): the camera keeps to the kart's own height in a long drop (it aimed halfway to the ground and
  lost the kart); the track's height on a bend is worked out as the race does it (it stepped at every lap point: "choppy"); on the
  track's own surface nothing drawn lifts the kart; the camera looks past the track's blue posts; its look along the slope follows the
  way the kart is going. Test: `py.cmd tools/neon/sbfall.py <region>`. The garden's lawn is laid round the patio, not under it
  (the two flickered from high up).
- PC: the same ramp and finish rules are in `kart.gd` and `race.gd`, PROTO 110; the tracks, the straight lanes, the kitchen and the
  lawn come with the re-export (`release_pc.py`). `tests/smoke.tscn` passes locally with them.

### Where web and PC stand (2026-11-13, end of the session)
- Web v201 (ONLINE 112): Y is the ability in Sandbox, the map Select. Before that web v200: computer racers 0 to 7, abilities and climbable hills in Sandbox, the mechanic's shop, slower phone pointer. Until the PC build with the same is out, PC (111) and web (112) do not race together. Before that: web v199 (online 111): Sandbox's clock, things to do, Easter eggs and Back to the track, and the no-stop tunnel on the web too (web only: the PC has had its own since build 68030144). PC build 68030144 = web v197's tracks (online 111): PC and web race together and have the same modes (Grand Prix, single, Reverse, Last Slice, Balloon Battle 5-3-1, Sandbox). Web v198's only addition, Settings > Kart stats, is in that PC build too. Before that: web v198. Before that: web v196 (online 110). PC build 68030144 has web v196's tracks, Balloon Battle, Sandbox, online Grand Prix and the controller's cursor (online 110): PC and web race together, and the PC has every mode the web has. What the web has and the PC has not is listed in OPEN WORK. v187 (phone fix), v188
  (Sandbox, first slice) and v189 (the second site's plumbing, switched off) are web only; nothing that moves a kart in a race changed.
- Web only so far: Balloon Battle (v182 to v185). Its PC port is the next PC job, after the owner has played it on the web
  (docs/BALLOON-BATTLE-PLAN.md). Sandbox: the first slice (the back garden) is on the web (v188); docs/SANDBOX-PLAN.md.
- OWED TO THE PC (the owner, 2026-11-13: "make sure to commit these changes to the pc version as well"): Balloon Battle
  (mode, arena, rules as of web v191, the one-line scoreboard) and Sandbox (everything in docs/SANDBOX-PLAN.md that the web has).
  Neither exists in the Godot project yet. Port Balloon Battle first (its rules are settled), then Sandbox: the web's reaches every track as of v193, so it can
  be ported once. What moves a kart in Sandbox and must be mirrored exactly: `sbG`, `sbBlocked`, `sbWalls`, `sbIdx`, the ramp-from-behind
  and loop-the-other-way rules and `sbStop` (all in tools/mini/sandbox.js and tools/mini/patch22..27.py). Sandbox is off line, so the
  online version does not move for it.
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
5. PC: `tests/smoke.tscn` (AI race; `tmp_neon`/`tmp_cam` no longer exist), the test of whatever changed (battle, sandbox, cpus,
   gpnet; online changes: xplay and xmodes cross-play with the browser), then `tools/release_pc.py` (export from CI, build, push).

### 2026-11-12 (move to the Windows PC)
| What broke | Why | Fix | Keep it fixed |
|---|---|---|---|
| Risk: a build on Windows would change every published file | Git for Windows converts line endings on checkout (`core.autocrlf=true`), and the build hashes file contents | `core.autocrlf false` in the repo, files checked out again, `.gitattributes` with `* -text` on `source`; a fresh build then differs from `main` only in the version stamp | After cloning anywhere new, set this before the first build and check `git status` in `app` after building |
| Risk: `inject_mini.py` and the patch scripts would rewrite the whole source with Windows line endings | They opened the source in text mode; on Windows Python turns every line ending into CRLF on write | `inject_mini.py` and `patch4.py` open files with `newline=''` | Any script that writes `crust-rush.html` or the files in `tools/mini` must pass `newline=''`; check `git diff --stat` shows only the lines you meant to change |
| Scripts could not run on Windows | Cloud-workspace paths, a bash build script, the software renderer flag | `tools\port_paths.py` rewrote the paths to `D:\crust-rush`, `webtest.py` replaces `webtest.sh`, `py.cmd` sets UTF-8 and the browser path | Run scripts through `py.cmd`; plain `python` reads files as cp1252 and can corrupt the source |
