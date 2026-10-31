"""Bloody Seafood - big-win stingers, one per celebration tier, climbing with it.

    python3 make_bigwin_stingers.py <out_dir>

Writes sfx_stinger_big/superwin/mega/epic/max.wav (mono, 44.1 kHz). Original, 2026-10-31:
MIDI rendered through FluidR3_GM (MIT) with fluidsynth, plus a synthesised splash.

Every tier is the same idea, made bigger: a timpani hit and a brass-section chord stab in
D minor (the bonus music's key), answered by a held chord. Climbing the tiers adds
trombones an octave down, then choir, then crash cymbals and a timpani roll, and the
chord rises (Dm -> F -> Bb -> D major for MAX, the one bright tier). Each opens with a
low-passed water splash so it ties to the blood-and-water sweep on screen. Peaks -3 dBFS.
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
BPM = 120
rng = np.random.default_rng(7)


def render(parts, beats):
    """parts: [(program or None for drums, [(beat, note, dur_beats, vel)])] -> mono float."""
    mid = mido.MidiFile(ticks_per_beat=TPB)
    for ch_i, (prog, notes) in enumerate(parts):
        ch = 9 if prog is None else ch_i
        tr = mido.MidiTrack(); mid.tracks.append(tr)
        ev = [(0, mido.Message("control_change", control=91, value=45, channel=ch))]
        if ch_i == 0:
            tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
        if prog is not None:
            ev.append((0, mido.Message("program_change", program=prog, channel=ch)))
        for b, n, d, v in notes:
            ev.append((int(b * TPB), mido.Message("note_on", note=n, velocity=v, channel=ch)))
            ev.append((int((b + d) * TPB), mido.Message("note_off", note=n, velocity=0, channel=ch)))
        last = 0
        for t, m in sorted(ev, key=lambda e: (e[0], e[1].type == "note_on")):
            tr.append(m.copy(time=t - last)); last = t
        tr.append(mido.MetaMessage("end_of_track", time=int(beats * TPB)))
    p = os.path.join(OUT, "_s.mid"); w = os.path.join(OUT, "_s.wav")
    mid.save(p)
    subprocess.run(["fluidsynth", "-ni", "-g", "0.5", "-r", str(SR), "-R", "1", "-C", "0", "-F", w, SF2, p],
                   check=True, capture_output=True)
    _, x = wavfile.read(w)
    os.remove(p); os.remove(w)
    x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
    return x.mean(1) if x.ndim == 2 else x


def splash(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = sosfilt(butter(2, [250, 3500], "bandpass", fs=SR, output="sos"), x)
    env = (1 - np.exp(-t / 0.008)) * np.exp(-t / 0.22)
    drops = np.zeros(n)
    for _ in range(18):
        s = int(rng.uniform(0.05, 0.7) * SR); m = int(0.03 * SR)
        tt = np.arange(m) / SR
        drops[s:s + m] += np.sin(2 * np.pi * rng.uniform(600, 1400) * tt * (1 + 2 * tt)) * np.exp(-tt / 0.008) * rng.uniform(0.1, 0.3)
    return x / np.abs(x).max() * env + drops


TIERS = {
    #          chord (stab)       held chord        extra layers                 length (beats)
    "big":      ((62, 65, 69), (50, 57, 62, 65), set(), 3.0),
    "superwin": ((65, 69, 72), (53, 60, 65, 69), {"trombone"}, 3.5),
    "mega":     ((70, 74, 77), (46, 53, 58, 62), {"trombone", "choir"}, 4.0),
    "epic":     ((70, 74, 77, 82), (46, 53, 58, 62, 65), {"trombone", "choir", "cymbal"}, 4.5),
    "max":      ((74, 78, 81, 86), (50, 57, 62, 66, 69), {"trombone", "choir", "cymbal", "roll"}, 5.5),
}

for name, (stab, held, extra, beats) in TIERS.items():
    lvl = list(TIERS).index(name)
    v = 100 + lvl * 6
    brass = [(0.0, n, 0.35, v) for n in stab] + [(0.5, n, beats - 1.0, v - 14) for n in held]
    timp = [(0.0, held[0] - 12, 1.0, 120)]
    if "roll" in extra:
        timp += [(0.5 + i * 0.125, held[0] - 12, 0.125, 70 + i * 4) for i in range(12)]
        timp += [(2.0, held[0] - 12, 1.5, 127)]
    parts = [(61, brass), (47, timp)]
    if "trombone" in extra:
        parts.append((57, [(0.0, stab[0] - 12, 0.35, v), (0.5, held[0], beats - 1.0, v - 10)]))
    if "choir" in extra:
        parts.append((52, [(0.5, n + 12, beats - 0.8, 96) for n in held[1:]]))
    drums = [(0.0, 49, 1.5, 110)] if "cymbal" in extra else []
    if "cymbal" in extra:
        drums += [(0.0, 57, 1.5, 100)]
    if name == "max":
        drums += [(2.0, 49, 2.0, 120), (2.0, 52, 2.0, 100)]
    if drums:
        parts.append((None, drums))
    x = render(parts, beats + 1.5)
    sp = splash() * (0.25 + 0.05 * lvl)
    out = np.zeros(max(len(x), len(sp)))
    out[:len(x)] += x
    out[:len(sp)] += sp
    out = out[:int((beats * 60 / BPM + 1.2) * SR)]
    fade = int(0.4 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = sosfilt(butter(2, 40, "highpass", fs=SR, output="sos"), out)
    out *= 10 ** (-3 / 20) / np.abs(out).max()
    wavfile.write(os.path.join(OUT, f"sfx_stinger_{name}.wav"), SR, out.astype(np.float32))
    print(name, f"{len(out) / SR:.2f} s")
