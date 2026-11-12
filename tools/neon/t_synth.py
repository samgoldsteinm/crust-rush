from gen import Track

def make():
    t = Track('synth', 'Synthwave Supreme', themeName='Neon sunset', look='sun', acc='#ff5fa2', acc2='#ffb43f',
              blurb='The last race of the night: a figure of eight under a huge striped sun, with a climbing loop over your own road and a glide straight into the sunset.')
    s0 = t.S(500, h=0)                          # start straight, east
    t.A(620, -22); t.A(620, 44); t.A(620, -22)
    s0b = t.S(160, h=0)
    a1 = t.A(520, 135, h=0)                     # north-west
    s2 = t.S(420, h=0)
    t.A(420, 32); t.A(420, -64); t.A(420, 32)   # esses
    s2b = t.S(700, h=0)                         # passes under the loop's way out
    a3 = t.A(430, -270, h=95, hR=95)            # the climbing loop, out over the road you came in on
    s4 = t.S(560, h=95, hR=95)                  # the bridge
    s4b = t.S(420, h=135, hR=30)                # up to the launch deck
    s4c = t.S(200, h=135, hR=0)
    g5 = t.S(1200, h=0, hR=135, tag='glide')    # the glide, into the sun
    s6 = t.S(160, h=0, hR=135)
    s6b = t.S(900, h=0, hR=60)
    a7 = t.A(480, 135, h=0, hR=0)               # east
    s8 = t.S(300, h=0)
    t.A(300, -90)                               # the hairpin detour
    s9 = t.S(380, h=0)
    a9 = t.A(230, 180, h=0)
    s9b = t.S(380, h=0)
    t.A(300, -90)
    s10 = t.S(600, h=0)
    t.build(close=(s10, s2b))
    for seg, f, lat in [(s0, .5, 0), (s2, .5, 22), (s2b, .35, -22), (a3, .3, 0), (a3, .7, 0), (s4, .5, 0), (s6b, .8, 0), (s8, .4, 22), (s9, .3, 0), (s9b, .6, 0), (s10, .5, -22)]:
        t.pad(seg, f, lat)
    for seg, f in [(s0, .8), (s2b, .55), (s8, .7), (s10, .25)]:
        t.ramp(seg, f)
    for seg, f in [(s2, .15), (s4, .1), (s8, .1), (s10, .75)]:
        t.box(seg, f)
    t.short(a9, .06, a9, .94, 0)
    return t
