"""Bloody Seafood - bonus music v4: pirate drinking shanties, rendered from MIDI.

    python3 compose_shanty.py <out_dir>

Writes four stem sets, each a folder of one MIDI file per part plus meta.json (tempo,
metre, length, stem gains, high-passes) that render_fs_music.py renders through FluidR3_GM
(MIT) with fluidsynth and mixes:

  bonus_intro   "Drunken Sailor" (traditional sea shanty, public domain) sung by one lone
                voice (Voice Oohs), free and slow - loops until the first free spin
  bonus_main    the crew take it up at 126 BPM, 4 passes of verse + chorus (32 bars):
                1 crew choir, accordion oom-pah, stomp and clap
                2 + fiddle with grace notes, harmony a third under, bass, snare, tambourine
                3 + palm-muted distortion guitar, picked bass, rock kit
                4 the metal finale: lead guitar on the tune an octave up, double kick,
                  crashes, the crew on full chords; tom fill back to the top
  super_intro   an original shanty (2026-10-31) in E minor, 6/8, the lone voice an octave
                down and darker
  super_main    the same tune by the crew at dotted crotchet = 104, 3 passes of 16 bars:
                crew -> fiddle and drums -> metal finale

The main loops open on a downbeat crash: the game cuts to them at the first free spin with
a lightning strike. Each loop is written three times and the middle one is kept, so
reverb and decays wrap seamlessly.
"""
import json
import os
import random
import sys

import mido

OUT = sys.argv[1]
TPB = 480
E = TPB // 2
LOOPS = 3
random.seed(7)


class Part:
    def __init__(self, name, program, channel, volume, reverb=40):
        self.name, self.ch = name, channel
        self.events = []
        if channel != 9:
            self.events.append((0, mido.Message("program_change", program=program, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=7, value=volume, channel=channel)))
        self.events.append((0, mido.Message("control_change", control=91, value=reverb, channel=channel)))

    def note(self, t, n, dur, vel, human=True):
        if human:
            t = max(0, t + random.randint(-6, 6))
            vel += random.randint(-5, 5)
        self.events.append((t, mido.Message("note_on", note=n, velocity=max(1, min(127, vel)), channel=self.ch)))
        self.events.append((t + max(1, dur - 10), mido.Message("note_off", note=n, velocity=0, channel=self.ch)))

    def cc(self, t, control, value):
        self.events.append((t, mido.Message("control_change", control=control, value=int(value), channel=self.ch)))

    def save(self, folder, bpm, end):
        mid = mido.MidiFile(ticks_per_beat=TPB)
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
        last = 0
        for t, m in sorted(self.events, key=lambda e: (e[0], e[1].type == "note_on")):
            tr.append(m.copy(time=t - last))
            last = t
        tr.append(mido.MetaMessage("end_of_track", time=max(0, end - last) + 4 * TPB))
        mid.save(os.path.join(folder, f"{self.name}.mid"))


def write(name, bpm, beats, bars, parts, gain, hp, lead, pad):
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    end = LOOPS * bars * beats * TPB
    for p in parts:
        p.save(folder, bpm, end)
    json.dump({"bpm": bpm, "beats": beats, "bars": bars, "gain": gain, "hp": hp, "lead": lead, "pad": pad},
              open(os.path.join(folder, "meta.json"), "w"), indent=1)
    print(name, f"{bars * beats * 60 / bpm:.2f} s loop")


def play(part, t0, line, unit, vel, shift=0, legato=1.0, accent=None):
    """line: [(note or None, units)]; unit = ticks per unit"""
    t = t0
    for i, (n, u) in enumerate(line):
        if n is not None:
            v = vel + (accent(t - t0) if accent else 0)
            part.note(t, n + shift, int(u * unit * legato), v)
        t += u * unit


def third_below(n, scale):
    """the diatonic third under n in the scale (pitch classes)"""
    pcs = sorted(scale)
    for d in range(1, 6):
        if (n - d) % 12 in pcs:
            lower = n - d
            for d2 in range(1, 6):
                if (lower - d2) % 12 in pcs:
                    return lower - d2
    return n - 3


