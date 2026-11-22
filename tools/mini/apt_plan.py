"""The owner's apartment: floor plan redrawn from THEIR sketch (2026-11-22, photo of a hand drawing), for them to check.
Positions are the sketch's own, read off the photo at about 70 px a metre (the sketch has no scale; sizes are a guess
that keeps its proportions). Metres, x east, y north (north = the top of the sketch). Output: scratch/apt_plan.png
Things marked ? are my guesses at what an unlabelled shape in the sketch is."""
from PIL import Image, ImageDraw, ImageFont

S = 95   # pixels per metre
X0, X1, Y0, Y1 = -0.3, 11.0, -0.4, 6.7
im = Image.new('RGB', (int((X1 - X0) * S) + 40, int((Y1 - Y0) * S) + 110), '#ffffff')
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('arial.ttf', 15)
    fb = ImageFont.truetype('arialbd.ttf', 21)
    fq = ImageFont.truetype('ariali.ttf', 15)
except OSError:
    f = fb = fq = ImageFont.load_default()
P = lambda x, y: (20 + (x - X0) * S, 20 + (Y1 - y) * S)


def rect(x0, y0, x1, y1, fill, out='#444444', w=2):
    d.rectangle([P(x0, y1), P(x1, y0)], fill=fill, outline=out, width=w)


def label(x, y, t, font=None, col='#222222'):
    d.multiline_text(P(x, y), t, fill=col, font=font or f, anchor='mm', align='center')


def wall(*pts, w=6):
    d.line([P(*p) for p in pts], fill='#111111', width=w)


