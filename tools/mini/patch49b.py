"""Patch 49b (web v210): every garage tab fits on a phone held sideways.
The owner: "add the color section back on mobile, or wherever we removed it". On a phone (844 x 390) the seven tabs need 492 px and had 427:
the last one (Theme) sat past the right edge, reached only by swiping the strip (scratch/gphone.py). On screens up to 960 px wide the
tabs' sides are narrower and the text a little smaller, so all seven show. (The PC's garage had lost its Colour tab: put back there.)
Run once: py.cmd tools/mini/patch49b.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 49b' not in s, 'already patched'
a = ".g-tabs button{border:0;background:transparent;border-radius:10px;padding:8px 13px;font-weight:700;font-size:14px;color:var(--muted);white-space:nowrap}"
assert s.count(a) == 1
s = s.replace(a, a + "@media (max-width:960px){.g-tabs button{padding:8px 6px;font-size:12.5px}.g-tabs{gap:2px}}/* (patch 49b: all seven tabs on a phone) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 49b applied')
