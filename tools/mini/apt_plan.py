"""The owner's apartment (their video 2026-11-22): my reading of the floor plan, drawn for them to correct.
Metres, x east, y north (the picture has north up). Output: scratch/apt_plan.png"""
from PIL import Image, ImageDraw, ImageFont

S = 80   # pixels per metre
W, H = 12.0, 9.0
im = Image.new('RGB', (int(W * S) + 80, int(H * S) + 120), '#ffffff')
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('arial.ttf', 15)
    fb = ImageFont.truetype('arialbd.ttf', 20)
except OSError:
    f = fb = ImageFont.load_default()
P = lambda x, y: (40 + x * S, 40 + (H - y) * S)


def rect(x0, y0, x1, y1, fill, out='#555555', w=1):
    a, b = P(x0, y1), P(x1, y0)
    d.rectangle([a, b], fill=fill, outline=out, width=w)


def label(x, y, t, font=None, col='#222222'):
    d.multiline_text(P(x, y), t, fill=col, font=font or f, anchor='mm', align='center')


# floors
rect(0, 0, 4.2, 9, '#d9cfbf')        # bedroom (carpet)
rect(4.2, 0, 7.4, 9, '#e9e1d2')      # living (laminate)
rect(7.4, 0, 12, 9, '#e9e1d2')       # kitchen / dining / entry
# rooms
label(2.1, 8.4, 'BEDROOM', fb)
label(5.8, 8.4, 'LIVING ROOM', fb)
label(9.7, 8.4, 'DINING', fb)
label(9.7, 4.6, 'KITCHEN\n(galley)', fb)
label(10.6, 0.9, 'ENTRY', fb)
label(5.8, 1.1, 'HALL', fb)
# outer walls
d.rectangle([P(0, 9), P(12, 0)], outline='#111111', width=5)
# bedroom wall with its door (mirror on it) from the hall
d.line([P(4.2, 9), P(4.2, 2.2)], fill='#111111', width=5)
d.line([P(4.2, 1.4), P(4.2, 0)], fill='#111111', width=5)
label(4.45, 1.8, 'door\n+mirror')
# bedroom furniture
rect(0.1, 4.2, 2.0, 6.6, '#2c4a7a'); label(1.05, 5.4, 'bed\nnavy\nfloral', col='#ffffff')
rect(0.05, 4.1, 0.25, 6.7, '#ddd6c8'); label(0.6, 3.7, 'herringbone\nheadboard')
rect(0.1, 7.2, 0.6, 8.9, '#e3dccd'); label(1.2, 8.0, 'dresser')
rect(2.6, 8.3, 4.0, 8.9, '#333333'); label(3.3, 7.8, 'desk +\nmonitor')
d.line([P(0.8, 9), P(2.4, 9)], fill='#7fb2e6', width=7); label(1.6, 9.25, 'window (curtains)')
rect(2.8, 0.1, 4.1, 0.5, '#ffffff'); label(3.45, 0.85, 'closet (white\nbifold)')
# living room
rect(4.4, 8.75, 6.0, 8.9, '#111111'); label(5.2, 8.15, 'TV + pink LED\nspeakers, records')
d.line([P(6.2, 9), P(7.3, 9)], fill='#7fb2e6', width=7); label(6.75, 9.25, 'sliding glass door')
rect(4.8, 4.6, 6.8, 7.4, '#efefef', '#999999'); label(5.8, 7.0, 'trellis rug')
rect(5.2, 5.6, 6.4, 6.3, '#ffffff', '#222222'); label(5.8, 5.95, 'coffee table')
rect(4.9, 3.6, 6.7, 4.4, '#8f9296'); label(5.8, 4.0, 'grey loveseat')
rect(6.8, 3.8, 7.3, 4.3, '#222222'); label(6.4, 3.3, 'office chair')
rect(4.3, 2.4, 7.3, 2.6, '#ffffff'); label(5.8, 2.9, 'white bifold closets')
# kitchen: peninsula on the west side, galley along the east wall
rect(7.4, 2.2, 8.0, 6.0, '#c8ccd0'); label(7.7, 6.4, 'peninsula\n(marble\ncounter)')
rect(11.3, 2.2, 12.0, 6.2, '#c8ccd0'); label(10.8, 3.0, 'sink,\nstove,\nmixer')
rect(11.2, 1.5, 12.0, 2.2, '#b4b8bc'); label(10.6, 1.85, 'fridge')
rect(11.4, 6.3, 12.0, 6.9, '#ffffff'); label(10.9, 6.6, 'coffee\nshelf')
rect(8.6, 7.0, 10.4, 8.0, '#1b1b1b'); label(9.5, 6.6, 'black dining table')
d.line([P(8.4, 9), P(10.6, 9)], fill='#7fb2e6', width=7); label(9.5, 9.25, 'window, table lamp')
# entry, front door
d.line([P(9.6, 0), P(10.6, 0)], fill='#ffffff', width=7); label(10.1, -0.25, 'front door')
rect(7.5, 0.1, 8.3, 0.5, '#ffffff'); label(8.5, 0.85, 'shoe cubby,\nbags')
label(8.6, 1.6, 'bikes,\nmap poster,\nvacuum')
d.text((40, int(H * S) + 85), 'My reading of the video (metres, north up). Please mark anything that is in the wrong place.', fill='#000000', font=f)
im.save('D:/crust-rush/scratch/apt_plan.png')
print('D:/crust-rush/scratch/apt_plan.png')