KICK, KICK2, SNARE, CLAP, HAT, OHAT, CRASH, CRASH2, RIDE, TAMB = 36, 35, 38, 39, 42, 46, 49, 57, 51, 54
TOMS = (50, 48, 47, 45, 43, 41)

# =========================================================================== Drunken Sailor
# D dorian, written in 2/4 eighths; two 2/4 bars make one 4/4 bar here. Traditional.
A4, B4, C5, D5, D4, E4, F4, G4, C4 = 69, 71, 72, 74, 62, 64, 65, 67, 60
VERSE = [
    [(A4, 1), (A4, 1), (A4, 1), (A4, 1), (A4, 1), (D4, 1), (F4, 1), (A4, 1)],   # what shall we do with a drunken sailor
    [(G4, 1), (G4, 1), (G4, 1), (G4, 1), (G4, 1), (C4, 1), (E4, 1), (G4, 1)],
    [(A4, 1), (A4, 1), (A4, 1), (A4, 1), (A4, 1), (B4, 1), (C5, 1), (D5, 1)],
    [(C5, 1), (A4, 1), (G4, 1), (E4, 1), (D4, 2), (D4, 2)],                     # ear-lye in the mor-ning
]
CHORUS = [
    [(A4, 2), (A4, 2), (A4, 1), (D4, 1), (F4, 1), (A4, 1)],                     # way hay and up she rises
    [(G4, 2), (G4, 2), (G4, 1), (C4, 1), (E4, 1), (G4, 1)],
    [(A4, 2), (A4, 2), (A4, 1), (B4, 1), (C5, 1), (D5, 1)],
    [(C5, 1), (A4, 1), (G4, 1), (E4, 1), (D4, 2), (D4, 2)],
]
DS_TUNE = VERSE + CHORUS                                    # 8 bars of 8 eighths
DS_CHORDS = [["Dm", "Dm"], ["C", "C"], ["Dm", "Dm"], ["C", "Dm"]] * 2   # per half bar
DORIAN = {2, 4, 5, 7, 9, 11, 0}
CHD = {"Dm": (50, 53, 57, 38), "C": (48, 52, 55, 36), "Em": (52, 55, 59, 40), "Am": (45, 48, 52, 45),
       "D": (50, 54, 57, 38), "G": (43, 47, 50, 43), "B7": (47, 51, 54, 35), "Cmaj": (48, 52, 55, 36)}


