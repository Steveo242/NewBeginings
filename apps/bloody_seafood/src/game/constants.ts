import _ from 'lodash';

import type { RawSymbol, SymbolState } from './types';

export const SYMBOL_SIZE = 100;

export const REEL_PADDING = 0.53;

// initial board (padded top and bottom)
export const INITIAL_BOARD: RawSymbol[][] = [
	[
		{ name: 'L3' },
		{ name: 'L2' },
		{ name: 'L2' },
		{ name: 'H3' },
		{ name: 'H2' },
		{ name: 'L1' },
		{ name: 'H4' },
		{ name: 'L3' },
		{ name: 'L2' },
	],
	[
		{ name: 'L1' },
		{ name: 'L3' },
		{ name: 'L3' },
		{ name: 'L3' },
		{ name: 'H3' },
		{ name: 'H1' },
		{ name: 'H1' },
		{ name: 'L3' },
		{ name: 'H2' },
	],
	[
		{ name: 'L3' },
		{ name: 'L3' },
		{ name: 'L1' },
		{ name: 'H4' },
		{ name: 'L3' },
		{ name: 'L2' },
		{ name: 'H4' },
		{ name: 'H4' },
		{ name: 'H1' },
	],
	[
		{ name: 'L3' },
		{ name: 'H1' },
		{ name: 'L2' },
		{ name: 'H2' },
		{ name: 'L2' },
		{ name: 'H3' },
		{ name: 'H1' },
		{ name: 'H1' },
		{ name: 'H1' },
	],
	[
		{ name: 'H4' },
		{ name: 'L1' },
		{ name: 'H4' },
		{ name: 'H3' },
		{ name: 'H1' },
		{ name: 'L3' },
		{ name: 'H4' },
		{ name: 'H1' },
		{ name: 'L2' },
	],
	[
		{ name: 'L2' },
		{ name: 'L3' },
		{ name: 'L2' },
		{ name: 'L2' },
		{ name: 'L1' },
		{ name: 'H1' },
		{ name: 'H2' },
		{ name: 'L3' },
		{ name: 'L1' },
	],
	[
		{ name: 'L1' },
		{ name: 'L2' },
		{ name: 'H1' },
		{ name: 'H3' },
		{ name: 'L3' },
		{ name: 'H3' },
		{ name: 'H4' },
		{ name: 'L2' },
		{ name: 'H1' },
	],
];

export const BOARD_DIMENSIONS = { x: INITIAL_BOARD.length, y: INITIAL_BOARD[0].length - 2 };

export const BOARD_SIZES = {
	width: SYMBOL_SIZE * BOARD_DIMENSIONS.x,
	height: SYMBOL_SIZE * BOARD_DIMENSIONS.y,
};

export const BACKGROUND_RATIO = 2039 / 1000;
export const PORTRAIT_BACKGROUND_RATIO = 1242 / 2208;
const PORTRAIT_RATIO = 800 / 1422;
const LANDSCAPE_RATIO = 1600 / 900;
const DESKTOP_RATIO = 1422 / 800;

const DESKTOP_HEIGHT = 800;
const LANDSCAPE_HEIGHT = 900;
const PORTRAIT_HEIGHT = 1422;
export const DESKTOP_MAIN_SIZES = { width: DESKTOP_HEIGHT * DESKTOP_RATIO, height: DESKTOP_HEIGHT };
export const LANDSCAPE_MAIN_SIZES = {
	width: LANDSCAPE_HEIGHT * LANDSCAPE_RATIO,
	height: LANDSCAPE_HEIGHT,
};
export const PORTRAIT_MAIN_SIZES = {
	width: PORTRAIT_HEIGHT * PORTRAIT_RATIO,
	height: PORTRAIT_HEIGHT,
};

export const HIGH_SYMBOLS = ['H1', 'H2', 'H3', 'H4', 'H5'];

export const INITIAL_SYMBOL_STATE: SymbolState = 'static';

const M_SIZE = 0.3;
const HIGH_SYMBOL_SIZE = 0.9;
const LOW_SYMBOL_SIZE = 0.9;
const SPECIAL_SYMBOL_SIZE = 1;

const SPIN_OPTIONS_SHARED = {
	reelFallInDelay: 80,
	reelPaddingMultiplierNormal: 1.25,
	reelPaddingMultiplierAnticipated: 18,
	reelFallOutDelay: 145,
};

export const SPIN_OPTIONS_DEFAULT = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 3.5,
	symbolFallInInterval: 30,
	symbolFallInBounceSpeed: 0.15,
	symbolFallInBounceSizeMulti: 0.5,
	symbolFallOutSpeed: 3.5,
	symbolFallOutInterval: 20,
};

export const SPIN_OPTIONS_FAST = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 7,
	symbolFallInInterval: 0,
	symbolFallInBounceSpeed: 0.3,
	symbolFallInBounceSizeMulti: 0.25,
	symbolFallOutSpeed: 7,
	symbolFallOutInterval: 0,
};