# floors: bedroom carpet, the rest laminate
rect(0, 1.1, 4.6, 6.1, '#d8cdbb', None, 0)
rect(4.6, 1.1, 10.3, 6.3, '#ebe3d4', None, 0)
rect(1.1, 0.3, 10.6, 1.1, '#ebe3d4', None, 0)
rect(1.1, 0.0, 2.8, 0.3, '#ebe3d4', None, 0)
# walls (as drawn): bedroom box, main room, the hall's south wall, the small box off the hall's west end
wall((0, 6.1), (4.6, 6.1), (4.6, 1.1), (3.4, 1.1))
wall((2.7, 1.1), (0, 1.1), (0, 6.1))
wall((4.6, 6.1), (4.6, 6.3), (10.3, 6.3), (10.3, 1.45))
wall((1.1, 1.1), (1.1, 0.0), (2.8, 0.0), (2.8, 0.3), (10.6, 0.3))
# room names
label(2.3, 5.0, 'BEDROOM', fb)
label(6.3, 5.95, 'LIVING ROOM', fb)
label(8.9, 6.0, 'KITCHEN / DINING', fb)
label(6.6, 0.7, 'HALL', fb)
# bedroom
rect(1.15, 5.55, 2.95, 6.07, '#e6dfd0'); label(2.05, 5.8, 'dresser + mirror')
rect(0.05, 4.35, 0.5, 4.8, '#ffffff'); label(0.75, 4.95, 'nightstand', font=fq)
d.ellipse([P(0.1, 1.45), P(0.3, 1.25)], fill='#222222'); label(0.55, 1.6, 'floor lamp', font=fq)
label(4.05, 5.85, 'anime poster', font=fq); rect(3.95, 1.3, 4.5, 1.85, '#9fb0bb'); label(3.9, 2.05, 'litter box, cat post', font=fq)
label(2.2, 2.7, 'laundry basket', font=fq)
rect(3.55, 4.35, 4.55, 5.6, '#3a3a3a'); label(4.05, 4.98, 'desk,\nmonitor,\ngaming\nchair', col='#ffffff')
rect(0.03, 3.05, 1.65, 4.3, '#2c4a7a'); label(0.85, 3.68, 'bed', col='#ffffff')
rect(0.0, 3.0, 0.12, 4.35, '#e8e2d6', '#888888', 1)
rect(0.8, 1.12, 2.7, 1.3, '#ffffff'); label(1.75, 1.55, 'closet (white bifold)')
d.line([P(2.7, 1.1), P(3.4, 1.1)], fill='#ebe3d4', width=6); d.line([P(3.4, 1.1), P(2.95, 0.6)], fill='#666666', width=3); label(3.95, 0.95, 'bedroom door', font=fq)
rect(4.42, 3.2, 4.58, 4.1, '#111111'); label(3.95, 3.65, 'TV (on\nthe wall)')
# the small box off the hall's west end and its door
label(1.75, 0.5, 'BATH-\nROOM', fb)
d.line([P(2.8, 0.3), P(2.8, 0.4)], fill='#111111', width=6); d.line([P(2.8, 0.4), P(3.45, 0.75)], fill='#666666', width=3); label(1.95, -0.22, 'bathroom door (mirror) at the hall''s end', font=fq)
rect(2.85, 0.32, 4.65, 0.5, '#ffffff'); label(3.75, 0.15, 'two white bifold closets', font=fq)
label(5.0, 0.12, 'vacuum', font=fq); label(7.3, 0.12, 'bike, map poster, shoes', font=fq)
wall((7.0, 1.1), (7.72, 1.1), (7.72, 2.5)); rect(9.7, 0.32, 10.45, 0.62, '#ffffff'); label(10.07, 0.15, 'shoe cubby', font=fq)
label(7.55, 5.95, 'lamps', font=fq)
# living room
rect(4.85, 6.18, 5.95, 6.28, '#111111'); label(5.4, 5.85, 'TV (pink LED)', font=fq)
rect(4.63, 4.1, 4.95, 5.0, '#ffffff'); label(5.35, 4.55, 'records,\nturntable', font=fq)
label(5.25, 5.25, 'speakers,\nARCADE sign', font=fq)
label(4.85, 2.75, 'tiger\nbanner', font=fq)
d.ellipse([P(4.68, 2.35), P(4.88, 2.15)], fill='#222222'); label(5.05, 2.0, 'floor\nlamp', font=fq)
rect(5.05, 1.4, 5.3, 1.65, '#e8dcc0'); label(5.2, 1.25, 'cat post', font=fq)
rect(7.26, 1.2, 7.68, 2.45, '#4a3a2c'); label(6.95, 1.85, 'black\nshelf', font=fq)
label(6.6, 5.55, 'plants', font=fq); rect(6.9, 4.4, 7.3, 4.8, '#222222'); label(7.05, 4.95, 'office chair', font=fq)
rect(5.07, 2.86, 7.0, 4.71, '#f3f3f3', '#999999'); label(6.05, 4.42, 'rug')
rect(5.5, 3.21, 6.5, 4.0, '#ffffff', '#222222'); label(6.0, 3.6, 'coffee\ntable')
rect(5.43, 2.0, 6.71, 2.86, '#8f9296'); label(6.07, 2.43, 'loveseat\n(faces the TV)', col='#ffffff')
# kitchen and dining
rect(7.57, 4.79, 9.5, 5.71, '#1b1b1b'); label(8.53, 5.25, 'dining table', col='#ffffff')
rect(7.36, 2.93, 8.36, 4.21, '#c8ccd0', None, 0); rect(7.79, 1.86, 8.21, 2.93, '#c8ccd0', None, 0); d.line([P(7.36,4.21),P(8.36,4.21),P(8.36,2.93),P(8.21,2.93),P(8.21,1.86),P(7.79,1.86),P(7.79,2.93),P(7.36,2.93),P(7.36,4.21)], fill='#444444', width=2); label(7.86, 3.57, 'countertop\nisland')
label(7.15, 3.6, 'narrow\ngap', font=fq)
rect(9.57, 1.93, 10.29, 4.5, '#c8ccd0'); label(9.93, 3.8, 'stove,\nmicro-\nwave')
label(9.93, 2.95, 'sink'); label(9.93, 2.25, 'dish-\nwasher')
rect(9.6, 4.55, 10.29, 5.0, '#ffffff'); label(9.93, 4.78, 'coffee\nshelf', font=fq)
rect(7.72, 1.86, 8.28, 2.5, '#b4b8bc'); label(8.0, 2.18, 'fridge', font=fq)
label(8.95, 3.2, 'galley', font=fq)
d.line([P(10.6, 0.33), P(10.6, 1.42)], fill='#ffffff', width=8); label(10.75, 0.88, 'front\ndoor', font=fq)
for (a, b, t) in ((1.25, 2.85, 'window (blinds), behind the dresser'), (6.3, 7.4, 'sliding door (vertical blinds)')):
    yy = 6.1 if b < 4.6 else 6.3
    d.line([P(a, yy), P(b, yy)], fill='#7fb2e6', width=8); label((a + b) / 2, yy + 0.17 if b > 4.6 else yy + 0.12, t, font=fq, col='#7a2020' if '?' in t else '#1d4f86')
d.text((20, int((Y1 - Y0) * S) + 40), 'Redrawn from your sketch (north = the top of your drawing). Everything placed from your sketch, video and photos.',
       fill='#000000', font=f)
d.text((20, int((Y1 - Y0) * S) + 64), 'Sizes are a guess that keeps your proportions: the bedroom about 4.6 x 5 m, the living room and kitchen 5.7 x 5.2 m.',
       fill='#000000', font=f)
im.save('D:/crust-rush/scratch/apt_plan6.png')
print('D:/crust-rush/scratch/apt_plan6.png')
