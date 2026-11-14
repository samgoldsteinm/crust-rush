# Sandbox / Free Roam: working plan

The owner's brief is in `docs/NEXT-MODES-BRIEF.md`, word for word (nine numbered sections and a closing summary to write
when it is finished). This file is the plan made from it, what was found in the code, and the state of the work.

## The roster (inspected 2026-11-13: `MAPS` in crust-rush.html; R is each track's world radius in game units; a kart is 12 long)
| # | Track | Theme | R | Cup |
|---|---|---|---|---|
| 0 4 8 12 | Margherita Ring, Basil Boulevard, Oven Rush Raceway, Sauce Spiral | kitchen | 1700-1900 | one in each of the first four cups |
| 1 5 9 13 | Hawaiian Bay, Pineapple Lagoon, Calzone Coast, Topping Tour | bay | 1850-1950 | |
| 2 6 10 14 | Pepperoni Peaks, Midnight Mozzarella, Neon Napoli, Pepper Moon Circuit | night | 1750-1900 | |
| 3 7 11 15 | Frosty Freezer, Freezer Burn Pass, Glacier Crust, Frozen Pie Peak | freezer | 1750-1950 | |
| 16-19 | Neon Grid Arena, Laser Slice Skyway, Hologram Heights, Synthwave Supreme | neon (night) | 2660-2850 | Neon Cup |
| 20-23 | Bedroom Blitz, Kitchen Chaos, Garage Overdrive, Backyard Mega Circuit | toy rooms | 1160 (4700 the garden) | Miniature Mayhem Cup |
| 24 | Prep Table Showdown | battle arena | | (Balloon Battle only: not part of the world) |

Two scales live in that list. Tracks 0-19 are a kart-sized country: roads, hills, water, towns. Tracks 20-23 are one real
house and its garden, where the kart is a 7.5 cm toy car (347 units to the metre). The brief asks for believable
proportions in the toy places, so the house is NOT shrunk or stretched to sit beside the others: the two are joined by a
way through that changes scale believably (below).

## The world, sketched (regions and what joins them; names are the tracks' own)
```
                        THE FREEZER RANGE                           north: cold, high
        Frozen Pie Peak --- Glacier Crust --- Freezer Burn Pass --- Frosty Freezer
              |  (pass road, snow line)                                   |  (cold-store road down)
   THE NEON DISTRICT            THE OLD TOWN (night tracks)          THE KITCHEN COUNTRY
   Synthwave Supreme            Pepper Moon Circuit                  Oven Rush Raceway -- Sauce Spiral
   Hologram Heights  --power--  Neon Napoli -- Midnight Mozzarella --  Basil Boulevard -- Margherita Ring
   Laser Slice Skyway  station  Pepperoni Peaks                           |  (the delivery road)
   Neon Grid Arena                   |  (harbour road)                    |
                                THE BAY                               HOME (toy scale)
                Topping Tour -- Calzone Coast -- Pineapple Lagoon     front street - Garage Overdrive
                                Hawaiian Bay --(coast road)-----------  Bedroom Blitz - hall - Kitchen Chaos
                                                                       Backyard Mega Circuit
```
- Neighbours are chosen by terrain and look: the freezer tracks are the high north, the bay tracks the southern shore, the
  kitchen-themed tracks the farmland between (Margherita Ring is the first track of the game: it is the middle of the
  map and the first fast-travel point), the night tracks an old town whose lights come on at dusk, the neon tracks a
  district beyond a power station where lit strips appear in the road before the first neon track comes into view (the
  brief's own example).
- HOME joins the rest at its front street. The scale changes inside something that is really there: the delivery
  scooter's box / a storm drain under the kerb / the model village in the garage (to be chosen with the owner: it decides
  what the first minute of Sandbox feels like). Inside the house everything is already one place: the three rooms, the
  garden and now the front of the house (web v179-v181) were built to one plan.
- Every region gets an approach you can see from a distance, a loop road, at least one fork and one shortcut, and places
  off the road: yards, side streets, overlooks.

