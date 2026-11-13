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
