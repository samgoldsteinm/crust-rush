# Balloon Battle: working plan

The owner's brief is in `docs/NEXT-MODES-BRIEF.md` (word for word). This file is the plan made from it and the state of
the work. Update it as things are built.

## What the brief asks for
- A mode called Balloon Battle: balloons tied to each kart, free driving in a compact arena, item boxes, pop rivals'
  balloons, protect your own; balloons show at a glance who is nearly out.
- Two rule sets were described: last kart standing (the classic), and a timed score battle (start with five balloons, a
  point per balloon popped, at none you come back with three and your score is halved, most points when time is up wins).
- A NEW map made only for this mode: a pizzeria prep table. An open middle; a pizza box with its lid propped open as a ramp
  onto a raised route; ingredient bins along the edge with gaps between them (cover, and ways to cut across and intercept).

## Decisions (mine, where the brief left a choice; change them if the owner says otherwise)
- Rules: the timed score battle is the default (three minutes; nobody sits out). Last kart standing can be a second
  setting later: the engine already has an elimination mode (`mode==='lss'`) to model it on.
- Items are the game's own (ITEM_KEYS). The brief's examples name another game's items; ours stay ours.
- Web first, off line against the CPU. Then the PC port, then friends' races. The mode adds its own physics branch, so
  NOTHING in a normal race changes and the online version does not move until battle itself goes on line.

## How the engine has to change (found by reading the web source, 2026-11-13)
- A kart is a free point (x, y, heading `a`, travel angle `ma`, speed) in `stepKart`. Everything that fences it in is
  measured from the track's centre line: off-road slowing (`lateral`), the side walls (`WALLD`), kerbs, pads, ramps,
  loops, the outer ring (`RIM`). The CPU drivers (`aiInput`), respawning, the minimap, standings (`prog`) and most
  projectiles (`railSync`, `homeStep`, `pepWall`: they ride the track by progress and lateral offset) do the same.
- So battle needs, behind one switch (`BATTLE`):
  1. An arena described as a height field: flat floor, boxes and round things with a height, ramps. One rule gives every
     wall: a kart cannot climb a step higher than a few units (it slides along it); it can drop off an edge and falls.
     The table's own raised lip is the outer wall. Collision then matches what is drawn, because both come from the
     same list of shapes.
  2. `stepKart`: in battle, no track walls, kerbs, off-road slowing, pads, loops or track ramps; ground height and
     blocking from the arena.
  3. Projectiles: fly straight, bounce off or break on arena walls; a homing one steers straight at its target.
     Dropped things stay where they are put (already positional).
  4. A hit: `spinOut` is where every hit lands, and `CURP` says whose it was. There: the victim loses a balloon, the
     attacker scores.
  5. CPU drivers: go for item boxes, chase the nearest rival they can reach, fire when lined up, steer round walls
     (three feelers against the height field), do not drive off the raised route by accident.
  6. Balloons on each kart (drawn, and popping), a score list and clock in the HUD, results by score.
  7. Menu: the mode, with its one arena; the arena never appears in the race track list or the cups.
- A small ring of track points is still made in the middle of the arena so the code that expects a track has one; the
  switch keeps it from fencing anybody in.

## The arena: the prep table (design units; a kart is about 12 long, top speed about 170 a second)
- A stainless table top, about 760 x 520. A raised lip all round (the outer wall).
- The open middle: nothing in it but a dusting of flour and four item boxes.
- North edge: a row of five steel ingredient bins with kart-wide gaps between them, and a lane behind them along the
  lip. Chase somebody into a gap and they can be met at the next one.
- South-west: a pizza box, lid propped open: the lid is the ramp up onto the raised route.
- The raised route: stacked pizza boxes and a cutting board along the south and east edges, one storey up, with a
  second way down (a bread board leaning on it) at the far end, and open edges you can drop off to pounce.
- Dressing (no collision unless it is one of the shapes above): dough balls, a rolling pin (a low wall), a sauce ladle,
  a pepper mill (a round pillar), a stack of plates, cheese and basil.
- Built in Blender where it shows (bins, pizza boxes, boards, pin, mill), as the owner asked; the collision shapes are
  the same boxes and cylinders the models are built to.

## Order of work
1. `BATTLE` switch, arena height field, kart physics branch, a flat test arena. Drive it.
2. Balloons, hits, score, clock, results.
3. Projectiles and each item's battle behaviour.
4. CPU drivers.
5. The real arena, modelled; menu entry; pictures; tests; publish web.
6. PC port (Godot). 7. Friends' races.