def drunken_sailor():
    # ---- intro: one lone voice, slow, rubato-ish swells; nothing else
    bpm, bars = 84, 8
    bar = 4 * TPB
    voice = Part("voice", 53, 0, 112, 100)           # Voice Oohs
    for loop in range(LOOPS):
        for b, line in enumerate(DS_TUNE):
            t = (loop * bars + b) * bar
            play(voice, t, line, E, 92 if b < 4 else 100, shift=-12, legato=1.0,
                 accent=lambda dt: 8 if dt % bar == 0 else 0)
            for k in range(8):                       # each phrase breathes: swell and ebb
                voice.cc(t + k * E, 11, 88 + 34 * (1 - abs(k - 3.5) / 3.5))
    write("bonus_intro", bpm, 4, bars, [voice], {"voice": 1.0}, {"voice": 90}, ["voice"], ["voice"])

    # ---- main: the crew, building to metal
    bpm, bars = 126, 32
    choir = Part("choir", 52, 0, 110, 60)            # Choir Aahs: the crew
    choir2 = Part("choir2", 52, 1, 96, 60)           # the harmony / full chords
    accord = Part("accord", 21, 2, 104, 35)          # Accordion
    fiddle = Part("fiddle", 110, 3, 108, 45)         # Fiddle
    bass = Part("bass", 32, 4, 108, 20)              # Acoustic Bass
    pbass = Part("pbass", 34, 5, 104, 15)            # Electric Bass (pick)
    dist = Part("dist", 30, 6, 100, 18)              # Distortion Guitar: power chords
    lead = Part("lead", 29, 7, 108, 40)              # Overdriven Guitar: the finale lead
    drums = Part("drums", 0, 9, 116, 30)
    for loop in range(LOOPS):
        for b in range(bars):
            t = (loop * bars + b) * bar
            p, i = b // 8, b % 8
            line = DS_TUNE[i]
            halves = DS_CHORDS[i]
            # the crew sing the tune in octaves from the top; louder each pass
            play(choir, t, line, E, 92 + 8 * p, shift=0)
            play(choir, t, line, E, 84 + 8 * p, shift=-12)
            if p >= 1:
                play(choir2, t, [(third_below(n, DORIAN), u) for n, u in line], E, 80 + 6 * p)
            for h, ch in enumerate(halves):
                c0, c1, c2, root = CHD[ch]
                th = t + h * 2 * TPB
                # accordion oom-pah: bass on the beat, chord on the off-beat (eases off for metal)
                av = 96 if p < 2 else 74
                accord.note(th, root + 12, TPB - 40, av + 6)
                for n in (c0, c1, c2):
                    accord.note(th + TPB, n + 12, TPB // 2, av)
                    if p >= 1:
                        accord.note(th + TPB + E, n + 12, TPB // 2 - 20, av - 12)
                if p == 1:
                    bass.note(th, root, TPB, 104)
                    bass.note(th + TPB, root + 7, TPB, 96)
                if p >= 2:                           # metal: chugging eighths
                    for k in range(4):
                        acc = k % 2 == 0
                        pbass.note(th + k * E, root, E - 20, 110 if acc else 96)
                        dur = E - 30 if p == 2 else E - 10
                        for n in (root + 12, root + 19, root + 24):
                            dist.note(th + k * E, n, dur, 112 if acc else 98)
                if p == 3:                           # the crew hold full chords over the riff
                    for n in (c0 + 12, c1 + 12, c2 + 12):
                        choir2.note(th, n, 2 * TPB, 84)
            if p == 1:                               # fiddle: the tune with grace notes
                tt = t
                for n, u in line:
                    if u == 1 and random.random() < 0.35:
                        fiddle.note(tt, n + 2, 40, 90, human=False)
                        fiddle.note(tt + 40, n + 12, u * E - 40, 104)
                    else:
                        fiddle.note(tt, n + 12, u * E, 104)
                    tt += u * E
            if p >= 2:                               # fiddle hands the tune to the guitar
                play(fiddle, t, line, E, 98, shift=12 if p == 2 else 24, legato=0.9)
            if p == 3:
                play(lead, t, line, E, 116, shift=12, legato=0.95)
                play(lead, t, line, E, 100, shift=0, legato=0.95)
            # ---- drums
            for beat in range(4):
                tb = t + beat * TPB
                if p == 0:                           # stomp and clap
                    if beat % 2 == 0:
                        drums.note(tb, KICK2, E, 112)
                    else:
                        drums.note(tb, CLAP, E, 100)
                elif p == 1:
                    drums.note(tb, KICK, E, 110 if beat % 2 == 0 else 92)
                    if beat % 2:
                        drums.note(tb, SNARE, E, 108)
                        drums.note(tb, CLAP, E, 84)
                    drums.note(tb, TAMB, E, 80)
                    drums.note(tb + E, TAMB, E, 66)
                else:
                    if beat % 2:
                        drums.note(tb, SNARE, E, 122)
                    drums.note(tb, HAT if p == 2 else RIDE, E, 96)
                    drums.note(tb + E, HAT if p == 2 else RIDE, E, 80)
                    if p == 2:
                        drums.note(tb, KICK, E, 118)
                        if beat in (1, 3):
                            drums.note(tb + E, KICK, E, 104)
                    else:                            # double kick
                        for k in range(4):
                            drums.note(tb + k * TPB // 4, KICK, TPB // 4, 116 if k == 0 else 100)
            # crashes: the top of each pass; every bar in the finale, every 2 in pass 3
            if i == 0 or (p == 3) or (p == 2 and i % 2 == 0):
                drums.note(t, CRASH if b % 2 == 0 else CRASH2, TPB, 120)
            # fills into the next pass
            if i == 7:
                if p == 0:
                    for k in range(4):
                        drums.note(t + 3 * TPB + k * TPB // 4, SNARE, TPB // 4, 80 + 10 * k)
                elif p in (1, 2):
                    for k in range(8):
                        drums.note(t + 2 * TPB + k * TPB // 4, SNARE if k < 4 else TOMS[k - 2], TPB // 4, 96 + 4 * k)
                else:                                # the finale's last bar: a big tom roll home
                    for k in range(16):
                        drums.note(t + k * TPB // 4, TOMS[min(5, k // 3)], TPB // 4, 100 + k)
    write("bonus_main", bpm, 4, bars, [choir, choir2, accord, fiddle, bass, pbass, dist, lead, drums],
          {"choir": 0.75, "choir2": 0.5, "accord": 0.7, "fiddle": 0.62, "bass": 0.8, "pbass": 0.72,
           "dist": 0.48, "lead": 0.55, "drums": 0.82},
          {"choir": 140, "choir2": 140, "accord": 120, "fiddle": 160, "dist": 90, "lead": 140},
          ["choir", "fiddle", "lead"], ["accord", "choir2", "dist"])


# ============================================================= the super bonus: original, 6/8
# E minor; (note, eighths), 6 eighths a bar. Original composition, 2026-10-31.
B3, E4_, Fs4, G4_, A4_, B4_, C5_, D5_, E5, D4_, Ds4, Ds5 = 59, 64, 66, 67, 69, 71, 72, 74, 76, 62, 63, 75
SUPER = [
    [(B3, 1), (E4_, 2), (E4_, 1), (Fs4, 1), (G4_, 1)],     # haul away, me bloody boys
    [(A4_, 2), (G4_, 1), (Fs4, 2), (E4_, 1)],
    [(D4_, 2), (Fs4, 1), (A4_, 2), (D5_, 1)],
    [(B4_, 3), (A4_, 1), (G4_, 1), (Fs4, 1)],
    [(B3, 1), (E4_, 2), (E4_, 1), (Fs4, 1), (G4_, 1)],
    [(A4_, 2), (B4_, 1), (C5_, 2), (B4_, 1)],
    [(A4_, 1), (G4_, 1), (Fs4, 1), (Ds4, 2), (Fs4, 1)],
    [(E4_, 5), (None, 1)],
    [(E5, 2), (D5_, 1), (B4_, 2), (G4_, 1)],               # chorus: fill the cup with red, red rum
    [(A4_, 2), (B4_, 1), (C5_, 3)],
    [(D5_, 2), (C5_, 1), (A4_, 2), (Fs4, 1)],
    [(B4_, 6)],
    [(E5, 2), (D5_, 1), (B4_, 2), (G4_, 1)],
    [(A4_, 2), (B4_, 1), (C5_, 2), (E5, 1)],
    [(Ds5, 2), (B4_, 1), (A4_, 1), (Fs4, 1), (Ds4, 1)],
    [(E4_, 3), (E4_, 1), (None, 2)],
]
SUPER_CHORDS = ["Em", "Am", "D", "G", "Em", "Am", "B7", "Em", "Em", "Am", "D", "G", "Em", "Cmaj", "B7", "Em"]
AEOLIAN = {4, 6, 7, 9, 11, 0, 2}


def super_shanty():
    # ---- intro: the lone voice, low and dark
    bpm, bars = 132, 16                             # crotchet 132 = dotted crotchet 88
    bar = 3 * TPB
    voice = Part("voice", 53, 0, 112, 104)
    for loop in range(LOOPS):
        for b, line in enumerate(SUPER):
            t = (loop * bars + b) * bar
            play(voice, t, line, E, 94 if b < 8 else 102, shift=-12)
            for k in range(6):
                voice.cc(t + k * E, 11, 90 + 32 * (1 - abs(k - 2.5) / 2.5))
    write("super_intro", bpm, 3, bars, [voice], {"voice": 1.0}, {"voice": 80}, ["voice"], ["voice"])

    # ---- main: dotted crotchet 104, 3 passes of 16 bars
    bpm, bars = 156, 48
    choir = Part("choir", 52, 0, 112, 60)
    choir2 = Part("choir2", 52, 1, 98, 60)
    accord = Part("accord", 21, 2, 104, 35)
    fiddle = Part("fiddle", 110, 3, 110, 45)
    bass = Part("bass", 32, 4, 108, 20)
    pbass = Part("pbass", 34, 5, 106, 15)
    dist = Part("dist", 30, 6, 102, 18)
    lead = Part("lead", 29, 7, 110, 40)
    drums = Part("drums", 0, 9, 118, 30)
    D3 = 3 * E                                       # a dotted crotchet: the 6/8 beat
    for loop in range(LOOPS):
        for b in range(bars):
            t = (loop * bars + b) * bar
            p, i = b // 16, b % 16
            line = SUPER[i]
            c0, c1, c2, root = CHD[SUPER_CHORDS[i]]
            play(choir, t, line, E, 94 + 8 * p)
            play(choir, t, line, E, 86 + 8 * p, shift=-12)
            if p >= 1:
                play(choir2, t, [(None if n is None else third_below(n, AEOLIAN), u) for n, u in line], E, 82 + 6 * p)
            for h in range(2):                       # two dotted-crotchet beats a bar
                th = t + h * D3
                av = 98 if p < 2 else 76
                accord.note(th, root + 12, E * 2 - 30, av + 6)
                for n in (c0, c1, c2):
                    accord.note(th + 2 * E, n + 12, E - 30, av)
                if p == 1:
                    bass.note(th, root, D3 - 20, 106)
                if p == 2:                           # metal: galloping 6/8 chug
                    for k in range(3):
                        acc = k == 0
                        pbass.note(th + k * E, root, E - 20, 112 if acc else 98)
                        for n in (root + 12, root + 19, root + 24):
                            dist.note(th + k * E, n, E - 15, 114 if acc else 100)
                    for n in (c0 + 12, c1 + 12, c2 + 12):
                        choir2.note(th, n, D3, 86)
            if p == 1:
                tt = t
                for n, u in line:
                    if n is not None:
                        if u == 1 and random.random() < 0.4:
                            fiddle.note(tt, n + 14, 40, 92, human=False)
                            fiddle.note(tt + 40, n + 12, u * E - 40, 106)
                        else:
                            fiddle.note(tt, n + 12, u * E, 106)
                    tt += u * E
            if p == 2:
                play(fiddle, t, line, E, 100, shift=24, legato=0.9)
                play(lead, t, line, E, 118, shift=12, legato=0.95)
                play(lead, t, line, E, 102, legato=0.95)
            # drums, per dotted-crotchet beat
            for h in range(2):
                th = t + h * D3
                if p == 0:
                    drums.note(th, KICK2, E, 114)
                    drums.note(th + 2 * E, CLAP, E, 96)
                elif p == 1:
                    drums.note(th, KICK, E, 112)
                    if h == 1:
                        drums.note(th, SNARE, E, 110)
                    for k in range(3):
                        drums.note(th + k * E, TAMB, E, 84 if k == 0 else 66)
                else:
                    if h == 1:
                        drums.note(th, SNARE, E, 124)
                    for k in range(3):
                        drums.note(th + k * E, RIDE, E, 98 if k == 0 else 80)
                    for k in range(6):               # double kick in sixteenths
                        drums.note(th + k * E // 2, KICK, E // 2, 116 if k == 0 else 100)
            if i == 0 or (p == 2 and i % 2 == 0):
                drums.note(t, CRASH if b % 4 == 0 else CRASH2, TPB, 122)
            if i == 15:
                if p < 2:
                    for k in range(6):
                        drums.note(t + k * E, SNARE if k < 3 else TOMS[k - 1], E, 96 + 5 * k)
                else:
                    for k in range(12):
                        drums.note(t + k * E // 2, TOMS[min(5, k // 2)], E // 2, 102 + k)
    write("super_main", bpm, 3, bars, [choir, choir2, accord, fiddle, bass, pbass, dist, lead, drums],
          {"choir": 0.75, "choir2": 0.5, "accord": 0.68, "fiddle": 0.6, "bass": 0.8, "pbass": 0.72,
           "dist": 0.5, "lead": 0.56, "drums": 0.84},
          {"choir": 140, "choir2": 140, "accord": 120, "fiddle": 160, "dist": 90, "lead": 140},
          ["choir", "fiddle", "lead"], ["accord", "choir2", "dist"])


drunken_sailor()
super_shanty()
