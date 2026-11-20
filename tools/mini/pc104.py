"""PC: the garage paint reflects the workshop, as the web's (gStudioEnvFrom: the room alone, full strength).
The ReflectionProbe (pc101) captured from inside the car: its reflections were the cabin and the driver (green for Basil),
so the paint read flat and a black car showed green streaks. Now it sees the room only (layer 2), at full strength.
    python tools/mini/pc104.py      (once, after pc103)"""
p = 'D:/crust-rush/godot/scripts/menu.gd'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("			pr.intensity = 0.5\n",
    "			pr.intensity = 1.0   # (pc104: full, as the web's envMap)\n"
    "			pr.cull_mask = 2   # (pc104) the room only: from inside the car it caught the cabin and the driver\n")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc104 applied')
