"""Bloody Seafood - big-win music, one track per celebration tier, two sets.

    python3 make_bigwin_music.py <out_dir>

Writes bgm_win_<tier>.wav (base game) and bgm_win_<tier>_fs.wav (bonuses) for the tiers
big / superwin / mega / epic / max (stereo, 44.1 kHz). Original, 2026-10-31: MIDI rendered
through FluidR3_GM (MIT) with fluidsynth.

Each track runs the tier's count-up (3 / 4 / 5 / 6.5 / 8 s) and ends on a held chord. Every
tier up is faster, longer, louder (+1.2 LU a tier) and has more in it:
  base  an original D major jig in 6/8 - fiddle and accordion with claps; + crew choir,
        bass and drums; + brass and timpani; + distortion guitars and crashes; MAX adds the
        lead guitar, double kick and a lift up a tone for the second half
  bonus the "Drunken Sailor" chorus (traditional, public domain) in D minor, 4/4, heavy
        from the start - crew and chugging guitars; + fiddle; + brass; + lead guitar and
        double kick; MAX lifts a tone with timpani and a choir pad
"""
import json
import os
import subprocess
import sys

import mido
import numpy as np
from scipy.io import wavfile

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
TPB = 480
rng = np.random.default_rng(11)

TIERS = ["big", "superwin", "mega", "epic", "max"]
COUNT_UP = [3.0, 4.0, 5.0, 6.5, 8.0]
FIDDLE, ACCORD, CHOIR, BRASS, TIMP, ABASS, PBASS, DIST, LEAD = 110, 21, 52, 61, 47, 32, 34, 30, 29
KICK, SNARE, CLAP, HAT, CRASH, CRASH2, RIDE, TAMB = 36, 38, 39, 42, 49, 57, 51, 54
TOMS = (50, 48, 47, 45, 43, 41)


class Song:
    def __init__(self):
        self.parts = {}                       # program (None = drums) -> [(beat, note, dur, vel)]

    def n(self, prog, beat, note, dur, vel):
        jitter = rng.uniform(-0.012, 0.012) if beat > 0 else 0
        self.parts.setdefault(prog, []).append((max(0, beat + jitter), note, dur, int(np.clip(vel + rng.integers(-4, 5), 1, 127))))

    def render(self, bpm, beats, path):
        mid = mido.MidiFile(ticks_per_beat=TPB)
        for i, (prog, notes) in enumerate(self.parts.items()):
            ch = 9 if prog is None else (i if i < 9 else i + 1)
            tr = mido.MidiTrack()
            mid.tracks.append(tr)
            if i == 0:
                tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
            ev = [(0, mido.Message("control_change", control=91, value=40, channel=ch))]
            if prog is not None:
                ev.append((0, mido.Message("program_change", program=prog, channel=ch)))
            for b, note, d, v in notes:
                ev.append((int(b * TPB), mido.Message("note_on", note=note, velocity=v, channel=ch)))
                ev.append((int((b + d) * TPB) - 5, mido.Message("note_off", note=note, velocity=0, channel=ch)))
            last = 0
            for t, m in sorted(ev, key=lambda e: (e[0], e[1].type == "note_on")):
                tr.append(m.copy(time=t - last))
                last = t
            tr.append(mido.MetaMessage("end_of_track", time=max(0, int(beats * TPB) - last)))
        p = path + ".mid"
        mid.save(p)
        subprocess.run(["fluidsynth", "-ni", "-g", "0.45", "-r", str(SR), "-R", "1", "-C", "0", "-F", path + ".raw.wav", SF2, p],
                       check=True, capture_output=True)
        _, x = wavfile.read(path + ".raw.wav")
        os.remove(p)
        os.remove(path + ".raw.wav")
        x = x.astype(np.float32) / (32768 if x.dtype == np.int16 else 1)
        x = x[:int(beats * 60 / bpm * SR)]
        fade = int(0.25 * SR)                  # the held chord rings out, then a short fade
        x[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
        return x


def finish(x, path, k):
    tmp = path + ".pre.wav"
    wavfile.write(tmp, SR, (x / np.abs(x).max() * 0.7).astype(np.float32))
    target = -19.0 + 1.2 * k
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11",
                    "-ar", str(SR), "-c:a", "pcm_s16le", path], check=True)
    os.remove(tmp)
    _, y = wavfile.read(path)
    print(os.path.basename(path), f"{len(y) / SR:.2f} s, peak {np.abs(y).max() / 32768:.3f}, "
          f"clipped {(np.abs(y) >= 32767).sum()}")


