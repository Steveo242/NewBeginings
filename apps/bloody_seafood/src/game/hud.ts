import { SYMBOL_SIZE } from './constants';
import { STACKED, STACKED_HALF_W, STACKED_ROW_H, stackedBar } from './barLayout';

// The free-spins HUD: the spin counter and the multiplier meter, stacked as one column of
// iron plaques. Positions are board-local (BoardContainer: the grid spans 0..7 symbols).
// On wide layouts the column stands in the open sky left of the tank - the tank's iron
// frame overhangs the grid by ~0.9 of a symbol, so it clears that plus a margin. Stacked
// (portrait) layouts have no side room, and the sky over the logo is gone on shorter
// phones (the meter sat off the top of the screen): there it takes the empty left half of
// the control row, where the bonus buy and play -/+ stand outside free spins, right over
// the strip's FREE SPINS count.
export const HUD_PANEL_W = SYMBOL_SIZE * 2.7;
const FRAME_OVERHANG = SYMBOL_SIZE * 0.95;
const GAP = SYMBOL_SIZE * 0.35;

type HudContext = {
	stateLayoutDerived: {
		isStacked: () => boolean;
		layoutType: () => string;
		canvasSizes: () => { width: number; height: number };
		mainLayout: () => { width: number; height: number; scale: number };
	};
	stateGameDerived: {
		boardLayout: () => { width: number; x: number; y: number; pivot: { x: number; y: number } };
	};
};

/** the multiplier meter's panel height, board units (GlobalMultiplier) */
export const HUD_PANEL_H = SYMBOL_SIZE * 1.8;

export const hudColumn = (
	context: HudContext,
	slot: 'counter' | 'multiplier',
): { x: number; y: number; scale?: number } => {
	if (context.stateLayoutDerived.isStacked() && slot === 'multiplier') {
		const canvas = context.stateLayoutDerived.canvasSizes();
		const main = context.stateLayoutDerived.mainLayout();
		const board = context.stateGameDerived.boardLayout();
		const { scale: sq, base } = stackedBar(canvas);
		// canvas px: the middle of the row left of the spin
		const cx = canvas.width * 0.5 - (STACKED.SPIN * 0.5 + STACKED_HALF_W * 0.5) * sq;
		const cy = base - (STACKED.STRIP_H + STACKED.ROW_PAD + STACKED_ROW_H * 0.5) * sq;
		// fit the panel in that slot (a little margin), never over its natural size
		const scale = Math.min(
			1,
			(STACKED_HALF_W * 0.92 * sq) / (HUD_PANEL_W * main.scale),
			(STACKED_ROW_H * 0.86 * sq) / (HUD_PANEL_H * main.scale),
		);
		// canvas -> MainContainer -> board-local
		const mx = (cx - canvas.width * 0.5) / main.scale + main.width * 0.5;
		const my = (cy - canvas.height * 0.5) / main.scale + main.height * 0.5;
		return { x: mx - board.x + board.pivot.x, y: my - board.y + board.pivot.y, scale };
	}
	if (context.stateLayoutDerived.isStacked()) {
		const x = context.stateGameDerived.boardLayout().width - HUD_PANEL_W * 0.5;
		return slot === 'counter'
			? { x: HUD_PANEL_W * 0.5, y: -SYMBOL_SIZE * 3.55 }
			: { x, y: -SYMBOL_SIZE * 3.55 };
	}
	const x = -FRAME_OVERHANG - GAP - HUD_PANEL_W * 0.5;
	// desktop / landscape phones: the left column holds balance, win and the menu, and the
	// counter rides in the play plate - the meter takes the bonus buy's spot at the top
	if (['landscape', 'desktop'].includes(context.stateLayoutDerived.layoutType())) return { x, y: SYMBOL_SIZE * 0.15 };
	return slot === 'counter' ? { x, y: SYMBOL_SIZE * 1.0 } : { x, y: SYMBOL_SIZE * 3.05 };
};
