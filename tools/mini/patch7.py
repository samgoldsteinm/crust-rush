# seventh engine patch (v155): no item boxes on the starting grid. Two Neon Cup tracks (holo .9938, synth .9917) had a row
# 14 and 17 track points before the start line, inside the grid, so karts started on top of a box; in reverse the same
# rows lay just past the line. Any row that would land in the start zone is moved to the nearest clear spot.
# Box positions are track data: NET_PROTO goes from 100 to 101 (PC: PROTO 101 with its next build, after the track
# export is re-run from the published web game). Run once: py.cmd tools\mini\patch7.py
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("const boxRow=(f,gi)=>{const p=track[def.neon?nfj(f):Math.floor(f*N)];",
    """/* No item boxes on the starting grid or just past the start line, whichever way the race runs: the grid reaches 38 track points
     back with twelve karts. A row that would land within 56 points before the line or 44 after it moves to the nearest clear spot. */
  const boxClear=j=>{j=((j%N)+N)%N;return j>=N-56?N-57:j<=44?45:j;};
  const boxRow=(f,gi)=>{const p=track[boxClear(def.neon?nfj(f):Math.floor(f*N))];""")
rep("NET_PROTO=100", "NET_PROTO=101")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