## What the engine does today, and what Sandbox needs (found by reading the web source)
- One track at a time. `loadMap` throws the world away and builds the next (2 to 10 s). Every builder (terrain, roads,
  scenery, the neon and toy rooms) assumes its track is at the origin and uses globals (`track`, `N`, `RIM`, `HILLS`...).
  Two tracks cannot stand in the world together as the code is.
- Driving is fenced by the track's centre line (`stepKart`): walls, kerbs, off-road slowing, the CPU drivers, respawns,
  the minimap, most items. Balloon Battle (web v182) added the other way: `BATTLE` switches those off and the ground and
  walls come from a list of shapes (`battleG`, `battleWalls` in tools/mini/battle.js): "what you can see is what stops
  you". Sandbox driving is that, grown: the shapes come from the world's own pieces, region by region.
- No coins or shop exist. There are achievements (`ACH`, saved as `crust-ach`) that unlock liveries and items, a garage
  with builds, `store` (the browser's storage), controller support (`PAD`), friends' races over WebRTC with a relay.
- So the choice that shapes everything (the brief asks for one streamed world; the engine is one track at a time):
  A. REGIONS JOINED BY REAL PASSAGES. Each region is one loaded world: a track kept exactly as it is, with its
     surroundings opened up and new roads, yards and secrets added, and gateways (a tunnel, a covered bridge, a gate house)
     on its edges. Driving into a gateway loads the neighbour while you are inside it. The world map, fast travel, the
     shared clock, coins, challenges and unlocks all work across regions. This can be built on the engine as it is.
  B. ONE STREAMED WORLD with no passages: needs the builders rewritten so pieces of several tracks can be built at any
     place and unloaded again, and the far landmarks drawn as stand-ins. Months, and it touches every track's code (and the
     PC's copy of it).
  Plan: build A first, in a way that B can replace region by region (region data is kept apart from region loading), and
  make HOME the first region because it is already one place and needs no gateway inside it.

  DECIDED BY THE OWNER, 2026-11-13: A. In their words: "I am happy with passage joined regions just try your best to make
  it unnoticeable that it's happening that way to the user. It should be a smooth transition of driving without
  interruption while the world loads. It actually works out this way because it will help fix the issue of the world at toy
  scale. Since you have to go through a tunnel or gate the world can load and the player won't notice the scale changing
  in real time".
  What that asks of a gateway (the bar for milestone 3; the scale gateway of milestone 4 is the same thing, no separate
  choice is needed any more):
  - The kart never stops, never loses control and never sees a loading screen: you drive in one end and out the other.
  - The passage is its own small world that stays loaded: long enough, at the top speed of the fastest class, to cover the
    slowest phone's load of the next region (measure it; make the passage bend so neither end can be seen from the other).
  - The neighbour is built in slices across frames while you drive (today loadMap builds a world in one blocking call: that
    is the work), the old region is thrown away only once it is out of sight, and nothing may hitch a frame.
  - If the load is not finished when you reach the far end, the passage must have more of itself to give (a longer bend, a
    spiral, a door that is still rising): never a wall, never a wait screen.
  - Scale: toy regions are entered through passages too, and the change of scale happens inside, where there is nothing
    of known size to compare against; the far mouth opens onto the new scale.
  - Friends' races: both players' passages must agree on where a kart is, so the passage is part of the track data.

## Milestones (each is a release the owner can drive)
1. FREE DRIVING AT HOME. Sandbox in the menu. The house as one region at toy scale: the three rooms joined by the hall
   and their doors, the back door to the garden, the garage's open door to the front street. The tracks stay as raced
   (their rails are the "natural access points": gaps with ramps on and off, used only in Sandbox). Collision from the
   real furniture and walls. No CPU drivers. Coins along driving lines; the first hidden coins; saved.
2. THE MAP AND FAST TRAVEL. Select (View/Back/Minus) opens it; on a phone, Map directly under Resume; labels, the
   tracks' outlines, you-are-here with heading; fast-travel points apart from plain labels; confirm; controller throughout.
3. THE CLOCK. One day/night cycle for the whole world; lamps, windows and neon come on; checked at driving speed.
4. THE FIRST COUNTRY REGION AND THE WAY THERE: Margherita Ring with its surroundings opened, the delivery road, the
   gateway between scales. Then region by region outward (kitchen country, bay, old town, freezer range, neon district).
5. THINGS TO DO: the pizza delivery between two regions (safe road, risky shortcut), a drift or jump challenge, Easter
   eggs per map; objective and reward shown, quick retry, discoveries saved.
6. COIN UNLOCKS: new karts (a low delivery kart, a retro open-wheeler, a chunky utility kart: modelled in Blender to the
   best existing karts' standard), two of the recently added cars as an early and a late prize (waiting on the owner's
   answer about those six cars: see docs/HANDOVER.md, web v173), preview, price, balance, buy, equip; owners keep theirs.
7. SPEED: frame times measured on the highest preset and on a phone; memory after revisits.
8. ONLINE FREE ROAM: friends in the same region see each other; the clock is shared; coins and unlocks stay each
   player's own; two real sessions tested. 9. THE WHOLE CHECK in the brief's section 9, and its closing summary.
PC: every milestone is ported after the web's has been driven by the owner (as agreed for Balloon Battle).

## State
- 2026-11-13: roster inspected, world sketched, engine findings written, milestones set. Nothing built yet.
  Waiting on nothing to start milestone 1.
- 2026-11-13 (later): the owner chose passage-joined regions, with seamless driving through the passages (see the decision
  above). The scale gateway needs no separate answer: it is a passage.
- 2026-11-13 (web v188): THE FIRST SLICE IS IN THE GAME. Sandbox is the fifth mode in the menu; its world for now is the
  back garden. See "How Sandbox works" below.

## How Sandbox works (web v188; read before touching it)
- Files: `tools/mini/sandbox.js` (all of it), `tools/mini/patch22.py` (the engine's hooks and what each is for),
  `tools/neon/sbtest.py` (the test), `battle.js` (hands each call over when `SBX` is set).
- A REGION IS A TRACK'S OWN WORLD, loaded exactly as for a race (same memory, same pictures; the race is untouched).
  Sandbox changes only what is under the one kart: `sbG(x,z,height)` is the ground and `sbWalls` the walls, in place of the
  lap's. The ground is the floor, the track as a ribbon with its real heights (a grid of lap points, `sbHashTrack`; it
  crosses over itself, so the level is chosen by the kart's own height), and EVERYTHING THAT IS DRAWN (since v191:
  `sbColumns`, see below; v188 listed the garden's things by hand). One rule makes every wall: nothing
  climbs a step higher than `SB_STEP`, and what is overhead is not in the way. The track's raised edge is a 4-unit bump:
  you drive on and off the track anywhere it lies on the ground (the brief's "natural access points"; no rail of a race
  is changed), and where it is high you fall off its side. The track's posts are solid (`TOYPOSTS`).
- `SBX` is on only between `startRace` (mode 'sb', off line, a region exists for the track) and `toMenu`/the next
  `loadMap`. `BATTLE` is on with it, so Balloon Battle's hooks carry it. One kart; no clock, lap, finish, ghost, rivals.
- Coins: gold ones in trails (a run of six every 3 m of track; lines and rings on open ground), back 40 s after being
  taken; pepperoni coins (10 each, six in the garden, one of them in the air off the high track) are found once and saved.
  The save is one record, `crust-sb` = {c: coins, r: {region:name: 1}}. No shop yet: prices come after the owner has played
  (the brief: "Set prices after checking how quickly coins accumulate in normal play").
- The camera stops short of solid things (`sbCam`); the kart's body and the camera read Sandbox's ground, not a lap point.
- To add a region: an entry in `SB_REG` (name, shapes in the room's own measure, coin lines, rare coins), and cases in
  `sbtest.py`. The garden's list is in garden metres, the same numbers as `toyYard` and `clearcheck.py backyard`.

## HOME is four regions joined by its doors (changed 2026-11-13, by me, for the phone)
The first plan made the whole house one region. Each room alone loads 150 to 300 MB of pictures on a phone (the reason
`freeCanvases` exists), so four at once would get the tab killed on the owner's iPhone. With the owner's choice of
passages, each room is a region and its doors are the passages: the back door (garden to kitchen), the hall (kitchen,
bedroom, garage), the garage's open door (to the front street). Milestone 1 becomes:
  1a. the back garden (done, v188)   1b. the other three rooms' things and coins (done, v191)   1c. the passages (done, v191, first form: see "Passages")
  (loadMap split into slices that run while you drive through; the bar is in "DECIDED BY THE OWNER" above).
Next after 1b/1c: the map (milestone 2), which needs at least two regions to be worth opening.

## Collision from what is drawn (web v191)
- `sbColumns(bounds)` runs once when Sandbox starts in a region. It goes through every triangle of the loaded world and
  keeps, for each square of floor (5 units in a room, 6 in the garden), up to six upright stretches that are solid there,
  each a top and an underside. `sbSurf` hands those to the same step rule as before. So a wall stops you, a table's legs
  stop you and its top does not, you can drive under the bed, and none of it is listed anywhere. A new room or a new
  prop needs nothing done.
- Left out on purpose (the reasons are in the comment above `SB_SOFT`): what is hidden; what is see-through or cut out
  (glass, nets, leaves, grass, cloth); the track's own surface, edges, undersides and jump ramps (the lap and the engine
  give those exactly); unnamed instanced things (the item boxes); anything flatter than 1.2 units; anything more than 70
  units above the track's highest point (ceilings: they filled a square's six places and made false walls).
- The room's own edge is `TOYROOM` (set by toyShell, toyBedroom, toyYard): past it is a wall, which is what closes an
  open door until it is a passage.
- THE LAP IS ALWAYS OPEN (`sbBlocked`): on the track's own surface at the kart's own level nothing drawn is in the way.
  The pictures are not exact where the track meets furniture: the kitchen's climb runs through the worktop's front edge,
  the bedroom's start line has a plate and a banner beam. In a race none of that matters; here the track wins.
- Cost, measured at Ultra on the PC: 0.2 to 0.5 s and 2.3 MB for a room, 0.2 s and 14.5 MB for the garden (it is
  fifteen times a room's floor). It happens once, as Sandbox starts. For passages it will have to be done in slices.
- The test draws what Sandbox understands: `py.cmd tools/neon/sbtest.py <region>` writes `scratch/sb_plan_<region>.png`
  (white floor, grey drive-up, black wall, blue drive-under, green track, coins). Coins were placed from those plans. The
  test also floods the floor from the track and fails if a coin lies where the kart cannot drive, drives the whole lap,
  and (garden) the walls. It found the three faults fixed in v191: gaps in the track lookup where lap points are 8
  apart, the false wall at the bedroom's start line, the worktop across the kitchen's climb.
- You choose where to start: in Sandbox the menu's track list shows the four places
  (`sbMenu`). Coins: gold trails on every track and on open floor; five or six pepperoni coins a room, under the bed,
  the desk, the table, the bench, in corners, and one hanging off the highest bend where a room has one.

## Passages (web v191, first form)
- A gate is an arched opening low in a wall with the next place's name on a plate above it (`SB_REG[..].gates`: wall,
  place along it, where it leads, which gate you come out of; drawn and made passable by `sbGates`). Today:
  garden (house wall, beside the back door) <-> kitchen (east wall, north) ; kitchen (east wall, south) <-> bedroom (west
  wall) ; bedroom (east wall) <-> garage (west wall). The garage's open door is kept for the way out to the street.
- Driving in: past the wall is a straight dark duct. As the kart goes in, the picture gives way to the duct (dark, ribs
  rushing past); the next room is built; the kart comes out of the matching gate at the speed it went in with, the
  room's name shown once. No loading screen, nothing to press. Measured on the PC at Ultra: 3 to 7 s from pointing at
  the gate to driving in the next room.
- HOW THE WAIT IS HIDDEN, AND ITS LIMIT. Building a room is still one long step (`loadMap`), during which the page
  cannot draw. The ribs are a page animation of transform and opacity only, which the browser's compositor keeps moving
  by itself, and the engine's sound keeps running, so the duct does not freeze. What does stop for that step is
  steering: the duct is straight, so there is nothing to steer. On a phone the step is several seconds on a room's
  first visit. The owner's bar is "without interruption": this meets it to the eye; the real cure, cutting `loadMap`
  into slices that run while the kart still drives in 3D, is the next work on passages (and is what the bigger world
  needs anyway). Check on the owner's phone how long the duct lasts.
- Placing a gate: `wallscan.py` (tools/neon/wallscan.py <region>) prints, per
  wall, the stretches with clear floor in front. A gate needs about 200 units clear so the kart does not come out into
  something. The engine's round outer limit (`RIM`) is off in Sandbox: a room's corners and the ducts lie outside it.
- The scale gateway (house to the street, toy to full size) will be this same thing with a longer duct: the owner's
  point, "the player won't notice the scale changing".

## A race from the start line (web v191), and the owner's online half of it (not built)
The owner, 2026-11-13 (word for word in docs/NEXT-MODES-BRIEF.md): drive up to a track's start line to start a race there;
start lines carry "little visible markers"; on line, up to 4 players at the start line join the same race through a
lobby with ready-up, the host starting it, on "a screen similar to the online screen we have now".
- Built (off line): `sbFlag` puts a chequered ring on the road and a small turning chequered flag at the region's start
  line. Within 46 units a button offers "Race here: <track>" (tap; Enter; D-pad up). It starts an ordinary single race on
  that track at the chosen speed class. Leaving the race or its results (`toMenu` asks `sbBack`) returns to Sandbox in the
  same place; the results screen's second button reads "Back to Sandbox". Tested by `sbtest.py` in every region.
- To build with friends in Sandbox (milestone 8), in this order:
  1. Friends share a region: each kart's place sent as in a race (the relay and WebRTC are there: `NET`), no host
     authority over free driving; coins and unlocks stay each player's own.
  2. The start line as a meeting point: a player who stops at the marker opens a lobby for that track; others in the
     region see "<name> is at the start line of <track>: join" and, driving to the marker, join it. Four at most.
  3. The lobby screen: the existing friends' lobby (`netShowLobby`) with a Ready button per player; the one who opened
     it is the host and can start only when everyone in it is ready. Leaving the marker's circle leaves the lobby.
  4. The race is the existing friends' race (host prepares, `netHostPrepare`); afterwards everyone is back in Sandbox
     at the start line. Online version to be bumped on web and PC together when the messages are added.

## The whole game as one world (web v193)
- Every track is a place: `sbRegOf(id)`. Kinds `toy` (the house), `open` (the fifteen pizza tracks, free driving on the pizza), `road` (Sauce
  Spiral and the Neon tracks: keep to the road). `SB_AREA` names each place's country; `SB_LINKS` says which places its passages lead to.
- Passages are warp tunnels (the owner's picture: streaks flying out of the middle of a black screen): `sbWarpMat` draws the mouth and the
  inside; `sbCover` holds the picture during the load with the kart on top; `sbPull` keeps the kart drawn beyond the wall. A sign above every
  mouth. On `road` places the mouth is an arch over the left-hand lane, placed on a clear straight (never on a bend, jump, loop or glide).
- The map (`sbMap`): the house to scale, the twenty tracks as round places in their five countries with a line for every passage; a chequered
  pin at each start line is a fast-travel point. Y / Select, M, or Map under Resume.
- Backwards: ramps from behind and loops the other way round, in Sandbox only. Stop: both brake buttons, or Park.
- Still to build from the brief: the clock, activities, the shop, online free roam, the start-line lobby; new land round the pizza tracks.