# ------------------------------------------------------------------------- base: D major jig
# (note, eighths); 6 eighths a bar. Original.
JIG = [
    [(74, 1), (78, 1), (81, 1), (81, 2), (78, 1)],
    [(79, 1), (83, 1), (79, 1), (78, 2), (76, 1)],
    [(74, 1), (78, 1), (81, 1), (86, 2), (81, 1)],
    [(83, 1), (81, 1), (79, 1), (76, 2), (73, 1)],
]
JIG_CH = [(50, 54, 57, 38), (55, 59, 62, 43), (50, 54, 57, 38), (45, 49, 52, 45)]   # D G D A
D_MAJ = (62, 66, 69, 74, 38)


def base(k):
    bpm = [150, 156, 165, 174, 180][k]
    bar_b = 3.0                                # crotchets a 6/8 bar
    bars = [3, 4, 5, 7, 8][k]                  # each covers the tier's count-up, each longer
    s = Song()
    for b in range(bars):
        t = b * bar_b
        up = 2 if k == 4 and b >= bars // 2 else 0
        c0, c1, c2, root = (v + up for v in JIG_CH[b % 4])
        e = 0.0
        for note, u in JIG[b % 4]:
            d = u * 0.5
            s.n(FIDDLE, t + e, note + up, d * 0.95, 104 + 3 * k)
            if k >= 1:
                s.n(CHOIR, t + e, note + up - 12, d, 92 + 3 * k)
            if k >= 2:
                s.n(BRASS, t + e, note + up - 12, d * 0.9, 100 + 3 * k)
            if k >= 4:
                s.n(LEAD, t + e, note + up, d * 0.95, 112)
            e += d
        for h in (0, 1.5):
            s.n(ACCORD, t + h, root + 12, 0.95, 98)
            for n in (c0, c1, c2):
                s.n(ACCORD, t + h + 1.0, n + 12, 0.45, 92)
            if k >= 1:
                s.n(ABASS if k < 3 else PBASS, t + h, root, 1.4, 106)
            if k >= 3:
                for j in range(3):
                    for n in (root + 12, root + 19, root + 24):
                        s.n(DIST, t + h + j * 0.5, n, 0.45, 112 if j == 0 else 98)
            # drums
            if k == 0:
                s.n(None, t + h + 1.0, CLAP, 0.4, 100)
                for j in range(3):
                    s.n(None, t + h + j * 0.5, TAMB, 0.4, 86 if j == 0 else 64)
            else:
                if k < 4:
                    s.n(None, t + h, KICK, 0.4, 112)
                else:
                    for j in range(6):
                        s.n(None, t + h + j * 0.25, KICK, 0.25, 112 if j == 0 else 96)
                if h:
                    s.n(None, t + h, SNARE, 0.4, 118)
                for j in range(3):
                    s.n(None, t + h + j * 0.5, HAT if k < 3 else RIDE, 0.4, 90 if j == 0 else 70)
        if k >= 2 and b % 2 == 0:
            s.n(TIMP, t, root - 12 if root - 12 >= 36 else root, 1.0, 110)
        if k >= 3 and (b % 2 == 0 or k == 4):
            s.n(None, t, CRASH if b % 4 == 0 else CRASH2, 1.5, 116)
    # the held final chord: everyone, a crash; MAX and EPIC a timpani roll into it
    t = bars * bar_b
    up = 2 if k == 4 else 0
    chord = [v + up for v in D_MAJ]
    if k >= 3:
        for j in range(8):
            s.n(TIMP, t - 1.0 + j * 0.125, chord[4], 0.125, 80 + 5 * j)
    for prog, shift, vel in [(FIDDLE, 12, 104), (ACCORD, 0, 96)] + ([(CHOIR, 0, 100)] if k >= 1 else []) \
            + ([(BRASS, 0, 108)] if k >= 2 else []) + ([(DIST, -12, 110)] if k >= 3 else []):
        for n in chord[:4]:
            s.n(prog, t, n + shift, 2.6, vel)
    s.n(ABASS if k < 3 else PBASS, t, chord[4], 2.6, 110)
    s.n(None, t, CRASH, 2.5, 122)
    s.n(None, t, KICK, 0.5, 120)
    if k >= 2:
        s.n(TIMP, t, chord[4], 2.0, 120)
    return s, bpm, t + 3.0


