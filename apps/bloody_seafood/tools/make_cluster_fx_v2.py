"""Bloody Seafood - cluster-win and spin sounds v2 (replaces make_cluster_fx.py's v1).

    python3 make_cluster_fx_v2.py <out_dir>

v1 was raw synthesis pushed into a soft limiter (peaks pinned at 0.95, audible
saturation) and the burst leaned on bright broadband noise. v2:
  sfx_cluster_hit_{1,2,3}   the reward, rendered from MIDI through FluidR3_GM (MIT) with
                            fluidsynth: a timpani hit on D, a short brass-section stab on a
                            D minor chord (in the music's key) and a glockenspiel sparkle -
                            three voicings so cascades don't repeat
  sfx_cluster_burst_{1,2,3} the wet splat, synthesised cleanly: a low resonant body thud, a
                            band-limited (300 Hz-3 kHz) squelch sweep, a soft low-passed splash
                            (under 5 kHz) and sine droplet blips - no hiss above 6 kHz
  sfx_btn_spin              the iron clank: inharmonic metal partials over a low thud with a
                            short band-limited strike
Every sound is peak-normalised to -1 dBFS with no limiting or clipping, then scaled down if
its RMS (first 250 ms) would exceed the game's other hits.
"""
import os
import subprocess
import sys

import mido
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
PEAK = 10 ** (-1 / 20)
RMS_MAX = 0.2
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(31)


def band(x, lo=None, hi=None, order=4):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def t(d):
    return np.arange(int(d * SR)) / SR


def place(buf, x, at):
    i = int(at * SR)
    buf[i:i + len(x)] += x[:max(0, len(buf) - i)]


def level(x, dur):
    x = x[: int(dur * SR)].astype(np.float64)
    x -= x.mean()
    f = int(0.015 * SR)
    x[-f:] *= np.linspace(1, 0, f)
    x *= PEAK / np.max(np.abs(x))
    r = np.sqrt(np.mean(x[: int(0.25 * SR)] ** 2))
    if r > RMS_MAX:
        x *= RMS_MAX / r
    return x


def write(name, x):
    wavfile.write(os.path.join(OUT, name + ".wav"), SR, (x * 32767).astype(np.int16))
    print(f"{name}: {len(x) / SR:.2f}s peak {np.max(np.abs(x)):.2f} rms {np.sqrt(np.mean(x[:11025] ** 2)):.3f}")


# ------------------------------------------------------------------ hit: MIDI -> fluidsynth
VOICINGS = [(62, 65, 69, 74), (65, 69, 74, 77), (57, 62, 65, 69)]  # Dm, Dm 1st inv, Dm low
for i, chord in enumerate(VOICINGS):
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))
    ev = [(0, mido.Message("program_change", program=47, channel=0)),   # timpani
          (0, mido.Message("program_change", program=61, channel=1)),   # brass section
          (0, mido.Message("program_change", program=9, channel=2)),    # glockenspiel
          (0, mido.Message("note_on", note=38, velocity=120, channel=0)),
          (300, mido.Message("note_off", note=38, velocity=0, channel=0))]
    for n in chord:
        ev += [(0, mido.Message("note_on", note=n, velocity=112, channel=1)),
               (150, mido.Message("note_off", note=n, velocity=0, channel=1))]
    for k, n in enumerate((chord[-1] + 12, chord[-1] + 19)):
        ev += [(40 + 30 * k, mido.Message("note_on", note=n, velocity=96, channel=2)),
               (400, mido.Message("note_off", note=n, velocity=0, channel=2))]
    last = 0
    for tk, m in sorted(ev, key=lambda e: (e[0], e[1].type != "program_change", e[1].type == "note_on")):
        tr.append(m.copy(time=tk - last)); last = tk
    tr.append(mido.MetaMessage("end_of_track", time=480))
    mpath = os.path.join(OUT, f"hit_{i + 1}.mid"); wpath = os.path.join(OUT, f"hit_{i + 1}_raw.wav")
    mid.save(mpath)
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", str(SR), "-R", "1", "-C", "0", "-F", wpath, SF2, mpath],
                   check=True, capture_output=True)
    sr, x = wavfile.read(wpath)
    x = x.astype(np.float64).mean(1) / 32768
    # a short wet slap under the stab (band-limited, quiet)
    slap = band(rng.standard_normal(int(0.08 * SR)), 300, 2200) * np.exp(-t(0.08) * 50) * 0.08
    place(x, slap, 0.0)
    write(f"sfx_cluster_hit_{i + 1}", level(x, 0.6))


# ------------------------------------------------------------------ burst: clean synthesis
for i in range(3):
    p = 2 ** ((i - 1) * 1.5 / 12)
    out = np.zeros(int(0.48 * SR))
    tt = t(0.24)
    f = (90 + 150 * np.exp(-tt * 38)) * p
    place(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 15) * 0.9, 0.0)        # body thud
    tt = t(0.18)
    noise = rng.standard_normal(len(tt))
    sq = np.zeros_like(tt)
    seg = 441
    for j in range(0, len(tt), seg):                                                          # squelch sweep
        u = j / len(tt)
        lo = (1500 - 1100 * u) * p
        sq[j:j + seg] = band(noise[j:j + seg + 200], lo, min(lo * 2.0, 3000), order=2)[: len(sq[j:j + seg])]
    place(out, sq * np.exp(-tt * 20) * 0.55, 0.002)
    tt = t(0.42)
    splash = band(band(rng.standard_normal(len(tt)), 600, None), None, 4500) * np.exp(-tt * 10) * (1 - np.exp(-tt * 200))
    place(out, splash * 0.16, 0.012)                                                          # soft splash
    for _ in range(8):                                                                        # droplets
        tt = t(0.035)
        fr = rng.uniform(900, 2200) * p
        place(out, np.sin(2 * np.pi * fr * tt * (1 + 3 * tt)) * np.exp(-tt * 110) * rng.uniform(0.12, 0.25),
              rng.uniform(0.05, 0.3))
    write(f"sfx_cluster_burst_{i + 1}", level(out, 0.48))


# ------------------------------------------------------------------ spin: the iron clank
out = np.zeros(int(0.45 * SR))
tt = t(0.45)
iron = sum(a * np.sin(2 * np.pi * f * tt + rng.uniform(0, 6.3)) * np.exp(-tt * d)
           for f, a, d in ((212, 0.7, 9), (587, 1.0, 13), (893, 0.8, 16), (1342, 0.6, 20), (1977, 0.4, 26), (2731, 0.25, 32)))
place(out, iron * 0.35, 0.0)
tt = t(0.015)
place(out, band(rng.standard_normal(len(tt)), 1500, 6000) * np.exp(-tt * 300) * 0.6, 0.0)
tt = t(0.2)
place(out, np.sin(2 * np.pi * np.cumsum(60 + 50 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 18) * 0.6, 0.0)
write("sfx_btn_spin", level(out, 0.45))
