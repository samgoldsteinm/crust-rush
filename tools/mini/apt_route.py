"""The apartment track: a first route over the approved floor plan (apt_plan.py -> scratch/apt_plan6.png), for the owner
to approve before anything is built. Floor-level track orange, raised track blue, numbered features. Metres as apt_plan.
Output: scratch/apt_route.png"""
import math
from PIL import Image, ImageDraw, ImageFont

S, X0, Y1 = 95, -0.3, 6.7
P = lambda x, y: (20 + (x - X0) * S, 20 + (Y1 - y) * S)
im = Image.open('D:/crust-rush/scratch/apt_plan6.png').convert('RGB')
d = ImageDraw.Draw(im, 'RGBA')
try:
    fb = ImageFont.truetype('arialbd.ttf', 17)
    f = ImageFont.truetype('arial.ttf', 15)
except OSError:
    fb = f = ImageFont.load_default()


def spline(pts, n=14):
    """Catmull-Rom through the points"""
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(len(pts) - 1, i + 2)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def run(pts, col, w=14):
    sp = spline(pts)
    d.line([P(*p) for p in sp], fill=col, width=w, joint='curve')
    return sp


OR, BL = (255, 106, 18, 235), (31, 85, 200, 235)
# 1 start, west along the hall on the floor, into the bedroom (the door's west half)
run([(8.6, 0.72), (6.0, 0.72), (3.6, 0.72), (3.05, 0.95), (2.95, 1.6), (2.85, 2.4), (2.45, 3.1), (2.0, 3.6), (1.7, 3.65)], OR)
# up onto the bed, across it, up to the dresser, along it, across to the desk, down the bedroom's east wall and out over the hall
run([(1.7, 3.65), (0.9, 3.65), (0.55, 3.9), (0.65, 4.45), (1.05, 5.0), (1.45, 5.8), (2.9, 5.8), (3.7, 5.3), (4.05, 4.85), (4.08, 4.0),
     (4.0, 2.9), (3.55, 2.1), (3.3, 1.5), (3.35, 0.95), (3.8, 0.7), (4.6, 0.72)], BL)
# the spiral round the cat post down to the floor
sp = []
cx, cy, r = 5.15, 1.45, 0.38
for k in range(0, 91):
    a = -math.pi / 2 + k / 90 * 2.5 * math.pi
    rr = r * (1 + 0.06 * math.sin(k / 90 * math.pi))
    sp.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
d.line([P(4.6, 0.72), P(*sp[0])], fill=BL, width=14)
d.line([P(*p) for p in sp[:50]], fill=BL, width=14, joint='curve')
d.line([P(*p) for p in sp[49:]], fill=OR, width=14, joint='curve')
# north up the living room's west side, along the TV wall, the loop by the sliding door, under the dining table, down the galley
end = sp[-1]
run([end, (4.85, 2.1), (4.95, 3.3), (4.95, 5.1), (5.3, 5.8), (6.2, 5.9), (6.9, 5.75), (7.4, 5.3), (8.5, 5.25), (9.05, 4.95), (8.96, 4.2),
     (8.96, 2.5), (8.95, 1.25), (8.75, 0.78), (8.6, 0.72)], OR)
# the loop
d.ellipse([P(6.55, 6.05), P(7.0, 5.6)], outline=OR, width=8)
# start line
d.line([P(8.35, 0.5), P(8.35, 0.95)], fill=(255, 255, 255, 255), width=6)
for i in range(4):
    d.rectangle([P(8.3, 0.5 + i * 0.11 + 0.055), P(8.41, 0.5 + i * 0.11)], fill=(0, 0, 0, 255))


def tag(n, x, y, t, tx, ty):
    d.ellipse([P(x - 0.17, y + 0.17), P(x + 0.17, y - 0.17)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    d.text(P(x, y), str(n), fill=(0, 0, 0, 255), font=fb, anchor='mm')


tags = [(1, 8.35, 1.25, 'Start in the hall by the kitchen, west down the hall past the bikes and closets'),
        (2, 2.4, 2.3, 'Into the bedroom, past the laundry basket, a ramp up onto the bed'),
        (3, 0.9, 3.25, 'Across the bedspread, up off the head of the bed onto the dresser'),
        (4, 2.15, 5.35, 'Along the dresser under the window, then a jump across to the desk'),
        (5, 3.6, 3.6, 'Off the desk: raised track down past the TV, over the litter box, out the door'),
        (6, 4.1, 1.35, 'Over the hall (the start straight runs underneath)'),
        (7, 5.75, 1.15, 'A spiral down round the cat post to the floor'),
        (8, 4.5, 4.2, 'North past the lamp, the banner, the speakers and the records'),
        (9, 6.75, 5.2, 'Along the TV wall, a loop-the-loop in front of the sliding door'),
        (10, 8.5, 4.35, 'Under the dining table between the chairs'),
        (11, 9.25, 3.0, 'Down the galley between the fridge and the dishwasher, back to the line')]
for n, x, y, t in tags:
    tag(n, x, y, t, 0, 0)
# legend under the plan
W, H = im.size
out = Image.new('RGB', (W, H + 300), '#ffffff')
out.paste(im, (0, 0))
d2 = ImageDraw.Draw(out)
d2.rectangle([20, H + 8, 50, H + 22], fill=OR[:3]); d2.text((58, H + 6), 'track on the floor', fill='#000', font=f)
d2.rectangle([230, H + 8, 260, H + 22], fill=BL[:3]); d2.text((268, H + 6), 'raised track (on furniture or piers)', fill='#000', font=f)
for i, (n, x, y, t) in enumerate(tags):
    d2.text((20 + (i // 6) * 560, H + 40 + (i % 6) * 24), '%d  %s' % (n, t), fill='#000', font=f)
d2.text((20, H + 190), 'About 38 m a lap (13 000 game units): 3 laps. Heights: bed 55 cm, dresser 85, desk 75 (measured from the photos, roughly).',
        fill='#000', font=f)
out.save('D:/crust-rush/scratch/apt_route.png')
print('D:/crust-rush/scratch/apt_route.png')
