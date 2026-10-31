"""Bloody Seafood - free-spins music v3: dark, storm-driven and building, rendered from MIDI.

    python3 compose_fs_music_v3.py <out_dir>

Writes one MIDI file per part (stems), a synthesised thunder stem (thunder.wav) and
meta.json (tempo, length, stem gains, high-passes) to <out_dir>; render_fs_music.py renders
the MIDI with fluidsynth through FluidR3_GM (MIT), adds the thunder and mixes.
Original composition, 2026-10-31.

D minor with the Phrygian flat second (Eb) and the harmonic-minor C#, 144 BPM, 32 bars
(~53.3 s) that loop:
  A  (1-8)   the storm gathers: staccato low-string ostinato in 3+3+2, taiko and timpani,
             a low choir pad swelling like wind; thunder on the downbeat
  B  (9-16)  the build: the hook enters on horns, violins stack the ostinato an octave up,
             kick and snare drive in, a cymbal swell and snare roll into...
  C  (17-24) the heavy section: hook on full brass + trombones + choir, palm-muted
             overdriven guitar, double kick, crashes; thunder on the downbeat
  D  (25-32) the hook a step higher over the same drive, then toms and a swell back to A
Three loops are rendered and the middle one kept, so reverb and decays wrap seamlessly.
"""
import json
import os
import sys

import mido
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
BPM = 144
TPB = 480                       # ticks per beat
E = TPB // 2                    # an eighth
S16 = TPB // 4
BAR = 4 * TPB
LOOPS = 3
BARS = 32
SR = 44100

# --- harmony: chord tones (octave 3-4) and root (octave 2) --------------------------------
CH = {
    "Dm": ((50, 53, 57), 38), "Eb": ((51, 55, 58), 39), "C": ((48, 52, 55), 36),
    "Bb": ((46, 50, 53), 34), "A": ((49, 52, 57), 33), "Gm": ((43, 46, 50), 31),
}
PROG = (["Dm", "Dm", "Eb", "Dm", "Dm", "Dm", "Bb", "A"]          # A
        + ["Gm", "Gm", "Eb", "Eb", "Bb", "Bb", "A", "A"]          # B
        + ["Dm", "Eb", "Dm", "C", "Bb", "Gm", "A", "A"]           # C
        + ["Dm", "Eb", "Dm", "C", "Bb", "Eb", "A", "A"])          # D
# the ostinato over each chord's root: 3+3+2 accents, the flat second as the sting
OST = [0, 0, 1, 0, 0, 1, 0, 12]
ACC = [1, 0, 0, 1, 0, 0, 1, 0]

# --- the hook: (note, eighths), 8 eighths a bar -------------------------------------------
HOOK = [
    [(62, 3), (65, 3), (64, 2)],                 # Dm   D. F. E
    [(63, 6), (62, 2)],                          # Eb   Eb... D
    [(62, 3), (69, 3), (67, 2)],                 # Dm   D. A. G
    [(65, 4), (64, 2), (61, 2)],                 # C    F  E C#
    [(70, 3), (69, 3), (67, 2)],                 # Bb   Bb. A. G
    [(67, 6), (65, 2)],                          # Gm   G... F
    [(64, 3), (65, 3), (61, 2)],                 # A    E. F. C#
    [(64, 8)],                                   # A    E (held, the turn back)
]


class Part:
    def __init__(self, name, program, channel, volume, reverb=40):
        self.name, self.ch = name, channel
        self.events = []  # (tick, msg)
        if channel != 9:
            self.events.append((0, mido.Message("program_change", program=program, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=7, value=volume, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=91, value=reverb, channel=channel)))

    def note(self, t, n, dur, vel):
        self.events.append((t, mido.Message("note_on", note=n, velocity=max(1, min(127, vel)), channel=self.ch)))
        self.events.append((t + max(1, dur - 10), mido.Message("note_off", note=n, velocity=0, channel=self.ch)))

    def cc(self, t, control, value):
        self.events.append((t, mido.Message("control_change", control=control, value=int(value), channel=self.ch)))

    def save(self):
        mid = mido.MidiFile(ticks_per_beat=TPB)
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
        last = 0
        for t, m in sorted(self.events, key=lambda e: (e[0], e[1].type == "note_on")):
            tr.append(m.copy(time=t - last))
            last = t
        tr.append(mido.MetaMessage("end_of_track", time=BAR))
        mid.save(os.path.join(OUT, f"{self.name}.mid"))


