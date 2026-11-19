"""PC: the underglow about a third brighter (web v247, patch 113).
    python tools/mini/pc102.py      (once, after pc101)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('view.gd', "const UG_GAIN := 1.0       # (web UG_GAIN)", "const UG_GAIN := 1.35      # (pc102: a third brighter; web UG_GAIN)")
rep('view.gd', "const UG_BOUNCE := 0.35    #", "const UG_BOUNCE := 0.47    # (pc102)")
rep('view.gd', "const UG_BOUNCE_R := 1.6   #", "const UG_BOUNCE_R := 2.15  # (pc102)")
rep('view.gd', 'hm.set_shader_parameter("ug_alpha", 0.1 + 0.6 * dark)', 'hm.set_shader_parameter("ug_alpha", 0.14 + 0.78 * dark)')
print('pc102 applied')
