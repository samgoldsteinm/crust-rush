# Balloon Battle on the PC: where each piece goes (researched 2026-11-14, nothing built yet)

PC line numbers are for `D:\crust-rush\godot` at commit c424cba. Web: `tools/mini/battle.js` (the whole mode) and every use of
`BATTLE` in `crust-rush.html`. Rules: `docs/BALLOON-BATTLE-PLAN.md`. Balloon Battle is OFF LINE only: nothing in `webnet.gd` may change.

## Read first
- The exported height map is the bare table: `__exportData` (godot/tools/glbexport.js:260) samples `groundAt`, not `battleG`. Port
  `bbArena`/`battleG` (battle.js:23-35) to GDScript, or export `BB.shapes/spawn/ramps` with the map (recommended, see Export).
- On the web `BATTLE` belongs to the map (`BATTLE=!!def.battle` in loadMap0). Mirror: `T.battle` on TrackData, and `race.mode = "bb"`.
- The web's meatball ignores the arena's walls (it is stepped by `itemsProj`, which has no battle branch). On the PC `meat2` goes
  through the common branch at race.gd:1998: adding walls there changes it unless it is left out. Decide: mirror, or fix both.
- PC thrown items have no level check; the web tests `sameLvl(k,p)` on every hit. Battle needs it: `abs(k.wy - bh) < 16`.
- The arena: id `preptable`, MAPS index 24, `laps:99`, `toy:1`, `rw:31`, `special:1`, no boxes/pads/ramps/shortcuts/loops of the
  track's own, not multi-level. Its dummy ring gives N of about 75. `RIM = R-38 = 1122`.

## Web hook -> PC place
**Kart ground and walls** (kart.gd)
- `if(BATTLE)tp=1` -> `step()` after kart.gd:263-264.
- `if(BATTLE)battleWalls(k);else{...}` -> kart.gd:341 `_walls()`. A new `_bb_walls()` can end with `_slide(nx, ny, 0.22, 0.5)`
  (kart.gd:650). Needs `bpx`, `bpy` (last free spot) and an 8-point `bb_touch` (battle.js:37).
- `_rim()` kart.gd:344 stays.
- `let G=BATTLE?battleG(...)` -> `_vertical()` kart.gd:839. Kerb height (kart.gd:842-845) and the lap-line count fix
  (kart.gd:385-388) are skipped in battle.
- New kart state: `bal`, `bb_s`, `bb_out`, `bb_i`, `bb_a`.

**AI** `aiInput -> battleAI` -> race.gd:812 `ai_input`, first line. Return the PC keys as at race.gd:948
(`steer, brake, nb, mul, use, back, hold, hold_sl, release`).

**Hits** `battleHit(k, CURP&&CURP.owner)` -> `spin_out()` after race.gd:1616-1617; the owner is `cur_p.get("owner")`. Report pops with
`fx.append({"t": "bb_pop", ...})`; banners and sounds in main.gd `_drain_events` (the `t == "spin"` block at 1343); the burst in
view.gd `race_event` (1486).

**Items** (race.gd)
- `rollItem -> bbRoll` -> race.gd:1197 `roll_item`; the box loop passes position 3 (race.gd:696).
- `useAbility` returns at once -> race.gd:1646-1648 (and hide the button, hud.gd:507: `ab_c` still charges).
- `BB_ITEMS`: pepperoni 3, trio 2, meatball 2, flour 1.5, chili 2; fallback pepperoni. The meatball is given to everyone unless it
  is switched off in Settings (`item_set.get("meatball", true) == false`), locked or not: `race.items_off` cannot tell those apart.
- Projectile walls `bbProjWalls` (battle.js:128) -> race.gd:1998-2002; level test on the flour blast (2057), the plain hit (2138) and
  meat2 (2027); `pGround`/`hazEy` -> view.gd:866 `_proj_ground`, race.gd:2239 `haz_ground`.

**Tick and finish** `battleTick` (battle.js:59-64) -> race.gd `update()` after 726 `cur_p = {}`, before 728: `if mode == "bb":
_bb_tick(dt); return` (skips the `_fin_at` loop). Off the table at `wy < -70`; `bb_out` countdown and respawn at the spawn furthest
from the others; at time up every kart gets `finished/place/finish_time`, `ai["auto"]=true`, `finish_count = karts.size()`.

**Start** `battleStart` -> main.gd `_start_race`, right after 1042-1043, before `view.setup`/`add_kart` (1048-1050) and
`cam_a = kart.ma` (1084). `bbSpawnAt` -> model on `Kart.respawn()` kart.gd:1028-1059.

**HUD** lap banner main.gd:1202-1203; wrong way main.gd:2364-2365; hide position (hud.gd:322), top bar (501-504), special (507),
wrong way (518); `hud.pb_text = ""` (main.gd:1063); no ghost (main.gd:1064 add "bb"); skip `test_drive` (main.gd:2380). With
LAPS=99 the progress bar and lap box would draw 98 marks: they must be hidden.

**Results** row text main.gd:1731-1733; buttons main.gd:1742 ("Battle again"), 1752 (hide), 1758 ("Change mode or driver");
`_finish_check` main.gd:1206-1208 add "bb" (else a best time is saved and achievements run). The web shows "Time!".

