"""Bloody Seafood - free-spins / super-spins music, composed and synthesised from scratch.

    python3 make_fs_music.py <out.wav> [ref_rms]

Original work, generated entirely by this script (no samples, no soundfonts): 160 BPM,
D minor, 32 bars (48 s) that loop seamlessly - every tail (reverb, decays) is wrapped back
onto the start. Four 8-bar sections over i-VI-VII-V (Dm Bb C A):
  A  four-on-the-floor kick, backbeat snare, 16th hats, driving distorted bass, 16th arp
  B  + syncopated brass stabs
  C  + string ostinato and tom fills, the arp climbs an octave
  D  everything, open hats, a noise riser and snare roll into the loop point
Pads and bass duck under the kick (sidechain). Mono, 44.1 kHz, normalised to ref_rms (the
base-game music's RMS) so the two sit at the same loudness.
"""
import math
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, lfilter

SR = 44100
BPM = 160
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 32
N = int(round(BARS * BAR * SR))
TAIL = int(2.5 * SR)
rng = np.random.default_rng(160)

out = sys.argv[1]
ref_rms = float(sys.argv[2]) if len(sys.argv) > 2 else 0.12

# D minor: i-VI-VII-V, two bars each
CHORDS = [(62, 65, 69), (58, 62, 65), (60, 64, 67), (57, 61, 64)]  # Dm Bb C A (MIDI)
ROOTS = [38, 34, 36, 33]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def t_at(bar, beat=0.0):
    return int(round((bar * BAR + beat * BEAT) * SR))


def chord_at(bar):
    return (bar // 2) % 4


def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x, fc):
    return x - lp(x, fc)


def saw(f, n, detune=0.0, phase=None):
    t = np.arange(n) / SR
    ph = rng.random() if phase is None else phase
    return 2 * ((f * (1 + detune) * t + ph) % 1.0) - 1


def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na)
    if na < n:
        k = min(nd, n - na)
        e[na:na + k] = np.linspace(1, s, k)
    if nr and n > nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


L = N + TAIL
drums = np.zeros(L)
bass = np.zeros(L)
arp = np.zeros(L)
brass = np.zeros(L)
strings = np.zeros(L)
fx = np.zeros(L)
kick_env = np.zeros(L)


def add(buf, at, x):
    end = min(len(buf), at + len(x))
    buf[at:end] += x[:end - at]


def kick(at):
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 9) + 0.25 * np.exp(-t * 300) * rng.standard_normal(n) * 0.3
    add(drums, at, 1.0 * np.tanh(1.6 * x))
    add(kick_env, at, np.exp(-t * 7))


def snare(at, g=0.6):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    noise = hp(rng.standard_normal(n), 1200) * np.exp(-t * 18)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    add(drums, at, g * (0.55 * noise + 0.5 * tone))


def hat(at, open_=False, g=0.16):
    n = int((0.22 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 7000) * np.exp(-t * (12 if open_ else 70))
    add(drums, at, g * x)


def tom(at, m, g=0.5):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = hz(m) * (1 + 0.5 * np.exp(-t * 20))
    add(drums, at, g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10))


def bass_note(at, m, dur):
    n = int(dur * SR)
    x = saw(hz(m), n) + 0.6 * saw(hz(m), n, 0.006) + 0.5 * np.sin(2 * np.pi * hz(m - 12) * np.arange(n) / SR)
    x = np.tanh(2.5 * x)
    x = lp(x, 700) * env_adsr(n, 0.004, 0.08, 0.7, 0.03)
    add(bass, at, 0.55 * x)


def arp_note(at, m, dur, bright):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * hz(m) * t)) * 0.6 + saw(hz(m), n, 0.003) * 0.4
    x = lp(sq, 1800 + 2600 * bright) * np.exp(-t * 14)
    add(arp, at, 0.16 * x)


def brass_stab(at, chord, dur):
    n = int(dur * SR)
    x = sum(saw(hz(m), n, d) for m in chord for d in (-0.004, 0.0, 0.005))
    x = lp(np.tanh(0.6 * x), 2600) * env_adsr(n, 0.012, 0.12, 0.45, 0.06)
    add(brass, at, 0.11 * x)


def string_note(at, m, dur, g=0.05):
    n = int(dur * SR)
    x = sum(saw(hz(m), n, d) for d in (-0.007, -0.0025, 0.0, 0.003, 0.008))
    x = lp(x, 3200) * env_adsr(n, 0.03, 0.05, 0.85, 0.05)
    add(strings, at, g * x)


