import _ from 'lodash';

import { recordBookEvent, checkIsMultipleRevealEvents, type BookEventHandlerMap } from 'utils-book';
import { stateBet } from 'state-shared';

import { eventEmitter } from './eventEmitter';
import { playBookEvent } from './utils';
import { winLevelMap, type WinLevel, type WinLevelData, type WinLevelAlias } from './winLevelMap';
import { stateGame, stateGameDerived } from './stateGame.svelte';
import { startsInFeature } from './constants';
import type { BookEvent, BookEventOfType, BookEventContext } from './typesBookEvent';
import type { Position } from './types';
import { clusterSfx, ALL_MUSIC, type SoundEffectName, type WinMusicName } from './sound';

// big/mega/epic get their own applause recording; superwin and max fall back
// to the generic sfx_applause loop.
export const WIN_LEVEL_APPLAUSE_SFX: Partial<Record<WinLevelAlias, SoundEffectName>> = {
	big: 'sfx_applause_big',
	mega: 'sfx_applause_mega',
	epic: 'sfx_applause_epic',
};

/**
 * The applause loop a tier starts, or undefined if that tier doesn't applaud.
 * Only the celebration tiers (`type: 'big'` - big/superwin/mega/epic/max, the
 * ones that get a banner) do; a regular win rings a bell instead.
 *
 * Whatever stops the loop has to agree with whatever started it, or the
 * applause outlives the win - that mismatch is exactly how the tier-specific
 * keys once got left looping forever.
 */
export const winLevelApplauseSfx = (winLevelData?: WinLevelData): SoundEffectName | undefined =>
	winLevelData?.type === 'big'
		? (WIN_LEVEL_APPLAUSE_SFX[winLevelData.alias] ?? 'sfx_applause')
		: undefined;

let activeApplauseSfx: SoundEffectName | undefined;
let activeWinMusic: WinMusicName | undefined;

const fadeAllMusic = (from: number, to: number, duration: number) =>
	ALL_MUSIC.forEach((name) => eventEmitter.broadcast({ type: 'soundFade', name, from, to, duration }));

/** bonus: the bonuses' set (in free spins, or the TOTAL HAUL after them) */
const winLevelSoundsPlay = ({ winLevelData, bonus = stateGame.gameType === 'freeSpins' }: { winLevelData: WinLevelData; bonus?: boolean }) => {
	if (winLevelData?.alias === 'max') eventEmitter.broadcastAsync({ type: 'uiHide' });
	if (winLevelData?.sound?.sfx) {
		eventEmitter.broadcast({ type: 'soundOnce', name: winLevelData.sound.sfx });
	}
	if (winLevelData?.sound?.bgm) {
		eventEmitter.broadcast({ type: 'soundMusic', name: winLevelData.sound.bgm });
	}
	// The celebration tiers get their own music, bigger each tier, over the ducked loop;
	// it rings out on its own when the count-up ends
	if (winLevelData?.type === 'big') {
		activeWinMusic = `bgm_win_${winLevelData.alias as 'big'}${bonus ? '_fs' : ''}` as WinMusicName;
		fadeAllMusic(1, 0, 150);
		eventEmitter.broadcast({ type: 'soundOnce', name: activeWinMusic, forcePlay: true });
	}
	// The celebration tiers applaud through the whole count-up. A regular win
	// gets two strikes of a bell instead - level 1 is "zero", silent.
	activeApplauseSfx = winLevelApplauseSfx(winLevelData);
	if (activeApplauseSfx) {
		eventEmitter.broadcast({ type: 'soundLoop', name: activeApplauseSfx });
	} else if (winLevelData?.level > 1) {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_win_bell' });
	}
};

const winLevelSoundsStop = ({ featureOver = false } = {}) => {
	if (activeApplauseSfx) {
		eventEmitter.broadcast({ type: 'soundStop', name: activeApplauseSfx });
		activeApplauseSfx = undefined;
	}
	if (activeWinMusic) {
		// the win track's last chord keeps ringing while the loop comes back up under it
		const name = activeWinMusic;
		activeWinMusic = undefined;
		fadeAllMusic(0, 1, 900);
		setTimeout(() => {
			if (activeWinMusic !== name) eventEmitter.broadcast({ type: 'soundStop', name });
		}, 2500);
	}
	// featureOver: the bonus has just ended. A bought bonus leaves the buy mode active,
	// so the mode check alone kept the bonus track playing on into the base game.
	if (!featureOver && (startsInFeature(stateBet.activeBetModeKey) || stateGame.gameType === 'freeSpins')) {
		eventEmitter.broadcast({ type: 'soundBonusMusic' });
	} else {
		// the next bonus starts again from its calm intro
		if (featureOver) eventEmitter.broadcast({ type: 'soundBonusMusicReset' });
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
	}
	eventEmitter.broadcastAsync({ type: 'uiShow' });
};

const animateSymbols = async ({ positions }: { positions: Position[] }) => {
	eventEmitter.broadcast({ type: 'boardShow' });
	await eventEmitter.broadcastAsync({
		type: 'boardWithAnimateSymbols',
		symbolPositions: positions,
	});
};