# --------------------------------------------------- bonus: "Drunken Sailor" chorus, D minor
A4, B4, C5, D5, D4, E4, F4, G4, C4 = 69, 71, 72, 74, 62, 64, 65, 67, 60
CHORUS = [
    [(A4, 2), (A4, 2), (A4, 1), (D4, 1), (F4, 1), (A4, 1)],
    [(G4, 2), (G4, 2), (G4, 1), (C4, 1), (E4, 1), (G4, 1)],
    [(A4, 2), (A4, 2), (A4, 1), (B4, 1), (C5, 1), (D5, 1)],
    [(C5, 1), (A4, 1), (G4, 1), (E4, 1), (D4, 2), (D4, 2)],
]
DS_CH = [[(50, 53, 57, 38)] * 2, [(48, 52, 55, 36)] * 2, [(50, 53, 57, 38)] * 2, [(48, 52, 55, 36), (50, 53, 57, 38)]]
D_MIN = (62, 65, 69, 74, 38)


def bonus(k):
    bpm = [132, 138, 144, 152, 160][k]
    bars = [2, 3, 4, 5, 6][k]
    s = Song()
    for b in range(bars):
        t = b * 4.0
        up = 2 if k == 4 and b >= bars // 2 else 0
        e = 0.0
        for note, u in CHORUS[b % 4]:
            d = u * 0.5
            s.n(CHOIR, t + e, note + up, d, 100 + 3 * k)
            s.n(CHOIR, t + e, note + up - 12, d, 92 + 3 * k)
            if k >= 1:
                s.n(FIDDLE, t + e, note + up + 12, d * 0.9, 100)
            if k >= 2:
                s.n(BRASS, t + e, note + up, d * 0.9, 104)
            if k >= 3:
                s.n(LEAD, t + e, note + up + 12, d * 0.95, 112)
            e += d
        for h, (c0, c1, c2, root) in enumerate(DS_CH[b % 4]):
            th = t + 2.0 * h
            root += up
            for j in range(4):
                s.n(PBASS, th + j * 0.5, root, 0.45, 110 if j % 2 == 0 else 96)
                for n in (root + 12, root + 19, root + 24):
                    s.n(DIST, th + j * 0.5, n, 0.42, 112 if j % 2 == 0 else 98)
            if k >= 4:
                for n in (c0 + 12 + up, c1 + 12 + up, c2 + 12 + up):
                    s.n(CHOIR, th, n, 2.0, 84)
        for beat in range(4):
            tb = t + beat
            if k < 3:
                s.n(None, tb, KICK, 0.4, 114 if beat % 2 == 0 else 100)
            else:
                for j in range(4):
                    s.n(None, tb + j * 0.25, KICK, 0.25, 114 if j == 0 else 98)
            if beat % 2:
                s.n(None, tb, SNARE, 0.4, 120)
            s.n(None, tb, HAT if k < 2 else RIDE, 0.4, 92)
            s.n(None, tb + 0.5, HAT if k < 2 else RIDE, 0.4, 74)
        if b % 2 == 0 or k >= 3:
            s.n(None, t, CRASH if b % 2 == 0 else CRASH2, 1.5, 118)
        if k >= 4 and b % 2 == 0:
            s.n(TIMP, t, 38 + up, 1.0, 112)
        if b == bars - 1:                      # fill into the held chord
            for j in range(8):
                s.n(None, t + 2.0 + j * 0.25, SNARE if j < 4 else TOMS[j - 2], 0.25, 100 + 3 * j)
    t = bars * 4.0
    up = 2 if k == 4 else 0
    chord = [v + up for v in D_MIN]
    for prog, shift, vel in [(CHOIR, 0, 104), (CHOIR, -12, 98), (DIST, -12, 114)] + ([(FIDDLE, 12, 102)] if k >= 1 else []) \
            + ([(BRASS, 0, 110)] if k >= 2 else []) + ([(LEAD, 12, 110)] if k >= 3 else []):
        for n in chord[:4]:
            s.n(prog, t, n + shift, 3.0, vel)
    s.n(PBASS, t, chord[4], 3.0, 112)
    s.n(None, t, CRASH, 3.0, 124)
    s.n(None, t, KICK, 0.5, 122)
    if k >= 2:
        s.n(TIMP, t, chord[4], 2.5, 122)
    return s, bpm, t + 3.5


report = {}
for k, tier in enumerate(TIERS):
    for make, suffix in ((base, ""), (bonus, "_fs")):
        song, bpm, beats = make(k)
        path = os.path.join(OUT, f"bgm_win_{tier}{suffix}.wav")
        finish(song.render(bpm, beats, path), path, k)
        report[f"bgm_win_{tier}{suffix}"] = round(beats * 60 / bpm, 2)
json.dump(report, open(os.path.join(OUT, "lengths.json"), "w"), indent=1)
