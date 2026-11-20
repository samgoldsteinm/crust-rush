"""PC: Sandbox headlights you can see. The owner: "i dont think we have added the headlights ... to the pc version".
The spot light's beam picture (light_projector, the web's cookie) blacked the whole light out in Godot, in either orientation,
so at night there was no beam at all. Now no picture: the cone and its edge fall-off shape it (34 degrees, angle attenuation 1.2),
aimed 140 ahead at the road, much stronger (Godot's units: 30 at full dark, was 3.2).
    python tools/mini/pc106.py      (once, after pc105)"""
p = 'D:/crust-rush/godot/scripts/sandbox_night.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc106' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("	spot.spot_angle = 35.5\n	spot.spot_angle_attenuation = 0.6\n",
    "	spot.spot_angle = 34.0   # (pc106: the cone and its soft edge shape the beam)\n	spot.spot_angle_attenuation = 1.2\n")
rep("	spot.light_projector = _cookie()\n",
    "	# (pc106) no beam picture: a light_projector blacked out the whole light (no headlights at all on the PC)\n")
rep("	spot.light_energy = 3.2 * maxf(", "	spot.light_energy = 30.0 * maxf(")
rep("	var to := kp + fwd * 120.0 + Vector3(0, -10, 0)", "	var to := kp + fwd * 140.0 + Vector3(0, -2, 0)   # (pc106)")
rep("r[\"off_track\"] > 1.2", "r[\"off_track\"] > 1.2", 0)  # (the test's threshold still holds: 30 x .95)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc106 applied')
