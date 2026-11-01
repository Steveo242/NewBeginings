"""Bloody Seafood - special landings and the anticipation heartbeat.

    python3 make_landing_fx.py <out_dir>

Writes (mono, 44.1 kHz, peaks -3 dBFS; the game's mix sets their level). Original,
2026-11-01: MIDI rendered through FluidR3_GM (MIT) with fluidsynth, plus synthesis.

  sfx_anchor_land_1..3  the SCATTER anchor hitting the board: a deep iron CLANG (struck
                        tubular bell + an inharmonic modal clang), a chain rattling out
                        after it, timpani and taiko under it and a low boom tail. Each
                        further anchor in a spin is two semitones higher, heavier and longer.
  sfx_wild_land         the BS wild: a sharp crack (side stick + clap), a dark sub thump,
                        and a short wet blood-splatter squelch - nothing like the anchor.
  sfx_heartbeat         a 4-beat lub-dub loop on the game's 90 BPM pulse (kick + taiko
                        through a low-pass) - faded up under the rope while a reel anticipates.
  sfx_antic_miss        the anticipation missing: a trombone sagging down a fourth, quick.
"""
import os
import subprocess
import sys

import mido
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
TPB = 480
rng = np.random.default_rng(1101)


def midi_render(name, tracks, bpm=120, bend=None):
    """tracks: [(program, channel, [(start_beats, note, dur_beats, vel)])] -> mono float.
    bend: [(beats, value -8192..8191)] pitch-wheel events on channel 0."""
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    ev = []
    for prog, ch, notes in tracks:
        if ch != 9:
            ev.append((0, mido.Message("program_change", program=prog, channel=ch)))
        ev.append((0, mido.Message("control_change", control=91, value=40, channel=ch)))
        for s, n, d, v in notes:
            ev.append((int(s * TPB), mido.Message("note_on", note=n, velocity=v, channel=ch)))
            ev.append((int((s + d) * TPB), mido.Message("note_off", note=n, velocity=0, channel=ch)))
    for s, v in bend or []:
        ev.append((int(s * TPB), mido.Message("pitchwheel", pitch=v, channel=0)))
    last = 0
    order = {"program_change": 0, "control_change": 1, "pitchwheel": 2, "note_off": 3, "note_on": 4}
    for t, m in sorted(ev, key=lambda e: (e[0], order[e[1].type])):
        tr.append(m.copy(time=t - last)); last = t
    tr.append(mido.MetaMessage("end_of_track", time=TPB * 4))
    p = os.path.join(OUT, f"_{name}.mid"); w = p[:-4] + ".wav"
    mid.save(p)
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", str(SR), "-R", "1", "-C", "0", "-F", w, SF2, p],
                   check=True, capture_output=True)
    _, x = wavfile.read(w)
    os.remove(p); os.remove(w)
    x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
    return x.mean(1) if x.ndim == 2 else x


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def place(dst, x, at):
    s = int(at * SR)
    dst[s:s + len(x)] += x[:max(0, len(dst) - s)]


def norm(x, peak_db=-3.0):
    x = filt(x, "highpass", 30)
    f = int(0.03 * SR); x[-f:] *= np.linspace(1, 0, f)
    return (x * 10 ** (peak_db / 20) / np.abs(x).max()).astype(np.float32)


def clang(f0, dur):
    """struck iron: inharmonic partials with their own decays, a hard strike on top"""
    t = tt(dur)
    parts = [(1.0, 1.0, 0.9), (2.32, 0.6, 0.55), (3.17, 0.45, 0.4), (4.46, 0.3, 0.28),
             (5.92, 0.2, 0.2), (7.41, 0.12, 0.14)]
    x = sum(a * np.exp(-t / d) * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) for r, a, d in parts)
    strike = filt(rng.standard_normal(len(t)), "bandpass", [1200, 7000]) * np.exp(-t / 0.004) * 0.7
    return (x + strike) * (1 - np.exp(-t / 0.001))


def chain(n, rate, pitch, dur):
    """links rattling out: resonant metallic ticks, slowing and fading"""
    out = np.zeros(int(dur * SR)); at = 0.0
    for i in range(n):
        at += (1 / rate) * (1 + 0.6 * i / n) * rng.uniform(0.8, 1.2)
        k = int(0.04 * SR); t = tt(0.04)
        tick = filt(rng.standard_normal(k), "bandpass", [2000 * pitch, 6500 * pitch]) * np.exp(-t / 0.005)
        ring = np.sin(2 * np.pi * rng.uniform(2600, 3600) * pitch * t) * np.exp(-t / 0.015) * 0.35
        place(out, (tick + ring) * (1 - i / n) ** 1.3, at)
    return out


