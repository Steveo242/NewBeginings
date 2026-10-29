import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';

import { SYMBOL_SIZE } from './constants';

// The stacked (portrait / near-square) bet UI, measured from the canvas alone. The bar
// is sized first - to a fixed share of the screen - and the board is then placed in what
// is left (stateGame boardLayout). Sizing the bar to fill whatever band the board left
// under it is what let it grow to ~40% of a phone screen.
//
// Authored in UI_BASE_SIZE units: one row of controls, the spin dead centre and
// the bigger the more it matters, over a slim info strip.
//   [ BUY BONUS ]  [-]  ( SPIN )  [+]  [auto] [turbo]
//   [menu]      BALANCE      PLAY      WIN
const B = UI_BASE_SIZE;

export const STACKED = {
	B,
	SPIN: B * 2.0,
	/** play -/+ */
	STEP: B * 0.85,
	/** autoplay, turbo */
	SMALL: B * 0.85,
	/** the menu icon on the strip */
	ICON: B * 0.6,
	/** BarButton's buy plaque is 1.9 B wide; drawn at this factor in the row */
	BUY_K: 0.95,
	GAP: B * 0.2,
	STRIP_H: B * 0.78,
	ROW_PAD: B * 0.16,
};

/** half the row: the spin's centre to the outer edge of the buy plaque / turbo */
export const STACKED_HALF_W = Math.max(
	B * 1.9 * STACKED.BUY_K + STACKED.GAP * 2 + STACKED.STEP,
	STACKED.GAP * 2.6 + STACKED.STEP + STACKED.SMALL * 2,
);
export const STACKED_ROW_W = STACKED.SPIN + STACKED_HALF_W * 2;
export const STACKED_ROW_H = STACKED.SPIN * 1.04;
export const STACKED_H = STACKED.STRIP_H + STACKED_ROW_H + STACKED.ROW_PAD * 2;

/** the whole stacked bar may take at most this share of the screen height */
const MAX_HEIGHT_SHARE = 0.19;
const WIDTH_RATIO = 0.94;
const MAX_SCALE = 0.42;

export const stackedBar = (canvas: { width: number; height: number }) => {
	const scale = Math.min(
		(canvas.width * WIDTH_RATIO) / STACKED_ROW_W,
		(canvas.height * MAX_HEIGHT_SHARE) / STACKED_H,
		MAX_SCALE,
	);
	return { scale, height: STACKED_H * scale };
};

// The tank's vertical reach round the grid's centre, in board units: the logo banner
// over it (BoardBanner caps it at ~260 + margins) and the iron base under it.
const TANK_ABOVE = SYMBOL_SIZE * 3.5 + SYMBOL_SIZE * 2.9;
const TANK_BELOW = SYMBOL_SIZE * 3.5 + SYMBOL_SIZE * 1.5;
/** share of the spare height that goes above the tank (sky); the rest sits under it */
const SLACK_ABOVE = 0.95;

/**
 * Where the grid's centre goes on a stacked canvas, in canvas px. Short of room, the
 * tank keeps standing on the bar and the logo over it shrinks (BoardBanner fits itself
 * to the band left above the grid).
 */
export const stackedBoardCenterY = (canvas: { width: number; height: number }, mainScale: number) => {
	const room = canvas.height - stackedBar(canvas).height;
	const slack = Math.max(room - (TANK_ABOVE + TANK_BELOW) * mainScale, 0);
	const centre = room - slack * (1 - SLACK_ABOVE) - TANK_BELOW * mainScale;
	return Math.max(centre, (SYMBOL_SIZE * 3.5 + 20) * mainScale);
};
