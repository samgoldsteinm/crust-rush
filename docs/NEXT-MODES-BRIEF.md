# Next two game modes: the owner's brief, word for word (2026-11-13)

Kept here so the brief survives between sessions. These are the user's own words; nothing below is a decision of mine.
Order given: first the reminder about the rooms, then Balloon Battle, then Sandbox ("definitely a bigger project").
The standing rules in `docs/HANDOVER.md` still apply to both (web and PC agree on anything that moves a kart; nothing that
risks online play; no copyrighted names or logos; test before publishing; a new version for each major update).

## The reminder
"Remember these scenes are supposed to be hyper realism"

## Balloon Battle
"Also let's add a new game mode

How Balloon Battle works

The mode is called Balloon Battle. Each kart starts with balloons tied to its back, and drivers can go anywhere in the arena. You grab item boxes, hunt down opponents, and try to pop their balloons while protecting your own. You might chase somebody with a red shell, then drop a banana in a narrow passage when another driver gets behind you. The balloons also tell you at a glance how close a rival is to losing their last one.

Classic Mario Kart played it as last kart standing. In Mario Kart 8 Deluxe, it's a timed score battle. You start with five balloons and earn a point each time you pop a rival's balloon. Lose all of yours and you respawn with three, but your score gets cut in half. Whoever has the most points when time expires wins.

What the maps are like

Balloon Battle usually takes place in a compact, purpose-built arena. There are no laps or required direction of travel. Drivers approach each other head-on, cross paths from the side, and double back during a chase. The visual theme can vary widely. Some courses are flat and divided by colorful walls, while others look like stunt stadiums with ramps and elevated routes.

For your pizza racing game, picture a battle on a pizzeria prep table. The open middle gives you room to spot a rival and line up a shot. A pizza box with its lid propped open forms a ramp onto a raised route. Along the edge, gaps between ingredient bins give you cover and a way to cut across the table. If someone chases you around a bin, they can see where you went and take the other side to meet you at the exit. That ability to intercept someone mid-chase is what makes the layout feel like a battle arena.
It will require a new map exclusively for the game mode"

## Sandbox / Free Roam
"This is another game mode for us to work on, definitely a bigger project but it will be worth it on completion

Build a Sandbox / Free Roam mode that connects every existing track into one large, driveable world. Keep the tracks themselves the same. The new content is the world around them: the roads that lead to each track, the land beside them, and the places players have seen during races but have never been able to reach. Use Mario Kart World's free roam as inspiration, and build the locations, activities, and rewards around our game's own identity.

1. Keep the tracks intact and open up their surroundings

Inspect the actual map roster and sketch how the locations fit together before implementing the world. Preserve each track's racing surface, corners, jumps, elevation, landmarks, and race layout. In Sandbox, create natural access points so I can drive onto a familiar track, follow part of it, and leave through an opening to explore somewhere new. Keep Sandbox access points separate from the barriers and checkpoint logic used during normal races and Grand Prix.

Give each region places worth driving around off the main route. For example, if I've always been able to see a building across a fence during a race, Sandbox could let me take a service road around the block, enter its yard, and look back at the track from the other side. I want to recognize the exact corner I've raced before and get a genuinely new view of it. Build open yards, side streets, overlooks, and usable terrain where they fit the setting. A network of narrow connector roads alone won't deliver that feeling.

2. Make the geography and boundaries believable

Choose neighboring regions based on their terrain, architecture, scale, and visual themes. Give each track a recognizable approach and let players see landmarks before reaching them. The approach to the Tron-style region, for example, could pass through a power facility where illuminated strips gradually appear in the pavement before the full neon track comes into view. Preserve believable Hot Wheels proportions in any toy-scale locations. Build loops, forks, and shortcuts so players can leave a region by a different route than they entered.

Every place that stops the vehicle should have a visible, believable reason. Use an anchored fence that meets a building or retaining wall at the ends, a solid building with a clear footprint, a rocky embankment, or a raised edge with a guardrail where the drop is closed to vehicles. Match collision closely to the visible object. If a fence ends and there's a kart-width opening onto driveable ground, let me drive through it. If that area has to be closed, finish the fence or place a believable physical obstacle there. Apply the same rule to the outer edge of the world.

Check barriers from the chase camera in both directions and with the smallest kart or bike. Watch for places where the vehicle stops a few feet before a wall, catches on empty space beside a post, or hits an invisible border across terrain that looks open. A player exploring for secrets should be able to trust what they see.

3. Add a proper Sandbox world map and fast travel