def boom(f_hi, f_lo, dur):
    t = tt(dur)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / 0.18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * 0.4)) * (1 - np.exp(-t / 0.003))


# ---------------------------------------------------------------- the anchor, 1st..3rd
for k in (1, 2, 3):
    up = 2 * (k - 1)
    dur = 1.5 + 0.25 * k
    perc = midi_render("anchor", [
        (14, 0, [(0, 40 + up, 3, 120)]),                          # tubular bell, low E
        (47, 1, [(0, 40 + up, 1, 124)] + ([(0, 33 + up, 1, 110)] if k > 1 else [])),   # timpani
        (116, 2, [(0, 36 + up, 1, 127)]),                         # taiko
    ])
    x = np.zeros(int(dur * SR))
    place(x, perc[:len(x)] * 1.3, 0.0)
    place(x, clang(98 * 2 ** (up / 12), dur) * 0.55, 0.0)
    place(x, chain(9 + 3 * k, 30, 2 ** (up / 12), dur) * (0.5 + 0.1 * k), 0.07)
    place(x, boom(90 + 6 * up, 34 + up, dur) * (0.7 + 0.15 * k), 0.0)
    x *= np.minimum(1, (dur - tt(dur)) / 0.3)
    wavfile.write(os.path.join(OUT, f"sfx_anchor_land_{k}.wav"), SR, norm(filt(x, "lowpass", 9000)))

# ---------------------------------------------------------------- the wild
dur = 0.85
crack = midi_render("wild", [(0, 9, [(0, 37, 0.3, 127), (0, 39, 0.3, 118)]),
                             (116, 0, [(0, 31, 0.5, 120)])])
x = np.zeros(int(dur * SR))
place(x, crack[:len(x)] * 1.2, 0.0)
place(x, boom(70, 30, 0.6) * 1.0, 0.0)                            # dark sub thump
# wet splatter: a squelch whose band sweeps down, then a few droplets pattering after
sq = rng.standard_normal(int(0.22 * SR)); out = np.zeros_like(sq); seg = 441
for j in range(0, len(sq), seg):
    u = j / len(sq); lo = 1800 - 1300 * u
    out[j:j + seg] = filt(sq[j:j + seg + 300], "bandpass", [lo, lo * 2.2])[:len(out[j:j + seg])]
place(x, out * np.exp(-tt(0.22) * 9) * 0.55, 0.012)
for i in range(6):
    n = int(0.03 * SR)
    d = filt(rng.standard_normal(n), "bandpass", [900, 3000]) * np.exp(-tt(0.03) / 0.006)
    place(x, d * rng.uniform(0.15, 0.3), 0.12 + i * rng.uniform(0.04, 0.07))
wavfile.write(os.path.join(OUT, "sfx_wild_land.wav"), SR, norm(x))

# ---------------------------------------------------------------- heartbeat loop
beat = 60 / 90; dur = 4 * beat
hb = midi_render("hb", [(0, 9, [(b, 36, 0.2, 120) for b in range(4)] + [(b + 0.28, 35, 0.2, 96) for b in range(4)]),
                        (116, 0, [(b, 31, 0.3, 100) for b in range(4)])], bpm=90)
x = np.zeros(int(dur * SR))
place(x, hb[:len(x)], 0.0)
tail = hb[len(x):len(x) + int(0.4 * SR)]                           # wrap the ring-out to the top
place(x, tail, 0.0)
x = filt(x, "lowpass", 900, 4)
x = filt(x, "highpass", 30)
wavfile.write(os.path.join(OUT, "sfx_heartbeat.wav"), SR, (x * 10 ** (-3 / 20) / np.abs(x).max()).astype(np.float32))

# ---------------------------------------------------------------- the miss: deflate
tb = midi_render("miss", [(57, 0, [(0, 55, 0.9, 110)])], bpm=120,
                 bend=[(0, 0)] + [(0.1 + i * 0.05, -int(8191 * min(1, i / 14) ** 1.4)) for i in range(15)])
x = tb[:int(0.9 * SR)].copy()
wavfile.write(os.path.join(OUT, "sfx_antic_miss.wav"), SR, norm(x, -4.0))
print("wrote anchor 1-3, wild, heartbeat, miss to", OUT)
