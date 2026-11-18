# Seats onto the older cars (2026-11-18)

The older cars' packs (made before car_convert.py) keep their whole cabin as one class-9 ("seat") shell, so the
Interior colour turned the whole cabin. These scripts take each car's ORIGINAL model (uploaded by the owner) only as a
map: the pack's shape is never changed, only the class of its cabin triangles (seat 9 near the source's seats, dark 1
elsewhere). Wheels and every vertex are identical (chk.py proves it), so nothing a race agrees on changes.

Part ids (c:) depend on the cabin box parts.py used at the time: rerun parts.py and pick by position, not by these numbers.
Run from this folder with py.cmd (Blender for exp.py / deci.py). Sources unpacked under scratch/cars_in/up/<name>/.
1. `blender --background --python exp.py -- <model> <car>.npz`  (an .obj that Blender reads short: `objnpz.py <obj> <car>.npz`)
2. `align.py <car>`: fits the source to the pack (axis order, flips, scale); writes <car>_al.npz
3. find the seats: `parts.py <car>` (loose parts in the cabin, NR=n rows), `labs.py <car>` (materials), `boxplot.py <car> <regex> x0 x1`
4. `transfer.py <car> <sel...>`; sel = c:<part ids> | r:<regex on mat@obj> | B:x0,x1,y0,y1,z0,z1,<regex> | m:<regex> (filter);
   CLS=1,6,9 to let carbon (6) triangles become seat too. Backs up the pack to scratch/cars_prev_seat first.
5. `look.py <car>` (top/side plot, red = seat) and `chk.py <car>` (shape and wheels unchanged).
A pack with NO seats inside (suv): `seatsel.py` + `deci.py` (Blender decimate) + `addseat.py` add the source's own seats.
NOTE py.cmd breaks a `|` in an argument: write alternatives as [..] classes.

What was used (2026-11-18):
- scissor   c:713,714 m:InteriorA           - roadster  r:seat[LR]_leather
- coupe     c:11,12,25,26 (front seats; the source has no rear seats)
- interceptor c:27,28                       - monster   c:16,17          - muscle c:1,3,5,6 (OBJ via objnpz.py)
- onyx      B:-1.0,0.25,0.3,2.6,-1.6,1.6,@interior[.]0[12][45]$
- chariot   CLS=1,6,9 c:6,7
- suv       seats ADDED (pack was hollow): the five Misc_Interior boxes in HANDOVER, 1326 tris base / 1799 HQ
- bike_neutron: left (its saddle is body paint in the pack). skywing = the Jesko upload, done by car_convert already.