for bar in range(BARS):
    sec = bar // 8           # 0 A, 1 B, 2 C, 3 D
    c = chord_at(bar)
    chord, root = CHORDS[c], ROOTS[c]
    last2 = bar >= BARS - 2
    for b in range(4):
        kick(t_at(bar, b))
        if b in (1, 3):
            snare(t_at(bar, b))
        for s in range(4):
            if s == 2 and sec == 3:
                hat(t_at(bar, b + s / 4), open_=True, g=0.12)
            else:
                hat(t_at(bar, b + s / 4), g=0.16 if s % 2 == 0 else 0.1)
    # driving 8th-note bass, octave jumps on the off-beats
    for e in range(8):
        m = root + (12 if e % 2 == 1 and e in (3, 7) else 0)
        bass_note(t_at(bar, e / 2), m, BEAT / 2 * 0.92)
    # 16th arpeggio over the chord, climbing an octave in C and D
    up = 12 if sec >= 2 else 0
    pattern = [0, 1, 2, 1, 0, 2, 1, 2]
    for s in range(16):
        m = chord[pattern[s % 8]] + 12 + up + (12 if s % 8 == 7 else 0)
        arp_note(t_at(bar, s / 4), m, BEAT / 4, bright=sec / 3)
    # brass stabs: syncopated "1 . . & . . 3 ." hits
    if sec >= 1:
        for beat_pos, dur in ((0, 0.6), (1.5, 0.35), (2.5, 0.35), (3.5, 0.3)):
            brass_stab(t_at(bar, beat_pos), [m + 12 for m in chord] if sec == 3 else list(chord), dur * BEAT * 2)
    # string ostinato: 8ths on the chord's top two notes, alternating
    if sec >= 2:
        for e in range(8):
            string_note(t_at(bar, e / 2), chord[1 + e % 2] + 12, BEAT / 2 * 0.95, g=0.045 if sec == 2 else 0.055)
        string_note(t_at(bar, 0), chord[0], BAR, g=0.03)
    # tom fill at the end of every 4th bar in C and D
    if sec >= 2 and bar % 4 == 3:
        for i, m in enumerate((50, 47, 45, 43)):
            tom(t_at(bar, 3 + i / 4), m)
    # D: snare roll + noise riser over the last two bars, into the loop point
    if last2:
        k = bar - (BARS - 2)
        for s in range(16):
            snare(t_at(bar, s / 4), g=0.18 + 0.3 * (k * 16 + s) / 32)

# riser: band-passed noise sweeping up over the last 2 bars
rs, re_ = t_at(BARS - 2), t_at(BARS)
n = re_ - rs
sweep = rng.standard_normal(n)
seg = 2048
y = np.zeros(n)
for i in range(0, n, seg):
    u = i / n
    blk = sweep[i:i + seg]
    y[i:i + seg] = hp(lp(blk, 800 + 9000 * u ** 2), 300 + 3000 * u ** 2)
fx[rs:re_] += 0.25 * y * np.linspace(0, 1, n) ** 2

# sidechain pump on everything tonal
duck = 1 - 0.55 * np.clip(kick_env, 0, 1)
bass *= duck
arp *= 0.6 + 0.4 * duck
brass *= 0.7 + 0.3 * duck
strings *= 0.5 + 0.5 * duck

# reverb on the melodic parts: an exponentially decaying noise impulse
ir_n = int(1.6 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 4.0)
ir = lp(ir, 5000)
ir /= np.sqrt((ir ** 2).sum())
wet = fftconvolve(arp * 0.8 + brass + strings, ir)[:L] * 0.35

mix = drums * 0.9 + bass + arp + brass + strings + fx + wet
# seamless loop: wrap every tail past the loop end back onto the start
loop = mix[:N].copy()
loop[:TAIL] += mix[N:N + TAIL]
loop = hp(loop, 30)
# glue: gentle bus compression via soft clip, then match the base music's RMS
loop = np.tanh(1.2 * loop / np.max(np.abs(loop))) / np.tanh(1.2)
loop *= ref_rms / np.sqrt(np.mean(loop ** 2))
peak = np.max(np.abs(loop))
if peak > 0.98:
    loop = np.tanh(loop / 0.98 * 1.1) * 0.98 / np.tanh(1.1)
wavfile.write(out, SR, (np.clip(loop, -1, 1) * 32767).astype(np.int16))
print(f"wrote {out}: {len(loop) / SR:.2f} s, rms {np.sqrt(np.mean(loop ** 2)):.4f}, peak {np.max(np.abs(loop)):.3f}")
