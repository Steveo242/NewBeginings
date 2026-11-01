"""Cut a licensed track into the bonus music's two loops: the calm intro and the main loop.

    python3 cut_bonus_music.py <src> <out_dir> <bpm> <phase_s> <intro_a> <intro_b> <drop> <end|rotate> <intro_lufs> <main_lufs>

Beats are counted on the grid phase_s + k * 60 / bpm (both measured from the track's
onsets). Writes out_dir/intro.wav and out_dir/main.wav, mono 44.1 kHz float:
- intro: beats intro_a..intro_b, the calm section, looping until the first free spin
- main: starts on the drop's downbeat (beat `drop`), so the game's cut lands on the hit.
  With an end beat, it runs drop..end and wraps back to the drop; `rotate` is for a source
  that already loops seamlessly end to start (the composer's own loop file): the whole loop,
  rotated to start at the drop
- each cut sits 4 ms ahead of the attack found near its grid beat, so no transient is
  chopped; a loop's last 40 ms crossfade into the audio that led into its first beat, so
  the wrap is seamless (no click, no gap)
- a fixed gain per clip sets its integrated loudness (ffmpeg ebur128); nothing clips
"""
import os
import re
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

SR = 44100
src, out_dir = sys.argv[1:3]
bpm, phase = float(sys.argv[3]), float(sys.argv[4])
intro_a, intro_b, drop = (int(v) for v in sys.argv[5:8])
end = sys.argv[8]
intro_lufs, main_lufs = float(sys.argv[9]), float(sys.argv[10])
XF = int(0.04 * SR)

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).astype(np.float64)


def attack(beat):
    """Sample 4 ms ahead of the attack within 40 ms of the grid beat."""
    t = int(round((phase + beat * 60 / bpm) * SR))
    w = int(0.002 * SR)
    seg = x[t - int(0.04 * SR):t + int(0.04 * SR)]
    e = np.convolve(seg ** 2, np.ones(w) / w, "same")
    hit = np.argmax(e > 0.3 * e.max())
    return t - int(0.04 * SR) + hit - int(0.004 * SR)


def loop(a, b):
    """x[a:b] whose tail crossfades (equal power) into what led into a."""
    y = x[a:b].copy()
    f = np.linspace(0, np.pi / 2, XF)
    y[-XF:] = x[b - XF:b] * np.cos(f) + x[a - XF:a] * np.sin(f)
    return y


def lufs(y):
    tmp = os.path.join(out_dir, "_m.wav")
    wavfile.write(tmp, SR, y.astype(np.float32))
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", tmp, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    os.remove(tmp)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])


os.makedirs(out_dir, exist_ok=True)
intro = loop(attack(intro_a), attack(intro_b))
d = attack(drop)
if end == "rotate":
    main = np.concatenate([x[d:], x[:d]])
else:
    main = loop(d, attack(int(end)))
for name, y, target in (("intro", intro, intro_lufs), ("main", main, main_lufs)):
    y = y * 10 ** ((target - lufs(y)) / 20)
    peak = np.abs(y).max()
    assert peak < 0.95, (name, peak)
    wavfile.write(os.path.join(out_dir, name + ".wav"), SR, y.astype(np.float32))
    print(f"{name}: {len(y) / SR:.3f} s, {lufs(y):.1f} LUFS, peak {20 * np.log10(peak):.1f} dBFS")
