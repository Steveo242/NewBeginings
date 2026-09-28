// The pulse every rhythmic animation locks to. The score has no drum beat; its bass band
// sits at ~88-100 BPM in the base game and ~91 in free spins, so 90 is the common pulse.
// Change it here and everything that breathes with the music follows.
export const BPM = 90;
export const BEAT_MS = 60000 / BPM;

/** 0..1 swell that peaks once every `beats` beats, phase-locked to one shared clock so
 *  every pulsing element on screen breathes together. */
export const pulse = (nowMs: number, beats = 2) => 0.5 - 0.5 * Math.cos((nowMs / (BEAT_MS * beats)) * Math.PI * 2);
