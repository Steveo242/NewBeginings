"""Render compose_fs_music.py's MIDI stems through FluidR3_GM (MIT) with fluidsynth and mix.

    python3 render_fs_music.py <stem_dir> <out.wav> <ref.wav>

- each stem rendered alone (44.1 kHz stereo, fluidsynth's own reverb on)
- non-bass parts high-passed at 140 Hz so the low end is just kick + bass, no mud
- stem gains set so the fiddle hook sits on top (checked in report(): lead vs pad energy
  in 1-4 kHz), gentle bus compression (2:1 above -18 dBFS, slow), no clipping anywhere
- the middle of the three rendered loops is kept: tails from the loop before run into it,
  so it loops seamlessly
- integrated loudness matched to ref.wav (the base music) with ffmpeg loudnorm, true peak
  capped at -1 dBTP
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
stem_dir, out, ref = sys.argv[1:4]
# v3+ compositions describe themselves in meta.json (tempo, length, gains, high-passes, which
# stems are the lead and the pad); without one, the v2 shanty's settings
META = {"bpm": 152, "bars": 24,
        "gain": {"lead": 0.6, "brass": 0.5, "chords": 0.78, "strings": 0.72, "bass": 0.85, "drums": 0.8},
        "hp": {"lead": 140, "brass": 140, "chords": 140, "strings": 140},
        "lead": ["lead"], "pad": ["chords", "strings"]}
if os.path.exists(os.path.join(stem_dir, "meta.json")):
    META = json.load(open(os.path.join(stem_dir, "meta.json")))
BPM, BARS, GAIN = META["bpm"], META["bars"], META["gain"]
LOOP = int(round(BARS * META.get("beats", 4) * 60 / BPM * SR))  # beats: crotchets a bar (3 for 6/8)


def render(name):
    wav = os.path.join(stem_dir, f"{name}.wav")
    # a stem with no MIDI is pre-rendered audio (v3's synthesised thunder)
    if os.path.exists(os.path.join(stem_dir, f"{name}.mid")):
        subprocess.run(["fluidsynth", "-ni", "-g", "0.5", "-r", str(SR), "-R", "1", "-C", "0",
                        "-F", wav, SF2, os.path.join(stem_dir, f"{name}.mid")], check=True, capture_output=True)
    sr, x = wavfile.read(wav)
    x = x.astype(np.float32) / 32768 if x.dtype == np.int16 else x.astype(np.float32)
    return x


def hp(x, fc):
    return sosfilt(butter(2, fc, "highpass", fs=SR, output="sos"), x, axis=0)


stems = {}
for name in GAIN:
    x = render(name)
    if name in META["hp"]:
        x = hp(x, META["hp"][name])
    stems[name] = x
n = min(len(x) for x in stems.values())
need = 2 * LOOP
mix = np.zeros((max(n, need), 2), np.float32)
for name, x in stems.items():
    mix[:len(x)] += GAIN[name] * x[:len(mix)]
seg = mix[LOOP:2 * LOOP].copy()

# gentle bus compression: RMS envelope, 2:1 above -18 dBFS, 30 ms attack / 250 ms release
env = np.sqrt(np.convolve((seg ** 2).mean(1), np.ones(1323) / 1323, mode="same")) + 1e-9
lvl = 20 * np.log10(env)
over = np.maximum(lvl + 18, 0)
gain_db = -over * 0.5
a_att, a_rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.25 * SR))
g = np.zeros_like(gain_db)
cur = 0.0
for i, v in enumerate(gain_db):
    cur = a_att * cur + (1 - a_att) * v if v < cur else a_rel * cur + (1 - a_rel) * v
    g[i] = cur
seg *= (10 ** (g / 20))[:, None]
seg /= np.max(np.abs(seg)) / 0.7
tmp = out + ".pre.wav"
wavfile.write(tmp, SR, seg)


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])


target = float(loudness(ref)["input_i"])
m = loudness(tmp)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                f"loudnorm=I={target}:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
                "-ar", str(SR), out], check=True)
os.remove(tmp)
f = loudness(out)
sr, y = wavfile.read(out)
y = y.astype(np.float32) / (32768 if y.dtype == np.int16 else 1)
mono = y.mean(1) if y.ndim == 2 else y
rms = np.sqrt(np.mean(mono ** 2))
print(f"ref {target} LUFS -> out {f['input_i']} LUFS, true peak {f['input_tp']} dBTP, "
      f"crest {20 * np.log10(np.max(np.abs(mono)) / rms):.1f} dB, clipped samples {(np.abs(y) >= 0.999).sum()}, "
      f"length {len(mono) / SR:.2f} s")


def band_energy(x, lo, hi):
    X = np.abs(np.fft.rfft(x.mean(1) if x.ndim == 2 else x))
    fr = np.fft.rfftfreq(len(x) if x.ndim == 1 else x.shape[0], 1 / SR)
    return 10 * np.log10((X[(fr >= lo) & (fr < hi)] ** 2).sum() + 1e-12)


sl = slice(LOOP, 2 * LOOP)
lead = band_energy(sum(GAIN[k] * stems[k][sl] for k in META["lead"]), 1000, 4000)
pad = band_energy(sum(GAIN[k] * stems[k][sl] for k in META["pad"]), 1000, 4000)
print(f"lead vs pad (1-4 kHz): {lead - pad:+.1f} dB")
