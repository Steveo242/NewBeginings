import _ from 'lodash';
import { stateBet } from 'state-shared';
import { createPlayBookUtils } from 'utils-book';
import { createGetEmptyPaddedBoard } from 'utils-slots';

import {
	SYMBOL_SIZE,
	REEL_PADDING,
	SYMBOL_INFO_MAP,
	BOARD_DIMENSIONS,
	MULTIPLIER_BACKGROUND_INFO_MAP,
} from './constants';
import { eventEmitter } from './eventEmitter';
import type { Bet, BookEvent, BookEventOfType } from './typesBookEvent';
import { bookEventHandlerMap } from './bookEventHandlerMap';
import { prepareWins, winsReady } from './lazyWins';
import type { RawSymbol, SymbolState } from './types';

// general utils
export const { getEmptyBoard } = createGetEmptyPaddedBoard({ reelsDimensions: BOARD_DIMENSIONS });
export const { playBookEvent, playBookEvents } = createPlayBookUtils({ bookEventHandlerMap });
export const playBet = async (bet: Bet) => {
	stateBet.winBookEventAmount = 0;
	// this round's win sheets start decoding now, while the reels spin (game/lazyWins.ts)
	winsReady.promise = prepareWins(bet.state as BookEvent[]);
	await playBookEvents(bet.state);
	eventEmitter.broadcast({ type: 'stopButtonEnable' });
};

// resume bet
const BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT = [
	'updateGlobalMult',
	'freeSpinTrigger',
	'updateFreeSpin',
	'setTotalWin',
];

export const convertTorResumableBet = (betToResume: Bet) => {
	const resumingIndex = Number(betToResume.event);
	const bookEventsBeforeResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex < resumingIndex,
	);
	const bookEventsAfterResume = betToResume.state.filter(
		(_, eventIndex) => eventIndex >= resumingIndex,
	);

	const bookEventToCreateSnapshot: BookEventOfType<'createBonusSnapshot'> = {
		index: 0,
		type: 'createBonusSnapshot',
		bookEvents: bookEventsBeforeResume.filter((bookEvent) =>
			BOOK_EVENT_TYPES_TO_RESERVE_FOR_SNAPSHOT.includes(bookEvent.type),
		),
	};

	const stateToResume = [bookEventToCreateSnapshot, ...bookEventsAfterResume];

	return { ...betToResume, state: stateToResume };
};

// other utils
export const getSymbolX = (reelIndex: number) => SYMBOL_SIZE * (reelIndex + REEL_PADDING);
export const getSymbolY = (symbolIndexOfBoard: number) => (symbolIndexOfBoard + 0.5) * SYMBOL_SIZE;

export const getSymbolKey = ({ rawSymbol }: { rawSymbol: RawSymbol }) => {
	if (rawSymbol.multiplier !== undefined) {
		return `${rawSymbol.name}_${rawSymbol.multiplier}` as keyof typeof SYMBOL_INFO_MAP;
	}
	return rawSymbol.name as keyof typeof SYMBOL_INFO_MAP;
};

export const getSymbolInfo = ({
	rawSymbol,
	state,
}: {
	rawSymbol: RawSymbol;
	state: SymbolState;
}) => {
	const symbolKey = getSymbolKey({ rawSymbol });
	const symbolInfoMap = SYMBOL_INFO_MAP[symbolKey];
	// 'win' is force-resolved to 'static' everywhere except spriteSheet-driven
	// symbols (see utils.ts history: this suppressed the old spine win
	// animations game-wide). Symbols still on spine keep that suppressed
	// behaviour until they're converted; spriteSheet symbols get their real
	// win animation.
	if (state === 'win' && symbolInfoMap.win.type === 'spriteSheet') {
		return symbolInfoMap.win;
	}
	const resolvedState = state === 'win' || state === 'postWinStatic' ? 'static' : state;
	return symbolInfoMap[resolvedState];
};

/** The rendered idle loop a resting symbol plays (v5), if it has one. */
export const getSymbolIdleInfo = ({ rawSymbol }: { rawSymbol: RawSymbol }) => {
	const map = SYMBOL_INFO_MAP[getSymbolKey({ rawSymbol })];
	return 'idle' in map ? map.idle : undefined;
};

export const getSymbolBackgroundInfo = ({
	rawSymbol,
	state,
}: {
	rawSymbol: RawSymbol;
	state: SymbolState;
}) => {
	if (rawSymbol.name === 'M') {
		const symbolKey = getSymbolKey({ rawSymbol }) as keyof typeof MULTIPLIER_BACKGROUND_INFO_MAP;
		return MULTIPLIER_BACKGROUND_INFO_MAP[symbolKey][state];
	}

	return null;
};
