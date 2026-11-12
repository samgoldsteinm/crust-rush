from gen import Track

def make():
    t = Track('holo', 'Hologram Heights', themeName='Neon tower', look='holo', acc='#4dffb8', acc2='#b56bff',
              blurb='Wind up the terraces of a tower of light around a giant spinning hologram, cross the roof and glide out over everything you just climbed.')
    s0 = t.S(900, h=0)                         # start straight, east
    t.A(800, 18); t.A(800, -18)
    s0b = t.S(300, h=0)
    a1 = t.A(560, 90, h=0)                     # north
    s2 = t.S(1010, h=0)
    r1 = t.A(640, 180, h=40)                   # the terraces: half turns, each tighter and higher
    r2 = t.A(530, 180, h=85)
    r3 = t.A(420, 180, h=115)
    r4 = t.A(310, 270, h=178)                  # onto the roof, heading west
    s5 = t.S(900, h=178)                      # the roof road, out over the terraces
    g6 = t.S(1300, h=0, tag='glide')           # the glide (the other way round this is a long ramp up)
    s7 = t.S(700, h=0)
    t.A(520, 28); t.A(520, -28)
    a8 = t.A(350, 90, h=0)                     # south
    s9 = t.S(60, h=0)
    c1 = t.A(300, -55); t.A(300, 110); c3 = t.A(300, -55)  # a hard chicane
    s9b = t.S(300, h=0)
    a10 = t.A(350, 90, h=0)                    # east
    s11 = t.S(300, h=0)
    s12 = t.S(1500, h=0)
    t.build(close=(s12, s9b))
    t.holo_seg = r4
    for seg, f, lat in [(s0, .4, 0), (s2, .5, -22), (r1, .5, 0), (r2, .5, 0), (r3, .5, 0), (s5, .25, 22), (s5, .6, -22), (s7, .7, 0), (s9b, .5, 0), (s11, .5, 22), (s12, .08, -22), (s12, .86, 0)]:
        t.pad(seg, f, lat)
    for seg, f in [(s0, .75), (s2, .1), (s12, .72)]:
        t.ramp(seg, f)
    for seg, f in [(s2, .8), (r3, .1), (s7, .3), (s12, .93)]:
        t.box(seg, f)
    t.short(c1, .08, c3, .92, 0)
    t.glide_rev(s12, .34, 300)
    return t
