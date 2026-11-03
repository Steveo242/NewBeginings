import * as PIXI from 'pixi.js';
import { withTimeout } from 'pixi-svelte';

import { stateApp } from './stateApp';
import assets from './assets';
import type { BookEvent } from './typesBookEvent';
import { SYMBOL_INFO_MAP } from './constants';

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
// v5.5: a sheet is only ever destroyed when nothing can still draw it. Releasing used to
// unload (destroy every texture) the moment a new round's book came in; a symbol whose
// AnimatedSprite still held those textures for a frame or two then drew a texture with no
// source - "Cannot read properties of null (reading '_resourceId')" - and the throw in the
// render loop blanked the board. Now: a sheet must go unused for KEEP_ROUNDS rounds, it is
// first dropped from loadedAssets (so Svelte swaps every SpriteSheet off it), and it is only
// unloaded after a couple of frames when a scan of the stage finds no sprite still bound
// to it. A load that arrives while an unload is in flight waits for it first.
const KEEP_ROUNDS = 2;
const lastNeeded = new Map<string, number>();
const unloading = new Map<string, Promise<void>>();
let round = 0;

const load = async (key: string) => {
	await unloading.get(key);
	if (stateApp.loadedAssets?.[key]) return;
	if (!loading.has(key)) {
		const { src } = assets[key as keyof typeof assets] as { src: string };
		loading.set(
			key,
			withTimeout(PIXI.Assets.load<PIXI.Spritesheet>(src), 20000, key)
				.then((sheet) => {
					stateApp.loadedAssets = { ...stateApp.loadedAssets, [key]: framesOf(sheet) };
				})
				.catch((error) => console.error('win sheet', key, error))
				.finally(() => loading.delete(key)),
		);
	}
	return loading.get(key)!;
};

const frame = () => new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

/** any sprite on the stage still drawing one of these textures */
const boundTo = (textures: Set<PIXI.Texture>) => {
	const stage = stateApp.pixiApplication?.stage;
	if (!stage) return false;
	const stack: PIXI.Container[] = [stage];
	while (stack.length) {
		const node = stack.pop()!;
		if (node instanceof PIXI.Sprite) {
			if (textures.has(node.texture)) return true;
			if (node instanceof PIXI.AnimatedSprite && node.textures.some((t) => textures.has(t as PIXI.Texture))) return true;
		}
		stack.push(...node.children);
	}
	return false;
};

const release = (key: string) => {
	const frames = stateApp.loadedAssets?.[key] as PIXI.Texture[] | undefined;
	if (!frames || loading.has(key) || unloading.has(key)) return;
	const { src } = assets[key as keyof typeof assets] as { src: string };
	const textures = new Set(frames);
	const { [key]: _, ...rest } = stateApp.loadedAssets;
	stateApp.loadedAssets = rest; // every SpriteSheet on this key now swaps to no frames
	const job = (async () => {
		// let Svelte apply that and a few frames render without it; never unload while bound
		for (let tries = 0; tries < 20; tries++) {
			await frame();
			await frame();
			if (!boundTo(textures)) {
				await PIXI.Assets.unload(src).catch(() => {});
				return;
			}
			await new Promise((r) => setTimeout(r, 500));
		}
		// still bound after ~10 s: keep it (a leak beats a crash) and put it back
		stateApp.loadedAssets = { ...stateApp.loadedAssets, [key]: frames };
	})().finally(() => unloading.delete(key));
	unloading.set(key, job);
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
	installRenderGuard();
	round += 1;
	const need = winKeysOf(bookEvents);
	for (const key of need) lastNeeded.set(key, round);
	for (const key of LAZY_WIN_KEYS) {
		if (need.includes(key) || WARM.includes(key)) continue;
		if (round - (lastNeeded.get(key) ?? 0) > KEEP_ROUNDS) release(key);
	}
	return Promise.all([...new Set([...need, ...WARM])].map(load));
};

// The render loop's last line of defence: if a sprite ever draws a texture whose source is
// gone, the throw would stop every later frame (a blank board). Catch it, put the symbol's
// STATIC texture (always resident) on any such sprite at the static's size - a reviewer
// never sees a missing symbol - (the empty texture only if even that is unavailable),
// report it once to the on-screen diagnostics, and go on.
type Info = { assetKey: string; sizeRatios: { width: number; height: number } };
const dead = (t: PIXI.Texture | undefined) => !t || t.destroyed || !t.source || t.source.destroyed;
const toStatic = (node: PIXI.AnimatedSprite) => {
	// SymbolAnimatedSprite labels its sprite with the sheet key: <SYMBOL>_<state>
	const [symbol, state] = String(node.label ?? '').split('_');
	const info = (SYMBOL_INFO_MAP as unknown as Record<string, Record<string, Info>>)[symbol];
	const stat = info?.static;
	const tex = stat && (stateApp.loadedAssets?.[stat.assetKey] as PIXI.Texture | undefined);
	const from = info?.[state];
	if (!tex || dead(tex) || !from) return false;
	const w = node.width * (stat.sizeRatios.width / from.sizeRatios.width);
	const h = node.height * (stat.sizeRatios.height / from.sizeRatios.height);
	node.stop();
	node.textures = [tex];
	node.width = w;
	node.height = h;
	return true;
};
let guarded = false;
const reported = new Set<string>();
const sanitize = (root: PIXI.Container) => {
	let fixed = 0;
	const stack: PIXI.Container[] = [root];
	while (stack.length) {
		const node = stack.pop()!;
		if (node instanceof PIXI.Sprite) {
			if (node instanceof PIXI.AnimatedSprite && node.textures.some((t) => dead(t as PIXI.Texture))) {
				if (!toStatic(node)) {
					node.stop();
					node.textures = [PIXI.Texture.EMPTY];
				}
				fixed++;
			} else if (dead(node.texture)) {
				node.texture = PIXI.Texture.EMPTY;
				fixed++;
			}
		}
		stack.push(...node.children);
	}
	return fixed;
};
export const installRenderGuard = () => {
	const app = stateApp.pixiApplication;
	if (guarded || !app?.renderer) return;
	guarded = true;
	const render = app.renderer.render.bind(app.renderer) as (...a: unknown[]) => void;
	(app.renderer as unknown as { render: (...a: unknown[]) => void }).render = (...args: unknown[]) => {
		try {
			render(...args);
		} catch (error) {
			const fixed = sanitize(app.stage);
			const msg = `render recovered (${fixed} sprite(s) on a destroyed texture): ${error instanceof Error ? error.message : String(error)}`;
			console.error(msg);
			if (!reported.has(msg) && typeof window !== 'undefined') {
				reported.add(msg);
				window.dispatchEvent(new ErrorEvent('error', { message: msg }));
			}
		}
	};
};

/** the current round's prepareWins(); the win handlers await it (normally long settled) */
export const winsReady: { promise: Promise<unknown> } = { promise: Promise.resolve() };
