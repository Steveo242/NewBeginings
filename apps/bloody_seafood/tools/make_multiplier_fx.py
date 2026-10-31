"""Bloody Seafood - global-multiplier sounds: one per step up, and the reset.

    python3 make_multiplier_fx.py <out_dir>

Writes <out_dir>/sfx_mult_up_1..6.wav and sfx_mult_down.wav (mono, 44.1 kHz). Original,
2026-10-31: MIDI rendered through FluidR3_GM (MIT) with fluidsynth, plus synthesis.

  UP   a ship's bell struck with a short rising brass stab (fifth -> octave, D) on top and a
       chain-ratchet clicking under it. Each step up is a semitone higher (the ratchet a
       little faster too), capped at the 6th step - the climb is audible without the 6th
       step turning into a squeak.
  DOWN the reset: a low hull thud, a gong whose pitch sags, and a groan of timber sliding
       down under it - heavy, short, and dark enough to sit under the music.
Peaks at -3 dBFS; the game's mix sets their level.
"""
import os
import subprocess
import sys

import mido
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample, sosfilt

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
TPB = 480
rng = np.random.default_rng(31)
STEPS = 6


def midi_render(name, notes, program, bpm=120):
    """notes: [(start_beats, midi_note, dur_beats, vel)] on one instrument -> mono float."""
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    ev = [(0, mido.Message("program_change", program=program, channel=0)),
          (0, mido.Message("control_change", control=91, value=30, channel=0))]
    for s, n, d, v in notes:
        ev.append((int(s * TPB), mido.Message("note_on", note=n, velocity=v, channel=0)))
        ev.append((int((s + d) * TPB), mido.Message("note_off", note=n, velocity=0, channel=0)))
    last = 0
    for t, m in sorted(ev, key=lambda e: (e[0], e[1].type == "note_on")):
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


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "lowpass", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def bell(f0, dur=1.6):
    """A ship's bell: inharmonic partials (hum, prime, minor third, fifth, nominal...),
    each decaying at its own rate, with a bright strike transient."""
    t = np.arange(int(dur * SR)) / SR
    parts = [(0.5, 0.35, 1.2), (1.0, 1.0, 0.9), (1.19, 0.55, 0.7), (1.5, 0.35, 0.55),
             (2.0, 0.6, 0.45), (2.52, 0.3, 0.3), (2.98, 0.25, 0.22), (4.07, 0.15, 0.12)]
    x = sum(a * np.exp(-t / d) * np.sin(2 * np.pi * f0 * r * t * (1 + 0.0007 * np.sin(2 * np.pi * 5 * t)))
            for r, a, d in parts)
    strike = bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t / 0.006) * 0.6
    return (x + strike) * (1 - np.exp(-t / 0.0015))


def ratchet(n_clicks, rate, pitch):
    """A chain ratchet: metallic clicks (resonant noise ticks), a pawl's rhythm."""
    out = np.zeros(int(SR * (n_clicks / rate + 0.2)))
    for i in range(n_clicks):
        s = max(0, int(i / rate * SR + rng.uniform(-0.003, 0.003) * SR))
        n = int(0.05 * SR); t = np.arange(n) / SR
        tick = bp(rng.standard_normal(n), 1800 * pitch, 5200 * pitch) * np.exp(-t / 0.006)
        ring = np.sin(2 * np.pi * 3100 * pitch * t) * np.exp(-t / 0.02) * 0.25
        out[s:s + n] += (tick + ring) * (0.6 + 0.4 * i / max(1, n_clicks - 1))
    return out


def norm(x, peak_db=-3.0):
    x = sosfilt(butter(2, 40, "highpass", fs=SR, output="sos"), x)
    return (x * 10 ** (peak_db / 20) / np.abs(x).max()).astype(np.float32)


def place(dst, x, at):
    s = int(at * SR)
    dst[s:s + len(x)] += x[:len(dst) - s]


# ---------------------------------------------------------------- UP, one per step
for k in range(1, STEPS + 1):
    up = k - 1                                                  # semitones above the first step
    # brass stab: D4+A4 then D5 (fifth -> octave), short and punchy
    stab = midi_render("stab", [(0, 62 + up, 0.22, 112), (0, 69 + up, 0.22, 104),
                                (0.25, 74 + up, 0.6, 120), (0.25, 62 + up, 0.6, 100)], 61, bpm=150)
    b = bell(587.33 * 2 ** (up / 12))                           # D5 bell
    r = ratchet(4 + k // 2, 26 + 3 * k, 2 ** (up / 12))
    x = np.zeros(int(1.8 * SR))
    place(x, r * 1.2, 0.0)                                      # the chain takes up first...
    place(x, b * 0.12, 0.09)                                    # ...the bell strikes on the catch
    place(x, stab[:int(1.7 * SR)] * 1.6, 0.09)  # bell, stab and chain within ~2 dB of each other
    fade = np.ones(len(x)); fade[-int(0.3 * SR):] = np.linspace(1, 0, int(0.3 * SR))
    wavfile.write(os.path.join(OUT, f"sfx_mult_up_{k}.wav"), SR, norm(x * fade))

# ---------------------------------------------------------------- DOWN, the reset
dur = 1.9
t = np.arange(int(dur * SR)) / SR
# hull thud: a sine whose pitch drops 80 -> 42 Hz, plus a dark noise knock
f = 42 + 38 * np.exp(-t / 0.12)
thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
knock = lp(rng.standard_normal(len(t)), 400, 4) * np.exp(-t / 0.04) * 0.8
# gong: inharmonic partials around 110 Hz sagging a quarter-tone
sag = 1 - 0.03 * (1 - np.exp(-t / 0.6))
gong = sum(a * np.exp(-t / d) * np.sin(2 * np.pi * 110 * r * np.cumsum(sag) / SR)
           for r, a, d in [(1.0, 1.0, 1.0), (1.48, 0.5, 0.7), (2.13, 0.35, 0.5), (2.74, 0.25, 0.35), (3.6, 0.12, 0.25)])
gong *= 1 - np.exp(-t / 0.01)
# groan: a buzzy tone sliding 70 -> 46 Hz through a low-pass, swelling then dying
gf = 70 - 24 * np.clip(t / 1.4, 0, 1)
saw = 2 * ((np.cumsum(gf) / SR) % 1) - 1
groan = lp(saw * (1 + 0.15 * np.sin(2 * np.pi * 7 * t)), 260, 4)
groan *= np.sin(np.pi * np.clip(t / 1.7, 0, 1)) ** 1.5 * 0.5
x = thud * 1.0 + knock + gong * 0.9 + groan       # gong up: phone speakers lose the thud
x *= np.minimum(1, (dur - t) / 0.25)
wavfile.write(os.path.join(OUT, "sfx_mult_down.wav"), SR, norm(lp(x, 3000)))
print("wrote", STEPS, "up steps + down to", OUT)
