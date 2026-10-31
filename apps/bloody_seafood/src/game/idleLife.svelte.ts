/**
 * Between-spins tank life, shared by IdleLife (which drives it) and the pieces it nudges:
 * Caustics brightens with `ripple`, and the resting symbol in cell `breathCell` swells a
 * touch while `breath` runs 0 -> 1. Everything rests at zero while a round plays.
 */
export const idleLife = $state({
	/** 0..1, a slow light ripple through the caustics */
	ripple: 0,
	/** `${reel}:${row}` of the symbol taking a breath, '' for none */
	breathCell: '',
	/** 0..1 progress of that breath */
	breath: 0,
});
