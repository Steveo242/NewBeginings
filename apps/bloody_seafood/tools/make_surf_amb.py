"""Bloody Seafood - harbour surf ambience (`amb_storm`), synthesised from scratch (no samples).

    python3 make_surf_amb.py <out.wav>

The old bed was a steady 14 s rain/storm loop; low-passed to kill its hiss it became a flat
"shhh" with no movement - plain noise. This one is built from what makes surf read as surf:
  - waves: each a swell (filter opening as it rises), a break (bright, fast attack) and a
    long receding wash whose fizz decays; 6-11 s apart, varied in size and brightness
  - lapping: small, darker slaps of water against the pier piles between the waves
  - a soft distant rumble so the bed never drops to silence
Every event wraps modulo the loop length, so the 48 s loop is seamless. Mono, 44.1 kHz,
~-20 dBFS RMS like the old bed, peak <= -1 dBFS; the game sets its level (Background.svelte).
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, istft, sosfiltfilt, stft

SR = 44100
L = 48 * SR
rng = np.random.default_rng(20261031)
NFFT = 2048
HOP = NFFT // 4


def shaped_noise(n, cutoff, tilt=-1.0, low=60.0):
    """Noise of n samples whose low-pass cutoff (Hz) follows cutoff(t in 0..1), with a
    spectral tilt (dB/oct, below cutoff) and a high-pass at `low`."""
    x = rng.standard_normal(n + NFFT)
    f, t, Z = stft(x, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    u = np.clip(t / (n / SR), 0, 1)
    fc = np.array([cutoff(v) for v in u])[None, :]
    F = np.maximum(f[:, None], 1.0)
    gain = (F / 500.0) ** (tilt / 6.02)                      # tilt around 500 Hz
    gain = gain / np.sqrt(1 + (F / fc) ** 6)                 # 3rd-order-ish roll-off at fc
    gain = gain / np.sqrt(1 + (low / F) ** 4)
    _, y = istft(Z * gain, SR, nperseg=NFFT, noverlap=NFFT - HOP)
    y = y[:n]
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-9)


def smooth_env(points, n):
    """Piecewise envelope from (time_fraction, level) points, eased (smoothstep)."""
    t = np.linspace(0, 1, n)
    env = np.zeros(n)
    for (a, va), (b, vb) in zip(points, points[1:]):
        m = (t >= a) & (t <= b)
        s = (t[m] - a) / max(b - a, 1e-9)
        s = s * s * (3 - 2 * s)
        env[m] = va + (vb - va) * s
    return env


def add_wrapped(buf, x, pos):
    idx = (np.arange(len(x)) + pos) % len(buf)
    np.add.at(buf, idx, x)


def wave(size, bright):
    """One wave, ~7-10 s: swell, break, wash."""
    dur = rng.uniform(7.0, 10.0) * (0.85 + 0.3 * size)
    n = int(dur * SR)
    brk = rng.uniform(0.28, 0.36)                       # where it breaks
    top = 1600 + 2600 * bright
    cut = lambda u: (350 + (top - 350) * (u / brk) ** 2.2 if u < brk          # opens on the rise
                     else 450 + (top - 450) * np.exp(-(u - brk) / 0.18))      # closes in the wash
    body = shaped_noise(n, cut, tilt=-1.5)
    env = smooth_env([(0, 0), (brk * 0.9, 0.55), (brk, 1.0), (brk + 0.06, 0.85),
                      (0.75, 0.3), (1.0, 0.0)], n)
    # the fizz: bright foam bubbling as the wash recedes, decaying, with a grainy flutter
    fizz = shaped_noise(n, lambda u: 6500, tilt=0.0, low=1800)
    grain = np.abs(shaped_noise(n, lambda u: 40, tilt=0, low=4))
    fenv = smooth_env([(0, 0), (brk, 0), (brk + 0.04, 1.0), (0.85, 0.15), (1.0, 0)], n)
    fizz *= fenv * (0.4 + 0.6 * grain / grain.max()) * 0.22 * bright
    # the break's low thump
    th = shaped_noise(n, lambda u: 180, tilt=-3, low=30)
    tenv = smooth_env([(0, 0), (brk - 0.01, 0), (brk + 0.01, 1), (brk + 0.12, 0), (1, 0)], n)
    return (body * env + fizz + th * tenv * 0.5) * size


def lap():
    """A slap of water against a pile: short, dark, a little hollow."""
    n = int(rng.uniform(0.35, 0.8) * SR)
    fc = rng.uniform(700, 1400)
    x = shaped_noise(n, lambda u: fc * (1 - 0.5 * u), tilt=-2, low=150)
    env = smooth_env([(0, 0), (0.06, 1), (0.25, 0.5), (1, 0)], n)
    return x * env


out = np.zeros(L)
# waves: random 5-8 s spacings, rescaled so they fill the loop exactly (the gap across the
# wrap is a normal one); they overlap, so one wash is still receding as the next swells
gaps = rng.uniform(5.0, 8.0, 7)
starts = np.concatenate([[0], np.cumsum(gaps * 48 / gaps.sum())[:-1]])
for s in starts:
    size = rng.uniform(0.55, 1.0)
    add_wrapped(out, wave(size, rng.uniform(0.35, 0.9)), int(s * SR))
# lapping between the waves, quieter right under a break
for s in np.cumsum(rng.uniform(0.5, 1.6, 80)):
    if s >= 48:
        break
    add_wrapped(out, lap() * rng.uniform(0.08, 0.2), int(s * SR))
# distant rumble, made loopable by crossfading its own ends
rum = shaped_noise(L + SR * 2, lambda u: 220, tilt=-3, low=25)
xf = np.linspace(0, 1, SR * 2)
loop = rum[:L].copy()
loop[:SR * 2] = rum[:SR * 2] * xf + rum[L:L + SR * 2] * (1 - xf)   # the end runs on into the start
out += loop * 0.22

out = sosfiltfilt(butter(2, 30, "highpass", fs=SR, output="sos"), out)
# the old bed's loudness (-20 dBFS RMS) so the game's levels still hold; peak <= -1 dBFS
out *= min(10 ** (-20 / 20) / np.sqrt(np.mean(out ** 2)), 10 ** (-1 / 20) / np.abs(out).max())
wavfile.write(sys.argv[1], SR, out.astype(np.float32))
print("wrote", sys.argv[1], f"{L / SR:.0f} s, rms {20 * np.log10(np.sqrt(np.mean(out ** 2))):.1f} dBFS")
