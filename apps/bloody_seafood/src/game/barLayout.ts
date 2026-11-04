import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';

import { LOGO_ASPECT, SYMBOL_SIZE } from './constants';

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
	STRIP_H: B * 0.86,
	ROW_PAD: B * 0.16,
};

/** an amount plate (BetBar's LabelPlate, 424 wide) less its rim and padding: the caption
 *  and value shrink to fit this, so the plate never resizes */
export const PLATE_TEXT_W = 400 * 1.06 - 64;

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

/**
 * The device's safe-area insets (notch / camera cut-out, home bar) in CSS px, read from
 * env() through a probe - app.html sets viewport-fit=cover, so a phone that draws under
 * them reports them here. Zero inside the Stake frame and on desktop.
 */
let probe: HTMLDivElement | undefined;
export const safeInsets = () => {
	if (typeof document === 'undefined' || !document.body) return { top: 0, bottom: 0 };
	if (!probe) {
		probe = document.createElement('div');
		probe.style.cssText =
			'position:fixed;left:0;top:0;width:0;height:0;visibility:hidden;pointer-events:none;' +
			'padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)';
		document.body.appendChild(probe);
	}
	const style = getComputedStyle(probe);
	return { top: parseFloat(style.paddingTop) || 0, bottom: parseFloat(style.paddingBottom) || 0 };
};

export const stackedBar = (canvas: { width: number; height: number }) => {
	const scale = Math.min(
		(canvas.width * WIDTH_RATIO) / STACKED_ROW_W,
		(canvas.height * MAX_HEIGHT_SHARE) / STACKED_H,
		MAX_SCALE,
	);
	const { bottom } = safeInsets();
	/** the bar stands on the safe area's bottom edge (its strip backing still runs to the screen's) */
	return { scale, height: STACKED_H * scale, bottom, base: canvas.height - bottom };
};

// The tank's vertical reach round the grid's centre, in board units: the logo banner
// over it (BoardBanner: its height + a 10-unit gap over the grid) and the iron base under it.
const LOGO_GAP = 10;
const TANK_BELOW = SYMBOL_SIZE * 3.5 + SYMBOL_SIZE * 1.5;
/** portrait side margin for the logo, a share of the screen width */
const PORTRAIT_SIDE_MARGIN = 0.025;
/** sky kept over the logo, a share of the screen height */
const SKY_MIN = 0.03;
/**
 * The logo's width in board units. Portrait gives it the tank's full span (1.25 x the
 * grid), never wider than the screen less small margins; elsewhere 0.92 x the grid.
 */
export const logoMaxWidth = (portrait: boolean, canvasWidth: number, mainScale: number) =>
	portrait
		? Math.min(SYMBOL_SIZE * 7 * 1.25, (canvasWidth * (1 - PORTRAIT_SIDE_MARGIN * 2)) / mainScale)
		: SYMBOL_SIZE * 7 * 0.92;

/**
 * Where the grid's centre goes on a stacked canvas, in canvas px. v5.6: the logo + tank
 * group fills the screen between the top safe area and the bar - in portrait the main
 * scale is width-bound (stateLayout) and the logo grows to the screen's width, and the spare
 * height is split evenly over the logo (never less than SKY_MIN) and under the tank, so the
 * group sits centred in the space above the controls. (It used to nearly all go over the
 * logo: the board sat low under a band of empty sky.) Short of room, the tank keeps
 * standing on the bar and the logo over it shrinks (BoardBanner fits itself to the band
 * left above the grid).
 */
export const stackedBoardCenterY = (
	canvas: { width: number; height: number },
	mainScale: number,
	portrait: boolean,
) => {
	const bar = stackedBar(canvas);
	const top = safeInsets().top + canvas.height * SKY_MIN;
	const above = SYMBOL_SIZE * 3.5 + LOGO_GAP + logoMaxWidth(portrait, canvas.width, mainScale) / LOGO_ASPECT;
	const room = bar.base - bar.height - top;
	const slack = Math.max(room - (above + TANK_BELOW) * mainScale, 0);
	const centre = bar.base - bar.height - slack * 0.5 - TANK_BELOW * mainScale;
	return Math.max(centre, safeInsets().top + (SYMBOL_SIZE * 3.5 + 20) * mainScale);
};
