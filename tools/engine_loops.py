"""Engine loops for both versions of the game, made from the user's own recordings (Pixabay):
  kart  <- freesound_community-engine-6000   (a small motor holding its revs: karts, bikes)
  race  <- dragon-studio-car-engine-372477   (the high-revving stretch of a sports car's rev: race cars)
  v8    <- dragon-studio-car-engine-roaring  (the deep middle of a big engine's roar: muscle cars, trucks)
Each loop is a 2.4 s texture stitched from pieces of the steady part of the recording, every join placed where the two
waveforms line up, its slow swell evened out and its end blended into its start, so it can run for minutes without a
repeating pattern (the old synthesised engine's two slightly detuned tones beat against each other: the "revolving hum").
Writes assets/sfx/eng_<name>.wav (22.05 kHz mono) and, with --preview DIR, a short drive through the gears for each.
Usage: python3 tools/engine_loops.py <dir with the three mp3s> [--preview DIR]"""
import glob, os, subprocess, sys, wave
import numpy as np

SR = 22050
SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'sfx')
PRE = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
# name: (file pattern, steady stretch in seconds)
VOICES = {'kart': ('*engine-6000*', 0.05, 1.90), 'race': ('*car-engine-372477*', 0.48, 0.80), 'v8': ('*roaring*', 0.74, 1.32)}


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0


def smooth(x, n):
    k = np.ones(n) / n
    return np.convolve(x, k, 'same')


def best_join(tail, seg, p, search):
    """the start near p in seg whose first len(tail) samples best continue tail"""
    n = len(tail)
    best, bp = -1e9, p
    for q in range(max(0, p - search), min(len(seg) - n - 1, p + search)):
        c = np.dot(tail, seg[q:q + n]) / (np.linalg.norm(seg[q:q + n]) + 1e-9)
        if c > best:
            best, bp = c, q
    return bp


def texture(seg, length, rng):
    xf = int(0.03 * SR)
    out = list(seg[:int(0.3 * SR)])
    while len(out) < length + 2 * xf:
        tail = np.array(out[-xf:])
        p = rng.integers(0, max(1, len(seg) - int(0.45 * SR)))
        p = best_join(tail, seg, p, int(0.012 * SR))
        c = int(rng.uniform(0.18, 0.42) * SR)
        piece = seg[p:p + c + xf]
        if len(piece) < xf * 2:
            continue
        w = np.linspace(0, 1, xf)
        mixed = tail * (1 - w) + piece[:xf] * w
        out = out[:-xf] + list(mixed) + list(piece[xf:])
    y = np.array(out)
    # the seam: the stretch just past the loop's end blends into its start
    L = length
    L = best_join(y[:xf], y, L, int(0.012 * SR))
    w = np.linspace(0, 1, xf)
    y[:xf] = y[L:L + xf] * (1 - w) + y[:xf] * w
    return y[:L]


def even_out(y):
    """flatten slow swells (anything slower than ~6 Hz) so nothing throbs, then high-pass the rumble"""
    env = np.sqrt(smooth(y * y, int(0.16 * SR)) + 1e-9)
    envl = np.sqrt(np.mean(y * y))
    y = y * np.clip(envl / env, 0.5, 2.0)
    # gentle 50 Hz high-pass (one pole)
    a = np.exp(-2 * np.pi * 50 / SR)
    o = np.zeros_like(y)
    prev_x = prev_o = 0.0
    for i, v in enumerate(y):
        prev_o = a * (prev_o + v - prev_x)
        prev_x = v
        o[i] = prev_o
    return o


def write(path, y):
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.8
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


def drive(loop, f=1.0):
    """a short drive: pull away through the gears, a boost, a drift, lift off"""
    GT = [0, .2, .42, .64, .86, 1.31]
    t = np.arange(int(11.0 * SR)) / SR
    sp = np.clip(np.where(t < 7.5, 1 - np.exp(-t / 2.4), (1 - np.exp(-7.5 / 2.4)) * np.exp(-(t - 7.5) / 1.6)), 0, 1.2)
    sp = sp + np.where((t > 5.0) & (t < 6.2), 0.15, 0)
    rate = np.zeros_like(t)
    for i, r in enumerate(sp):
        gi = 0
        while gi < 4 and r > GT[gi + 1]:
            gi += 1
        rpm = min(1.12, .3 + .7 * min(1, (r - GT[gi]) / (GT[gi + 1] - GT[gi])) + (.12 if 5.0 < t[i] < 6.2 else 0))
        ef = (24 + rpm * 58 + gi * 4)
        rate[i] = ef / (24 + .75 * 58 + 8)
    rate = smooth(rate, int(0.05 * SR))
    ph = np.cumsum(rate) % len(loop)
    i0 = ph.astype(int)
    fr = ph - i0
    y = loop[i0] * (1 - fr) + loop[(i0 + 1) % len(loop)] * fr
    return y * np.clip(t / 0.3, 0, 1) * np.clip((11.0 - t) / 0.5, 0, 1)


rng = np.random.default_rng(7)
os.makedirs(OUT, exist_ok=True)
for name, (pat, a, b) in VOICES.items():
    files = glob.glob(os.path.join(SRC, pat))
    if not files:
        print('missing', pat)
        continue
    x = load(files[0])
    seg = x[int(a * SR):int(b * SR)]
    y = texture(seg, int(2.4 * SR), rng)
    # evened out round the loop (three copies, keep the middle) so the end still runs into the start
    y = even_out(np.concatenate([y, y, y]))[len(y):2 * len(y)]
    write(os.path.join(OUT, 'eng_%s.wav' % name), y)
    print(name, 'from', os.path.basename(files[0]), '%.2f-%.2f s ->' % (a, b), '%.2f s' % (len(y) / SR))
    if PRE:
        os.makedirs(PRE, exist_ok=True)
        d = drive(y)
        wp = os.path.join(PRE, 'drive_%s.wav' % name)
        write(wp, d)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wp, '-b:a', '128k', wp[:-4] + '.mp3'], check=True)
