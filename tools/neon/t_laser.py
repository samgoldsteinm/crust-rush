from gen import Track

def make():
    t = Track('laser', 'Laser Slice Skyway', themeName='Neon skyway', look='city',
              blurb='A skyway of light over a sleeping city: climb to the high road, corkscrew down through your own lane and launch off the sky deck for a long glide home.')
    s0 = t.S(700, h=0)                        # main straight, east
    t.A(900, 16); t.A(900, -32); t.A(900, 16) # a fast weave
    s0b = t.S(300, h=0)
    a1 = t.A(480, 90, h=0)                    # north
    s2 = t.S(260, h=20)
    t.A(560, -26, h=50); t.A(560, 26, h=80)   # climbing S
    a3 = t.A(380, 90, h=110)                  # west, up to the skyway
    s4 = t.S(380, h=110)                      # the skyway
    t.A(520, 30, h=110); t.A(520, -60, h=110); t.A(520, 30, h=110)
    s4b = t.S(420, h=110)
    a5 = t.A(260, 270, h=0)                   # corkscrew down, out under the skyway
    s6 = t.S(560, h=0)                        # north, under the skyway
    t.A(640, 22); t.A(640, -22)
    s6b = t.S(200, h=0)
    a7 = t.A(400, -180, h=0)                  # hairpin
    s8 = t.S(260, h=0)                        # south
    t.A(560, -24); t.A(560, 48); t.A(560, -24)
    s8b = t.S(500, h=0)                       # under the skyway again
    a9 = t.A(300, -90, h=0)                   # west
    s10 = t.S(600, h=120, hR=0)               # climb to the sky deck
    s11 = t.S(400, h=120, hR=0)               # sky deck
    g12 = t.S(1050, h=0, hR=120, tag='glide') # the glide
    s13 = t.S(150, h=0, hR=120)
    s14 = t.S(600, h=0, hR=0)
    a15 = t.A(420, 180, h=0)                  # last hairpin
    s16 = t.S(300, h=0)
    t.A(520, -32); t.A(520, 64); t.A(520, -32)
    s16b = t.S(500, h=0)                      # back straight to the line
    t.build(close=(s0, s8b))
    for seg, f, lat in [(s0, .45, 0), (s0b, .3, -24), (s4, .3, 0), (s4b, .5, 22), (s6, .7, 0), (s8, .35, -22), (s8b, .6, 22), (s10, .03, 0), (s14, .75, 0), (s16, .4, 22), (s16b, .35, -22)]:
        t.pad(seg, f, lat)
    for seg, f in [(s0, .72), (s4b, .08), (s6, .4), (s8, .7)]:
        t.ramp(seg, f)
    for seg, f in [(s2, .5), (s4b, .9), (s8, .12), (s16, .2)]:
        t.box(seg, f)
    t.short(a7, .1, a7, .9, 0)
    t.short(a15, .1, a15, .9, 0)
    return t
