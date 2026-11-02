import * as PIXI from 'pixi.js';

import { stateApp } from './stateApp';
import assets from './assets';
import type { BookEvent } from './typesBookEvent';

/** every pack's frames in frame-name order (as pixi-svelte's spriteSheet processor) */
const framesOf = (sheet: PIXI.Spritesheet) => {
	const all: Record<string, PIXI.Texture> = Object.assign(
		{},
		...[sheet, ...(sheet.linkedSheets ?? [])].map((s) => s.textures),
	);
	return Object.keys(all)
		.sort()
		.map((name) => all[name]);
};

// The 512px win sheets are too big to keep every symbol's resident on a phone (~40 MB of
// GPU memory each), so they load per round: as soon as the bet's book is in - before the
// reels even start - every symbol the book will win with is fetched and decoded, and the
// rest are released. The lows win most often, so their sheets stay warm. They stay WebP:
// a Basis (UASTC) twin is ~2.3x the download, and with only a handful resident at a time
// the memory it would save matters far less than for the always-resident land/idle sheets.
const WARM = ['L1_win', 'L2_win', 'L3_win'];
export const LAZY_WIN_KEYS = ['H1_win', 'H2_win', 'H3_win', 'H4_win', 'L1_win', 'L2_win', 'L3_win', 'W_win', 'S_win'];

const loading = new Map<string, Promise<void>>();

const load = (key: string) => {
	if (stateApp.loadedAssets?.[key]) return Promise.resolve();
	if (!loading.has(key)) {
		const { src } = assets[key as keyof typeof assets] as { src: string };
		loading.set(
			key,
			PIXI.Assets.load<PIXI.Spritesheet>(src)
				.then((sheet) => {
					stateApp.loadedAssets = { ...stateApp.loadedAssets, [key]: framesOf(sheet) };
				})
				.catch((error) => console.error('win sheet', key, error))
				.finally(() => loading.delete(key)),
		);
	}
	return loading.get(key)!;
};

const release = (key: string) => {
	if (!stateApp.loadedAssets?.[key] || loading.has(key)) return;
	const { src } = assets[key as keyof typeof assets] as { src: string };
	const { [key]: _, ...rest } = stateApp.loadedAssets;
	stateApp.loadedAssets = rest;
	PIXI.Assets.unload(src).catch(() => {});
};

/** Win sheet keys a bet's book will play (cluster wins + the scatter/wild that land in them). */
export const winKeysOf = (bookEvents: BookEvent[]) => {
	const keys = new Set<string>();
	for (const event of bookEvents) {
		if (event.type !== 'winInfo') continue;
		for (const win of event.wins) keys.add(`${win.symbol}_win`);
	}
	if (bookEvents.some((event) => event.type === 'freeSpinTrigger')) keys.add('S_win');
	return [...keys].filter((key) => LAZY_WIN_KEYS.includes(key));
};

/** Start loading this round's win sheets (don't await: decoding runs while the reels spin)
 *  and release the ones it won't use. */
export const prepareWins = (bookEvents: BookEvent[]) => {
	const need = winKeysOf(bookEvents);
	for (const key of LAZY_WIN_KEYS) {
		if (!need.includes(key) && !WARM.includes(key)) release(key);
	}
	return Promise.all([...new Set([...need, ...WARM])].map(load));
};

/** the current round's prepareWins(); the win handlers await it (normally long settled) */
export const winsReady: { promise: Promise<unknown> } = { promise: Promise.resolve() };
