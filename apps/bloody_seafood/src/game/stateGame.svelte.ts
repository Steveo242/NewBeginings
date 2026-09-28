import _ from 'lodash';
import type { Tween } from 'svelte/motion';

import { stateBet } from 'state-shared';
import { createEnhanceBoard, createReelForCascading } from 'utils-slots';
import { createGetWinLevelDataByWinLevelAlias } from 'utils-shared/winLevel';

import type { GameType, RawSymbol, SymbolState } from './types';
import { stateLayoutDerived } from './stateLayout';
import { winLevelMap } from './winLevelMap';
import { eventEmitter } from './eventEmitter';
import {
	SYMBOL_SIZE,
	BOARD_SIZES,
	INITIAL_BOARD,
	BOARD_DIMENSIONS,
	SPIN_OPTIONS_DEFAULT,
	SPIN_OPTIONS_FAST,
	SPIN_OPTIONS_ANTICIPATED,
	INITIAL_SYMBOL_STATE,
} from './constants';

const PREMIUMS = ['H1', 'H2', 'H3', 'H4'];
const REEL_STOP_SFX = [
	'sfx_reel_stop_1',
	'sfx_reel_stop_2',
	'sfx_reel_stop_3',
	'sfx_reel_stop_4',
	'sfx_reel_stop_5',
] as const;

/** When a scatter last snapped the anticipation rope (Anticipations holds the strain off briefly after). */
export const rope = { snappedAt: -Infinity };

const onSymbolLand = ({
	rawSymbol,
	anticipating,
}: {
	rawSymbol: RawSymbol;
	anticipating: boolean;
}) => {
	// a heavy thump + iron clang; not forced, so a run of premiums landing together
	// plays one hit instead of stacking into a wall of noise
	if (PREMIUMS.includes(rawSymbol.name)) {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_premium_land' });
	}

	if (rawSymbol.name === 'S') {
		// a scatter dropping into a straining reel breaks the rope: the strain stops dead
		if (anticipating) {
			eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_rope_strain' });
			eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_rope_snap', forcePlay: true });
			rope.snappedAt = performance.now();
		}
		eventEmitter.broadcast({ type: 'soundScatterCounterIncrease' });
		eventEmitter.broadcast({
			type: 'soundOnce',
			name: 'sfx_scatter_toot',
		});
	}

	if (rawSymbol.name === 'M') {
		eventEmitter.broadcast({
			type: 'soundOnce',
			name: 'sfx_multiplier_landing',
		});
	}
};

const board = _.range(BOARD_DIMENSIONS.x).map((reelIndex) => {
	const reel = createReelForCascading({
		reelIndex,
		symbolHeight: SYMBOL_SIZE,
		initialSymbols: INITIAL_BOARD[reelIndex],
		initialSymbolState: INITIAL_SYMBOL_STATE,
		onReelStopping: () => {
			// stops 1-5 are one thud pitched up a step each (161 -> 238 Hz): climb them
			// across the seven reels instead of the same thud seven times
			eventEmitter.broadcast({
				type: 'soundOnce',
				name: REEL_STOP_SFX[Math.min(4, Math.round((reelIndex * 4) / (BOARD_DIMENSIONS.x - 1)))],
				forcePlay: !stateBet.isTurbo,
			});
		},
		onSymbolLand: ({ rawSymbol }) =>
			onSymbolLand({ rawSymbol, anticipating: reel.reelState.anticipating }),
	});

	reel.reelState.spinOptions = () =>
		reel.reelState.spinType === 'fast'
			? SPIN_OPTIONS_FAST
			: reel.reelState.spinType === 'anticipated'
				? SPIN_OPTIONS_ANTICIPATED
				: SPIN_OPTIONS_DEFAULT;

	return reel;
});

export type Reel = (typeof board)[number];
export type ReelSymbol = Reel['reelState']['symbols'][number];

export type TumbleSymbol = {
	symbolY: Tween<number>;
	rawSymbol: RawSymbol;
	symbolState: SymbolState;
	oncomplete: () => void;
};

export type MultiplierSymbol = {
	initX: number;
	initY: number;
	symbolX: Tween<number>;
	symbolY: Tween<number>;
	rawSymbol: RawSymbol;
	symbolState: SymbolState;
	oncomplete: () => void;
};

export const stateGame = $state({
	board,
	gameType: 'basegame' as GameType,
	tumbleBoardAdding: [] as TumbleSymbol[][],
	tumbleBoardBase: [] as TumbleSymbol[][],
	multiplierBoard: [] as (MultiplierSymbol | undefined)[][],
	scatterCounter: 0,
});

/**
 * Sits the board slightly above centre: the band below it carries the bet
 * bar and the band above it the title banner, and the bar needs the larger
 * share. Dead centre split them evenly and left the bar squeezed.
 */
const BOARD_CENTER_Y_RATIO = 0.47;

const boardLayout = () => ({
	x: stateLayoutDerived.mainLayout().width * 0.5,
	y: stateLayoutDerived.mainLayout().height * BOARD_CENTER_Y_RATIO,
	anchor: { x: 0.5, y: 0.5 },
	pivot: { x: BOARD_SIZES.width / 2, y: BOARD_SIZES.height / 2 },
	...BOARD_SIZES,
});

const boardRaw = () =>
	board.map((reel) => reel.reelState.symbols.map((reelSymbol) => reelSymbol.rawSymbol));

const tumbleBoardCombined = () => {
	const tumbleBoardCombined = stateGame.tumbleBoardBase.map((tumbleReelBase, reelIndex) => {
		const tumbleReelAdding = stateGame.tumbleBoardAdding[reelIndex] ?? [];
		return [...tumbleReelAdding, ...tumbleReelBase];
	});

	return tumbleBoardCombined;
};

const scatterLandIndex = () => {
	if (stateGame.scatterCounter > 5) return 5;
	if (stateGame.scatterCounter < 1) return 1;
	return stateGame.scatterCounter as 1 | 2 | 3 | 4 | 5;
};

const { enhanceBoard } = createEnhanceBoard();
const enhancedBoard = enhanceBoard({ board: stateGame.board });

// win levels

export const { getWinLevelDataByWinLevelAlias } = createGetWinLevelDataByWinLevelAlias({
	winLevelMap,
});

export const stateGameDerived = {
	onSymbolLand,
	boardLayout,
	boardRaw,
	tumbleBoardCombined,
	scatterLandIndex,
	enhancedBoard,
	getWinLevelDataByWinLevelAlias,
};