* Controller: Pressing Select during Sandbox opens the world map directly while driving. Use the equivalent View/Back/Minus input through the project's existing controller mappings. Pressing Select again or using Back should return me to driving.
* Mobile: When I pause Sandbox, add a Map option directly under Resume. Tapping it opens the same world map. Back should return to the pause menu, with Resume ready to use.
* Map layout: Show the actual world from above. Label every section using its in-game name, draw the recognizable track layouts and connecting roads, and show my current position and facing direction. I should be able to open the map at a fork, see which road reaches the region I want, close it, and make the turn. Keep labels legible on a phone and support controller navigation throughout.
* Fast travel: Place clearly marked fast-travel points in selected sections. Make ordinary region labels visually distinct from selectable destinations so it's obvious where I can travel. Selecting a destination should show its name and let me confirm. Load its road surface and collision, then place my vehicle on clear ground facing a useful exit or landmark. Every destination must also be reachable by driving.
* Online behavior: Opening the map or pause menu should affect only my controls. Fast travel should move only my vehicle and update my position for the other players. If I fast travel during a timed delivery or driving challenge, end that attempt cleanly so teleporting can't complete the objective.

4. Use one smooth day/night cycle

Give the whole world a shared clock. If I leave a track at sunset, drive through two regions, or fast travel, the time of day should remain consistent. Gradually blend the sky, sun angle, ambient light, fog, shadows, and artificial lighting. Preserve the character of each location through local lighting. A neon district can glow during the day, and a brightly lit kitchen can have windows looking out onto a dark landscape.

Check these transitions at driving speed. Roads, barriers, coins, and exits need to stay readable at dusk and at night. Pay particular attention to tunnel exits and region boundaries where sudden exposure, fog, or sky changes would be obvious.

5. Reward curiosity with coins, secrets, and short challenges

Use regular coins to lead players along satisfying driving lines. Put rarer collectible coins in places that reward exploration or skill. The newly accessible surroundings are ideal for this. Let me spot a coin on a loading dock from the racecourse, then work out which side street reaches the ramp behind it. Leave room for discovery on the world map so region labels and fast-travel markers don't give away every secret.

Add optional activities that start and finish in the world. Include a pizza delivery between two regions with a safe route and a riskier shortcut, a drift or jump challenge built around the existing handling, and hidden Easter eggs specific to individual maps. Show the objective and coin reward when an activity starts, offer a quick retry, and save unique discoveries. Tune rewards so exploring a new section feels worthwhile.

6. Add coin-based kart and car unlocks

Create several new kart styles with noticeably different silhouettes from the driving camera. A low delivery kart, a retro open-wheel racer, or a chunky utility kart could work. Inspect the garage and choose designs that add variety to the current lineup. Match the modeling, materials, wheel detail, and livery quality of the best existing vehicles.

Also choose two actual cars from the ones I most recently added and make them coin unlocks. Give one an attainable early price and make the other a longer-term goal. Preserve ownership for players who already earned or purchased them. Use the existing garage, currency, and save systems wherever possible. Let players preview a locked vehicle, see its price and their balance, unlock it, and equip it. Set prices after checking how quickly coins accumulate in normal play.

7. Optimize for smooth 60 FPS driving

Use the Three.js optimization techniques and quality settings already working in the project. Stream the world around the player, preload in the direction of travel, and keep distant landmarks visible at an appropriate level of detail. Account for open terrain and shortcuts when predicting where the player might go. Someone driving straight across a yard or making a sudden U-turn still needs the ground, barriers, and nearby scenery ready in time.

Profile frame times during full-speed crossings, sharp turns toward a new region, map opening and closing, fast travel, and sustained drives through several regions. Check memory after revisiting areas. Test supported mobile and desktop settings, including the highest quality preset. Report the devices or environments tested and the slowest sections observed.

8. Support online free roam if the project can support it

Inspect the multiplayer and hosting setup early. Let players share a world, meet up at a named section, cruise together, or split up and explore independently. Synchronize vehicle movement and the world clock. Keep coins, challenge rewards, garage ownership, and unique collectibles per player. Each client should stream the areas it needs even when players are on opposite sides of the world.

Test with two actual sessions. Have one player open the map while the other keeps driving, fast travel to another region, then meet back up by road. Verify reconnects and reward persistence. If online play depends on unavailable hosting or backend work, finish the single-player experience and identify exactly what remains.

9. Verify the complete experience in-game

Start from the normal menu and reach every track by driving. Use the world map to navigate at least one unfamiliar route. Test Select on controller, verify that Map sits directly beneath Resume on mobile, and fast travel to every marked destination. Drive along region edges and through apparent gaps to check that visible scenery and collision agree. Complete a challenge, find a hidden coin, buy a vehicle, restart, and equip it. Finally, run the original race and Grand Prix modes to verify their layouts and rules still work.

When finished, summarize the connected regions using their actual names, the areas players can explore for the first time, the fast-travel destinations, the new kart unlocks and prices, the two recent cars selected, measured performance, and what you verified online."