ost_lo = Part("ost_lo", 48, 0, 110, 30)      # String Ensemble 1, short notes: staccato cellos/basses
ost_hi = Part("ost_hi", 48, 1, 92, 35)       # the same an octave up: violins, from the build
brass = Part("brass", 61, 2, 100, 50)        # Brass Section: the hook
horns = Part("horns", 60, 3, 96, 55)         # French Horn: the hook in B, low brass support later
choir = Part("choir", 52, 4, 96, 70)         # Choir Aahs: the wind pad, the hook in C
guitar = Part("guitar", 29, 5, 84, 20)       # Overdriven Guitar: palm-muted power chords
taiko = Part("taiko", 116, 6, 118, 45)       # Taiko Drum
timp = Part("timp", 47, 7, 104, 50)          # Timpani
bass = Part("bass", 43, 8, 104, 25)          # Contrabass
drums = Part("drums", 0, 9, 112, 35)

KICK, SNARE, HAT, OHAT, CRASH, RIDE, CHINA = 36, 38, 42, 46, 49, 51, 52
TOMS = (50, 48, 47, 45, 43, 41)


def melody(part, t0, bar, vel, shift=0):
    t = t0
    for n, e in bar:
        part.note(t, n + shift, e * E, vel)
        t += e * E


for loop in range(LOOPS):
    for b in range(BARS):
        t = (loop * BARS + b) * BAR
        sec = b // 8
        chord, root = CH[PROG[b]]
        heavy = sec >= 2
        # ostinato: staccato eighths on the root (octave 2-3), accents in 3+3+2
        for i, (iv, acc) in enumerate(zip(OST, ACC)):
            n = root + 12 + iv
            ost_lo.note(t + i * E, n, E // 2, (112 if acc else 84) + (6 if heavy else 0))
            if sec >= 1:
                ost_hi.note(t + i * E, n + 24, E // 2, (96 if acc else 72) + (8 if heavy else 0))
            if heavy:
                ost_lo.note(t + i * E, n - 12, E // 2, 100 if acc else 76)
        # bass: long root, re-struck on the accents
        for i in (0, 3, 6):
            bass.note(t + i * E, root, 3 * E if i < 6 else 2 * E, 108)
        # choir: wind pad - the chord, swelling and ebbing over two bars (expression CC11)
        if sec in (0, 1):
            for n in chord:
                choir.note(t, n + 12, BAR, 70 if sec == 0 else 78)
            for k in range(8):
                v = 50 + 70 * np.sin(np.pi * ((b % 2) * 8 + k) / 16)
                choir.cc(t + k * TPB // 2, 11, v)
        # the hook
        if sec == 1:
            melody(horns, t, HOOK[b - 8], 92)
        elif sec == 2:
            choir.cc(t, 11, 127)
            melody(brass, t, HOOK[b - 16], 112)
            melody(horns, t, HOOK[b - 16], 100, shift=-12)
            melody(choir, t, HOOK[b - 16], 92)
        elif sec == 3:
            choir.cc(t, 11, 127)
            up = 2 if b < 28 else 0                              # a step higher, then home
            melody(brass, t, HOOK[b - 24], 118, shift=up)
            melody(horns, t, HOOK[b - 24], 104, shift=up - 12)
            melody(choir, t, HOOK[b - 24], 96, shift=up + 12)
        # guitar: palm-muted root+fifth eighths, open on the accents
        if heavy:
            for i, acc in enumerate(ACC):
                d = 3 * E // 2 if acc else E // 3
                for n in (root + 12, root + 19):
                    guitar.note(t + i * E, n, d, 104 if acc else 80)
        # taiko and timpani: the storm's heartbeat, 3+3+2
        for i, acc in enumerate(ACC):
            if acc:
                taiko.note(t + i * E, 48 if i == 0 else 52, E, 120 if i == 0 else 104)
        if sec == 0 or heavy:
            taiko.note(t + 7 * E, 55, E, 90)
        if b % 2 == 0 or heavy:
            timp.note(t, root + 12, TPB, 110 if heavy else 96)
        if b % 8 == 7:                                           # timpani roll into the next section
            for i in range(8):
                timp.note(t + 2 * TPB + i * S16, CH[PROG[(b + 1) % BARS]][1] + 12, S16, 70 + i * 6)
        # kit
        if sec >= 1:
            for beat in range(4):
                bt = t + beat * TPB
                if heavy:                                        # double kick on the drive
                    drums.note(bt, KICK, E, 118)
                    drums.note(bt + E, KICK, E, 96)
                elif beat in (0, 2):
                    drums.note(bt, KICK, E, 112)
                if beat in (1, 3) and (heavy or b >= 12):
                    drums.note(bt, SNARE, E, 116)
                elif beat == 2 and not heavy:
                    drums.note(bt, SNARE, E, 104)                # half-time backbeat early in B
                for k in range(4 if (heavy or b >= 12) else 2):
                    step = TPB // (4 if (heavy or b >= 12) else 2)
                    drums.note(bt + k * step, RIDE if heavy else HAT, step, 82 if k == 0 else 58)
        else:
            drums.note(t + 7 * E, TOMS[4], E, 92)                # floor tom answers the taiko
        if b in (0, 16, 20, 24, 28):
            drums.note(t, CRASH, BAR // 2, 112)
            if heavy:
                drums.note(t, CHINA, BAR // 2, 90)
        # cymbal swell and snare roll into the heavy section
        if b in (14, 15):
            for i in range(16):
                drums.note(t + i * S16 * 2, RIDE, S16 * 2, 40 + (b - 14) * 32 + i * 2)
        if b == 15:
            for i in range(16):
                drums.note(t + i * S16, SNARE, S16, 54 + i * 4)
        # tom run back into A
        if b == 31:
            for i, n in enumerate(TOMS):
                drums.note(t + 2 * TPB + i * (TPB // 3), n, E, 104 + i * 3)   # six toms over two beats
            for i in range(8):
                drums.note(t + i * S16 * 2, CRASH, S16 * 2, 30 + i * 10)

for p in (ost_lo, ost_hi, brass, horns, choir, guitar, taiko, timp, bass, drums):
    p.save()


# --- thunder: a synthesised close strike at the downbeats of A and C ------------------------
def thunder(rng, dur=4.5):
    """Crack + rolling rumble, low-passed (no broadband hiss): an initial bright-ish crack
    (band-limited to 2.5 kHz) and a brown-noise rumble whose roll is uneven."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    brown = np.cumsum(rng.standard_normal(n)); brown -= np.convolve(brown, np.ones(2048) / 2048, "same")
    rumble = sosfilt(butter(4, 320, "lowpass", fs=SR, output="sos"), brown)
    roll = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * (0.7 * t + 0.2 * t ** 2)))
    env = (1 - np.exp(-t / 0.05)) * np.exp(-t / 1.4) * roll
    crack = sosfilt(butter(4, [300, 2500], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
    cenv = np.exp(-t / 0.12) * (t < 0.6)
    x = rumble / np.abs(rumble).max() * env + 0.35 * crack / np.abs(crack).max() * cenv
    x = sosfilt(butter(2, 2500, "lowpass", fs=SR, output="sos"), x)
    return x / np.abs(x).max()


rng = np.random.default_rng(144)
total = int(round(LOOPS * BARS * 4 * 60 / BPM * SR)) + 8 * SR
th = np.zeros(total, np.float32)
for loop in range(LOOPS):
    for b in (0, 16):
        s = int(round((loop * BARS + b) * 4 * 60 / BPM * SR))
        x = thunder(rng)
        th[s:s + len(x)] += x[:total - s]
wavfile.write(os.path.join(OUT, "thunder.wav"), SR, np.stack([th, th], 1))

json.dump({
    "bpm": BPM, "bars": BARS,
    # stem gains: the hook (brass / horns / choir) on top, the ostinato and drums driving
    "gain": {"ost_lo": 0.9, "ost_hi": 0.8, "brass": 0.62, "horns": 0.5, "choir": 0.8, "guitar": 0.45,
             "taiko": 0.3, "timp": 0.6, "bass": 0.45, "drums": 0.66, "thunder": 0.22},
    # high-passes (Hz): only bass, taiko, timpani and thunder keep the low end
    "hp": {"ost_lo": 70, "ost_hi": 200, "brass": 140, "horns": 110, "choir": 160, "guitar": 120, "drums": 40},
    "lead": ["brass", "horns", "choir"], "pad": ["ost_lo", "ost_hi", "guitar"],
}, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("wrote stems to", OUT, f"loop {BARS * 4 * 60 / BPM:.2f} s x {LOOPS}")