export const MOTION_BLUR_VELOCITY = 31;

export const zIndexes = {
	background: {
		backdrop: -3,
		normal: -2,
		feature: -1,
	},
};

const explosion = {
	type: 'spine',
	assetKey: 'explosion',
	animationName: 'explosion',
	sizeRatios: { width: 1, height: 1 },
};

const h1Static = { type: 'sprite', assetKey: 'h1.webp', sizeRatios: { width: 1, height: 1 } };
const h2Static = { type: 'sprite', assetKey: 'h2.webp', sizeRatios: { width: 1, height: 1 } };
const h3Static = { type: 'sprite', assetKey: 'h3.webp', sizeRatios: { width: 1, height: 1 } };
const h4Static = { type: 'sprite', assetKey: 'h4.webp', sizeRatios: { width: 1, height: 1 } };
const h5Static = { type: 'sprite', assetKey: 'h5.webp', sizeRatios: { width: 1, height: 1 } };

const l1Static = { type: 'sprite', assetKey: 'l1.webp', sizeRatios: { width: 1, height: 1 } };
const l2Static = { type: 'sprite', assetKey: 'l2.webp', sizeRatios: { width: 1, height: 1 } };
const l3Static = { type: 'sprite', assetKey: 'l3.webp', sizeRatios: { width: 1, height: 1 } };
const l4Static = { type: 'sprite', assetKey: 'l4.webp', sizeRatios: { width: 1, height: 1 } };

const sStatic = { type: 'sprite', assetKey: 's.png', sizeRatios: { width: 1, height: 1 } };
const wStatic = { type: 'sprite', assetKey: 'w.png', sizeRatios: { width: 1, height: 1 } };

const m2Static = {
	type: 'sprite',
	assetKey: 'm1_2x.png',
	sizeRatios: { width: 0.88, height: 0.88 },
};
const m4Static = {
	type: 'sprite',
	assetKey: 'm1_4x.png',
	sizeRatios: { width: 0.88, height: 0.88 },
};
const m5Static = { type: 'sprite', assetKey: 'm2_5x.png', sizeRatios: { width: 1, height: 1 } };
const m7Static = { type: 'sprite', assetKey: 'm2_7x.png', sizeRatios: { width: 1, height: 1 } };
const m10Static = { type: 'sprite', assetKey: 'm3_10x.png', sizeRatios: { width: 1, height: 1 } };

const wSizeRatios = { width: 1.5 * 0.9, height: SPECIAL_SYMBOL_SIZE * 1.15 };
const sSizeRatios = { width: 2.5, height: SPECIAL_SYMBOL_SIZE * 2.3 };

// Static-only Rust radial glow (spec s3: "sits behind, static position...
// no hard edges") - replaces the Spine 'low/mid/high_multiplier_static'
// animations for the states that only ever show a static frame anyway
// (static/spin/postWinStatic). 'win'/'land'/'explosion' stay on the Spine
// skeleton below untouched - those are real, still-working animations
// (the multiplier plate's landing flourish), not part of this redesign.
const backgroundLowStatic = {
	type: 'sprite',
	assetKey: 'mBackgroundLow',
	sizeRatios: { width: M_SIZE, height: M_SIZE },
};
const backgroundMidStatic = {
	type: 'sprite',
	assetKey: 'mBackgroundMid',
	sizeRatios: { width: M_SIZE, height: M_SIZE },
};
const backgroundHighStatic = {
	type: 'sprite',
	assetKey: 'mBackgroundHigh',
	sizeRatios: { width: M_SIZE, height: M_SIZE },
};

const backgroundLow = {
	explosion,
	win: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'low_multiplier_pay',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
	postWinStatic: backgroundLowStatic,
	static: backgroundLowStatic,
	spin: backgroundLowStatic,
	land: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'low_multiplier_land',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
};

const backgroundMid = {
	explosion,
	win: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'mid_multiplier_pay',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
	postWinStatic: backgroundMidStatic,
	static: backgroundMidStatic,
	spin: backgroundMidStatic,
	land: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'mid_multiplier_land',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
};

const backgroundHigh = {
	explosion,
	win: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'high_multiplier_pay',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
	postWinStatic: backgroundHighStatic,
	static: backgroundHighStatic,
	spin: backgroundHighStatic,
	land: {
		type: 'spine',
		assetKey: 'M',
		animationName: 'high_multiplier_land',
		sizeRatios: { width: M_SIZE, height: M_SIZE },
	},
};