## Added by the owner, 2026-11-13 (Sandbox: races from the start line)
"In sand box mode if you drive up to the start line of a race you can initiate the race track to start a race, the start lines of race tracks should have little visible markers for the player to see if they want to start a race. In online play if up to 4 players go to the start line they can all join the same race. It will first create a lobby and the host will have to start the race after everyone that's joined has ready-ed up. There will be a screen similar to the online screen we have now showing each player and giving them a ready up option before the race starts"

## Added by the owner, 2026-11-13 (later): the race from Sandbox, and Balloon Battle changes
"Once the race starts it's like as if you were racing directly on that track until the race is over and then it goes back to like sandbox where you can drive anywhere
Also on the balloon map part of one of the wooden ramps runs straight into the large square piece on the ground. Also some of the objects placed around can be driven through. The ramps only cover about half of the actual ledge, they should go from end to end because right now there are little spots next to the ramp the player can get stuck in. There should also be more item boxes because you can only eliminate people with items. Each player should have 3 balloons and any homing items should be removed for the balloon game mode , as well as items that drop on the floor. It should only be projectiles the player has to aim or speed boosts. The auto drive speed boost items should also be removed for this game mode"

## Added by the owner, 2026-11-13 (later still)
"add flour bomb and meatball to the balloon game mode and continue with the sandbox between the rest of the maps in the game."

## Added by the owner, 2026-11-13 (two more)
"make sure to commit these changes to the pc version as well"
"also once all the changes are complete lets update the website"
(The website beside the game is the PC Edition page, `pc.html` in the app repository, with `pc/` its trailer and stills. It still says seventeen tracks and names only single races, Grand Prix, Reverse and Last Slice Standing.)

## Added by the owner, 2026-11-13 (from a play-test of Kitchen Chaos and the toy cup, with screenshots)
- "this is an image of the track going through the kitchen counter on the kitchen map lets fix this" / "there is also something invisible on the track in the second image that was stopping me from going forward" (on the blue climb, lap 2 of 4, near the right-hand rail)
- "the books also slightly run into the track"
- "also make the shortcuts like this not have any curve and just be straight. when they curve to the right slightly back into the track it forces the player to run into the wall. there are a few tracks that have shortcuts like this in the hotwheels grand prix so look over them and fix any that have the issue"
- "also im noticing every race is ending slightly before the actual finish line lets fix this as well"

## Added by the owner, 2026-11-13 and 14 (Balloon Battle and Sandbox, with screenshots; all answered in web v191 and v192)
- "this ramp is also undriveable in balloon battle because its stuck to the box in front of it and too high up please fix this"
- "when you drive up the ramp that does work on to the top piece the camera angle is really bad and the car sort of floats on the object"
- "im noticing that going up some of the ramps or spirals are still a little choppy especially in the sandbox mode. the ground near the house is also flashing when im on the higher up spots like the spiral. i uploaded a picture of the are that is doing it. its where the grey sidewalk is that connects to the house"
- "the camera is also really bad at following the car when you jump from a high piece of the track to the ground, test it a few times and adjust the camera to work better"

## Added by the owner, 2026-11-14 (Sandbox, from a play-test of web v191/v192, with a picture of a "warp" star field: bright streaks of white, violet and blue flying out from the middle of a black screen)
- "when driving through the tunnels into the other rooms i dont want the car to dissappear i want to drive on a track where it looks like im going through a tunnel with this sort of design. i uploaded a picture for you to see."
- "also dont forget to add a map with fast travel in the pause menu and on controller make the y button open the map"
- "and add signs above the tunnels into each section of the map."
- "also some maps you cant go backwards on the tracks but you should be able to go backwards."
- "also if you hold down both brake buttons in sandbox it should completely stop the car and there should be a park button on screen that will stop the car in place that way you can stop at races easier."
- "also going around the loops is a little glitchy in sandbox mode"
- (later the same day, after seeing test pictures) "im noticing in the images you rendered that some of the signs for the locations are covered make sure they are more visible, also make it so you can zoom in on specfic tracks in the map section and can see where you are on the map and where the tunnel to the other room is"

## Added by the owner, 2026-11-14 (three more, while web v193 was being tested)
- (controller menus) "also im thinking instead of the yellow boxes on controller it should just be an on screen cursor and mouse. the scroll function should work the same as the on screen mouse moves to the bottom of the screen the screen will scroll down and same thing for up. this way the user has total control of what they click on. the mouse will be controlled with the left stick and make scrolling a right stick function as well even though it also works with the mouse"
- (online Grand Prix) "also grand prix wasnt working online after one race it was saying race again or change driver but no to the next race option please look into that. it was between 2 computers on the web app but make sure its working online on all platforms"
- (trees) "also update all the maps with the new trees we made a while ago im noticing some of the older maps still have the old blocky trees and shrubs. take new photos for their preview when you finish as well"
- (the same day, later) "Also when you are finished explain clearly what is on the pc version compared to the web version and begin making sure they are both fully updated"
