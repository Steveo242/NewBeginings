import { SYMBOL_SIZE } from './constants';

// The free-spins HUD: the spin counter and the multiplier meter, stacked as one column of
// iron plaques. Positions are board-local (BoardContainer: the grid spans 0..7 symbols).
// On wide layouts the column stands in the open sky left of the tank - the tank's iron
// frame overhangs the grid by ~0.9 of a symbol, so it clears that plus a margin. Stacked
// (portrait) layouts have no side room, and the logo fills the strip right above the
// tank: the meter goes up into the open sky above the logo's right end.
export const HUD_PANEL_W = SYMBOL_SIZE * 2.7;
const FRAME_OVERHANG = SYMBOL_SIZE * 0.95;
const GAP = SYMBOL_SIZE * 0.35;

type HudContext = {
	stateLayoutDerived: { isStacked: () => boolean };
	stateGameDerived: { boardLayout: () => { width: number } };
};

export const hudColumn = (context: HudContext, slot: 'counter' | 'multiplier') => {
	if (context.stateLayoutDerived.isStacked()) {
		const x = context.stateGameDerived.boardLayout().width - HUD_PANEL_W * 0.5;
		return slot === 'counter'
			? { x: HUD_PANEL_W * 0.5, y: -SYMBOL_SIZE * 3.55 }
			: { x, y: -SYMBOL_SIZE * 3.55 };
	}
	const x = -FRAME_OVERHANG - GAP - HUD_PANEL_W * 0.5;
	return slot === 'counter' ? { x, y: SYMBOL_SIZE * 1.0 } : { x, y: SYMBOL_SIZE * 3.05 };
};