const _wrap = (m) => m;

export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = _wrap({
	reveal: async (bookEvent: BookEventOfType<'reveal'>, { bookEvents }: BookEventContext) => {
		eventEmitter.broadcast({ type: 'tumbleWinAmountReset' });
		eventEmitter.broadcast({ type: 'boardShow' });
		const isBonusGame = checkIsMultipleRevealEvents({ bookEvents });
		if (isBonusGame) {
			eventEmitter.broadcast({ type: 'stopButtonEnable' });
			recordBookEvent({ bookEvent });
		}

		// the math names the bonus reveals 'freegame', the front end 'freeSpins': taken raw,
		// every gameType === 'freeSpins' check failed in the bonus (big wins brought back the
		// base music and the base win set)
		stateGame.gameType = bookEvent.gameType === 'basegame' ? 'basegame' : 'freeSpins';
		await stateGameDerived.enhancedBoard.spin({ revealEvent: bookEvent });
		eventEmitter.broadcast({ type: 'soundScatterCounterClear' });
	},
	winInfo: async (bookEvent: BookEventOfType<'winInfo'>) => {
		const gm = Math.max(1, ...bookEvent.wins.map((w: any) => Number(w?.meta?.globalMult ?? 1)));
		eventEmitter.broadcast({ type: 'globalMultiplierUpdate', multiplier: gm });
		const promise1 = async () => {
			// the cluster hits: a bass thump, a brass ching and a wet slap (one of three takes)
			eventEmitter.broadcast({ type: 'soundOnce', name: clusterSfx('hit') });
			await animateSymbols({ positions: _.flatten(bookEvent.wins.map((win) => win.positions)) });
		};

		const promise2 = async () => {
			await eventEmitter.broadcastAsync({
				type: 'showClusterWinAmounts',
				wins: bookEvent.wins.map((win) => {
					return {
						win: win.meta.winWithoutMult,
						mult: win.meta.globalMult,
						result: win.meta.winWithoutMult * win.meta.globalMult,
						reel: win.meta.overlay.reel,
						row: win.meta.overlay.row,
					};
				}),
			});
		};

		await Promise.all([promise1(), promise2()]);
	},
	updateTumbleWin: async (bookEvent: BookEventOfType<'updateTumbleWin'>) => {
		if (bookEvent.amount > 0) {
			eventEmitter.broadcast({ type: 'tumbleWinAmountShow' });
			eventEmitter.broadcast({
				type: 'tumbleWinAmountUpdate',
				amount: bookEvent.amount,
				animate: false,
			});
		}
	},
	updateGrid: async (bookEvent: BookEventOfType<'updateGrid'>) => {
  if (bookEvent.globalMultiplier != null) eventEmitter.broadcast({ type: 'globalMultiplierUpdate', multiplier: bookEvent.globalMultiplier });
 },
	setTotalWin: async (bookEvent: BookEventOfType<'setTotalWin'>) => {
		stateBet.winBookEventAmount = bookEvent.amount;
	},
	freeSpinTrigger: async (bookEvent: BookEventOfType<'freeSpinTrigger'>) => {
		// animate scatters
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
		await animateSymbols({ positions: bookEvent.positions });
		// the storm rolls in (StormCinematic + Background), then the free spin intro
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		await eventEmitter.broadcastAsync({ type: 'stormCinematic' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'jng_intro_fs' });
		eventEmitter.broadcast({ type: 'soundBonusMusic' });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinIntroUpdate',
			totalFreeSpins: bookEvent.totalFs,
		});
		stateGame.gameType = 'freeSpins';
		eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
		eventEmitter.broadcast({ type: 'boardFrameGlowShow' });
		eventEmitter.broadcast({ type: 'globalMultiplierShow' });
		await eventEmitter.broadcastAsync({
			type: 'globalMultiplierUpdate',
			multiplier: 1, // resets when multiplier === 1
		});
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: undefined,
			total: bookEvent.totalFs,
		});
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerButtonShow' });
		eventEmitter.broadcast({ type: 'drawerFold' });
	},
	updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
		// the first free spin: the music drops and lightning strikes (once per bonus)
		eventEmitter.broadcast({ type: 'soundBonusMusicDrop' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({
			type: 'freeSpinCounterUpdate',
			current: bookEvent.amount,
			total: bookEvent.total,
		});
	},
	updateGlobalMult: async (bookEvent: BookEventOfType<'updateGlobalMult'>) => {
		eventEmitter.broadcast({ type: 'globalMultiplierShow' });
		if (bookEvent.globalMult === 1) {
			eventEmitter.broadcast({ type: 'tumbleWinAmountReset' });
			eventEmitter.broadcast({ type: 'boardShow' });
		}
		await eventEmitter.broadcastAsync({
			type: 'globalMultiplierUpdate',
			multiplier: bookEvent.globalMult, // resets when multiplier === 1
		});
	},
	freeSpinEnd: async (bookEvent: BookEventOfType<'freeSpinEnd'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		stateGame.gameType = 'basegame';
		eventEmitter.broadcast({ type: 'boardFrameGlowHide' });
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		// clear the in-feature HUD before TOTAL HAUL, not after it - they used to sit
		// under the outro (a stale "FREE SPIN 8 OF 8" and a TUMBLE WIN of $0.00)
		eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_youwon_panel' });
		winLevelSoundsPlay({ winLevelData, bonus: true });
		await eventEmitter.broadcastAsync({
			type: 'freeSpinOutroCountUp',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop({ featureOver: true });
		eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
		eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		eventEmitter.broadcast({ type: 'drawerButtonHide' });
	},
	boardMultiplierInfo: async (bookEvent: BookEventOfType<'boardMultiplierInfo'>) => {
		eventEmitter.broadcast({ type: 'tumbleWinAmountShow' });
		await eventEmitter.broadcastAsync({
			type: 'tumbleWinAmountUpdate',
			amount: bookEvent.winInfo.tumbleWin,
			animate: false,
		});
		eventEmitter.broadcast({ type: 'multiplierBoardShow' });
		eventEmitter.broadcast({ type: 'multiplierBoardInit' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'tumble_win_4' });
		await eventEmitter.broadcastAsync({ type: 'multiplierBoardAnimate' });
		eventEmitter.broadcast({ type: 'boardWithMovingMultiplierTexts' });
		await eventEmitter.broadcastAsync({ type: 'multiplierBoardMove' });
		eventEmitter.broadcast({ type: 'multiplierBoardReset' });
		eventEmitter.broadcast({ type: 'multiplierBoardHide' });
		eventEmitter.broadcast({ type: 'multiplierTotalShow' });
		eventEmitter.broadcast({
			type: 'multiplierTotalUpdate',
			totalMultiplier: bookEvent.winInfo.boardMult,
		});
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_win' });
		await eventEmitter.broadcastAsync({ type: 'multiplierTotalAnimate' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_a' });
		eventEmitter.broadcast({ type: 'multiplierTotalHide' });
		await eventEmitter.broadcastAsync({
			type: 'tumbleWinAmountUpdate',
			amount: bookEvent.winInfo.totalWin,
			animate: true,
		});
	},
	tumbleBoard: async (bookEvent: BookEventOfType<'tumbleBoard'>) => {
		eventEmitter.broadcast({ type: 'boardHide' });
		eventEmitter.broadcast({ type: 'tumbleBoardShow' });
		eventEmitter.broadcast({ type: 'tumbleBoardInit', addingBoard: bookEvent.newSymbols });
		// the winning symbols burst: a wet splat over a water splash, synced to the blood-burst
		eventEmitter.broadcast({ type: 'soundOnce', name: clusterSfx('burst') });
		await eventEmitter.broadcastAsync({
			type: 'tumbleBoardExplode',
			explodingPositions: bookEvent.explodingSymbols,
		});
		eventEmitter.broadcast({ type: 'tumbleBoardRemoveExploded' });
		await eventEmitter.broadcastAsync({ type: 'tumbleBoardSlideDown' });
		eventEmitter.broadcast({
			type: 'boardSettle',
			board: stateGameDerived
				.tumbleBoardCombined()
				.map((tumbleReel) => tumbleReel.map((tumbleSymbol) => tumbleSymbol.rawSymbol)),
		});
		eventEmitter.broadcast({ type: 'tumbleBoardReset' });
		eventEmitter.broadcast({ type: 'tumbleBoardHide' });
		eventEmitter.broadcast({ type: 'boardShow' });
	},
	setWin: async (bookEvent: BookEventOfType<'setWin'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];

		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({
			type: 'winUpdate',
			amount: bookEvent.amount,
			winLevelData,
		});
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	finalWin: async (bookEvent: BookEventOfType<'finalWin'>) => {
		eventEmitter.broadcast({ type: 'globalMultiplierHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
	},
	// customised
	createBonusSnapshot: async (bookEvent: BookEventOfType<'createBonusSnapshot'>) => {
		const { bookEvents } = bookEvent;

		function findLastBookEvent<T>(type: T) {
			return _.findLast(bookEvents, (bookEvent) => bookEvent.type === type) as
				| BookEventOfType<T>
				| undefined;
		}

		const lastFreeSpinTriggerEvent = findLastBookEvent('freeSpinTrigger' as const);
		const lastUpdateFreeSpinEvent = findLastBookEvent('updateFreeSpin' as const);
		const lastSetTotalWinEvent = findLastBookEvent('setTotalWin' as const);
		const lastUpdateGlobalMultEvent = findLastBookEvent('updateGlobalMult' as const);

		if (lastFreeSpinTriggerEvent) await playBookEvent(lastFreeSpinTriggerEvent, { bookEvents });
		if (lastUpdateFreeSpinEvent) playBookEvent(lastUpdateFreeSpinEvent, { bookEvents });
		if (lastSetTotalWinEvent) playBookEvent(lastSetTotalWinEvent, { bookEvents });
		if (lastUpdateGlobalMultEvent) playBookEvent(lastUpdateGlobalMultEvent, { bookEvents });
	},
});