**Camera** main.gd `_camera` (2150): `rg` at 2175, `cy` at 2180 (`rz - min(8, (rz - rg) * .55)`), the pull-in at 2219-2232 reads the
arena ground. Body footing view.gd:484-487; held item height view.gd:798.

**Menu** `MODES` menu.gd:28 and `MODE_NOTE` menu.gd:31; on choosing the mode load or leave the arena (main.gd:773-777 handler ->
`_menu_preview_map`, main.gd:2452); boot guard main.gd 168-174 and `_load_settings` 3430-3432 (mode and map are restored
independently); the track list `_track()` menu.gd:1284 filters the arena out, 1192-1199 hold the title and Start text. Leaving the
mode when hosting or joining: main.gd `_web_join` 1531, `_web_host_room` 1586, `_menu_host` 3463, `_menu_join` 3508.

## How a mode works on the PC
`MODES` (menu.gd:28) -> `var mode` (menu.gd:39) -> `go.emit({...})` (menu.gd:1385) -> `_menu_go(o)` (main.gd:2498) -> `_race_on(id)`
-> `load_map` -> `_start_race({})` (main.gd:1008). The mode is `main.sel["mode"]` and reaches the race as `race.mode` (race.gd:72),
set at main.gd:1041-1043. Test override: env `CR_MODE`, `CR_MAP` (main.gd:169-172). Every `lss` special case (the closest existing
example): main.gd 1041-1043, 1064, 1191-1192, 1207, 1225, 1464, 1732, 2099, 3586, 3636, 3662; race.gd 728-731, 754-807;
menu.gd 31, 1195. Results: `_show_results()` main.gd:1679-1776. Karts: `make_cfg` race.gd:103-145 (8 slots, the player in slot 4),
`setup_cfg` 149-201 (index = the web's `bbI`), `_make_kart` 521-541.

## Export and loading
- track.gd `_read` (100-201) needs: `map, name, N, R, RIM, RW, CURB, WALLD, KS, BASE0, ACCEL, TURN, LAPS, KERB_H, classMul, track,
  ramps, pads, obstacles, grid, light, height{...}`; nothing in it breaks on the arena.
- The menu's list: main.gd `scan_maps()` 229-252 (folders with `<id>.json` and `<id>.gltf`; from `<id>.info.json` only
  `name, mi, theme, cup` are copied, line 245).
- Which maps are exported: only the index list in `godot/.github/workflows/maps.yml` (two places); 24 is missing from both.
- To do: add 24 to both lists; ciexport.py:78 add `battle:!!MAPS[mapIdx].battle` to the info card; after ciexport.py:66 add
  `d['battle'] = {shapes:BB.shapes, spawn:BB.spawn, ramps:BB.ramps, T:BB.T, step:BB_STEP, r:BB_R, x0:BB_X0, floor:BB_FLOOR,
  start:BB_START, back:BB_BACK}` and read it in track.gd; main.gd:245 copy `"battle"`.
- A local export: from `D:\crust-rush\godot` run `WEB=D:/crust-rush/app OUT=D:/crust-rush/godot/maps MI=24 py.cmd tools/ciexport.py`.

## Drawing and HUD
- Balloons: copy the pattern of `_draw_held(k)` view.gd:773-801 (a node made on demand, placed from `v["rx"], v["ry"], v["rz"],
  v["rma"]`, freed in `clear()`). Web numbers, battle.js:96-110: sphere r 1.9, y scale 1.22, colour `BB_COL[bbI%8]`; anchor 5 behind
  the kart; `sp = i - (min(bal,n)-1)/2`; `lag = min(6, |speed|*0.03)`; `y = py + 14 - |sp|*1.1 + sin(t*1.7+ph)*0.5`; hidden while
  `bbOut > 0`. Pop: `fx.burst` + `fx.ring` + bump sound.
- The read-out: copy the toast pill at hud.gd:526-532. Web: left 10, top 64, bold 14, text `m:ss · N pt(s) · 3rd`.
- Banners: `'+1'`, `'All popped! Back with 3'`, `'Off the table!'`, `'Time!'`.

## Tests
tests/smoke.gd starts a race headlessly with `main.auto_drive = true`; map and mode from env. A battle test:
`CR_MAP=preptable CR_MODE=bb CR_HD=0 <godot console exe> --headless --path D:\crust-rush\godot --fixed-fps 120 res://tests/battle.tscn`.
Web numbers to compare: `tools/neon/bbtest.py` (15 to 38 pops a round, nobody stuck over 4 s, nobody off the table).

## Risks
1. tests/allmaps.gd fails on the arena (needs `worst * T.L > 4000`): skip battle maps there.
2. `_finish_check`/`_progress_finish` would save a best time and award achievements; `Ach.n_tracks` would count the arena.
3. Standings are by `prog` (race.gd:544-558): use a `bb_rank` (score, then balloons, then index) for the read-out.
4. Lap toasts and final-lap music (main.gd:1247-1255) fire as a kart circles the centre ring unless gated.
5. Online must stay off without touching webnet.gd: `host_start` accepts any map with `mi < 99`; leave the mode and the map in
   main.gd when hosting or joining, keep "bb" out of main.gd:3586, and filter the arena from the host's track picker.
6. Every hook stays behind the flag, the new level check on projectiles included: a normal race must read nothing here.
7. The PC waits `fin_t = 3.5` before results where the web uses 2.4.
8. No preview picture or song for the arena until the shots and music exports are re-run (both fail safe).
