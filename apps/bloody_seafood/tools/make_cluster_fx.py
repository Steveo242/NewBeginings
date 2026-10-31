"""Bloody Seafood - cluster-win sounds, synthesised from scratch (no samples).

    python3 make_cluster_fx.py [out_dir]

sfx_cluster_hit_{1,2,3}   the moment a cluster wins: a deep bass thump, a bright brass
                          "ching" (inharmonic struck-metal partials) and a small wet slap
                          - the reward. ~0.55 s.
sfx_cluster_burst_{1,2,3} the winning symbols bursting (build_explode_v2.py's blood-burst):
                          a wet, punchy splat/squelch over a short water splash with
                          droplet spatters. ~0.45 s, attack under 5 ms so it lands with
                          the burst's first frame.
sfx_btn_spin              the spin button: a heavy ship-metal clank - an iron latch thrown /
                          anchor-chain link hit: sharp transient, inharmonic iron partials,
                          a short ring-out (~0.4 s) over a low thud.
Three variants each with slightly different pitch, timing and noise, so a long cascade
never repeats the same sound. Mono 44.1 kHz WAVs, RMS-matched to RMS_TARGET (the median of
the game's existing SFX) with peaks soft-limited under 0.95.
"""
import os
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
RMS_TARGET = 0.27  # first 250 ms, like the existing hits (tumble_win_1 0.11, explosion_b 0.33, premium_land 0.32)


def band(x, lo=None, hi=None, order=4):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def t(dur):
    return np.arange(int(dur * SR)) / SR


def place(buf, x, at):
    i = int(at * SR)
    buf[i:i + len(x)] += x[:max(0, len(buf) - i)]


def finish(x):
    x = x - np.mean(x)
    fade = int(0.01 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)
    x *= RMS_TARGET / np.sqrt(np.mean(x[: int(0.25 * SR)] ** 2) + 1e-12)
    peak = np.max(np.abs(x))
    if peak > 0.95:
        x = np.tanh(x / peak * 1.4) / np.tanh(1.4) * 0.95
    return x


def hit(seed):
    rng = np.random.default_rng(seed)
    p = 2 ** (rng.uniform(-1.5, 1.5) / 12)
    out = np.zeros(int(0.6 * SR))
    # bass thump: pitch-dropping sine with a hard click
    tt = t(0.32)
    f = (52 + 70 * np.exp(-tt * 30)) * p
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 11)
    thump[: int(0.003 * SR)] += rng.standard_normal(int(0.003 * SR)) * 0.6
    place(out, np.tanh(1.8 * thump) * 0.9, 0.0)
    # brass ching: inharmonic struck-metal partials, bright and short, a little shimmer
    tt = t(0.55)
    base = 1180 * p
    ching = np.zeros_like(tt)
    for ratio, amp, dec in ((1.0, 1.0, 7), (2.32, 0.6, 9), (3.98, 0.4, 12), (5.41, 0.25, 15), (8.17, 0.15, 20)):
        ching += amp * np.sin(2 * np.pi * base * ratio * tt * (1 + 0.002 * np.sin(2 * np.pi * 6 * tt)) + rng.uniform(0, 6.3)) * np.exp(-tt * dec)
    ching += band(rng.standard_normal(len(tt)), 5000, 12000) * np.exp(-tt * 60) * 0.5  # strike
    place(out, ching * 0.32, 0.008)
    # wet slap under it
    tt = t(0.12)
    slap = band(rng.standard_normal(len(tt)), 300, 2500) * np.exp(-tt * 45)
    place(out, slap * 0.5, 0.0)
    return finish(out)


def burst(seed):
    rng = np.random.default_rng(seed)
    p = 2 ** (rng.uniform(-2, 2) / 12)
    out = np.zeros(int(0.48 * SR))
    # splat: a low wet body (resonant thud with a fast pitch fall) and a squelch (band-swept noise)
    tt = t(0.22)
    f = (95 + 160 * np.exp(-tt * 40)) * p
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 16)
    place(out, np.tanh(2.2 * body) * 0.8, 0.0)
    tt = t(0.2)
    noise = rng.standard_normal(len(tt))
    squelch = np.zeros_like(tt)
    seg = 512
    for i in range(0, len(tt), seg):  # the band sweeps down: the wet "chlk"
        u = i / len(tt)
        lo = (1800 - 1400 * u) * p
        squelch[i:i + seg] = band(noise[i:i + seg + 256], lo, lo * 2.4, order=2)[:len(squelch[i:i + seg])]
    squelch *= np.exp(-tt * 18) * (1 + 0.6 * np.sin(2 * np.pi * 38 * tt))
    place(out, squelch * 0.9, 0.0)
    # water splash: bright hiss with a soft tail
    tt = t(0.45)
    splash = band(rng.standard_normal(len(tt)), 2500, 11000) * (np.exp(-tt * 9) * (1 - np.exp(-tt * 300)))
    place(out, splash * 0.35, 0.01)
    # droplet spatters: tiny pitched blips scattered after the hit
    for _ in range(9):
        at = rng.uniform(0.04, 0.32)
        tt = t(0.03)
        fr = rng.uniform(1400, 3200) * p
        blip = np.sin(2 * np.pi * fr * tt * (1 + 2.5 * tt)) * np.exp(-tt * 140)
        place(out, blip * rng.uniform(0.08, 0.2), at)
    return finish(out)


def clank():
    rng = np.random.default_rng(42)
    out = np.zeros(int(0.45 * SR))
    tt = t(0.45)
    # iron: a dense cluster of inharmonic partials, the low ones ringing longest
    iron = np.zeros_like(tt)
    for f, amp, dec in ((212, 0.7, 9), (587, 1.0, 13), (893, 0.8, 16), (1342, 0.6, 20), (1977, 0.45, 26),
                        (2731, 0.35, 32), (3610, 0.25, 40)):
        iron += amp * np.sin(2 * np.pi * f * tt * (1 - 0.004 * tt) + rng.uniform(0, 6.3)) * np.exp(-tt * dec)
    place(out, iron * 0.35, 0.0)
    # the strike: a hard broadband click and a gritty rattle of the latch settling
    tt = t(0.02)
    place(out, band(rng.standard_normal(len(tt)), 1500, 9000) * np.exp(-tt * 250) * 1.2, 0.0)
    tt = t(0.08)
    rattle = band(rng.standard_normal(len(tt)), 2000, 6000) * np.exp(-tt * 40) * (np.sin(2 * np.pi * 55 * tt) > 0.3)
    place(out, rattle * 0.25, 0.045)
    # low thud of the heavy part landing
    tt = t(0.2)
    thud = np.sin(2 * np.pi * np.cumsum(60 + 50 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 18)
    place(out, np.tanh(2 * thud) * 0.6, 0.0)
    return finish(out)


os.makedirs(OUT, exist_ok=True)
x = clank()
wavfile.write(os.path.join(OUT, "sfx_btn_spin.wav"), SR, (x * 32767).astype(np.int16))
print("sfx_btn_spin", f"{len(x) / SR:.2f}s rms {np.sqrt(np.mean(x ** 2)):.3f}")
for i in range(3):
    for name, fn, seed in ((f"sfx_cluster_hit_{i + 1}", hit, 100 + i), (f"sfx_cluster_burst_{i + 1}", burst, 200 + i)):
        x = fn(seed)
        wavfile.write(os.path.join(OUT, name + ".wav"), SR, (x * 32767).astype(np.int16))
        print(name, f"{len(x) / SR:.2f}s rms {np.sqrt(np.mean(x ** 2)):.3f} peak {np.max(np.abs(x)):.2f}")