## State
- 2026-11-13: plan written.
- 2026-11-13 (in web v180, switched off): step 1 and most of 2 and 4 are written but NOT yet driven or tested:
  `tools/mini/battle.js` (arena shapes `bbArena`, `battleG`, `battleWalls`, balloons, `battleHit`, `battleTick`, `battleAI`,
  the scoreboard), `tools/mini/t_battle.py` (the ring of track points; map id `preptable`, `battle:1, special:1`),
  `toyBattle` in mini.js (placeholder blocks drawn from the shapes), `tools/mini/patch19.py` (the engine's hooks; the list is
  at the top of battle.js). The mode's button in the menu is `hidden`: to try it, in a test page run
  `mode='bb';goRace(MAPS.findIndex(m=>m.battle))`.
- Not done: step 3 (projectiles still ride the dummy ring: `pepWall`, `homeStep`, `railSync`, `trackAt` uses in `itemsProj` and
  the older item code need a battle branch; `battleProjWall` is ready for them), the real arena models, results polish,
  pictures, tests, the PC port, friends' races.
- 2026-11-13, web v182: PLAYABLE on the web, off line against seven CPU drivers. Done: the arena as a height field with the
  one-step wall rule; the prep table in a tiled alcove (walls on three sides, the open front has only the table's raised
  edge: go over it and you lose a balloon and are set back on the table); the arena's models built in Blender to the
  collision shapes (`tools/blender/battle.py`: bbtable, bbbins, bbboxes, bbblock, bbprops; `bMats` / `bPk` in models.js);
  balloons, hits, score, clock, respawn, results by points; the items' battle behaviour (patch20.py: free flight, bounce
  off walls, straight homing, levels, the freezer by distance, the pizza cutter at the leader, no drivers' specials);
  CPU drivers (targets, feelers, ramps between levels, unsticking); the menu's fourth mode and its note; the loading
  screen and results name the mode; lap read-outs, the minimap and the wrong-way sign are hidden; friends' races leave the
  mode (`bbNoNet`).
- Tests: `py.cmd tools/neon/bbtest.py 185 [shots]` runs a whole round fast and prints scores, balloons, the longest any
  kart stood still, bad numbers and karts off the table; with `shots` it photographs the menu, the round and the results.
  Last run: about 15 to 25 pops a round, nobody stuck over 4 s, no errors.
- NOT done, in this order: (1) a play-test by the owner (feel, arena size, three minutes, five balloons, how hard the CPU
  drivers are); (2) the PC port: battle.js into GDScript beside race.gd's `ai_input`, `use_item`, `spin_out`, the arena's
  shapes exported with the track (maps.yml index 24), menu and HUD; (3) friends' races (host decides hits and scores; a
  new online version); (4) last kart standing as a second rule set; (5) polish: a picture for the loading screen, the
  results' "Race again" wording, a sound for a pop, flour and sauce on the table, something on the walls (a shelf, an
  order rail), CPU drivers that use the raised route on purpose.
- 2026-11-13, web v183: driven by key presses for the first time (`py.cmd tools/neon/bbdrive.py`: steering, sliding along
  walls, picking up and using items all work by hand; the earlier tests used a self-driving player). That found: a box
  could give a track-only item (it gave "sauce", which works by race position): a battle's boxes now give only
  `BB_ITEMS` (`bbRoll`): pepperoni, the trio, dough, oil, flour, chili, garlic, the rush, and only those left switched on
  in the item settings. A corner arrow board stood on the table (`neonSigns` is off in a battle). The "of 8" read-out is
  hidden. About 28 pops a round now.

## 2026-11-13 (web v190): the scoreboard
The owner had the list of everyone's balloons removed ("way too big and in the way"). The HUD is one small line: clock, your points, your place.

## 2026-11-13 (web v191): the owner's play-test of the arena and the rules
Their words are in docs/NEXT-MODES-BRIEF.md. What changed, all in `tools/mini/battle.js` (and the models in `tools/blender/battle.py`):
- Three balloons each (it was five); you still come back with three and half your points.
- Items: only what you aim or steer yourself: pepperoni, pepperoni trio, bowling meatball, flour bomb, chili boost (the
  owner added the flour bomb and the meatball back by name the same day; the meatball is given to everyone here, unlocked or
  not). Gone from this mode: dough ball (homes), olive oil (dropped), delivery rush (drives itself), garlic shield.
  Do not add an item that homes, lies on the table or drives the kart.
- Sixteen item boxes (it was eight).
- Each ramp is as wide as the ledge it leads to (beside the narrower ones was a pocket a kart got stuck in); the fifth
  pan is gone and the peel with its handle is a plain bread board (the handle lay across the table into that pan); the
  rolling pin's handles are solid.
- Checked: a full battle run fast (38 pops, nothing stuck, nothing but those three items ever held, nothing left on the table).
- The same day, from the top of the boxes: "the camera angle is really bad and the car sort of floats on the object". The camera's
  height, the drawn ground and the car body's footing read the lap's ground (the bare table) instead of the arena's. They read
  `battleG` now (`tools/mini/patch25.py`), and `bbCam` keeps the camera out of the boxes, the block and the pans. Pictures of the
  kart on every raised part: the session's `bbtop.py` (keep the idea: place the kart on each surface and look).
