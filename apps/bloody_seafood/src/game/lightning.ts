// The win outline's colours (WinFlash): a soft warm gold matching the brass UI, the same for
// every symbol so the set reads as one - a glow colour round a pale core. Per-symbol
// colours (the shark's red, the angelfish's pink) fought the deep blue water and the art.

export type Bolt = { glow: number; mid: number };

const GOLD: Bolt = { glow: 0xe8c26a, mid: 0xfff0c8 };

export const SYMBOL_BOLT: Record<string, Bolt> = {
	H1: GOLD,
	H2: GOLD,
	H3: GOLD,
	H4: GOLD,
	W: GOLD,
	S: GOLD,
	L1: GOLD,
	L2: GOLD,
	L3: GOLD,
};

export const isHighValue = (name: string) => ['H1', 'H2', 'H3', 'H4', 'W', 'S'].includes(name);

/** The storm's lightning, live: Background writes the strike's brightness (0..1) here every
 *  frame while the bonus storm is in, and the win outlines surge with it. */
export const storm = { pulse: 0 };
