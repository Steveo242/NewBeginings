"""Bloody Seafood - free-spins music v2: a composed sea-shanty rocker, rendered from MIDI.

    python3 compose_fs_music.py <out_dir>

Writes one MIDI file per part (stems) to <out_dir>; render_fs_music.py renders them with
fluidsynth through FluidR3_GM (MIT) and mixes. Original composition, 2026-10-31.

D minor, 152 BPM, 24 bars (~37.9 s) that loop:
  A  (1-8)   the hook on fiddle, oom-pah accordion, bass and drums
             Dm Bb F C | Dm Bb F A          (i VI III VII | i VI III V)
  B  (9-16)  the build: strings swell, brass answers in long notes, toms, a snare roll
             Bb C Dm Dm | Bb C A A
  A' (17-24) the hook again, fiddle + brass in unison, open hats, crashes
Three loops are rendered and the middle one kept, so reverb and decays wrap seamlessly.
"""
import os
import sys

import mido

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
BPM = 152
TPB = 480                       # ticks per beat
E = TPB // 2                    # an eighth
BAR = 4 * TPB
LOOPS = 3
BARS = 24

# --- harmony ---------------------------------------------------------------------------
CH = {  # chord tones (MIDI, octave 4) and bass root (octave 2)
    "Dm": ((62, 65, 69), 38), "Bb": ((58, 62, 65), 34), "F": ((60, 65, 69), 41),
    "C": ((60, 64, 67), 36), "A": ((61, 64, 69), 33),
}
PROG = (["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "A"]
        + ["Bb", "C", "Dm", "Dm", "Bb", "C", "A", "A"]
        + ["Dm", "Bb", "F", "C", "Dm", "Bb", "F", "A"])

# --- the hook: (note, eighths), 8 eighths a bar ------------------------------------------
HOOK = [
    [(69, 1), (69, 1), (74, 2), (72, 1), (69, 1), (65, 1), (69, 1)],     # Dm
    [(70, 1), (74, 1), (77, 2), (76, 1), (74, 1), (72, 1), (74, 1)],     # Bb
    [(72, 1), (69, 1), (65, 1), (69, 1), (72, 2), (74, 1), (72, 1)],     # F
    [(76, 2), (74, 1), (72, 1), (67, 2), (72, 2)],                       # C
    [(69, 1), (69, 1), (74, 2), (72, 1), (69, 1), (65, 1), (69, 1)],     # Dm
    [(70, 1), (74, 1), (77, 2), (76, 1), (74, 1), (72, 1), (74, 1)],     # Bb
    [(72, 1), (69, 1), (65, 1), (67, 1), (69, 2), (72, 1), (69, 1)],     # F
    [(76, 2), (73, 1), (69, 1), (69, 4)],                                # A -> back to Dm
]
# B: the brass answers in long notes over the build
ANSWER = [[(74, 4), (77, 4)], [(76, 4), (79, 4)], [(77, 6), (74, 2)], [(81, 8)],
          [(74, 4), (77, 4)], [(76, 4), (79, 4)], [(76, 4), (73, 4)], [(76, 8)]]


class Part:
    def __init__(self, name, program, channel, volume):
        self.name, self.ch = name, channel
        self.events = []  # (tick, msg)
        if channel != 9:
            self.events.append((0, mido.Message("program_change", program=program, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=7, value=volume, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=91, value=40, channel=channel)))  # reverb send

    def note(self, t, n, dur, vel):
        self.events.append((t, mido.Message("note_on", note=n, velocity=vel, channel=self.ch)))
        self.events.append((t + max(1, dur - 10), mido.Message("note_off", note=n, velocity=0, channel=self.ch)))

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


lead = Part("lead", 110, 0, 112)        # Fiddle
brass = Part("brass", 61, 1, 92)        # Brass Section
accord = Part("chords", 21, 2, 78)      # Accordion
strings = Part("strings", 48, 3, 70)    # String Ensemble 1
bass = Part("bass", 33, 4, 104)         # Electric Bass (finger)
drums = Part("drums", 0, 9, 110)

KICK, SNARE, HAT, OHAT, CRASH, TOMS = 36, 38, 42, 46, 49, (50, 48, 47, 45)


def melody(part, t0, bar, vel, shift=0):
    t = t0
    for n, e in bar:
        part.note(t, n + shift, e * E, vel)
        t += e * E


for loop in range(LOOPS):
    for b in range(BARS):
        t = (loop * BARS + b) * BAR
        sec = 0 if b < 8 else (1 if b < 16 else 2)
        chord, root = CH[PROG[b]]
        # lead
        if sec == 0:
            melody(lead, t, HOOK[b], 100)
        elif sec == 2:
            melody(lead, t, HOOK[b - 16], 110)
            melody(brass, t, HOOK[b - 16], 88, shift=-12)
        else:
            melody(brass, t, ANSWER[b - 8], 92)
        # oom-pah accordion: chords on the off-beats (quieter, and sparser in the build)
        for beat in range(4):
            if sec == 1 and beat % 2:
                continue
            for n in chord:
                accord.note(t + beat * TPB + E, n, E, 70 if sec != 1 else 60)
        # strings: sustained chord, from the build on
        if sec >= 1:
            for n in chord:
                strings.note(t, n, BAR, 58 if sec == 1 else 52)
            strings.note(t, chord[0] - 12, BAR, 50)
        # bass: eighths locked to the kick, root / octave / fifth
        fifth = root + 7
        pat = [root, root, root + 12, root, fifth, root, root + 12, fifth]
        for i, n in enumerate(pat):
            bass.note(t + i * E, n, E, 104 if i % 2 == 0 else 88)
        # drums
        for beat in range(4):
            bt = t + beat * TPB
            if beat in (0, 2):
                drums.note(bt, KICK, E, 118)
            elif sec == 2:  # A': four on the floor
                drums.note(bt, KICK, E, 100)
            if beat in (1, 3):
                drums.note(bt, SNARE, E, 112)
            drums.note(bt, HAT, E // 2, 80)
            if sec == 2 and beat == 3:
                drums.note(bt + E, OHAT, E, 78)
            else:
                drums.note(bt + E, HAT, E // 2, 62)
        if b in (0, 8, 16, 12):
            drums.note(t, CRASH, BAR // 2, 100)
        # fills: toms at the end of every 8th bar, a snare roll into A'
        if b in (7, 23):
            for i, n in enumerate(TOMS):
                drums.note(t + 2 * TPB + i * (E // 2) * 2, n, E, 100)
        if b == 15:
            for i in range(16):
                drums.note(t + i * (TPB // 4), SNARE, TPB // 4, 60 + i * 3)

for p in (lead, brass, accord, strings, bass, drums):
    p.save()
print("wrote stems to", OUT, f"loop {BARS * 4 * 60 / BPM:.2f} s x {LOOPS}")