export const SYMBOL_INFO_MAP = {
	H1: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'H1_win',
			sizeRatios: { width: 0.5 * 1.15, height: HIGH_SYMBOL_SIZE * 0.57 },
		},
		postWinStatic: h1Static,
		static: h1Static,
		spin: h1Static,
		land: h1Static,
	},
	H2: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'H2_win',
			sizeRatios: { width: 0.5, height: HIGH_SYMBOL_SIZE * 0.57 },
		},
		postWinStatic: h2Static,
		static: h2Static,
		spin: h2Static,
		land: h2Static,
	},
	H3: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'H3_win',
			sizeRatios: { width: 0.5 * 0.9, height: HIGH_SYMBOL_SIZE * 0.53 },
		},
		postWinStatic: h3Static,
		static: h3Static,
		spin: h3Static,
		land: h3Static,
	},
	H4: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'H4_win',
			sizeRatios: { width: 0.5 * 0.9, height: HIGH_SYMBOL_SIZE * 0.53 },
		},
		postWinStatic: h4Static,
		static: h4Static,
		spin: h4Static,
		land: h4Static,
	},
	H5: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'H5_win',
			sizeRatios: { width: 0.5 * 0.9, height: HIGH_SYMBOL_SIZE * 0.53 },
		},
		postWinStatic: h5Static,
		static: h5Static,
		spin: h5Static,
		land: h5Static,
	},
	L1: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'L1_win',
			sizeRatios: { width: 0.5 * 0.75, height: LOW_SYMBOL_SIZE * 0.65 },
		},
		postWinStatic: l1Static,
		static: l1Static,
		spin: l1Static,
		land: l1Static,
	},
	L2: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'L2_win',
			sizeRatios: { width: 0.5 * 0.75, height: LOW_SYMBOL_SIZE * 0.65 },
		},
		postWinStatic: l2Static,
		static: l2Static,
		spin: l2Static,
		land: l2Static,
	},
	L3: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'L3_win',
			sizeRatios: { width: 0.5 * 0.75, height: LOW_SYMBOL_SIZE * 0.63 },
		},
		postWinStatic: l3Static,
		static: l3Static,
		spin: l3Static,
		land: l3Static,
	},
	L4: {
		explosion,
		win: {
			type: 'spriteSheet',
			assetKey: 'L4_win',
			sizeRatios: { width: 0.5 * 0.75, height: LOW_SYMBOL_SIZE * 0.63 },
		},
		postWinStatic: l4Static,
		static: l4Static,
		spin: l4Static,
		land: l4Static,
	},
	W: {
		explosion,
		postWinStatic: wStatic,
		static: wStatic,
		spin: wStatic,
		win: {
			type: 'spriteSheet',
			assetKey: 'W_win',
			sizeRatios: wStatic.sizeRatios,
		},
		land: wStatic,
	},
	S: {
		explosion,
		postWinStatic: sStatic,
		static: sStatic,
		spin: sStatic,
		win: {
			type: 'spriteSheet',
			assetKey: 'S_win',
			sizeRatios: sStatic.sizeRatios,
		},
		land: sStatic,
	},
	M_2: {
		explosion,
		postWinStatic: m2Static,
		static: m2Static,
		spin: m2Static,
		win: {
			type: 'spine',
			assetKey: 'M',
			animationName: '2x',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
		land: {
			type: 'spine',
			assetKey: 'M',
			animationName: '2x_land',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
	},
	M_4: {
		explosion,
		postWinStatic: m4Static,
		static: m4Static,
		spin: m4Static,
		win: {
			type: 'spine',
			assetKey: 'M',
			animationName: '4x',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
		land: {
			type: 'spine',
			assetKey: 'M',
			animationName: '4x_land',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
	},
	M_5: {
		explosion,
		postWinStatic: m5Static,
		static: m5Static,
		spin: m5Static,
		win: {
			type: 'spine',
			assetKey: 'M',
			animationName: '5x',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
		land: {
			type: 'spine',
			assetKey: 'M',
			animationName: '5x_land',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
	},
	M_7: {
		explosion,
		postWinStatic: m7Static,
		static: m7Static,
		spin: m7Static,
		win: {
			type: 'spine',
			assetKey: 'M',
			animationName: '7x',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
		land: {
			type: 'spine',
			assetKey: 'M',
			animationName: '7x_land',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
	},
	M_10: {
		explosion,
		postWinStatic: m10Static,
		static: m10Static,
		spin: m10Static,
		win: {
			type: 'spine',
			assetKey: 'M',
			animationName: '10x',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
		land: {
			type: 'spine',
			assetKey: 'M',
			animationName: '10x_land',
			sizeRatios: { width: M_SIZE, height: M_SIZE },
		},
	},
	M_TAKEN_2: backgroundLow,
	M_TAKEN_4: backgroundLow,
	M_TAKEN_5: backgroundMid,
	M_TAKEN_7: backgroundMid,
	M_TAKEN_10: backgroundHigh,
} as const;

export const MULTIPLIER_BACKGROUND_INFO_MAP = {
	M_2: backgroundLow,
	M_4: backgroundLow,
	M_5: backgroundMid,
	M_7: backgroundMid,
	M_10: backgroundHigh,
};

export const SCATTER_LAND_SOUND_MAP = {
	1: 'sfx_scatter_stop_1',
	2: 'sfx_scatter_stop_2',
	3: 'sfx_scatter_stop_3',
	4: 'sfx_scatter_stop_4',
	5: 'sfx_scatter_stop_5',
} as const;
