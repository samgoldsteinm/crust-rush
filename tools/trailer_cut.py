#!/usr/bin/env python3
"""Joins the clips recorded by tests/trailer.gd into the download page's trailer.

  trailer_cut.py one  <frames dir> <secs> <out.mp4>    last <secs> of a Movie Maker PNG sequence (+ its .wav) -> mp4
  trailer_cut.py join <out dir> <clip.mp4>...          clips -> trailer.mp4 (0.5 s cross-fades), poster.jpg, shot-N.jpg
"""
import glob
import json
import os
import re
import subprocess
import sys

FPS = 30
FADE = 0.5
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p"]


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         check=True, capture_output=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return out.strip() != ""


def one(frames_dir, secs, out):
    frames = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    if not frames:
        sys.exit("no frames in " + frames_dir)
    keep = int(round(float(secs) * FPS))
    first = max(0, len(frames) - keep)
    m = re.match(r"^(.*?)(\d+)\.png$", os.path.basename(frames[0]))
    prefix, digits = m.group(1), len(m.group(2))
    start_no = int(m.group(2)) + first
    pattern = os.path.join(frames_dir, f"{prefix}%0{digits}d.png")
    wavs = glob.glob(os.path.join(frames_dir, "*.wav"))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-framerate", str(FPS), "-start_number",
           str(start_no), "-i", pattern]
    if wavs:
        cmd += ["-ss", f"{first / FPS:.3f}", "-i", wavs[0], "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "160k",
                "-shortest"]
    cmd += ["-frames:v", str(len(frames) - first)] + X264 + [out]
    print(f"{len(frames)} frames, keeping {len(frames) - first} from #{start_no}, audio: {bool(wavs)}")
    run(cmd)


def join(out_dir, clips):
    os.makedirs(out_dir, exist_ok=True)
    durs = [duration(c) for c in clips]
    audio = all(has_audio(c) for c in clips)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning"]
    for c in clips:
        cmd += ["-i", c]
    fv, fa = [], []
    v, a, t = "0:v", "0:a", durs[0]
    for i in range(1, len(clips)):
        off = t - FADE
        fv.append(f"[{v}][{i}:v]xfade=transition=fade:duration={FADE}:offset={off:.3f}[v{i}]")
        fa.append(f"[{a}][{i}:a]acrossfade=d={FADE}[a{i}]")
        v, a = f"v{i}", f"a{i}"
        t = off + durs[i]
    # fade in from black and out at the end so the loop on the page reads as one piece
    fv.append(f"[{v}]fade=t=in:d=0.4,fade=t=out:st={t - 0.6:.3f}:d=0.6[vout]")
    graph = ";".join(fv + (fa + [f"[{a}]afade=t=in:d=0.4,afade=t=out:st={t - 0.8:.3f}:d=0.8[aout]"] if audio else []))
    cmd += ["-filter_complex", graph, "-map", "[vout]"]
    cmd += (["-map", "[aout]", "-c:a", "aac", "-b:a", "160k"] if audio else ["-an"])
    trailer = os.path.join(out_dir, "trailer.mp4")
    run(cmd + X264 + ["-movflags", "+faststart", trailer])
    # stills: one from each clip, and the poster from the first clip once the race is moving
    for i, c in enumerate(clips):
        at = durs[i] * (0.8 if i == 0 else 0.55)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-ss", f"{at:.2f}", "-i", c, "-frames:v", "1", "-update", "1",
             "-q:v", "3", os.path.join(out_dir, f"shot-{i + 1}.jpg")])
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-ss", f"{durs[0] * 0.8:.2f}", "-i", clips[0],
         "-frames:v", "1", "-update", "1", "-q:v", "2", os.path.join(out_dir, "poster.jpg")])
    print(f"trailer {t:.1f} s from {len(clips)} clips, audio: {audio}")


if __name__ == "__main__":
    if sys.argv[1] == "one":
        one(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        join(sys.argv[2], sys.argv[3:])
